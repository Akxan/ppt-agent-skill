#!/usr/bin/env python3
"""HTML -> 真矢量 SVG 转换（文字保留为可编辑 <text> 元素）

核心方案：Puppeteer + dom-to-svg
- Puppeteer 在 headless 浏览器中打开 HTML
- 转换前做三类预处理：
  1. 选择性栅格化：dom-to-svg 画不出来的绘制（径向/锥形/多层渐变、filter、mask、
     background-image:url、mix-blend-mode）截成图层嵌回页面，文字与卡片保持矢量
  2. 卡片打标：给每张卡片根节点加 `pptx-card` class，供 svg2pptx 成组与做入场动画
  3. 兜底改写：简单伪元素物化、CSS border 三角形转 SVG、渐变文字改纯色
- dom-to-svg 直接将 DOM 树转为 SVG，保留 <text> 元素

降级方案：Puppeteer PDF + pdf2svg（文字变 path，不可编辑）

首次运行自动安装依赖（dom-to-svg, puppeteer, esbuild）到 skill 根目录的 node_modules。

用法：
    python3 html2svg.py <html_dir_or_file> [-o output_dir] [--no-raster]
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

CONVERT_SCRIPT = r"""
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const ISOLATE_CSS = `
html.__ppt_iso * { visibility: hidden !important; }
html.__ppt_iso:not(.__ppt_tgt), html.__ppt_iso body:not(.__ppt_tgt) { background: none !important; }
html.__ppt_iso .__ppt_anc { opacity: 1 !important; filter: none !important; mix-blend-mode: normal !important;
  -webkit-mask-image: none !important; mask-image: none !important; }
html.__ppt_iso .__ppt_tgt { visibility: visible !important; }
html.__ppt_iso.__ppt_whole .__ppt_tgt * { visibility: visible !important; }
html.__ppt_iso.__ppt_bg .__ppt_tgt { color: transparent !important; -webkit-text-fill-color: transparent !important;
  text-shadow: none !important; }
[data-ppt-baked]::before, [data-ppt-baked]::after { content: none !important; }
`;

// 在页面内找出需要栅格化的元素，打上 data-ppt-raster-id 并返回截图区域
function findRasterTargets(viewW, viewH) {
    const targets = [];
    let seq = 0;

    const unsupportedBg = (bg) => {
        if (!bg || bg === 'none') return false;
        if (/radial-gradient|conic-gradient|repeating-[a-z]+-gradient|url\(/.test(bg)) return true;
        let depth = 0;
        for (const ch of bg) {
            if (ch === '(') depth++;
            else if (ch === ')') depth--;
            else if (ch === ',' && depth === 0) return true;   // 多层背景
        }
        return false;
    };
    const flagsOf = (cs) => ({
        bg: unsupportedBg(cs.backgroundImage),
        filter: !!cs.filter && cs.filter !== 'none',
        mask: (!!cs.maskImage && cs.maskImage !== 'none') ||
              (!!cs.webkitMaskImage && cs.webkitMaskImage !== 'none'),
        blend: !!cs.mixBlendMode && cs.mixBlendMode !== 'normal',
        clip: !!cs.clipPath && cs.clipPath !== 'none',
    });
    // dom-to-svg 按包围盒输出，旋转/斜切会丢失
    const isRotated = (cs) => {
        const m = /^matrix\(([^)]+)\)$/.exec(cs.transform || '');
        if (!m) return false;
        const v = m[1].split(',').map(parseFloat);
        return Math.abs(v[1]) > 0.01 || Math.abs(v[2]) > 0.01;
    };
    const pseudoNeedsRaster = (el) => ['::before', '::after'].some((p) => {
        const cs = getComputedStyle(el, p);
        if (!cs.content || cs.content === 'none' || cs.content === 'normal') return false;
        const f = flagsOf(cs);
        return f.bg || f.filter || f.mask || f.blend || f.clip;
    });
    const blurPad = (cs) => {
        let pad = 0;
        const m = /blur\(([\d.]+)px\)/.exec(cs.filter || '');
        if (m) pad += parseFloat(m[1]) * 3;
        if (cs.boxShadow && cs.boxShadow !== 'none') pad += 48;
        return pad;
    };
    const clipRect = (r, pad) => {
        const x0 = Math.max(0, Math.floor(r.left - pad));
        const y0 = Math.max(0, Math.floor(r.top - pad));
        const x1 = Math.min(viewW, Math.ceil(r.right + pad));
        const y1 = Math.min(viewH, Math.ceil(r.bottom + pad));
        return (x1 - x0 < 1 || y1 - y0 < 1) ? null : { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
    };
    const unionRect = (el) => {
        let r = el.getBoundingClientRect();
        let box = { left: r.left, top: r.top, right: r.right, bottom: r.bottom };
        for (const d of el.querySelectorAll('*')) {
            const dr = d.getBoundingClientRect();
            if (dr.width === 0 && dr.height === 0) continue;
            box.left = Math.min(box.left, dr.left); box.top = Math.min(box.top, dr.top);
            box.right = Math.max(box.right, dr.right); box.bottom = Math.max(box.bottom, dr.bottom);
        }
        return box;
    };
    const push = (el, mode, rect, extra) => {
        if (!rect) return;
        const id = 'r' + (++seq);
        el.setAttribute('data-ppt-raster-id', id);
        targets.push(Object.assign({ id, mode }, rect, extra || {}));
    };
    const SVG_UNSUPPORTED = 'filter, pattern, mask, clipPath, use, foreignObject, textPath, marker, symbol, ' +
                            '[gradientUnits="userSpaceOnUse"], [gradientTransform]';
    // 描边引用了带透明色标的渐变（渐隐线）：矢量层只能取首色，改走位图
    const hasFadingStroke = (svg) => Array.from(svg.querySelectorAll('[stroke^="url("]')).some((node) => {
        const m = /url\(["']?#([^"')]+)/.exec(node.getAttribute('stroke'));
        const grad = m && document.getElementById(m[1]);
        return !!grad && Array.from(grad.querySelectorAll('stop')).some(
            (stop) => parseFloat(getComputedStyle(stop).stopOpacity) < 1);
    });
    const outside = (r, clip) => r.right <= clip.left || r.left >= clip.right ||
                                 r.bottom <= clip.top || r.top >= clip.bottom;
    const overflows = (r, clip) => r.left < clip.left - 1 || r.top < clip.top - 1 ||
                                   r.right > clip.right + 1 || r.bottom > clip.bottom + 1;

    // clip：祖先 overflow 裁剪区的交集（svg2pptx 不做几何裁剪，被裁掉一部分的装饰只能走位图）
    const walk = (el, clip) => {
        if (el instanceof SVGSVGElement) {
            const optIn = el.getAttribute('data-pptx') === 'raster';
            const r = el.getBoundingClientRect();
            if (clip && r.width > 0 && outside(r, clip)) {
                el.style.setProperty('visibility', 'hidden', 'important');
            } else if (optIn || el.querySelector(SVG_UNSUPPORTED) || hasFadingStroke(el) ||
                       (clip && r.width > 0 && overflows(r, clip))) {
                push(el, 'whole', clipRect(unionRect(el), 2), { svg: true });
            }
            return;
        }
        if (!(el instanceof HTMLElement)) return;
        if (['SCRIPT', 'STYLE', 'HEAD', 'META', 'LINK', 'TITLE'].includes(el.tagName)) return;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return;

        const isRoot = el === document.documentElement || el === document.body;
        const optIn = el.getAttribute('data-pptx') === 'raster';
        const f = flagsOf(cs);
        const pseudo = pseudoNeedsRaster(el);
        const rotated = !isRoot && isRotated(cs);
        const hasText = (el.innerText || '').trim().length > 0;
        const rect = el.getBoundingClientRect();
        let clipped = false;
        if (clip && !isRoot && rect.width > 0 && rect.height > 0 && !hasText) {
            if (outside(rect, clip)) {                    // 完全在裁剪区外：浏览器里本就不可见
                el.style.setProperty('visibility', 'hidden', 'important');
                return;
            }
            clipped = overflows(rect, clip);
        }
        if (optIn || rotated || clipped || f.bg || f.filter || f.mask || f.blend || f.clip || pseudo) {
            if (isRoot) {
                if (f.bg || pseudo) push(el, 'bg', { x: 0, y: 0, w: viewW, h: viewH }, { root: true });
            } else if (optIn || rotated || !hasText) {
                // 纯装饰子树（含被祖先裁剪的），或旋转元素（印章/徽标，文字一并入图）
                push(el, 'whole', clipRect(unionRect(el), blurPad(cs)));
                return;
            } else if (f.bg || f.clip || pseudo) {
                push(el, 'bg', clipRect(el.getBoundingClientRect(), blurPad(cs)));
            }
            // 带文字的容器上的 filter/mask/blend 无法保真，保持矢量并放弃该效果
        }
        let childClip = clip;
        if (!isRoot && (cs.overflowX !== 'visible' || cs.overflowY !== 'visible')) {
            childClip = clip ? {
                left: Math.max(clip.left, rect.left), top: Math.max(clip.top, rect.top),
                right: Math.min(clip.right, rect.right), bottom: Math.min(clip.bottom, rect.bottom),
            } : { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom };
        }
        for (const child of el.children) walk(child, childClip);
    };
    walk(document.documentElement, null);
    return targets;
}

function isolateTarget(t) {
    const el = document.querySelector('[data-ppt-raster-id="' + t.id + '"]');
    const root = document.documentElement;
    root.classList.add('__ppt_iso', t.mode === 'whole' ? '__ppt_whole' : '__ppt_bg');
    el.classList.add('__ppt_tgt');
    for (let a = el.parentElement; a; a = a.parentElement) a.classList.add('__ppt_anc');
}

async function replaceTarget(t, dataUrl) {
    const el = document.querySelector('[data-ppt-raster-id="' + t.id + '"]');
    const root = document.documentElement;
    root.classList.remove('__ppt_iso', '__ppt_whole', '__ppt_bg');
    el.classList.remove('__ppt_tgt');
    document.querySelectorAll('.__ppt_anc').forEach((a) => a.classList.remove('__ppt_anc'));

    const img = new Image();
    img.src = dataUrl;
    img.setAttribute('data-ppt-raster', t.mode);
    const base = 'position:absolute;left:0;top:0;margin:0;padding:0;border:0;max-width:none;max-height:none;' +
                 'pointer-events:none;visibility:visible;opacity:1;transform:none;filter:none;' +
                 'width:' + t.w + 'px;height:' + t.h + 'px;';
    const important = (node, props) => {
        for (const [k, v] of Object.entries(props)) node.style.setProperty(k, v, 'important');
    };

    if (t.root) {
        img.style.cssText = base + 'z-index:-2147483000;';
        document.body.appendChild(img);
        important(document.documentElement, { background: 'none' });
        important(document.body, { background: 'none' });
        document.body.setAttribute('data-ppt-baked', '1');
    } else if (t.svg) {
        // 内联 SVG：原图隐藏占位，位图紧随其后
        const z = getComputedStyle(el).zIndex;
        img.style.cssText = base + (z !== 'auto' ? 'z-index:' + z + ';' : '');
        important(el, { visibility: 'hidden' });
        el.after(img);
    } else if (t.mode === 'whole') {
        // 元素保留盒子（不影响布局与 nth-child），自身绘制清空，子节点隐藏，位图作为子节点
        for (const child of el.children) important(child, { visibility: 'hidden' });
        important(el, {
            'background': 'none', 'border-color': 'transparent', 'box-shadow': 'none', 'filter': 'none',
            'mask-image': 'none', '-webkit-mask-image': 'none', 'mix-blend-mode': 'normal', 'opacity': '1',
            'overflow': 'visible', 'clip-path': 'none', 'transform': 'none', 'outline': 'none',
            // 元素自身的文字节点已在位图里，矢量层不再输出（svg2pptx 跳过全透明文字）
            'color': 'transparent', '-webkit-text-fill-color': 'transparent', 'text-shadow': 'none',
        });
        el.setAttribute('data-ppt-baked', '1');
        img.style.cssText = base;
        el.appendChild(img);
    } else {
        // 只烘焙背景/边框/伪元素，子内容保持矢量
        important(el, {
            'isolation': 'isolate', 'background-image': 'none', 'background-color': 'transparent',
            'border-color': 'transparent', 'box-shadow': 'none',
        });
        el.setAttribute('data-ppt-baked', '1');
        img.style.cssText = base + 'z-index:-1;';
        el.appendChild(img);
    }
    // 位图定位到截图区域（按实测位置校正，不依赖包含块）
    const r = img.getBoundingClientRect();
    img.style.left = (t.x - r.left) + 'px';
    img.style.top = (t.y - r.top) + 'px';
    try { await img.decode(); } catch (e) { /* 解码失败时仍继续 */ }
}

// 卡片打标：优先 data-card-id，其次 class 以 card 结尾的最外层元素
function markCards() {
    let cards = Array.from(document.querySelectorAll('[data-card-id]'));
    if (!cards.length) {
        cards = Array.from(document.querySelectorAll('[class]')).filter((el) =>
            Array.from(el.classList).some((c) => /(^|[-_])card$/i.test(c)));
    }
    cards = cards.filter((el) => !cards.some((o) => o !== el && o.contains(el)));
    cards.forEach((el) => el.classList.add('pptx-card'));
    return cards.length;
}

// 兜底改写：dom-to-svg 读不到的简单 CSS 特性转成真实 DOM / 标准属性
function applyFallbacks() {
    // 0. SVG 渐变色标里的 var(--x) 解析成实际颜色（dom-to-svg 会原样输出 var()，下游认不出）
    for (const stop of document.querySelectorAll('svg stop')) {
        const cs = getComputedStyle(stop);
        stop.setAttribute('stop-color', cs.stopColor);
        stop.setAttribute('stop-opacity', cs.stopOpacity);
    }

    // 1. CSS border 三角形（内容盒为 0、仅一条有色边框）改为 SVG polygon
    //    用 clientWidth 判定：border-box 下 computed width 含边框，永远不为 0
    for (const el of document.querySelectorAll('*')) {
        if (!(el instanceof HTMLElement) || el.clientWidth !== 0 || el.clientHeight !== 0) continue;
        if (el.children.length || (el.textContent || '').trim()) continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'inline' || cs.display === 'none') continue;
        const sides = ['Top', 'Right', 'Bottom', 'Left'].map((s) => ({
            dir: s.toLowerCase(),
            size: parseFloat(cs['border' + s + 'Width']) || 0,
            color: cs['border' + s + 'Color'],
        }));
        if (sides.filter((s) => s.size > 0).length < 2) continue;
        const solid = sides.filter((s) => s.size > 0 && s.color !== 'transparent' && !/,\s*0\)$/.test(s.color));
        if (solid.length !== 1) continue;

        const [bt, br, bb, bl] = sides.map((s) => s.size);
        const totalW = bl + br, totalH = bt + bb;
        el.style.width = totalW + 'px';
        el.style.height = totalH + 'px';
        el.style.border = 'none';
        const svgNS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(svgNS, 'svg');
        svg.setAttribute('width', String(totalW));
        svg.setAttribute('height', String(totalH));
        svg.style.display = 'block';
        svg.style.overflow = 'visible';
        // 有色边在哪一侧，三角形的底边就在哪一侧，尖角指向对侧
        const points = {
            bottom: `${totalW / 2},0 0,${totalH} ${totalW},${totalH}`,
            top: `0,0 ${totalW},0 ${totalW / 2},${totalH}`,
            left: `0,0 ${totalW},${totalH / 2} 0,${totalH}`,
            right: `${totalW},0 0,${totalH / 2} ${totalW},${totalH}`,
        }[solid[0].dir];
        const polygon = document.createElementNS(svgNS, 'polygon');
        polygon.setAttribute('points', points);
        polygon.setAttribute('fill', solid[0].color);
        svg.appendChild(polygon);
        el.appendChild(svg);
    }

    // 2. background-clip:text 渐变文字 -> 取渐变首色作为文字颜色
    for (const el of document.querySelectorAll('*')) {
        const cs = getComputedStyle(el);
        if ((cs.webkitBackgroundClip || cs.backgroundClip) !== 'text') continue;
        const m = (cs.backgroundImage || '').match(/(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))/);
        el.style.backgroundImage = 'none';
        el.style.background = 'none';
        el.style.webkitBackgroundClip = 'border-box';
        el.style.backgroundClip = 'border-box';
        el.style.webkitTextFillColor = 'unset';
        el.style.color = m ? m[1] : cs.color;
    }

    // 3. 独立使用的 -webkit-text-fill-color -> 标准 color
    for (const el of document.querySelectorAll('*')) {
        const cs = getComputedStyle(el);
        const fill = cs.webkitTextFillColor;
        if (!fill || fill === cs.color || fill === 'rgba(0, 0, 0, 0)' || fill === 'transparent') continue;
        el.style.color = fill;
        el.style.webkitTextFillColor = 'unset';
    }
}

(async () => {
    const config = JSON.parse(process.argv[2]);
    const VIEW = { width: 1280, height: 720 };
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--font-render-hinting=none']
    });

    for (const item of config.files) {
        const page = await browser.newPage();
        await page.setViewport({ ...VIEW, deviceScaleFactor: config.scale });
        await page.goto('file://' + item.html, { waitUntil: 'networkidle0', timeout: 30000 });
        await page.evaluate(async () => {
            await document.fonts.ready;
            await Promise.all(Array.from(document.images).map((img) =>
                img.complete ? null : new Promise((r) => { img.onload = r; img.onerror = r; })));
        });
        await page.addScriptTag({ path: config.bundlePath });

        // 卡片打标必须在栅格化之前（栅格化会追加 img 子节点）
        const cardCount = await page.evaluate(markCards);

        let rasterCount = 0;
        if (config.raster) {
            await page.addStyleTag({ content: ISOLATE_CSS });
            const targets = await page.evaluate(findRasterTargets, VIEW.width, VIEW.height);
            for (const t of targets) {
                await page.evaluate(isolateTarget, t);
                // 大面积透明图层按 1x 截取（柔光/纹理不需要 2x，PNG 体积差 4 倍）；背景与小图层保持高清
                const large = !t.root && t.w * t.h >= 400000;
                const shot = await page.screenshot({
                    clip: { x: t.x, y: t.y, width: t.w, height: t.h, scale: large ? 1 / config.scale : 1 },
                    omitBackground: !t.root,
                    type: t.root ? 'jpeg' : 'png',
                    ...(t.root ? { quality: 92 } : {}),
                    encoding: 'base64',
                });
                const mime = t.root ? 'image/jpeg' : 'image/png';
                await page.evaluate(replaceTarget, t, 'data:' + mime + ';base64,' + shot);
                rasterCount++;
            }
        }

        if (config.fallbacks) await page.evaluate(applyFallbacks);

        const svgString = await page.evaluate(async () => {
            const { documentToSVG, inlineResources } = window.__domToSvg;
            const svgDoc = documentToSVG(document);
            await inlineResources(svgDoc.documentElement);
            for (const t of svgDoc.querySelectorAll('text')) {
                const c = t.getAttribute('color');
                if (c && !t.getAttribute('fill')) {
                    t.setAttribute('fill', c);
                    t.removeAttribute('color');
                }
            }
            return new XMLSerializer().serializeToString(svgDoc);
        });

        fs.writeFileSync(item.svg, svgString, 'utf-8');
        console.log('SVG: ' + path.basename(item.html) + ' (cards=' + cardCount + ', raster layers=' + rasterCount + ')');
        await page.close();
    }

    await browser.close();
    console.log('Done: ' + config.files.length + ' SVGs');
})();
"""

FALLBACK_SCRIPT = r"""
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
    const config = JSON.parse(process.argv[2]);
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });
    for (const item of config.files) {
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720 });
        await page.goto('file://' + item.html, { waitUntil: 'networkidle0', timeout: 30000 });
        await page.pdf({ path: item.pdf, width: '1280px', height: '720px',
                         printBackground: true, preferCSSPageSize: true });
        console.log('PDF: ' + path.basename(item.html));
        await page.close();
    }
    await browser.close();
})();
"""

BUNDLE_ENTRY = """
import { documentToSVG, elementToSVG, inlineResources } from 'dom-to-svg';
window.__domToSvg = { documentToSVG, elementToSVG, inlineResources };
"""

# 依赖装在 skill 根目录，跨次调用复用（puppeteer 约 55MB，不值得每个输出目录装一份）
WORK_DIR = Path(__file__).resolve().parent.parent


def natural_key(path: Path) -> list:
    """自然排序：slide-2 排在 slide-10 前面。"""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def _node_can_require(module: str) -> bool:
    result = subprocess.run(["node", "-e", f"require('{module}')"],
                            capture_output=True, text=True, timeout=20, cwd=str(WORK_DIR))
    return result.returncode == 0


def _ensure_module(module: str, timeout: int) -> bool:
    if _node_can_require(module):
        return True
    print(f"Installing {module}...")
    subprocess.run(["npm", "install", module], capture_output=True, text=True, timeout=timeout, cwd=str(WORK_DIR))
    return _node_can_require(module)


def ensure_puppeteer() -> bool:
    """确保 skill 根目录装有 puppeteer（html2png.py 也用这个入口）。"""
    if not shutil.which("node") or not shutil.which("npm"):
        print("Node.js/npm not found. Install Node.js >= 18 and retry.", file=sys.stderr)
        return False
    if not _ensure_module("puppeteer", 300):
        print("puppeteer unavailable", file=sys.stderr)
        return False
    return True


def ensure_deps() -> tuple:
    """安装依赖，返回 (方案名, bundle 路径)。方案名: dom-to-svg / pdf2svg / none"""
    if not ensure_puppeteer():
        return ("none", None)
    if not _ensure_module("dom-to-svg", 120):
        print("dom-to-svg unavailable, using pdf2svg fallback", file=sys.stderr)
        return ("pdf2svg", None)

    bundle_path = WORK_DIR / "dom-to-svg.bundle.js"
    if not bundle_path.exists():
        print("Building dom-to-svg browser bundle...")
        entry_path = WORK_DIR / ".bundle_entry.js"
        entry_path.write_text(BUNDLE_ENTRY)
        try:
            result = subprocess.run(
                ["npx", "-y", "esbuild", str(entry_path), "--bundle", "--format=iife",
                 f"--outfile={bundle_path}", "--platform=browser"],
                capture_output=True, text=True, timeout=120, cwd=str(WORK_DIR))
        finally:
            entry_path.unlink(missing_ok=True)
        if result.returncode != 0:
            print(f"esbuild failed: {result.stderr}", file=sys.stderr)
            return ("pdf2svg", None)

    return ("dom-to-svg", str(bundle_path))


def run_node(script: str, config: dict, tmp_name: str) -> bool:
    script_path = WORK_DIR / tmp_name
    script_path.write_text(script)
    try:
        result = subprocess.run(["node", str(script_path), json.dumps(config)],
                                cwd=str(WORK_DIR), timeout=600)
        return result.returncode == 0
    finally:
        script_path.unlink(missing_ok=True)


def convert_dom_to_svg(html_files, output_dir, bundle_path, raster=True, scale=2.0, fallbacks=True) -> bool:
    config = {
        "bundlePath": bundle_path,
        "raster": raster,
        "fallbacks": fallbacks,
        "scale": scale,
        "files": [{"html": str(f), "svg": str(output_dir / (f.stem + ".svg"))} for f in html_files],
    }
    print(f"Converting {len(html_files)} HTML files (dom-to-svg, text editable)...")
    return run_node(CONVERT_SCRIPT, config, ".dom2svg_tmp.js")


def convert_pdf2svg(html_files, output_dir) -> bool:
    """降级方案：Puppeteer PDF + pdf2svg（文字变 path，不可编辑）"""
    if not shutil.which("pdf2svg"):
        print("pdf2svg not found (macOS: brew install pdf2svg / Debian: apt install pdf2svg)", file=sys.stderr)
        return False

    pdf_tmp = WORK_DIR / ".pdf_tmp"
    pdf_tmp.mkdir(exist_ok=True)
    config = {"files": [{"html": str(f), "pdf": str(pdf_tmp / (f.stem + ".pdf"))} for f in html_files]}
    try:
        print(f"Step 1/2: HTML -> PDF ({len(html_files)} files)...")
        if not run_node(FALLBACK_SCRIPT, config, ".fallback_tmp.js"):
            return False
        print("Step 2/2: PDF -> SVG (WARNING: text becomes paths, NOT editable)...")
        success = 0
        for item in config["files"]:
            svg_path = output_dir / (Path(item["pdf"]).stem + ".svg")
            result = subprocess.run(["pdf2svg", item["pdf"], str(svg_path)],
                                    capture_output=True, text=True, timeout=60)
            success += result.returncode == 0
        return success > 0
    finally:
        shutil.rmtree(pdf_tmp, ignore_errors=True)


def convert(html_path: Path, output_dir: Path, raster: bool = True, scale: float = 2.0,
            fallbacks: bool = True) -> bool:
    html_files = [html_path] if html_path.is_file() else sorted(html_path.glob("*.html"), key=natural_key)
    if not html_files:
        print(f"No HTML files in {html_path}", file=sys.stderr)
        return False

    output_dir.mkdir(parents=True, exist_ok=True)
    method, bundle_path = ensure_deps()
    if method == "none":
        return False
    if method == "dom-to-svg":
        if convert_dom_to_svg(html_files, output_dir, bundle_path, raster=raster, scale=scale,
                              fallbacks=fallbacks):
            print(f"\nDone! {len(html_files)} SVGs -> {output_dir}")
            return True
        print("dom-to-svg failed, falling back to pdf2svg...")
    return convert_pdf2svg(html_files, output_dir)


def main():
    parser = argparse.ArgumentParser(description="HTML -> SVG (editable text, unsupported paint rasterized)")
    parser.add_argument("path", help="HTML file or directory of slides")
    parser.add_argument("-o", "--output", help="Output directory (default: <slides parent>/svg)")
    parser.add_argument("--no-raster", action="store_true",
                        help="Skip selective rasterization (unsupported backgrounds/filters will be lost)")
    parser.add_argument("--no-fallbacks", action="store_true", help=argparse.SUPPRESS)  # 调试用
    parser.add_argument("--scale", type=float, default=2.0,
                        help="Device pixel ratio for rasterized layers (default: 2)")
    args = parser.parse_args()

    html_path = Path(args.path).resolve()
    output_dir = Path(args.output).resolve() if args.output else html_path.parent / "svg"
    ok = convert(html_path, output_dir, raster=not args.no_raster, scale=args.scale,
                 fallbacks=not args.no_fallbacks)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
