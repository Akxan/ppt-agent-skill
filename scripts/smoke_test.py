#!/usr/bin/env python3
"""冒烟测试：改完风格 / 图表 / 文档 / 脚本后跑一遍。

快速套件（默认全跑，几秒钟，只需 Python 标准库）：
  styles      26 个预置风格 JSON 字段完整，且各有 mock HTML 与截图
  mocks       风格 mock 通过幻灯片合同与管线兼容检查
  charts      18 种图表都能从注册表取到模板，模板本身通过兼容检查
  validators  validate.py 对正确样例放行、对错误样例报错
  resources   resource_loader.py 的 menu / resolve 能按策划稿取到资源
  docs        文档里引用的 references/ 与 scripts/ 路径全部存在

慢速套件（--export，约 1 分钟，需要 Node.js、python-pptx）：
  export      真实跑 HTML -> SVG -> PPTX，并检查背景、卡片成组、切换与动画是否写入

用法：
    python3 scripts/smoke_test.py                 # 快速套件
    python3 scripts/smoke_test.py mocks charts    # 指定套件
    python3 scripts/smoke_test.py --export        # 快速套件 + 导出管线
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import contracts as C
import resource_loader
import validate as V

ROOT = C.SKILL_DIR
GALLERY = ROOT / "ppt-output" / "style-gallery"


class Suite:
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def check(self, ok: bool, message: str) -> bool:
        if ok:
            self.passed += 1
        else:
            self.failures.append(message)
        return bool(ok)

    def absorb(self, report: V.Report, label: str) -> None:
        self.check(not report.errors, f"{label}: " + "; ".join(report.errors))
        self.warnings += [f"{label}: {w}" for w in report.warnings]


# ── 快速套件 ────────────────────────────────────────────────────────────────

def suite_styles(s: Suite) -> None:
    styles = C.load_styles()
    s.check(len(styles) == 26, f"预置风格应为 26 个，实际 {len(styles)}")
    ids = [style["style_id"] for style in styles]
    s.check(len(set(ids)) == len(ids), "style_id 有重复")
    for style in styles:
        sid = style["style_id"]
        s.absorb(V.validate_style(style, preset=True), sid)
        s.check((GALLERY / f"{sid}.html").exists(), f"{sid}: 缺少 mock HTML")
        s.check((GALLERY / f"{sid}.png").exists(), f"{sid}: 缺少截图 PNG")


def suite_mocks(s: Suite) -> None:
    for style in C.load_styles():
        path = GALLERY / f"{style['style_id']}.html"
        if path.exists():
            s.absorb(V.validate_slide(path.read_text(encoding="utf-8")), path.name)


def suite_charts(s: Suite) -> None:
    for chart_id in C.CHARTS:
        try:
            title, body = C.chart_section(chart_id)
        except (KeyError, OSError) as exc:
            s.check(False, f"{chart_id}: {exc}")
            continue
        templates = re.findall(r"```html\s*\n(.*?)\n```", body, re.S)
        if not s.check(bool(templates), f"{chart_id}: 小节「{title}」里没有 HTML 模板"):
            continue
        for index, template in enumerate(templates, start=1):
            label = f"{chart_id} 模板 {index}"
            errors = [m for level, m, _ in C.scan_compat(template) if level == "error"]
            s.check(not errors, f"{label}: " + "; ".join(errors))
            if "var(--" not in template:                      # 涨跌红绿等惯例色的变体允许写死
                s.warnings.append(f"{label}: 未使用 CSS 变量，不会随风格切换")
            if re.search(r"<text\b", template):
                s.warnings.append(f"{label}: 内联 SVG 含 <text>，转 PPTX 后位置可能有 3-5px 偏差")
    for alias, expected in (("kpi-card", "kpi"), ("Ring_Chart", "ring"), ("stacked_bar", "grouped_bar")):
        s.check(C.normalize_chart(alias) == expected, f"图表别名 {alias} 应归一为 {expected}")


def _planning_fixture() -> list[dict]:
    card = lambda kind, title, **extra: {"card_type": kind, "title": title, "content": "示例内容", **extra}  # noqa: E731
    return [
        {"page_number": 1, "page_type": "cover", "title": "封面", "cards": []},
        {"page_number": 2, "page_type": "content", "title": "增长概览", "goal": "营收翻倍",
         "layout_hint": "主次结合",
         "content_summary": {"data_highlights": [{"value": "2.4M", "label": "MAU"}]},
         "cards": [card("data", "月活", chart_type="kpi", data_points=["2.4M"]),
                   card("list", "驱动因素"), card("comparison", "同比")]},
        {"page_number": 3, "page_type": "end", "title": "谢谢", "cards": []},
    ]


def suite_validators(s: Suite) -> None:
    page = {"title": "市场规模", "goal": "千亿赛道", "content": ["2026 年规模 1200 亿"], "data_needs": []}
    outline = {"ppt_outline": {
        "cover": {"title": "AI 安全年度报告"}, "table_of_contents": {"title": "目录", "content": ["一", "二"]},
        "parts": [{"part_title": "第一部分", "pages": [page, page]},
                  {"part_title": "第二部分", "pages": [page, page]}],
        "end_page": {"title": "总结"}}}
    s.check(not V.validate_outline(outline, (7, 9)).errors, "正确的大纲被判错")
    s.check(V.validate_outline(outline, (20, 25)).errors, "页数不符的大纲未报错")
    thin = {"ppt_outline": {"cover": {"title": "x"}, "parts": [{"part_title": "a", "pages": [page]}]}}
    s.check(any("至少 2 页" in e for e in V.validate_outline(thin).errors), "单页 part 未报错")

    good = _planning_fixture()
    report = V.validate_planning(good)
    s.check(not report.errors, "正确的策划稿被判错: " + "; ".join(report.errors))

    def broken(mutate) -> list[str]:
        pages = _planning_fixture()
        mutate(pages[1])
        return V.validate_planning(pages).errors

    cases = {
        "卡片不足": lambda p: p.update(cards=p["cards"][:1]),
        "card_type 非法": lambda p: p["cards"][0].update(card_type="chart_placeholder"),
        "chart_type 非法": lambda p: p["cards"][0].update(chart_type="treemap"),
        "缺 layout_hint": lambda p: p.pop("layout_hint"),
        "卡片类型单一": lambda p: [c.update(card_type="text", chart_type=None, data_points=None) for c in p["cards"]],
        "多个 anchor": lambda p: [c.update(role="anchor") for c in p["cards"]],
        "超出密度上限": lambda p: p.update(density_label="low"),
    }
    for name, mutate in cases.items():
        s.check(bool(broken(mutate)), f"策划稿错误样例「{name}」未被拦下")

    style = C.load_styles()[0]
    s.check(not V.validate_style(style).errors, "预置风格作为 style.json 被判错")
    s.check(V.validate_style({"style_name": "x", "background": {}}).errors, "残缺的 style.json 未报错")

    slide = ('<style>:root{--bg-primary:#000;--text-primary:#fff;--accent-1:#0ff}'
             'body{width:1280px;height:720px;font-variant-numeric:tabular-nums}</style>'
             '<div class="card" data-card-id="a">12</div>')
    s.check(not V.validate_slide(slide).errors, "正确的幻灯片被判错")
    s.check(V.validate_slide(slide + "<script>1</script>").errors, "含 <script> 的幻灯片未报错")
    s.check(V.validate_slide(slide.replace("1280px", "1920px")).errors, "画布尺寸错误未报错")


def suite_resources(s: Suite) -> None:
    menu = resource_loader.generate_menu()
    for token in ("`hero-top`", "`image_hero`", "`cover`", "`kpi`", "`dark_tech`"):
        s.check(token in menu, f"menu 里缺少 {token}")
    text, unresolved = resource_loader.resolve_resources(_planning_fixture())
    s.check(not unresolved, f"resolve 有未解析的引用: {unresolved}")
    for expected in ("# 图表：KPI 指标卡", "封面页", "结束页", "主次"):
        s.check(expected in text, f"resolve 结果缺少「{expected}」")
    for layout in C.LAYOUTS:
        s.check((C.REFS_DIR / "layouts" / f"{layout}.md").exists(), f"layouts/{layout}.md 不存在")
    for card_type in C.BLOCK_CARD_TYPES:
        name = card_type.replace("_", "-")
        s.check((C.REFS_DIR / "blocks" / f"{name}.md").exists(), f"blocks/{name}.md 不存在")
    for page_type in C.PAGE_TYPES:
        if page_type != "content":
            s.check((C.REFS_DIR / "page-templates" / f"{page_type}.md").exists(),
                    f"page-templates/{page_type}.md 不存在")


_PATH_REF = re.compile(r"(?<![\w/.-])((?:references|scripts|assets|docs)/[\w./-]+\.(?:md|py|svg|png))")
_MD_LINK = re.compile(r"\]\(([^)#\s]+?\.(?:md|py|svg|png|html))(?:#[^)]*)?\)")


def suite_docs(s: Suite) -> None:
    docs = [ROOT / name for name in ("SKILL.md", "README.md", "README_EN.md", "ATTRIBUTIONS.md")]
    docs += sorted(C.REFS_DIR.rglob("*.md")) + sorted((ROOT / "scripts").glob("*.md"))
    for doc in docs:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.S)        # 代码块里的示例路径不算引用
        refs = {(ROOT / ref) for ref in _PATH_REF.findall(text)}
        refs |= {(doc.parent / link).resolve() for link in _MD_LINK.findall(text)
                 if not link.startswith(("http", "/"))}
        for ref in sorted(refs):
            if "<" in str(ref) or "*" in str(ref) or "{" in str(ref):
                continue
            s.check(ref.exists(), f"{doc.relative_to(ROOT)} 引用了不存在的 {ref.relative_to(ROOT) if ref.is_relative_to(ROOT) else ref}")


# ── 慢速套件：真实导出 ──────────────────────────────────────────────────────

CARD_SLIDE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
:root{--bg-primary:#0b1120;--text-primary:#fff;--accent-1:#22D3EE}
*{margin:0;box-sizing:border-box}
body{width:1280px;height:720px;overflow:hidden;color:var(--text-primary);font-family:Arial,sans-serif;
  background:radial-gradient(circle at 30% 20%,#1e3a8a,var(--bg-primary));font-variant-numeric:tabular-nums}
.grid{position:absolute;left:40px;top:80px;width:1200px;display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.card{height:200px;padding:24px;border-radius:12px;background:#1e293b}
</style></head><body><div class="grid">
<div class="card" data-card-id="a"><h3>营收</h3><p>2.4M</p></div>
<div class="card" data-card-id="b"><h3>增长</h3><p>47%</p>
  <svg width="60" height="20" viewBox="0 0 60 20"><polygon points="0,20 30,0 60,20" fill="var(--accent-1)"/></svg></div>
<div class="card" data-card-id="c"><h3>留存</h3><p>92%</p>
  <svg width="80" height="80" viewBox="0 0 80 80"><defs><linearGradient id="g"><stop offset="0%" stop-color="var(--accent-1)"/>
    <stop offset="100%" stop-color="var(--text-primary)"/></linearGradient></defs>
    <circle cx="40" cy="40" r="32" fill="none" stroke="url(#g)" stroke-width="8" stroke-dasharray="150 201"
            transform="rotate(-90 40 40)"/></svg></div>
</div></body></html>"""


def suite_export(s: Suite) -> None:
    try:
        from pptx import Presentation
    except ImportError:
        s.check(False, "未安装 python-pptx（pip install python-pptx lxml Pillow）")
        return
    python = sys.executable
    with tempfile.TemporaryDirectory(prefix="ppt-smoke-") as tmp:
        work = Path(tmp)
        slides = work / "slides"
        slides.mkdir()
        # slide-2 / slide-10 的顺序用来验证自然排序
        (slides / "slide-1.html").write_text((GALLERY / "dark_tech.html").read_text(encoding="utf-8"), encoding="utf-8")
        (slides / "slide-2.html").write_text(CARD_SLIDE, encoding="utf-8")
        (slides / "slide-10.html").write_text((GALLERY / "royal_red.html").read_text(encoding="utf-8"), encoding="utf-8")

        def run(script: str, *args: str) -> bool:
            result = subprocess.run([python, str(ROOT / "scripts" / script), *args],
                                    capture_output=True, text=True, timeout=600)
            return s.check(result.returncode == 0, f"{script} 退出码 {result.returncode}: {result.stderr[-300:]}")

        if not run("html_packager.py", str(slides), "-o", str(work / "preview.html")):
            return
        if not run("html2svg.py", str(slides), "-o", str(work / "svg")):
            return
        svgs = sorted((work / "svg").glob("*.svg"))
        s.check(len(svgs) == 3, f"应生成 3 个 SVG，实际 {len(svgs)}")
        for svg in svgs:
            s.check(svg.read_text(encoding="utf-8", errors="ignore").count("<text") >= 2,
                    f"{svg.name}: 可编辑文字过少")
        pptx_path = work / "deck.pptx"
        if not run("svg2pptx.py", str(work / "svg"), "-o", str(pptx_path), "--animate", "fade"):
            return

        prs = Presentation(str(pptx_path))
        s.check(len(prs.slides) == 3, f"PPTX 应有 3 页，实际 {len(prs.slides)}")
        p_ns = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
        for index, slide in enumerate(prs.slides, start=1):
            xml = slide._element
            s.check(xml.find(f"{p_ns}transition") is not None, f"第 {index} 页缺少页间切换")
            s.check(xml.find(f".//{p_ns}bg") is not None, f"第 {index} 页没有幻灯片背景（背景丢失）")
        card_slide = prs.slides[1]._element                    # slide-2 应排在 slide-10 前面
        groups = card_slide.findall(f".//{p_ns}grpSp")
        s.check(len(groups) == 3, f"卡片页应有 3 个组合，实际 {len(groups)}")
        effects = card_slide.findall(f".//{p_ns}animEffect")
        s.check(len(effects) == 3, f"卡片页应有 3 个入场动画，实际 {len(effects)}")
        a_ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
        s.check(card_slide.find(f".//{a_ns}custGeom") is not None, "polygon 未转成自定义形状")
        arcs = [g for g in card_slide.iter(f"{a_ns}prstGeom") if g.get("prst") == "arc"]
        s.check(len(arcs) == 1, "渐变描边（色标为 CSS 变量）的环形进度弧丢失")


SUITES = {"styles": suite_styles, "mocks": suite_mocks, "charts": suite_charts,
          "validators": suite_validators, "resources": suite_resources, "docs": suite_docs}


def main() -> int:
    parser = argparse.ArgumentParser(description="PPT Agent Skill 冒烟测试")
    parser.add_argument("suites", nargs="*", choices=[*SUITES, "export", []], help="要跑的套件（默认全部快速套件）")
    parser.add_argument("--export", action="store_true", help="追加跑真实导出管线（慢）")
    parser.add_argument("--warnings", action="store_true", help="列出全部警告")
    args = parser.parse_args()

    names = list(args.suites) or list(SUITES)
    if args.export and "export" not in names:
        names.append("export")
    total_fail = 0
    for name in names:
        suite = Suite(name)
        (suite_export if name == "export" else SUITES[name])(suite)
        status = "PASS" if not suite.failures else "FAIL"
        print(f"[{status}] {name}: {suite.passed} passed, {len(suite.failures)} failed, {len(suite.warnings)} warnings")
        for message in suite.failures:
            print(f"    FAIL {message}")
        if args.warnings:
            for message in suite.warnings:
                print(f"    WARN {message}")
        total_fail += len(suite.failures)
    return 1 if total_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
