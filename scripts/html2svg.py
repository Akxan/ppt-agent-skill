#!/usr/bin/env python3
"""HTML -> 真矢量 SVG 转换（文字保留为可编辑 <text> 元素）

核心方案：Puppeteer + dom-to-svg
- Puppeteer 在 headless 浏览器中打开 HTML
- dom-to-svg 直接将 DOM 树转为 SVG，保留 <text> 元素
- 不经过 PDF 中转，文字不会变成 path

降级方案：Puppeteer PDF + pdf2svg（文字变 path，不可编辑）

首次运行自动安装依赖（dom-to-svg, puppeteer, esbuild）。

用法：
    python3 html2svg.py <html_dir_or_file> [-o output_dir]
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

_NPM = "npm.cmd" if platform.system() == "Windows" else "npm"

# Puppeteer + dom-to-svg bundle 注入脚本
CONVERT_SCRIPT = r"""
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
    const config = JSON.parse(process.argv[2]);
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu',
               '--font-render-hinting=none']
    });

    for (const item of config.files) {
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720 });

        await page.goto('file://' + item.html, {
            waitUntil: 'networkidle0',
            timeout: 30000
        });
        await new Promise(r => setTimeout(r, 500));

        // 注入预打包的 dom-to-svg bundle
        await page.addScriptTag({ path: config.bundlePath });

        // 预处理：在 Node.js 端读取图片文件转 base64，传给浏览器替换 src
        // (浏览器端 canvas.toDataURL 会因 file:// CORS 被阻止)
        const imgSrcs = await page.evaluate(() => {
            const imgs = document.querySelectorAll('img');
            return Array.from(imgs).map(img => img.getAttribute('src') || '');
        });

        const imgDataMap = {};
        const htmlDir = path.dirname(item.html);  // HTML文件所在目录
        for (const src of imgSrcs) {
            if (!src) continue;
            if (src.startsWith('data:')) continue;  // 跳过已内联的
            // 处理 file:// 和绝对/相对路径
            let filePath = src;
            if (filePath.startsWith('file://')) filePath = filePath.slice(7);
            // 相对路径以HTML文件所在目录为基准resolve
            if (!path.isAbsolute(filePath)) {
                filePath = path.resolve(htmlDir, filePath);
            }
            if (fs.existsSync(filePath)) {
                const data = fs.readFileSync(filePath);
                const ext = path.extname(filePath).slice(1) || 'png';
                const mime = ext === 'jpg' ? 'image/jpeg' : `image/${ext}`;
                imgDataMap[src] = `data:${mime};base64,${data.toString('base64')}`;
            } else {
                console.warn('Image not found:', filePath, '(src:', src, ')');
            }
        }

        if (Object.keys(imgDataMap).length > 0) {
            await page.evaluate((dataMap) => {
                const imgs = document.querySelectorAll('img');
                for (const img of imgs) {
                    const origSrc = img.getAttribute('src');
                    if (origSrc && dataMap[origSrc]) {
                        img.src = dataMap[origSrc];
                    }
                }
            }, imgDataMap);
            // 等待图片重新渲染
            await new Promise(r => setTimeout(r, 300));
        }

        // === 预处理：将 dom-to-svg 不支持的 CSS 特性转为真实 DOM ===
        await page.evaluate(() => {
            // 1. 物化伪元素 ::before / ::after -> 真实 span
            // dom-to-svg 无法读取 CSS 伪元素，导致箭头/装饰丢失
            const all = document.querySelectorAll('*');
            for (const el of all) {
                for (const pseudo of ['::before', '::after']) {
                    const style = getComputedStyle(el, pseudo);
                    const content = style.content;
                    if (!content || content === 'none' || content === '""' || content === "''") continue;

                    const w = parseFloat(style.width) || 0;
                    const h = parseFloat(style.height) || 0;
                    const bg = style.backgroundColor;
                    const border = style.borderTopWidth;
                    const borderColor = style.borderTopColor;

                    // 只处理有尺寸或有边框的伪元素（箭头/装饰块）
                    if ((w > 0 || h > 0 || parseFloat(border) > 0) && content !== 'normal') {
                        const span = document.createElement('span');
                        span.style.display = style.display === 'none' ? 'none' : 'inline-block';
                        span.style.position = style.position;
                        span.style.width = style.width;
                        span.style.height = style.height;
                        span.style.backgroundColor = bg;
                        span.style.borderTop = style.borderTop;
                        span.style.borderRight = style.borderRight;
                        span.style.borderBottom = style.borderBottom;
                        span.style.borderLeft = style.borderLeft;
                        span.style.transform = style.transform;
                        span.style.top = style.top;
                        span.style.left = style.left;
                        span.style.right = style.right;
                        span.style.bottom = style.bottom;
                        span.style.borderRadius = style.borderRadius;
                        span.setAttribute('data-pseudo', pseudo);

                        // 文本内容（去掉引号）
                        const textContent = content.replace(/^["']|["']$/g, '');
                        if (textContent && textContent !== 'normal' && textContent !== 'none') {
                            span.textContent = textContent;
                            span.style.color = style.color;
                            span.style.fontSize = style.fontSize;
                            span.style.fontWeight = style.fontWeight;
                        }

                        if (pseudo === '::before') {
                            el.insertBefore(span, el.firstChild);
                        } else {
                            el.appendChild(span);
                        }
                    }
                }
            }

            // 2. 将 conic-gradient 环形图转为 SVG
            // 查找带有 conic-gradient 背景的元素
            for (const el of document.querySelectorAll('*')) {
                const bg = el.style.background || el.style.backgroundImage || '';
                const computed = getComputedStyle(el);
                const bgImage = computed.backgroundImage || '';

                if (!bgImage.includes('conic-gradient')) continue;

                const rect = el.getBoundingClientRect();
                const size = Math.min(rect.width, rect.height);
                if (size <= 0) continue;

                // 解析 conic-gradient 的百分比和颜色
                const match = bgImage.match(/conic-gradient\(([^)]+)\)/);
                if (!match) continue;

                const gradStr = match[1];
                // 提取百分比（典型格式: #color 0% 75%, #color2 75% 100%）
                const percMatch = gradStr.match(/([\d.]+)%/g);
                let percentage = 75; // 默认
                if (percMatch && percMatch.length >= 2) {
                    percentage = parseFloat(percMatch[1]);
                }

                // 提取颜色
                const colorMatch = gradStr.match(/(#[0-9a-fA-F]{3,8}|rgb[a]?\([^)]+\))/g);
                const mainColor = colorMatch ? colorMatch[0] : '#4CAF50';
                const bgColor = colorMatch && colorMatch.length > 1 ? colorMatch[1] : '#e0e0e0';

                // 创建 SVG 替换
                const svgNS = 'http://www.w3.org/2000/svg';
                const svg = document.createElementNS(svgNS, 'svg');
                svg.setAttribute('width', String(size));
                svg.setAttribute('height', String(size));
                svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
                svg.style.display = el.style.display || 'block';
                svg.style.position = computed.position;
                svg.style.top = computed.top;
                svg.style.left = computed.left;

                const cx = size / 2, cy = size / 2;
                const r = size * 0.4;
                const circumference = 2 * Math.PI * r;
                const strokeWidth = size * 0.15;

                // 背景圆环
                const bgCircle = document.createElementNS(svgNS, 'circle');
                bgCircle.setAttribute('cx', String(cx));
                bgCircle.setAttribute('cy', String(cy));
                bgCircle.setAttribute('r', String(r));
                bgCircle.setAttribute('fill', 'none');
                bgCircle.setAttribute('stroke', bgColor);
                bgCircle.setAttribute('stroke-width', String(strokeWidth));

                // 进度圆环
                const fgCircle = document.createElementNS(svgNS, 'circle');
                fgCircle.setAttribute('cx', String(cx));
                fgCircle.setAttribute('cy', String(cy));
                fgCircle.setAttribute('r', String(r));
                fgCircle.setAttribute('fill', 'none');
                fgCircle.setAttribute('stroke', mainColor);
                fgCircle.setAttribute('stroke-width', String(strokeWidth));
                fgCircle.setAttribute('stroke-dasharray', `${circumference * percentage / 100} ${circumference}`);
                fgCircle.setAttribute('stroke-linecap', 'round');
                fgCircle.setAttribute('transform', `rotate(-90 ${cx} ${cy})`);

                svg.appendChild(bgCircle);
                svg.appendChild(fgCircle);

                // 保留子元素（如百分比文字），放到 foreignObject 不行
                // 直接添加 SVG text
                const textEl = el.querySelector('*');
                if (el.textContent && el.textContent.trim()) {
                    const svgText = document.createElementNS(svgNS, 'text');
                    svgText.setAttribute('x', String(cx));
                    svgText.setAttribute('y', String(cy));
                    svgText.setAttribute('text-anchor', 'middle');
                    svgText.setAttribute('dominant-baseline', 'central');
                    svgText.setAttribute('fill', computed.color);
                    svgText.setAttribute('font-size', computed.fontSize);
                    svgText.setAttribute('font-weight', computed.fontWeight);
                    svgText.textContent = el.textContent.trim();
                    svg.appendChild(svgText);
                }

                el.style.background = 'none';
                el.style.backgroundImage = 'none';
                el.insertBefore(svg, el.firstChild);
            }

            // 3. 将 CSS border 三角形箭头修复
            // 查找宽高为 0 但有 border 的元素（CSS 三角形技巧）
            for (const el of document.querySelectorAll('*')) {
                const cs = getComputedStyle(el);
                const w = parseFloat(cs.width);
                const h = parseFloat(cs.height);
                if (w !== 0 || h !== 0) continue;

                const bt = parseFloat(cs.borderTopWidth) || 0;
                const br = parseFloat(cs.borderRightWidth) || 0;
                const bb = parseFloat(cs.borderBottomWidth) || 0;
                const bl = parseFloat(cs.borderLeftWidth) || 0;

                // 至少两个边框有宽度才是三角形
                const borders = [bt, br, bb, bl].filter(v => v > 0);
                if (borders.length < 2) continue;

                const btc = cs.borderTopColor;
                const brc = cs.borderRightColor;
                const bbc = cs.borderBottomColor;
                const blc = cs.borderLeftColor;

                // 找有色边框（非 transparent）
                const nonTransparent = [];
                if (bt > 0 && !btc.includes('0)') && btc !== 'transparent') nonTransparent.push({dir: 'top', size: bt, color: btc});
                if (br > 0 && !brc.includes('0)') && brc !== 'transparent') nonTransparent.push({dir: 'right', size: br, color: brc});
                if (bb > 0 && !bbc.includes('0)') && bbc !== 'transparent') nonTransparent.push({dir: 'bottom', size: bb, color: bbc});
                if (bl > 0 && !blc.includes('0)') && blc !== 'transparent') nonTransparent.push({dir: 'left', size: bl, color: blc});

                if (nonTransparent.length !== 1) continue;

                // 用实际尺寸的 div 替换
                const arrow = nonTransparent[0];
                const totalW = bl + br;
                const totalH = bt + bb;
                el.style.width = totalW + 'px';
                el.style.height = totalH + 'px';
                el.style.border = 'none';

                // 用 SVG 绘制三角形
                const svgNS = 'http://www.w3.org/2000/svg';
                const svg = document.createElementNS(svgNS, 'svg');
                svg.setAttribute('width', String(totalW));
                svg.setAttribute('height', String(totalH));
                svg.style.display = 'block';
                svg.style.overflow = 'visible';

                const polygon = document.createElementNS(svgNS, 'polygon');
                let points = '';
                if (arrow.dir === 'bottom') points = `0,0 ${totalW},0 ${totalW/2},${totalH}`;
                else if (arrow.dir === 'top') points = `${totalW/2},0 0,${totalH} ${totalW},${totalH}`;
                else if (arrow.dir === 'right') points = `0,0 ${totalW},${totalH/2} 0,${totalH}`;
                else if (arrow.dir === 'left') points = `${totalW},0 0,${totalH/2} ${totalW},${totalH}`;
                polygon.setAttribute('points', points);
                polygon.setAttribute('fill', arrow.color);
                svg.appendChild(polygon);
                el.appendChild(svg);
            }

            // 4. 修复 background-clip: text 渐变文字
            // dom-to-svg 不支持此特性，导致渐变背景变成色块、文字变白
            for (const el of document.querySelectorAll('*')) {
                const cs = getComputedStyle(el);
                const bgClip = cs.webkitBackgroundClip || cs.backgroundClip || '';
                if (bgClip !== 'text') continue;

                // 提取渐变/背景中的主色作为文字颜色
                const bgImage = cs.backgroundImage || '';
                let mainColor = '#FF6900'; // fallback
                const colorMatch = bgImage.match(/(#[0-9a-fA-F]{3,8}|rgb[a]?\([^)]+\))/);
                if (colorMatch) mainColor = colorMatch[1];

                // 清除渐变背景效果，改用直接 color
                el.style.backgroundImage = 'none';
                el.style.background = 'none';
                el.style.webkitBackgroundClip = 'border-box';
                el.style.backgroundClip = 'border-box';
                el.style.webkitTextFillColor = 'unset';
                el.style.color = mainColor;
                console.warn('html2svg fallback: background-clip:text -> color:' + mainColor, el.tagName);
            }

            // 5. 修复 -webkit-text-fill-color（非 background-clip:text 的独立使用）
            for (const el of document.querySelectorAll('*')) {
                const cs = getComputedStyle(el);
                const fillColor = cs.webkitTextFillColor;
                if (!fillColor || fillColor === cs.color) continue;
                // 如果 text-fill-color 与 color 不同，SVG 中会丢失
                // 将 text-fill-color 值应用到 color
                if (fillColor !== 'rgba(0, 0, 0, 0)' && fillColor !== 'transparent') {
                    el.style.color = fillColor;
                    el.style.webkitTextFillColor = 'unset';
                }
            }

            // 6. 修复 mask-image / -webkit-mask-image（SVG 不支持）
            // 根据元素层级智能降级：底层图片降透明度，前景元素直接移除蒙版
            for (const el of document.querySelectorAll('*')) {
                const cs = getComputedStyle(el);
                const maskImg = cs.maskImage || cs.webkitMaskImage || '';
                if (!maskImg || maskImg === 'none') continue;

                // 清除 mask
                el.style.maskImage = 'none';
                el.style.webkitMaskImage = 'none';

                // 判断是否为底层装饰图片（通过 z-index、pointer-events、opacity 推断）
                const zIndex = parseInt(cs.zIndex) || 0;
                const pointerEvents = cs.pointerEvents;
                const isImg = el.tagName === 'IMG';
                const currentOpacity = parseFloat(cs.opacity) || 1;

                if (isImg || pointerEvents === 'none' || zIndex <= 0) {
                    // 底层氛围图：降低透明度 + 限制尺寸，不要遮挡内容
                    const newOpacity = Math.min(currentOpacity, 0.15);
                    el.style.opacity = String(newOpacity);
                    // 如果图片过大，限制为容器的合理比例
                    if (isImg) {
                        const parent = el.parentElement;
                        if (parent) {
                            const parentRect = parent.getBoundingClientRect();
                            const elRect = el.getBoundingClientRect();
                            if (elRect.width > parentRect.width * 0.8) {
                                el.style.maxWidth = '60%';
                                el.style.maxHeight = '60%';
                            }
                        }
                    }
                    console.warn('html2svg fallback: mask-image -> opacity:' + newOpacity + ' (background layer)', el.tagName);
                } else {
                    // 前景元素：只移除蒙版，保持原样
                    console.warn('html2svg fallback: mask-image removed (foreground)', el.tagName);
                }
            }
        });
        await new Promise(r => setTimeout(r, 300));

        // === 执行 DOM -> SVG 转换 ===
        let svgString = await page.evaluate(async () => {
            const { documentToSVG, inlineResources } = window.__domToSvg;
            const svgDoc = documentToSVG(document);
            await inlineResources(svgDoc.documentElement);

            // 后处理：将 <text> 的 color 属性转为 fill（SVG 标准）
            const texts = svgDoc.querySelectorAll('text');
            for (const t of texts) {
                const c = t.getAttribute('color');
                if (c && !t.getAttribute('fill')) {
                    t.setAttribute('fill', c);
                    t.removeAttribute('color');
                }
            }

            return new XMLSerializer().serializeToString(svgDoc);
        });

        fs.writeFileSync(item.svg, svgString, 'utf-8');
        console.log('SVG: ' + path.basename(item.html));
        await page.close();
    }

    await browser.close();
    console.log('Done: ' + config.files.length + ' SVGs');
})();
"""

# 降级 PDF 方案脚本
FALLBACK_SCRIPT = r"""
const puppeteer = require('puppeteer');
const fs = require('fs');
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
        await page.goto('file://' + item.html, {
            waitUntil: 'networkidle0',
            timeout: 30000
        });
        await new Promise(r => setTimeout(r, 500));
        await page.pdf({
            path: item.pdf,
            width: '1280px',
            height: '720px',
            printBackground: true,
            preferCSSPageSize: true
        });
        console.log('PDF: ' + path.basename(item.html));
        await page.close();
    }
    await browser.close();
    console.log('Done: ' + config.files.length + ' PDFs');
})();
"""

# esbuild 打包入口
BUNDLE_ENTRY = """
import { documentToSVG, elementToSVG, inlineResources } from 'dom-to-svg';
window.__domToSvg = { documentToSVG, elementToSVG, inlineResources };
"""


def ensure_deps(work_dir: Path) -> tuple:
    """安装依赖，返回 (方案名, bundle路径)"""
    # puppeteer
    r = subprocess.run(
        ["node", "-e", "require('puppeteer')"],
        capture_output=True, text=True, timeout=10, cwd=str(work_dir)
    )
    if r.returncode != 0:
        print("Installing puppeteer...")
        subprocess.run([_NPM, "install", "puppeteer"],
                       capture_output=True, text=True, timeout=180, cwd=str(work_dir))

    # dom-to-svg
    r = subprocess.run(
        ["node", "-e", "require('dom-to-svg')"],
        capture_output=True, text=True, timeout=10, cwd=str(work_dir)
    )
    if r.returncode != 0:
        print("Installing dom-to-svg...")
        subprocess.run([_NPM, "install", "dom-to-svg"],
                       capture_output=True, text=True, timeout=60, cwd=str(work_dir))
        r = subprocess.run(
            ["node", "-e", "require('dom-to-svg')"],
            capture_output=True, text=True, timeout=10, cwd=str(work_dir)
        )

    if r.returncode != 0:
        print("dom-to-svg unavailable, using pdf2svg fallback", file=sys.stderr)
        return ("pdf2svg", None)

    # 打包 dom-to-svg 为浏览器 bundle
    bundle_path = work_dir / "dom-to-svg.bundle.js"
    if not bundle_path.exists():
        print("Building dom-to-svg browser bundle...")
        entry_path = work_dir / ".bundle_entry.js"
        entry_path.write_text(BUNDLE_ENTRY)
        r = subprocess.run(
            ["npx.cmd" if platform.system() == "Windows" else "npx", "-y", "esbuild", str(entry_path),
             "--bundle", "--format=iife",
             f"--outfile={bundle_path}", "--platform=browser"],
            capture_output=True, text=True, timeout=60, cwd=str(work_dir)
        )
        if entry_path.exists():
            entry_path.unlink()
        if r.returncode != 0:
            print(f"esbuild failed: {r.stderr}", file=sys.stderr)
            return ("pdf2svg", None)

    return ("dom-to-svg", str(bundle_path))


def convert_dom_to_svg(html_files, output_dir, work_dir, bundle_path):
    """用 dom-to-svg 方案转换"""
    config = {
        "bundlePath": bundle_path,
        "files": [
            {"html": str(f), "svg": str(output_dir / (f.stem + ".svg"))}
            for f in html_files
        ]
    }

    script_path = work_dir / ".dom2svg_tmp.js"
    script_path.write_text(CONVERT_SCRIPT)

    try:
        print(f"Converting {len(html_files)} HTML files (dom-to-svg, text editable)...")
        r = subprocess.run(
            ["node", str(script_path), json.dumps(config)],
            cwd=str(work_dir), timeout=300
        )
        if r.returncode != 0:
            return False

        # 验证是否有 <text> 元素
        first_svg = output_dir / (html_files[0].stem + ".svg")
        if first_svg.exists():
            content = first_svg.read_text(errors="ignore")
            text_count = content.count("<text ")
            print(f"Text elements: {text_count} (editable in PPT)")
        return True
    finally:
        if script_path.exists():
            script_path.unlink()


def convert_pdf2svg(html_files, output_dir, work_dir):
    """降级方案：Puppeteer PDF + pdf2svg"""
    if not shutil.which("pdf2svg"):
        print("pdf2svg not found. Install: sudo apt install pdf2svg", file=sys.stderr)
        return False

    pdf_tmp = work_dir / ".pdf_tmp"
    pdf_tmp.mkdir(exist_ok=True)

    config = {
        "files": [
            {"html": str(f), "pdf": str(pdf_tmp / (f.stem + ".pdf"))}
            for f in html_files
        ]
    }

    script_path = work_dir / ".fallback_tmp.js"
    script_path.write_text(FALLBACK_SCRIPT)

    try:
        print(f"Step 1/2: HTML -> PDF ({len(html_files)} files)...")
        r = subprocess.run(
            ["node", str(script_path), json.dumps(config)],
            cwd=str(work_dir), timeout=300
        )
        if r.returncode != 0:
            return False

        print("Step 2/2: PDF -> SVG (WARNING: text becomes paths, NOT editable)...")
        success = 0
        for item in config["files"]:
            svg_name = Path(item["pdf"]).stem + ".svg"
            svg_path = output_dir / svg_name
            r = subprocess.run(
                ["pdf2svg", item["pdf"], str(svg_path)],
                capture_output=True, text=True, timeout=30
            )
            if r.returncode == 0:
                print(f"  OK {svg_name}")
                success += 1
        return success > 0
    finally:
        if script_path.exists():
            script_path.unlink()
        if pdf_tmp.exists():
            shutil.rmtree(pdf_tmp)


def convert(html_dir: Path, output_dir: Path) -> bool:
    """主转换入口"""
    if html_dir.is_file():
        html_files = [html_dir]
    else:
        html_files = sorted(html_dir.glob("*.html"))

    # work_dir 固定为项目根（脚本所在目录的父目录），让 puppeteer 一次性安装可跨调用复用
    # 否则每个 ppt-output/<test_dir>/ 都会单独装 ~55MB 的 puppeteer
    work_dir = Path(__file__).resolve().parent.parent

    if not html_files:
        print(f"No HTML files in {html_dir}", file=sys.stderr)
        return False

    output_dir.mkdir(parents=True, exist_ok=True)

    method, bundle_path = ensure_deps(work_dir)

    if method == "dom-to-svg" and bundle_path:
        ok = convert_dom_to_svg(html_files, output_dir, work_dir, bundle_path)
        if ok:
            print(f"\nDone! {len(html_files)} SVGs -> {output_dir}")
            return True
        print("dom-to-svg failed, falling back to pdf2svg...")

    return convert_pdf2svg(html_files, output_dir, work_dir)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 html2svg.py <html_dir_or_file> [-o output_dir]")
        sys.exit(1)

    html_path = Path(sys.argv[1]).resolve()
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        output_dir = Path(sys.argv[idx + 1]).resolve()
    else:
        output_dir = (html_path.parent if html_path.is_file() else html_path.parent) / "svg"

    success = convert(html_path, output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
