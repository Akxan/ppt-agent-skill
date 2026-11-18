#!/usr/bin/env python3
"""build_hero.py -- 把 26 张风格截图拼成 5 板块 hero 拼图

输出：
  assets/hero-all.png         总览：26 风格 5 板块网格（适合 README 顶部）
  assets/hero-<category>.png  每个板块单独一张
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

import contracts as C

GALLERY = C.SKILL_DIR / "ppt-output" / "style-gallery"
ASSETS = C.SKILL_DIR / "assets"
ASSETS.mkdir(exist_ok=True)


def load_categories() -> dict:
    """板块 -> {cn, en, ids}，顺序与内容都取自风格库。"""
    categories = {key: {"cn": label["cn"], "en": label["en"], "ids": []}
                  for key, label in C.STYLE_CATEGORIES.items()}
    for style in C.load_styles():
        categories[style["category"]]["ids"].append(style["style_id"])
    return categories


CATEGORIES = load_categories()

THUMB_W, THUMB_H = 480, 270  # 16:9 缩略图
GAP = 20
PADDING = 60
LABEL_HEIGHT = 60
BG_COLOR = (10, 10, 12)
LABEL_COLOR = (255, 255, 255)
SUB_COLOR = (180, 200, 220)


def get_font(size: int, bold: bool = False, cjk: bool = False):
    """获取字体。cjk=True 优先选含中文字符的字体。"""
    if cjk:
        candidates = [
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except OSError:
                continue
    return ImageFont.load_default()


def make_thumbnail(img_path: Path, w: int = THUMB_W, h: int = THUMB_H) -> Image.Image:
    if not img_path.exists():
        thumb = Image.new("RGB", (w, h), (40, 40, 48))
        return thumb
    img = Image.open(img_path).convert("RGB")
    img.thumbnail((w * 2, h * 2))  # high-res first
    img = img.resize((w, h), Image.LANCZOS)
    return img


def build_category_image(cat_key: str, cat_data: dict) -> Image.Image:
    ids = cat_data["ids"]
    n = len(ids)
    cols = 4 if n >= 6 else (3 if n >= 4 else n)
    rows = (n + cols - 1) // cols

    width = PADDING * 2 + cols * THUMB_W + (cols - 1) * GAP
    height = PADDING + LABEL_HEIGHT + rows * THUMB_H + (rows - 1) * GAP + PADDING

    canvas = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    title_font = get_font(28, bold=True, cjk=True)
    caption_font = get_font(12)
    accent_font = get_font(11, bold=True)

    draw.text((PADDING, PADDING - 10), cat_data["cn"], fill=LABEL_COLOR, font=title_font)
    sub_text = f"{cat_data['en'].upper()}  ·  {n} STYLES"
    draw.text((PADDING, PADDING + 26), sub_text, fill=(110, 200, 230), font=accent_font)
    accent_y = PADDING + 22
    draw.line([(PADDING + len(cat_data["cn"]) * 30 + 12, accent_y), (PADDING + len(cat_data["cn"]) * 30 + 60, accent_y)], fill=(34, 211, 238), width=2)

    for i, sid in enumerate(ids):
        row = i // cols
        col = i % cols
        x = PADDING + col * (THUMB_W + GAP)
        y = PADDING + LABEL_HEIGHT + row * (THUMB_H + GAP)

        thumb = make_thumbnail(GALLERY / f"{sid}.png")
        canvas.paste(thumb, (x, y))

        draw.rectangle([(x, y), (x + THUMB_W - 1, y + THUMB_H - 1)], outline=(40, 50, 65), width=1)

        label_overlay = Image.new("RGBA", (THUMB_W, 28), (0, 0, 0, 180))
        canvas.paste(label_overlay, (x, y + THUMB_H - 28), label_overlay)
        draw.text((x + 10, y + THUMB_H - 22), sid, fill=(220, 230, 240), font=caption_font)

    return canvas


def build_all_categories_grid() -> Image.Image:
    total_styles = sum(len(c["ids"]) for c in CATEGORIES.values())

    cols = 5
    n = total_styles
    rows = (n + cols - 1) // cols

    thumb_w, thumb_h = 360, 202
    gap = 14
    padding = 80
    header = 200

    width = padding * 2 + cols * thumb_w + (cols - 1) * gap
    height = padding + header + rows * thumb_h + (rows - 1) * gap + padding

    canvas = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for x_pos, y_pos, color, radius in [
        (int(width * 0.85), 100, (99, 102, 241, 80), 400),
        (int(width * 0.15), height - 200, (34, 211, 238, 60), 350),
    ]:
        for r in range(radius, 0, -8):
            alpha = int(color[3] * (1 - r / radius) * 0.3)
            odraw.ellipse([(x_pos - r, y_pos - r), (x_pos + r, y_pos + r)],
                         fill=(color[0], color[1], color[2], alpha))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    title_font = get_font(56, bold=True, cjk=True)
    sub_font = get_font(20, cjk=True)
    accent_font = get_font(13, bold=True)
    caption_font = get_font(11)

    draw.ellipse([(padding, padding + 10), (padding + 12, padding + 22)], fill=(34, 211, 238))
    draw.text((padding + 24, padding + 8), "PPT AGENT SKILL · WORLD-CLASS", fill=(34, 211, 238), font=accent_font)
    draw.text((padding, padding + 50), f"{total_styles} 风格预览画廊", fill=(255, 255, 255), font=title_font)
    draw.text((padding, padding + 130),
              f"{len(CATEGORIES)} 板块 · {len(C.CHARTS)} 图表 · 世界级排版 · Linear / Anthropic / Stripe / Apple / NYT 标杆",
              fill=(180, 200, 220), font=sub_font)

    all_styles = []
    for cat in CATEGORIES.values():
        all_styles.extend(cat["ids"])

    for i, sid in enumerate(all_styles):
        row = i // cols
        col = i % cols
        x = padding + col * (thumb_w + gap)
        y = padding + header + row * (thumb_h + gap)

        thumb = make_thumbnail(GALLERY / f"{sid}.png", thumb_w, thumb_h)
        canvas.paste(thumb, (x, y))
        draw.rectangle([(x, y), (x + thumb_w - 1, y + thumb_h - 1)], outline=(40, 50, 65), width=1)

        label_h = 24
        label_overlay = Image.new("RGBA", (thumb_w, label_h), (0, 0, 0, 200))
        canvas.paste(label_overlay, (x, y + thumb_h - label_h), label_overlay)
        draw.text((x + 8, y + thumb_h - label_h + 6), sid, fill=(220, 230, 240), font=caption_font)

    return canvas


def main():
    print("Building category images...")
    for cat_key, cat_data in CATEGORIES.items():
        img = build_category_image(cat_key, cat_data)
        out = ASSETS / f"hero-{cat_key.replace('_', '-')}.png"
        img.save(out, optimize=True)
        print(f"  ✓ {out.name} ({img.width}x{img.height})")

    print("\nBuilding overall grid...")
    grid = build_all_categories_grid()
    out = ASSETS / "hero-all.png"
    grid.save(out, optimize=True)
    print(f"  ✓ {out.name} ({grid.width}x{grid.height})")

    print(f"\nDone. Outputs in {ASSETS}/")


if __name__ == "__main__":
    main()
