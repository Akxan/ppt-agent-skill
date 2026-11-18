#!/usr/bin/env python3
"""数据合同的单一真源：6 步 pipeline 各产物的枚举、图表注册表、风格字段、管线兼容规则。

validate.py / resource_loader.py / gallery.py / build_hero.py / smoke_test.py 都从这里取值。
改枚举或新增图表、风格板块时只改这一个文件，再同步 references/ 下的说明文档。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
REFS_DIR = SKILL_DIR / "references"
CANVAS_W, CANVAS_H = 1280, 720

# ── 页面与版式 ──────────────────────────────────────────────────────────────

PAGE_TYPES = ("cover", "toc", "section", "content", "end")

# 版式 id -> 文档里出现过的中文叫法（策划稿的 layout_hint 两种写法都接受）
LAYOUTS = {
    "single-focus": ("单一焦点",),
    "symmetric": ("50/50 对称", "对称"),
    "asymmetric": ("非对称两栏", "非对称"),
    "three-column": ("三栏等宽", "三栏"),
    "primary-secondary": ("主次结合",),
    "hero-top": ("顶部英雄式", "英雄式"),
    "mixed-grid": ("混合网格",),
    "l-shape": ("L 形", "L形"),
    "t-shape": ("T 形", "T形"),
    "waterfall": ("瀑布流", "瀑布"),
}
# 版式本身容纳的卡片数下限；未列出的版式按 3 张
LAYOUT_MIN_CARDS = {"single-focus": 1, "symmetric": 2, "asymmetric": 2}
DEFAULT_MIN_CARDS = 3


def normalize_layout(value: Any) -> str | None:
    """'主次结合' / 'primary_secondary' / '英雄式 + 下方三栏' -> 版式 id；认不出返回 None。"""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    slug = text.lower().replace("_", "-").replace(" ", "-")
    if slug in LAYOUTS:
        return slug
    hits = [(text.find(alias), layout_id) for layout_id, aliases in LAYOUTS.items()
            for alias in aliases if alias in text]
    return min(hits)[1] if hits else None


# ── 卡片 ────────────────────────────────────────────────────────────────────

BASE_CARD_TYPES = ("text", "data", "list", "tag_cloud", "process", "data_highlight")
BLOCK_CARD_TYPES = ("timeline", "diagram", "quote", "comparison", "people", "image_hero", "matrix_chart")
CARD_TYPES = BASE_CARD_TYPES + BLOCK_CARD_TYPES
DATA_CARD_TYPES = ("data", "data_highlight")
CARD_STYLES = ("accent", "elevated", "filled", "outline", "glass", "transparent")
CARD_ROLES = ("anchor", "support", "context")

# 页面密度（可选字段 density_label）-> 卡片数上限 / 正文字号下限(px)
DENSITY = {
    "low": {"max_cards": 2, "min_body_font_px": 24},
    "mid_low": {"max_cards": 3, "min_body_font_px": 20},
    "medium": {"max_cards": 4, "min_body_font_px": 18},
    "high": {"max_cards": 6, "min_body_font_px": 16},
    "dashboard": {"max_cards": 8, "min_body_font_px": 14},
}

# ── 图表注册表：chart_type -> references/charts/<file> 里的 "## <section>. " 小节 ──

CHARTS = {
    "progress_bar": {"file": "basic.md", "section": 1, "name": "进度条", "aliases": ()},
    "comparison_bar": {"file": "basic.md", "section": 2, "name": "对比柱", "aliases": ("compare_bar",)},
    "ring": {"file": "basic.md", "section": 3, "name": "环形图", "aliases": ("ring_chart",)},
    "sparkline": {"file": "basic.md", "section": 4, "name": "迷你折线", "aliases": ()},
    "waffle": {"file": "basic.md", "section": 5, "name": "点阵图", "aliases": ("waffle_chart",)},
    "kpi": {"file": "basic.md", "section": 6, "name": "KPI 指标卡", "aliases": ("kpi_card",)},
    "metric_row": {"file": "basic.md", "section": 7, "name": "指标行", "aliases": ()},
    "rating": {"file": "basic.md", "section": 8, "name": "评分指示器", "aliases": ()},
    "radar": {"file": "advanced.md", "section": 1, "name": "雷达图", "aliases": ()},
    "timeline": {"file": "advanced.md", "section": 2, "name": "时间线", "aliases": ()},
    "funnel": {"file": "advanced.md", "section": 3, "name": "漏斗图", "aliases": ()},
    "gauge": {"file": "advanced.md", "section": 4, "name": "仪表盘", "aliases": ()},
    "grouped_bar": {"file": "advanced.md", "section": 5, "name": "多组对比柱", "aliases": ("stacked_bar",)},
    "simple_map": {"file": "advanced.md", "section": 6, "name": "简单地理", "aliases": ()},
    "world_choropleth": {"file": "complex.md", "section": 15, "name": "世界地图", "aliases": ("world_map",)},
    "network_graph": {"file": "complex.md", "section": 16, "name": "关系网络", "aliases": ("network",)},
    "sankey_flow": {"file": "complex.md", "section": 17, "name": "桑基图", "aliases": ("sankey",)},
    "heatmap_calendar": {"file": "complex.md", "section": 18, "name": "热力日历", "aliases": ("heatmap",)},
}
_CHART_ALIASES = {alias: chart_id for chart_id, spec in CHARTS.items() for alias in spec["aliases"]}


def normalize_chart(value: Any) -> str | None:
    """'kpi-card' / 'KPI_Card' / 'kpi' -> 'kpi'；认不出返回 None。"""
    if not isinstance(value, str) or not value.strip():
        return None
    slug = value.strip().lower().replace("-", "_").replace(" ", "_")
    return slug if slug in CHARTS else _CHART_ALIASES.get(slug)


def chart_section(chart_id: str, refs_dir: Path = REFS_DIR) -> tuple[str, str]:
    """取某个图表在 charts/*.md 里的小节 -> (标题, 正文 markdown)。"""
    spec = CHARTS[chart_id]
    text = (refs_dir / "charts" / spec["file"]).read_text(encoding="utf-8")
    match = re.search(rf"^## {spec['section']}\. (.+?)$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        raise KeyError(f"charts/{spec['file']} 缺少小节 '## {spec['section']}. '（chart_type={chart_id}）")
    return match.group(1).strip(), match.group(2).strip().removesuffix("---").strip()


# ── 风格 ────────────────────────────────────────────────────────────────────

STYLE_CATEGORIES = {
    "dark_professional": {"cn": "暗色专业", "en": "Dark Professional", "file": "dark.md"},
    "light_premium": {"cn": "浅色高级", "en": "Light Premium", "file": "light.md"},
    "vibrant": {"cn": "活力鲜明", "en": "Vibrant", "file": "vibrant.md"},
    "cultural_oriental": {"cn": "东方文化", "en": "Cultural Oriental", "file": "cultural.md"},
    "natural_retro": {"cn": "自然/复古", "en": "Natural / Retro", "file": "natural.md"},
}
# style.json 生成 CSS 变量所必需的字段（自定义风格的最低要求）
STYLE_CORE_FIELDS = ("background", "card", "text", "accent")
# 预置风格库额外要求的字段
STYLE_PRESET_FIELDS = ("style_id", "style_name", "category", "inspiration", "mood_keywords", "design_soul",
                       "variation_strategy", "decoration_dna", "typography", "decorations", "font_imports")
STYLE_DNA_FIELDS = ("signature_move", "forbidden", "recommended_combos")
STYLE_TYPOGRAPHY_FIELDS = ("display_font", "body_font", "display_letter_spacing", "tabular_nums")
_STYLE_ID = re.compile(r"^[a-z][a-z0-9_]*$")


def load_styles(refs_dir: Path = REFS_DIR) -> list[dict]:
    """读出预置风格库：按板块顺序返回 references/styles/<板块>.md 里的全部风格 JSON。"""
    styles = []
    for category in STYLE_CATEGORIES.values():
        text = (refs_dir / "styles" / category["file"]).read_text(encoding="utf-8")
        for block in re.findall(r"```json\s*\n(.*?)\n```", text, re.S):
            try:
                style = json.loads(block)
            except json.JSONDecodeError:
                continue
            if isinstance(style, dict) and _STYLE_ID.match(str(style.get("style_id", ""))):
                styles.append(style)
    return styles


def style_css_variables(style: dict) -> dict[str, str]:
    """风格 JSON -> :root 里的 CSS 变量（Prompt #4 "CSS 变量模板" 的代码实现）。"""
    background, card = style.get("background", {}), style.get("card", {})
    text, accent = style.get("text", {}), style.get("accent", {})
    primary = list(accent.get("primary", [])) + ["", ""]
    secondary = list(accent.get("secondary", [])) + ["", ""]
    typography = style.get("typography", {})
    variables = {
        "--bg-primary": background.get("primary", ""),
        "--bg-secondary": background.get("gradient_to", ""),
        "--card-bg-from": card.get("gradient_from", ""),
        "--card-bg-to": card.get("gradient_to", ""),
        "--card-border": card.get("border", ""),
        "--card-radius": f"{card.get('border_radius', 12)}px",
        "--text-primary": text.get("primary", ""),
        "--text-secondary": text.get("secondary", ""),
        "--accent-1": primary[0], "--accent-2": primary[1],
        "--accent-3": secondary[0], "--accent-4": secondary[1],
    }
    for key, var in (("display_font", "--display-font"), ("body_font", "--body-font"),
                     ("serif_italic_font", "--serif-italic-font"), ("mono_font", "--mono-font")):
        if typography.get(key):
            variables[var] = typography[key]
    return variables


CORE_CSS_VARIABLES = ("--bg-primary", "--bg-secondary", "--card-bg-from", "--card-bg-to", "--card-border",
                      "--card-radius", "--text-primary", "--text-secondary",
                      "--accent-1", "--accent-2", "--accent-3", "--accent-4")

# ── 管线兼容规则：(级别, 正则, 说明) ────────────────────────────────────────
#   error  转换后内容缺失或行为不确定，必须改
#   lost   该效果在可编辑 PPTX 里丢失或退化（预览页与 PNG 版 PPTX 不受影响）
#   raster html2svg 自动截成图层：外观保真，但这部分在 PPT 里是图片、不可编辑
# 详细说明见 references/pipeline-compat.md

COMPAT_RULES = (
    ("error", r"<script\b", "<script>：幻灯片必须是静态 HTML，预览页的沙箱 iframe 不执行脚本"),
    ("error", r"<(canvas|video|iframe|object|embed)\b", "<canvas>/<video>/<iframe>：不会被转换，内容丢失"),
    ("error", r"@keyframes|\banimation(-name)?\s*:", "CSS 动画：转换只取静态一帧；动效请用 svg2pptx 的 --animate"),
    ("lost", r"text-shadow\s*:(?!\s*none)", "text-shadow：文字阴影/辉光丢失"),
    ("lost", r"(-webkit-)?background-clip\s*:\s*text", "background-clip:text：渐变文字退化为渐变首色"),
    ("lost", r"backdrop-filter\s*:(?!\s*none)", "backdrop-filter：背景模糊丢失，卡片保留半透明填充"),
    ("lost", r"::first-(letter|line)|::marker", "::first-letter/::first-line/::marker：样式丢失"),
    ("lost", r"stroke-dashoffset", "stroke-dashoffset：被忽略，环形图请用 stroke-dasharray=\"弧长 周长\""),
    ("raster", r"(radial|conic)-gradient\(|repeating-[a-z]+-gradient\(", "径向/锥形/重复渐变"),
    ("raster", r"(?<![\w-])filter\s*:(?!\s*none)", "filter（blur 等）"),
    ("raster", r"(-webkit-)?mask(-image)?\s*:(?!\s*none)", "mask-image"),
    ("raster", r"clip-path\s*:(?!\s*none)", "clip-path"),
    ("raster", r"background(-image)?\s*:[^;{}]*url\(", "CSS 背景图"),
    ("raster", r"mix-blend-mode\s*:(?!\s*normal)", "mix-blend-mode"),
    ("raster", r"transform\s*:[^;{}]*(rotate|skew)", "旋转/斜切变换"),
)


def scan_compat(html_text: str) -> list[tuple[str, str, int]]:
    """扫描一页 HTML -> [(级别, 说明, 命中次数)]，忽略 CSS/HTML 注释里的内容。"""
    source = re.sub(r"/\*.*?\*/|<!--.*?-->", "", html_text, flags=re.S)
    findings = []
    for level, pattern, message in COMPAT_RULES:
        hits = len(re.findall(pattern, source, flags=re.I))
        if hits:
            findings.append((level, message, hits))
    return findings


# ── JSON 读取 ───────────────────────────────────────────────────────────────

def load_json(path: Path) -> Any:
    """读取 JSON，容忍 ```json 围栏与 [PPT_OUTLINE]...[/PPT_OUTLINE] 这类包裹标记。"""
    text = Path(path).read_text(encoding="utf-8").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    candidates = [fenced.group(1)] if fenced else []
    for opener, closer in (("{", "}"), ("[", "]")):
        first, last = text.find(opener), text.rfind(closer)
        if 0 <= first < last:
            candidates.append(text[first:last + 1])
    for candidate in sorted(candidates, key=len, reverse=True):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError(f"无法解析 JSON：{path}")
