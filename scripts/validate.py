#!/usr/bin/env python3
"""严格模式：校验 6 步 pipeline 的产物是否符合数据合同（可选，不跑也能出稿）。

  validate.py outline  OUTPUT_DIR/outline.json  [--pages 12 | --pages 10-15]
  validate.py planning OUTPUT_DIR/planning.json
  validate.py style    OUTPUT_DIR/style.json    [--preset]
  validate.py slides   OUTPUT_DIR/slides        [--planning OUTPUT_DIR/planning.json]
  validate.py visual   OUTPUT_DIR/png           [--planning OUTPUT_DIR/planning.json]
  validate.py all      OUTPUT_DIR               一次检查目录里已有的全部产物

退出码：0 通过；1 存在 ERROR。加 --strict 时 WARN 也算失败。
合同定义见 scripts/contracts.py，规则说明见 references/strict-mode.md。
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import contracts as C


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.notes.append(message)

    def merge(self, other: "Report", prefix: str = "") -> None:
        self.errors += [prefix + m for m in other.errors]
        self.warnings += [prefix + m for m in other.warnings]
        self.notes += [prefix + m for m in other.notes]

    def print(self, title: str) -> None:
        print(f"== {title} ==")
        for label, items in (("ERROR", self.errors), ("WARN ", self.warnings), ("INFO ", self.notes)):
            for item in items:
                print(f"{label} {item}")
        if not self.errors and not self.warnings:
            print("OK")


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _natural_key(path: Path) -> list:
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", path.name)]


# ── outline.json ────────────────────────────────────────────────────────────

def validate_outline(payload: Any, expected_pages: tuple[int, int] | None = None) -> Report:
    report = Report()
    outline = payload.get("ppt_outline", payload) if isinstance(payload, dict) else None
    if not isinstance(outline, dict):
        report.error("根节点应为对象，且包含 ppt_outline")
        return report

    cover = outline.get("cover")
    if not isinstance(cover, dict) or not _text(cover.get("title")):
        report.error("cover.title 缺失")
    parts = outline.get("parts")
    if not isinstance(parts, list) or not parts:
        report.error("parts 缺失或为空")
        return report

    content_pages = 0
    for index, part in enumerate(parts, start=1):
        label = f"parts[{index}]"
        if not isinstance(part, dict):
            report.error(f"{label} 应为对象")
            continue
        if not _text(part.get("part_title")):
            report.error(f"{label}.part_title 缺失")
        pages = part.get("pages") if isinstance(part.get("pages"), list) else []
        if len(pages) < 2:
            report.error(f"{label} 只有 {len(pages)} 页，每个 part 至少 2 页")
        for page_index, page in enumerate(pages, start=1):
            page_label = f"{label}.pages[{page_index}]"
            if not isinstance(page, dict) or not _text(page.get("title")):
                report.error(f"{page_label}.title 缺失")
                continue
            if not _text(page.get("goal")):
                report.warn(f"{page_label}（{page['title']}）缺少 goal")
            if not [item for item in page.get("content") or [] if _text(item)]:
                report.warn(f"{page_label}（{page['title']}）content 为空，没有可支撑的要点")
        content_pages += len(pages)

    if len(parts) < 2:
        report.warn("只有 1 个 part，缺少递进结构")
    if not isinstance(outline.get("end_page"), dict):
        report.warn("end_page 缺失")

    has_toc = isinstance(outline.get("table_of_contents"), dict)
    low = content_pages + 2 + (1 if has_toc else 0)          # 封面 + 结束页 (+ 目录)
    high = low + len(parts)                                  # 每个 part 可再加一张章节封面
    report.note(f"内容页 {content_pages} 页，成稿约 {low}-{high} 页")
    if expected_pages and (high < expected_pages[0] or low > expected_pages[1]):
        report.error(f"页数不符：要求 {expected_pages[0]}-{expected_pages[1]} 页，大纲只能展开为 {low}-{high} 页")
    return report


# ── planning.json ───────────────────────────────────────────────────────────

def planning_pages(payload: Any) -> list[dict]:
    """策划稿 -> 页面列表。接受页面数组，或 {"pages": [...]}。"""
    if isinstance(payload, dict):
        payload = payload.get("pages")
    return [page for page in payload if isinstance(page, dict)] if isinstance(payload, list) else []


def page_number(page: dict) -> Any:
    return page.get("page_number")


def card_chart(card: dict) -> Any:
    return card.get("chart_type")


def _card_has_data(card: dict) -> bool:
    return (card.get("card_type") in C.DATA_CARD_TYPES or bool(card_chart(card))
            or bool(card.get("data_points")))


def _validate_card(card: dict, label: str, report: Report) -> None:
    card_type = card.get("card_type")
    if card_type not in C.CARD_TYPES:
        report.error(f"{label}: card_type '{card_type}' 不合法，可选 {', '.join(C.CARD_TYPES)}")
    title = _text(card.get("title"))
    body = card.get("content")
    has_body = bool(_text(body)) or (isinstance(body, list) and any(_text(item) for item in body))
    if not (title or has_body or card.get("data_points") or card_chart(card)):
        report.error(f"{label}: 空卡片（没有标题、正文、数据或图表）")
    chart = card_chart(card)
    if chart and not C.normalize_chart(chart):
        report.error(f"{label}: chart_type '{chart}' 不在图表库里，可选 {', '.join(C.CHARTS)}")
    if card.get("card_style") is not None and card["card_style"] not in C.CARD_STYLES:
        report.error(f"{label}: card_style '{card['card_style']}' 不合法，可选 {', '.join(C.CARD_STYLES)}")
    if card.get("role") is not None and card["role"] not in C.CARD_ROLES:
        report.error(f"{label}: role '{card['role']}' 不合法，可选 {', '.join(C.CARD_ROLES)}")


def _validate_page(page: dict, report: Report) -> None:
    label = f"第 {page_number(page)} 页"
    page_type = page.get("page_type")
    if page_type not in C.PAGE_TYPES:
        report.error(f"{label}: page_type '{page_type}' 不合法，可选 {', '.join(C.PAGE_TYPES)}")
    if not _text(page.get("title")):
        report.error(f"{label}: title 缺失")

    cards = [card for card in page.get("cards") or [] if isinstance(card, dict)]
    for index, card in enumerate(cards, start=1):
        _validate_card(card, f"{label} 卡片 {index}", report)
    roles = [card.get("role") for card in cards if card.get("role")]
    if roles and roles.count("anchor") != 1:
        report.error(f"{label}: 使用 role 时必须恰好 1 张 anchor 卡片（现有 {roles.count('anchor')} 张）")

    density = page.get("density_label")
    if density is not None:
        if density not in C.DENSITY:
            report.error(f"{label}: density_label '{density}' 不合法，可选 {', '.join(C.DENSITY)}")
        elif len(cards) > C.DENSITY[density]["max_cards"]:
            report.error(f"{label}: {len(cards)} 张卡片超过 {density} 密度上限 {C.DENSITY[density]['max_cards']}")

    if page_type != "content":
        return
    if not _text(page.get("goal")):
        report.warn(f"{label}: 缺少 goal（这页最想让观众记住什么）")
    layout = C.normalize_layout(page.get("layout_hint"))
    if not _text(page.get("layout_hint")):
        report.error(f"{label}: 内容页缺少 layout_hint")
    elif layout is None:
        report.warn(f"{label}: layout_hint '{page['layout_hint']}' 不是已知版式，无法路由到 layouts/")

    minimum = C.LAYOUT_MIN_CARDS.get(layout, C.DEFAULT_MIN_CARDS)
    if len(cards) < minimum:
        report.error(f"{label}: 只有 {len(cards)} 张卡片，{layout or '该'} 版式至少 {minimum} 张")
    if len(cards) >= C.DEFAULT_MIN_CARDS:
        if len({card.get("card_type") for card in cards}) < 2:
            report.error(f"{label}: 所有卡片都是同一种 card_type，至少用 2 种")
        if not any(_card_has_data(card) for card in cards):
            report.error(f"{label}: 没有数据卡片（data / data_highlight / 带图表或 data_points 的卡片）")


def validate_planning(payload: Any) -> Report:
    report = Report()
    pages = planning_pages(payload)
    if not pages:
        report.error("没有找到页面：策划稿应为页面对象数组")
        return report

    numbers = [page_number(page) for page in pages]
    if not all(isinstance(n, int) for n in numbers):
        report.error("每页都需要整数 page_number")
    elif sorted(numbers) != list(range(1, len(pages) + 1)):
        report.warn(f"page_number 不是从 1 开始的连续编号：{numbers}")
    if len(set(numbers)) != len(numbers):
        report.error("page_number 有重复")

    for page in pages:
        _validate_page(page, report)

    if pages[0].get("page_type") != "cover":
        report.warn("第一页不是 cover")
    if pages[-1].get("page_type") != "end":
        report.warn("最后一页不是 end")

    content = [page for page in pages if page.get("page_type") == "content"]
    with_data = [page for page in content
                 if (page.get("content_summary") or {}).get("data_highlights")
                 or any(_card_has_data(c) for c in page.get("cards") or [] if isinstance(c, dict))]
    if content and len(with_data) / len(content) < 0.6:
        report.warn(f"只有 {len(with_data)}/{len(content)} 个内容页含数据，低于 60%")

    streak, previous = 1, None
    for page in content:
        layout = C.normalize_layout(page.get("layout_hint"))
        streak = streak + 1 if layout and layout == previous else 1
        if streak == 3:
            report.warn(f"第 {page_number(page)} 页起连续 3 个内容页使用 {layout} 版式，缺少节奏变化")
        previous = layout
    report.note(f"{len(pages)} 页，其中内容页 {len(content)} 页")
    return report


# ── style.json ──────────────────────────────────────────────────────────────

def validate_style(style: Any, preset: bool = False) -> Report:
    """preset=True 时按预置风格库的完整字段要求检查。"""
    report = Report()
    if not isinstance(style, dict):
        report.error("根节点应为对象")
        return report
    for name in C.STYLE_CORE_FIELDS:
        if not isinstance(style.get(name), dict):
            report.error(f"缺少对象字段 {name}")
    if not _text(style.get("style_name")) and not _text(style.get("style_id")):
        report.error("缺少 style_name / style_id")
    accent = style.get("accent") if isinstance(style.get("accent"), dict) else {}
    for group in ("primary", "secondary"):
        if not isinstance(accent.get(group), list) or len(accent[group]) < 2:
            report.error(f"accent.{group} 需要 2 个颜色（对应 --accent-{'1/2' if group == 'primary' else '3/4'}）")
    missing = [var for var, value in C.style_css_variables(style).items()
               if var in C.CORE_CSS_VARIABLES and not value]
    if missing:
        report.error(f"无法生成 CSS 变量：{', '.join(missing)}")

    if not preset:
        if not isinstance(style.get("typography"), dict):
            report.warn("缺少 typography，字体将回落到系统默认")
        return report

    for name in C.STYLE_PRESET_FIELDS:
        if name not in style:
            report.error(f"缺少字段 {name}")
    if style.get("category") not in C.STYLE_CATEGORIES:
        report.error(f"category '{style.get('category')}' 不合法，可选 {', '.join(C.STYLE_CATEGORIES)}")
    dna = style.get("decoration_dna") if isinstance(style.get("decoration_dna"), dict) else {}
    for name in C.STYLE_DNA_FIELDS:
        if not dna.get(name):
            report.error(f"decoration_dna.{name} 缺失")
    if len(dna.get("forbidden") or []) < 3:
        report.error("decoration_dna.forbidden 至少列出 3 项")
    if len(style.get("mood_keywords") or []) < 3:
        report.error("mood_keywords 至少 3 个")
    typography = style.get("typography") if isinstance(style.get("typography"), dict) else {}
    for name in C.STYLE_TYPOGRAPHY_FIELDS:
        if name not in typography:
            report.error(f"typography.{name} 缺失")
    if not isinstance(style.get("font_imports"), list):
        report.error("font_imports 应为数组")
    return report


# ── slides/*.html ───────────────────────────────────────────────────────────

_CARD_CLASS = re.compile(r"class\s*=\s*[\"'][^\"']*(?<![\w-])[\w-]*card(?![\w-])", re.I)
_BODY_SELECTOR = re.compile(r"(^|[\s,>])(body|p|li|td)(?![\w-])|\.(body|desc|text|content)(?![\w-])", re.I)


def count_cards(html: str) -> int:
    marked = len(re.findall(r"\bdata-card-id\s*=", html))
    return marked or len(_CARD_CLASS.findall(html))


def validate_slide(html: str, page: dict | None = None) -> Report:
    report = Report()
    if not re.search(r"width\s*:\s*1280px", html) or not re.search(r"height\s*:\s*720px", html):
        report.error(f"未声明 {C.CANVAS_W}x{C.CANVAS_H} 固定画布")
    if "var(--" not in html:
        report.warn("没有使用 CSS 变量，颜色全部硬编码，跨页风格无法统一")
    elif not all(var in html for var in ("--bg-primary", "--text-primary", "--accent-1")):
        report.warn("未使用标准变量名（--bg-primary / --text-primary / --accent-1 ...），图表模板无法自动适配")
    if re.search(r"<link[^>]+href\s*=\s*[\"']https?://(?!fonts\.)", html, re.I):
        report.warn("引用了外部样式表，离线打开或转换时可能丢失")
    if re.search(r"<img[^>]+src\s*=\s*[\"']https?://", html, re.I):
        report.warn("引用了远程图片，转 PPTX 时不会嵌入，请先下载到 images/")

    raster = []
    for level, message, hits in C.scan_compat(html):
        if level == "error":
            report.error(f"{message}（{hits} 处）")
        elif level == "lost":
            report.warn(f"{message}（{hits} 处）")
        else:
            raster.append(message)
    if raster:
        report.note("将转为图层（不可编辑）：" + "、".join(raster))

    sizes = [float(v) for v in re.findall(r"font-size\s*:\s*([\d.]+)px", html)]
    if sizes and min(sizes) < 9:
        report.warn(f"存在 {min(sizes):g}px 的文字，投影时不可读")
    if re.search(r"\d", re.sub(r"<style.*?</style>", "", html, flags=re.S)) and "tabular-nums" not in html:
        report.warn("页面含数字但未启用 font-variant-numeric: tabular-nums")

    if not page:
        return report
    expected = len([c for c in page.get("cards") or [] if isinstance(c, dict)])
    found = count_cards(html)
    if expected and found < expected:
        report.warn(f"策划稿有 {expected} 张卡片，HTML 里只标出 {found} 张"
                    "（卡片根节点应带 data-card-id 或 class 含 card）")
    density = C.DENSITY.get(page.get("density_label"))
    if density:
        too_small = sorted({float(size) for selector, block in re.findall(r"([^{}]+)\{([^{}]*)\}", html)
                            if _BODY_SELECTOR.search(selector)
                            for size in re.findall(r"font-size\s*:\s*([\d.]+)px", block)
                            if float(size) < density["min_body_font_px"]})
        if too_small:
            report.warn(f"正文字号 {too_small} 低于 {page['density_label']} 密度的下限 "
                        f"{density['min_body_font_px']}px")
    return report


def validate_slides(slides: Path, planning: list[dict] | None = None) -> Report:
    report = Report()
    files = [slides] if slides.is_file() else sorted(slides.glob("*.html"), key=_natural_key)
    if not files:
        report.error(f"{slides} 下没有 HTML 文件")
        return report
    if planning and len(files) != len(planning):
        report.warn(f"HTML {len(files)} 页，策划稿 {len(planning)} 页，数量不一致，跳过逐页对照")
        planning = None
    for index, path in enumerate(files):
        page = planning[index] if planning else None
        report.merge(validate_slide(path.read_text(encoding="utf-8"), page), prefix=f"{path.name}: ")
    report.note(f"{len(files)} 个 HTML 文件")
    return report


# ── png/*.png（像素级检查，不依赖配色深浅）────────────────────────────────

def validate_png(path: Path, page_type: str | None = None) -> Report:
    report = Report()
    try:
        from PIL import Image
    except ImportError:
        report.warn("未安装 Pillow，跳过截图检查（pip install Pillow）")
        return report
    if path.stat().st_size < 10_000:
        report.error(f"文件仅 {path.stat().st_size} 字节，疑似截图失败")
        return report
    image = Image.open(path).convert("L")
    width, height = image.size
    if abs(width / height - 16 / 9) > 0.02:
        report.error(f"尺寸 {width}x{height} 不是 16:9")
    elif width < 960:
        report.warn(f"尺寸 {width}x{height} 偏小")

    # 内容量 = 相邻像素明暗跳变的比例。与背景深浅无关，空白页接近 0。
    small = image.resize((160, 90))
    pixels = small.load()
    edges = sum(1 for y in range(90) for x in range(1, 160) if abs(pixels[x, y] - pixels[x - 1, y]) > 14)
    density = edges / (159 * 90)
    sparse_ok = page_type in ("cover", "section", "end")
    if density < 0.002:
        report.error(f"画面几乎没有内容（边缘密度 {density:.4f}）")
    elif density < 0.012 and not sparse_ok:
        report.warn(f"内容偏少（边缘密度 {density:.4f}），请确认不是大面积留白")
    return report


def validate_pngs(pngs: Path, planning: list[dict] | None = None) -> Report:
    report = Report()
    files = [pngs] if pngs.is_file() else sorted(pngs.glob("*.png"), key=_natural_key)
    if not files:
        report.error(f"{pngs} 下没有 PNG 文件")
        return report
    if planning and len(files) != len(planning):
        planning = None
    for index, path in enumerate(files):
        page_type = planning[index].get("page_type") if planning else None
        report.merge(validate_png(path, page_type), prefix=f"{path.name}: ")
    report.note(f"{len(files)} 张截图")
    return report


# ── 整个输出目录 ────────────────────────────────────────────────────────────

def validate_all(output_dir: Path) -> Report:
    report = Report()
    planning = None
    steps = (
        ("outline.json", lambda p: validate_outline(C.load_json(p))),
        ("planning.json", lambda p: validate_planning(C.load_json(p))),
        ("style.json", lambda p: validate_style(C.load_json(p))),
    )
    for name, check in steps:
        path = output_dir / name
        if not path.exists():
            report.warn(f"{name}: 不存在，跳过")
            continue
        try:
            report.merge(check(path), prefix=f"{name}: ")
            if name == "planning.json":
                planning = planning_pages(C.load_json(path))
        except ValueError as exc:
            report.error(f"{name}: {exc}")

    slides = output_dir / "slides"
    if slides.is_dir():
        report.merge(validate_slides(slides, planning), prefix="slides/")
    else:
        report.error("slides/ 不存在")
    if (output_dir / "png").is_dir():
        report.merge(validate_pngs(output_dir / "png", planning), prefix="png/")

    count = len(list(slides.glob("*.html"))) if slides.is_dir() else 0
    for name in ("preview.html", "presentation.pptx"):
        if not (output_dir / name).exists():
            report.warn(f"{name} 尚未生成（Step 6 后处理）")
    svg_dir = output_dir / "svg"
    if svg_dir.is_dir() and count and len(list(svg_dir.glob("*.svg"))) != count:
        report.error(f"svg/ 有 {len(list(svg_dir.glob('*.svg')))} 个文件，slides/ 有 {count} 页")
    return report


def _page_range(text: str) -> tuple[int, int]:
    low, _, high = text.partition("-")
    return int(low), int(high or low)


def main() -> int:
    parser = argparse.ArgumentParser(description="PPT pipeline 产物校验（严格模式）")
    parser.add_argument("--strict", action="store_true", help="WARN 也算失败")
    sub = parser.add_subparsers(dest="command", required=True)
    outline = sub.add_parser("outline", help="校验 outline.json")
    outline.add_argument("path")
    outline.add_argument("--pages", type=_page_range, help="用户要求的页数，如 12 或 10-15")
    sub.add_parser("planning", help="校验 planning.json").add_argument("path")
    style = sub.add_parser("style", help="校验 style.json")
    style.add_argument("path")
    style.add_argument("--preset", action="store_true", help="按预置风格库的完整字段要求检查")
    for name, help_text in (("slides", "校验 HTML 设计稿"), ("visual", "检查幻灯片截图")):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("path")
        cmd.add_argument("--planning", help="planning.json，用于逐页对照")
    sub.add_parser("all", help="检查输出目录里已有的全部产物").add_argument("path")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"ERROR 路径不存在：{path}", file=sys.stderr)
        return 1
    try:
        planning = planning_pages(C.load_json(Path(args.planning))) if getattr(args, "planning", None) else None
        if args.command == "outline":
            report = validate_outline(C.load_json(path), args.pages)
        elif args.command == "planning":
            report = validate_planning(C.load_json(path))
        elif args.command == "style":
            report = validate_style(C.load_json(path), preset=args.preset)
        elif args.command == "slides":
            report = validate_slides(path, planning)
        elif args.command == "visual":
            report = validate_pngs(path, planning)
        else:
            report = validate_all(path)
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    report.print(f"{args.command}: {path}")
    return 1 if report.errors or (args.strict and report.warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
