#!/usr/bin/env python3
"""HTML 打包工具 -- 将多页 HTML 合并为可翻页的单文件预览

每页 HTML 放在独立的 iframe srcdoc 中，CSS 完全隔离。翻页带淡入过渡。
加 --animate 时在浏览器里模拟卡片入场动画，参数含义与 svg2pptx.py 相同，
没有 PowerPoint 也能预览动效。

用法:
  python html_packager.py <slides_directory> [-o output.html] [--title "Title"]
      [--animate none|fade|wipe|rise|zoom] [--animate-trigger click|auto]
"""

from __future__ import annotations

import argparse
import base64
import html as html_module
import json
import re
import sys
from pathlib import Path

ENTRANCE_EFFECTS = ("fade", "wipe", "rise", "zoom")     # 与 pptx_motion.ENTRANCE_EFFECTS 保持一致


def natural_key(path: Path) -> list:
    """自然排序：slide-2 排在 slide-10 前面。"""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def inline_images(html_content: str, html_dir: Path) -> str:
    """将 HTML 中引用的本地图片转为 base64 内联。"""
    mime_types = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                  "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}

    def replace_src(match):
        prefix, path_str, closing = match.groups()
        img_path = Path(path_str)
        if not img_path.is_absolute():
            img_path = html_dir / path_str
        if not (img_path.exists() and img_path.is_file()):
            return match.group(0)
        ext = img_path.suffix.lower().lstrip(".")
        data = base64.b64encode(img_path.read_bytes()).decode()
        return f"{prefix}data:{mime_types.get(ext, f'image/{ext}')};base64,{data}{closing}"

    html_content = re.sub(r'(src=["\'])([^"\']+?)(["\'])', replace_src, html_content)
    return re.sub(r'(url\(["\']?)([^"\')\s]+?)(["\']?\))', replace_src, html_content)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0a0a0a;
    display: flex; flex-direction: column; align-items: center;
    min-height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  }
  .toolbar {
    position: fixed; top: 0; left: 0; right: 0; height: 48px;
    background: rgba(10,10,10,0.95); border-bottom: 1px solid rgba(255,255,255,0.1);
    display: flex; align-items: center; justify-content: center; gap: 16px;
    z-index: 1000; backdrop-filter: blur(10px);
  }
  .toolbar button {
    background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
    color: #fff; padding: 6px 16px; border-radius: 6px; cursor: pointer;
    font-size: 14px; transition: background 0.2s;
  }
  .toolbar button:hover { background: rgba(255,255,255,0.2); }
  .toolbar button:disabled { opacity: 0.3; cursor: not-allowed; }
  .page-info { font-size: 14px; color: rgba(255,255,255,0.7); min-width: 80px; text-align: center; }
  .stage {
    margin-top: 60px; width: 90vw; max-width: 1280px;
    aspect-ratio: 16/9; overflow: hidden;
    border-radius: 8px; box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    background: #111; position: relative;
  }
  .stage.clickable { cursor: pointer; }
  .slide-frame {
    width: 1280px; height: 720px;
    transform-origin: top left;
    position: absolute; top: 0; left: 0;
    border: none;
    opacity: 0; pointer-events: none;
    transition: opacity 0.35s ease;
  }
  .slide-frame.active { opacity: 1; pointer-events: auto; }
  .stage.clickable .slide-frame.active { pointer-events: none; }
  .nav-hint { position: fixed; bottom: 12px; color: rgba(255,255,255,0.35); font-size: 12px; }
</style>
</head>
<body>
<div class="toolbar">
  <button id="btn-prev" onclick="go(-1)">Prev</button>
  <span class="page-info" id="page-info">1 / __TOTAL__</span>
  <button id="btn-next" onclick="advance()">Next</button>
</div>
<div class="stage" id="stage">
__IFRAMES__
</div>
<div class="nav-hint" id="hint"></div>
<script>
const MOTION = __MOTION__;            // {animate, trigger, duration, stagger}
const frames = Array.from(document.querySelectorAll('.slide-frame'));
const total = frames.length;
const info = document.getElementById('page-info');
const stage = document.getElementById('stage');
let cur = 0, pending = [], timers = [];

// 卡片入场的隐藏态（与 pptx_motion.py 的四种效果对应）
const HIDE_CSS = `
  .pptx-anim { transition: opacity DURms ease, transform DURms ease, clip-path DURms ease !important; }
  .pptx-hide.pptx-fade { opacity: 0 !important; }
  .pptx-hide.pptx-rise { opacity: 0 !important; transform: translateY(43px) !important; }
  .pptx-hide.pptx-zoom { opacity: 0 !important; transform: scale(0.85) !important; }
  .pptx-hide.pptx-wipe { clip-path: inset(0 100% 0 0) !important; }
`.replace(/DUR/g, MOTION.duration);

// 与 html2svg.py 的卡片识别规则一致：优先 data-card-id，其次 class 以 card 结尾的最外层元素
function cardsOf(frame) {
  const doc = frame.contentDocument;
  if (!doc) return [];
  let cards = Array.from(doc.querySelectorAll('[data-card-id]'));
  if (!cards.length) {
    cards = Array.from(doc.querySelectorAll('[class]')).filter(el =>
      Array.from(el.classList).some(c => /(^|[-_])card$/i.test(c)));
  }
  return cards.filter(el => !cards.some(o => o !== el && o.contains(el)));
}

function prepare(frame) {
  timers.forEach(clearTimeout); timers = [];
  pending = [];
  if (MOTION.animate === 'none') return;
  const doc = frame.contentDocument;
  if (!doc) return;
  if (!doc.getElementById('pptx-anim-style')) {
    const style = doc.createElement('style');
    style.id = 'pptx-anim-style';
    style.textContent = HIDE_CSS;
    doc.head.appendChild(style);
  }
  pending = cardsOf(frame);
  pending.forEach(el => {
    el.classList.remove('pptx-anim');
    el.classList.add('pptx-' + MOTION.animate, 'pptx-hide');
  });
  if (MOTION.trigger === 'auto') {
    const queue = pending; pending = [];
    queue.forEach((el, i) => timers.push(setTimeout(() => reveal(el),
      400 + i * (MOTION.duration + MOTION.stagger))));
  }
}

function reveal(el) {
  el.classList.add('pptx-anim');
  el.getBoundingClientRect();          // 强制回流，让过渡从隐藏态开始
  el.classList.remove('pptx-hide');
}

function resize() {
  const scale = Math.min(stage.clientWidth / 1280, stage.clientHeight / 720);
  frames.forEach(f => f.style.transform = 'scale(' + scale + ')');
}
function show(i) {
  cur = i;
  prepare(frames[i]);
  frames.forEach((f, idx) => f.classList.toggle('active', idx === i));
  info.textContent = (i + 1) + ' / ' + total;
  document.getElementById('btn-prev').disabled = i === 0;
}
function go(d) {
  const n = cur + d;
  if (n >= 0 && n < total) show(n);
}
// 前进：本页还有没出场的卡片就先出一张，否则翻到下一页
function advance() {
  if (pending.length) reveal(pending.shift());
  else go(1);
}
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') go(-1);
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') { e.preventDefault(); advance(); }
});
if (MOTION.animate !== 'none' && MOTION.trigger === 'click') {
  stage.classList.add('clickable');
  stage.addEventListener('click', advance);
}
document.getElementById('hint').textContent = MOTION.animate === 'none'
  ? '方向键翻页'
  : (MOTION.trigger === 'click' ? '点击画面或按 → ：逐张出现卡片，出完后翻页' : '方向键翻页，卡片自动依次出现');
window.addEventListener('resize', resize);
window.addEventListener('load', () => { resize(); show(0); });   // 等 iframe 加载完才能找到卡片
resize();
</script>
</body>
</html>"""


def build_preview(slide_files: list, title: str = "PPT Preview", animate: str = "none",
                  trigger: str = "click") -> str:
    """构建可翻页的预览 HTML，每页用独立 iframe 实现 CSS 隔离。"""
    iframes = []
    for index, path in enumerate(slide_files):
        content = inline_images(Path(path).read_text(encoding="utf-8"), Path(path).parent)
        iframes.append(
            f'<iframe class="slide-frame{" active" if index == 0 else ""}" id="slide-{index}" '
            f'srcdoc="{html_module.escape(content, quote=True)}" '
            f'sandbox="allow-same-origin" frameborder="0" scrolling="no"></iframe>')
    motion = {"animate": animate, "trigger": trigger, "duration": 500, "stagger": 150}
    return (PAGE_TEMPLATE
            .replace("__TITLE__", html_module.escape(title))
            .replace("__TOTAL__", str(len(slide_files)))
            .replace("__MOTION__", json.dumps(motion))
            .replace("__IFRAMES__", "\n".join(iframes)))


def main():
    parser = argparse.ArgumentParser(description="HTML Packager for PPT Agent")
    parser.add_argument("path", help="Directory containing slide HTML files")
    parser.add_argument("-o", "--output", default=None, help="Output HTML file")
    parser.add_argument("--title", default="PPT Preview", help="Title")
    parser.add_argument("--animate", default="none", choices=["none", *ENTRANCE_EFFECTS],
                        help="在预览里模拟卡片入场动画（与 svg2pptx.py 的同名参数一致）")
    parser.add_argument("--animate-trigger", default="click", choices=["click", "auto"],
                        help="click=点击逐张出现；auto=进入页面后自动依次出现")
    args = parser.parse_args()

    slides_dir = Path(args.path)
    if not slides_dir.is_dir():
        print(f"Error: {slides_dir} is not a directory", file=sys.stderr)
        sys.exit(1)
    html_files = sorted(slides_dir.glob("*.html"), key=natural_key)
    if not html_files:
        print(f"Error: No HTML files in {slides_dir}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or str(slides_dir.parent / "preview.html")
    Path(output_path).write_text(
        build_preview(html_files, title=args.title, animate=args.animate, trigger=args.animate_trigger),
        encoding="utf-8")
    print(f"Created: {output_path} ({len(html_files)} slides, animate={args.animate})")


if __name__ == "__main__":
    main()
