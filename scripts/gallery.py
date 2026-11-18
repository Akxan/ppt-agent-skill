#!/usr/bin/env python3
"""gallery.py -- 风格预览画廊生成器

读取 references/styles/ 下的预置风格（经 contracts.load_styles），生成：
- ppt-output/style-gallery/index.html   按板块分组的卡片墙，缩略图用各风格的截图
- ppt-output/style-gallery/<style_id>.png（加 --screenshots 时重新截图）

用法:
    python3 scripts/gallery.py                 # 生成 index.html
    python3 scripts/gallery.py --screenshots   # 先给每个 mock 重新截图，再生成 index.html
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import contracts as C

GALLERY_DIR = C.SKILL_DIR / "ppt-output" / "style-gallery"
REPO_URL = "https://github.com/Akxan/ppt-agent-skill"


def group_by_category(styles: list) -> dict:
    groups = {category: [] for category in C.STYLE_CATEGORIES}
    for style in styles:
        groups[style["category"]].append(style)
    return groups


def get_swatches(style: dict) -> list:
    """提取 5 个代表色用于 swatch 行。"""
    bg = style.get("background", {})
    accent = style.get("accent", {})
    primary = accent.get("primary", [])
    secondary = accent.get("secondary", [])
    swatches = []
    if isinstance(bg.get("primary"), str) and bg["primary"].startswith("#"):
        swatches.append(bg["primary"])
    swatches.extend(primary[:2])
    swatches.extend(secondary[:2])
    # fallback 默认色
    while len(swatches) < 5:
        swatches.append("#888888")
    return swatches[:5]


def build_index_html(grouped: dict) -> str:
    """生成统一索引 HTML。"""
    sections = []

    for cat, label in C.STYLE_CATEGORIES.items():
        styles = grouped.get(cat, [])
        if not styles:
            continue
        cn, en = label["cn"], label["en"]
        cards = []
        for s in styles:
            sid = s["style_id"]
            name = s["style_name"]
            inspiration = s.get("inspiration", "")
            keywords = s.get("mood_keywords", [])
            sw_html = "".join(f'<div class="sw" style="background:{c}"></div>' for c in get_swatches(s))
            kw_html = " · ".join(keywords[:3])
            cards.append(f"""
        <a class="card" href="{sid}.html" target="_blank" rel="noopener">
          <div class="frame">
            <img src="{sid}.png" alt="{name}" loading="lazy">
          </div>
          <div class="meta">
            <div class="row1">
              <span class="name">{name}</span>
              <span class="open">↗</span>
            </div>
            <div class="row2">
              <span class="id">{sid}</span>
              <span class="dot">·</span>
              <span class="insp">{inspiration}</span>
            </div>
            <div class="kw">{kw_html}</div>
            <div class="swatches">{sw_html}</div>
          </div>
        </a>
""".strip())

        sections.append(f"""
    <section class="section">
      <div class="section-head">
        <div class="section-cn">{cn}</div>
        <div class="section-en">{en}</div>
        <div class="section-count">{len(styles)} 风格</div>
      </div>
      <div class="grid">
        {chr(10).join(cards)}
      </div>
    </section>
""".strip())

    body = "\n".join(sections)
    total = sum(len(v) for v in grouped.values())

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PPT Agent Skill · {total} 风格预览画廊</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    background: #0a0a0c;
    color: #fff;
    font-family: 'Inter', -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
    min-height: 100vh;
  }}
  .header {{
    padding: 60px 60px 40px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }}
  .header .label {{
    font-size: 11px;
    letter-spacing: 0.18em;
    color: #22D3EE;
    font-weight: 600;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }}
  .header .label::before {{
    content: '';
    width: 6px; height: 6px; border-radius: 50%;
    background: #22D3EE;
    box-shadow: 0 0 10px currentColor;
  }}
  .header h1 {{
    font-family: 'Inter Tight', sans-serif;
    font-size: 56px;
    font-weight: 700;
    letter-spacing: -0.045em;
    margin-top: 14px;
    line-height: 1;
  }}
  .header h1 em {{
    font-family: Georgia, 'Source Serif Pro', serif;
    font-style: italic;
    font-weight: 400;
    color: #22D3EE;
  }}
  .header .deck {{
    font-size: 16px;
    line-height: 1.6;
    color: rgba(255,255,255,0.65);
    max-width: 720px;
    margin-top: 18px;
    letter-spacing: -0.005em;
  }}
  .header .stats {{
    display: flex; gap: 48px; margin-top: 32px;
  }}
  .header .stat .num {{
    font-family: 'Inter Tight', sans-serif;
    font-size: 32px; font-weight: 700;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.025em;
  }}
  .header .stat .l {{
    font-size: 11px;
    color: rgba(255,255,255,0.5);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 4px;
  }}

  .section {{
    padding: 50px 60px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }}
  .section-head {{
    display: flex; align-items: baseline; gap: 14px; margin-bottom: 28px;
  }}
  .section-cn {{
    font-family: 'Inter Tight', sans-serif;
    font-size: 22px; font-weight: 700;
    letter-spacing: -0.025em;
  }}
  .section-en {{
    font-size: 11px;
    color: rgba(255,255,255,0.4);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
  }}
  .section-count {{
    margin-left: auto;
    font-size: 11px;
    color: rgba(255,255,255,0.5);
    letter-spacing: 0.05em;
    font-family: 'JetBrains Mono', monospace;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
    gap: 18px;
  }}
  .card {{
    background: #14141a;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    transition: border-color 0.15s, transform 0.15s;
    display: flex;
    flex-direction: column;
  }}
  .card:hover {{
    border-color: rgba(34,211,238,0.4);
    transform: translateY(-2px);
  }}
  .frame {{
    aspect-ratio: 16 / 9;
    overflow: hidden;
    position: relative;
    background: #000;
  }}
  .frame img {{
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  .meta {{
    padding: 14px 16px;
  }}
  .row1 {{
    display: flex; align-items: center; justify-content: space-between;
  }}
  .row1 .name {{
    font-family: 'Inter Tight', sans-serif;
    font-size: 14px; font-weight: 700;
    letter-spacing: -0.015em;
  }}
  .row1 .open {{
    font-size: 14px;
    color: rgba(255,255,255,0.4);
  }}
  .row2 {{
    display: flex; gap: 6px; align-items: center;
    font-size: 11px;
    color: rgba(255,255,255,0.5);
    margin-top: 4px;
  }}
  .row2 .id {{
    font-family: 'JetBrains Mono', monospace;
    color: #22D3EE;
  }}
  .row2 .dot {{ opacity: 0.4; }}
  .kw {{
    font-size: 11px;
    color: rgba(255,255,255,0.55);
    margin-top: 8px;
    line-height: 1.5;
  }}
  .swatches {{
    display: flex; gap: 4px; margin-top: 10px;
  }}
  .sw {{
    width: 18px; height: 18px; border-radius: 4px;
    border: 1px solid rgba(255,255,255,0.1);
  }}

  .footer {{
    padding: 40px 60px 60px;
    text-align: center;
    color: rgba(255,255,255,0.3);
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}
  .footer a {{
    color: rgba(255,255,255,0.5);
    text-decoration: none;
    transition: color 0.15s;
  }}
  .footer a:hover {{ color: #22D3EE; }}
</style>
</head>
<body>
  <header class="header">
    <div class="label">PPT AGENT SKILL · WORLD-CLASS</div>
    <h1>风格预览<em>画廊。</em></h1>
    <p class="deck">{total} 个演示文稿风格，按 {len(C.STYLE_CATEGORIES)} 板块分组。每张卡片是真实 1280×720 设计稿的截图，点击打开原尺寸 HTML。</p>
    <div class="stats">
      <div class="stat"><div class="num">{total}</div><div class="l">STYLES</div></div>
      <div class="stat"><div class="num">{len(C.STYLE_CATEGORIES)}</div><div class="l">CATEGORIES</div></div>
      <div class="stat"><div class="num">{len(C.CHARTS)}</div><div class="l">CHART TYPES</div></div>
    </div>
  </header>

{body}

  <footer class="footer">
    <a href="{REPO_URL}" target="_blank">PPT AGENT SKILL · MMXXVI</a>
  </footer>
</body>
</html>
"""


def take_screenshots(styles: list) -> bool:
    """给每个风格 mock 截图（1920x1080），复用 html2png 的 Puppeteer 脚本。"""
    from html2png import SCREENSHOT_SCRIPT
    from html2svg import ensure_puppeteer, run_node

    if not ensure_puppeteer():
        return False
    files = [{"html": str(GALLERY_DIR / f"{s['style_id']}.html"), "png": str(GALLERY_DIR / f"{s['style_id']}.png")}
             for s in styles if (GALLERY_DIR / f"{s['style_id']}.html").exists()]
    return run_node(SCREENSHOT_SCRIPT, {"scale": 1.5, "files": files}, ".gallery_screenshot.js")


def main():
    parser = argparse.ArgumentParser(description="PPT Style Gallery Generator")
    parser.add_argument("--screenshots", action="store_true",
                        help="先给每个 mock 重新截图（需要 Node.js / puppeteer）")
    parser.add_argument("--out", default=str(GALLERY_DIR / "index.html"), help="index.html 输出路径")
    args = parser.parse_args()

    styles = C.load_styles()
    if not styles:
        print("Error: no styles found in references/styles/", file=sys.stderr)
        sys.exit(1)

    if args.screenshots:
        print("Taking screenshots...")
        if not take_screenshots(styles):
            print("Screenshot step failed", file=sys.stderr)
            sys.exit(1)

    grouped = group_by_category(styles)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_index_html(grouped), encoding="utf-8")

    print(f"Gallery index: {out_path} ({len(styles)} styles)")
    for category, label in C.STYLE_CATEGORIES.items():
        print(f"  {label['cn']} ({label['en']}): {len(grouped[category])}")


if __name__ == "__main__":
    main()
