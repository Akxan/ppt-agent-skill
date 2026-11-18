#!/usr/bin/env python3
"""资源路由：按策划稿字段从 references/ 取出需要的版式 / 组件 / 图表 / 页面模板说明。

  menu     列出全部可选资源（id + 一句话说明），Step 4 写策划稿时选型用
  resolve  取出策划稿引用到的资源正文，Step 5c 写某一页 HTML 前读取

路由规则（枚举与图表注册表见 scripts/contracts.py）：
  layout_hint -> references/layouts/<版式>.md
  page_type   -> references/page-templates/<类型>.md（content 页没有模板）
  card_type   -> references/blocks/<组件>.md（text/data/list 等基础卡片见 bento-grid.md，无单独文件）
  chart_type  -> references/charts/{basic,advanced,complex}.md 里对应的小节
  card_style  -> references/blocks/card-styles.md

用法：
  python3 resource_loader.py menu
  python3 resource_loader.py resolve --planning OUTPUT_DIR/planning.json --page 3
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import contracts as C
from validate import card_chart, page_number, planning_pages


def read_resource(path: Path) -> tuple[str, str, str]:
    """资源文件 -> (标题, 引用块摘要, 正文)。约定：首个 # 标题，其后紧跟 > 引用块。"""
    title, quote, body = "", [], []
    state = "head"
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if state == "head":
            if stripped.startswith("# "):
                title, state = stripped[2:].strip(), "quote"
        elif state == "quote":
            if stripped.startswith(">"):
                quote.append(stripped[1:].strip())
            elif stripped or quote:
                state = "body"
                body.append(line)
        else:
            body.append(line)
    return title, "\n".join(quote).strip(), "\n".join(body).strip()


def generate_menu(refs_dir: Path = C.REFS_DIR) -> str:
    sections = []
    for directory, field in (("layouts", "layout_hint"), ("blocks", "card_type"), ("page-templates", "page_type")):
        lines = [f"### {directory}/  （{field}）"]
        for path in sorted((refs_dir / directory).glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            title, quote, _ = read_resource(path)
            summary = quote.splitlines()[0] if quote else ""
            lines.append(f"- `{path.stem.replace('-', '_') if directory == 'blocks' else path.stem}` {title}"
                         + (f" — {summary}" if summary else ""))
        sections.append("\n".join(lines))

    lines = ["### charts/  （chart_type）"]
    for chart_id, spec in C.CHARTS.items():
        lines.append(f"- `{chart_id}` {spec['name']}（{spec['file']}）")
    sections.append("\n".join(lines))

    lines = ["### styles/  （style_id）"]
    for style in C.load_styles(refs_dir):
        category = C.STYLE_CATEGORIES[style["category"]]["cn"]
        lines.append(f"- `{style['style_id']}` {style['style_name']} — {category} · {style.get('inspiration', '')}")
    sections.append("\n".join(lines))
    return "\n\n".join(sections)


def resolve_resources(pages: list[dict], refs_dir: Path = C.REFS_DIR) -> tuple[str, list[str]]:
    """-> (拼接好的资源正文, 找不到资源的引用列表)"""
    files: dict[Path, None] = {}          # 保持首次出现的顺序
    charts: dict[str, None] = {}
    unresolved: list[str] = []

    def want(path: Path, ref: str, required: bool = True) -> None:
        if path.exists():
            files.setdefault(path)
        elif required:
            unresolved.append(ref)

    for page in pages:
        page_type = page.get("page_type")
        if page_type in C.PAGE_TYPES and page_type != "content":
            want(refs_dir / "page-templates" / f"{page_type}.md", f"page_type={page_type}")
        if page.get("layout_hint"):
            layout = C.normalize_layout(page["layout_hint"])
            if layout:
                want(refs_dir / "layouts" / f"{layout}.md", f"layout_hint={layout}")
            else:
                unresolved.append(f"layout_hint={page['layout_hint']}")
        for card in page.get("cards") or []:
            if not isinstance(card, dict):
                continue
            card_type = card.get("card_type")
            if isinstance(card_type, str):
                # 基础卡片类型没有单独文件，不算缺失
                want(refs_dir / "blocks" / f"{card_type.replace('_', '-')}.md", f"card_type={card_type}",
                     required=card_type in C.BLOCK_CARD_TYPES)
            if card.get("card_style"):
                want(refs_dir / "blocks" / "card-styles.md", "card_style")
            chart = card_chart(card)
            if chart:
                chart_id = C.normalize_chart(chart)
                if chart_id:
                    charts.setdefault(chart_id)
                else:
                    unresolved.append(f"chart_type={chart}")

    sections = []
    for path in files:
        title, _, body = read_resource(path)
        sections.append(f"# {title}\n\n{body}")
    for chart_id in charts:
        title, body = C.chart_section(chart_id, refs_dir)
        sections.append(f"# 图表：{title}\n\n{body}")
    return "\n\n---\n\n".join(sections), unresolved


def main() -> int:
    parser = argparse.ArgumentParser(description="按策划稿字段加载 references/ 资源")
    sub = parser.add_subparsers(dest="mode", required=True)
    for name in ("menu", "resolve"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--refs-dir", default=str(C.REFS_DIR), help="references 目录（默认取 skill 自带的）")
        cmd.add_argument("--output", help="写入文件（默认输出到 stdout）")
    resolve = sub.choices["resolve"]
    resolve.add_argument("--planning", required=True, help="planning.json")
    resolve.add_argument("--page", type=int, help="只取某一页的资源（默认整份策划稿）")
    args = parser.parse_args()

    refs_dir = Path(args.refs_dir)
    if not refs_dir.is_dir():
        print(f"ERROR: references 目录不存在：{refs_dir}", file=sys.stderr)
        return 1

    if args.mode == "menu":
        result = generate_menu(refs_dir)
    else:
        try:
            pages = planning_pages(C.load_json(Path(args.planning)))
        except (OSError, ValueError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        if args.page is not None:
            pages = [page for page in pages if page_number(page) == args.page]
        if not pages:
            print("ERROR: 策划稿里没有匹配的页面", file=sys.stderr)
            return 1
        result, unresolved = resolve_resources(pages, refs_dir)
        for ref in unresolved:
            print(f"WARN: 找不到资源 {ref}", file=sys.stderr)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Written to {args.output} ({len(result)} chars)", file=sys.stderr)
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
