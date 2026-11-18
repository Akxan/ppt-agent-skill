#!/usr/bin/env python3
"""PNG -> PPTX：每张截图铺满一页（像素级保真，文字不可编辑）

所有 CSS 效果原样保留，任何版本的 PowerPoint / WPS / Keynote 都能打开；
代价是内容成为像素，无法编辑，也无法做卡片入场动画（页间切换可用）。

用法：
    python3 scripts/png2pptx.py <png_dir_or_file> -o output.pptx [--transition fade]
"""

import argparse
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

from pptx_motion import TRANSITIONS, TRANSITION_SPEEDS, apply_transition
from svg2pptx import SLIDE_H, SLIDE_W, natural_key


def convert(png_input, output_path, transition="fade", transition_speed="med", advance_after=None):
    png_input = Path(png_input)
    png_files = [png_input] if png_input.is_file() else sorted(png_input.glob("*.png"), key=natural_key)
    if not png_files:
        print(f"Error: no PNG files found in {png_input}", file=sys.stderr)
        sys.exit(1)

    prs = Presentation()
    prs.slide_width = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    blank = prs.slide_layouts[6]
    for index, png_file in enumerate(png_files, start=1):
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(str(png_file), Emu(0), Emu(0), Emu(SLIDE_W), Emu(SLIDE_H))
        apply_transition(slide, transition, speed=transition_speed, advance_after=advance_after)
        print(f"  [{index}/{len(png_files)}] {png_file.name}")
    prs.save(str(output_path))
    print(f"Saved: {output_path} ({len(png_files)} slides, transition={transition})")


def main():
    parser = argparse.ArgumentParser(description="PNG to PPTX (full-slide images)")
    parser.add_argument("png", help="PNG file or directory")
    parser.add_argument("-o", "--output", default="presentation.pptx")
    parser.add_argument("--transition", default="fade", choices=sorted(TRANSITIONS) + ["none"],
                        help="页间切换效果（默认 fade）")
    parser.add_argument("--transition-speed", default="med", choices=TRANSITION_SPEEDS)
    parser.add_argument("--advance-after", type=float, default=None, metavar="SECONDS",
                        help="每页停留若干秒后自动翻页")
    args = parser.parse_args()
    convert(args.png, args.output, transition=args.transition, transition_speed=args.transition_speed,
            advance_after=args.advance_after)


if __name__ == "__main__":
    main()
