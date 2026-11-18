#!/usr/bin/env python3
"""HTML -> PNG 截图（像素级保真，文字不可编辑）

Puppeteer 以 1280x720 视口截图；--scale 为设备像素比（2 -> 2560x1440）。
依赖与 html2svg.py 共用 skill 根目录的 node_modules。

用法：
    python3 scripts/html2png.py <html_dir_or_file> [-o output_dir] [--scale 2]
"""

import argparse
import sys
from pathlib import Path

from html2svg import ensure_puppeteer, natural_key, run_node

SCREENSHOT_SCRIPT = r"""
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
    const config = JSON.parse(process.argv[2]);
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--font-render-hinting=none']
    });
    for (const item of config.files) {
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: config.scale });
        await page.goto('file://' + item.html, { waitUntil: 'networkidle0', timeout: 30000 });
        await page.evaluate(async () => {
            await document.fonts.ready;
            await Promise.all(Array.from(document.images).map((img) =>
                img.complete ? null : new Promise((r) => { img.onload = r; img.onerror = r; })));
        });
        await page.screenshot({ path: item.png, type: 'png', clip: { x: 0, y: 0, width: 1280, height: 720 } });
        console.log('PNG: ' + path.basename(item.html));
        await page.close();
    }
    await browser.close();
})();
"""


def convert(html_path: Path, output_dir: Path, scale: float = 2.0) -> bool:
    html_files = [html_path] if html_path.is_file() else sorted(html_path.glob("*.html"), key=natural_key)
    if not html_files:
        print(f"No HTML files in {html_path}", file=sys.stderr)
        return False
    if not ensure_puppeteer():
        return False
    output_dir.mkdir(parents=True, exist_ok=True)
    config = {"scale": scale,
              "files": [{"html": str(f), "png": str(output_dir / (f.stem + ".png"))} for f in html_files]}
    print(f"Converting {len(html_files)} HTML files -> PNG ({scale}x)...")
    if not run_node(SCREENSHOT_SCRIPT, config, ".html2png_tmp.js"):
        return False
    print(f"Done! {len(html_files)} PNGs -> {output_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(description="HTML -> PNG screenshots")
    parser.add_argument("path", help="HTML file or directory of slides")
    parser.add_argument("-o", "--output", help="Output directory (default: <slides parent>/png)")
    parser.add_argument("--scale", type=float, default=2.0, help="Device pixel ratio (default: 2)")
    args = parser.parse_args()
    html_path = Path(args.path).resolve()
    output_dir = Path(args.output).resolve() if args.output else html_path.parent / "png"
    sys.exit(0 if convert(html_path, output_dir, args.scale) else 1)


if __name__ == "__main__":
    main()
