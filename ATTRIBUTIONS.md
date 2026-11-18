# Attributions

本项目建立在开源社区的工作之上。

---

## sunbigfly/ppt-agent-skills (MIT License)

**仓库**：https://github.com/sunbigfly/ppt-agent-skills
**作者**：sunbigfly
**许可**：MIT License (Copyright © 2025 sunbigfly)

### 仍在使用的资源

以下目录的文件来自该项目，为适配本项目的单一流程与导出管线做过修改：

| 目录 | 内容 |
|------|------|
| `references/principles/` | 6 份设计原则（visual-hierarchy / cognitive-load / composition / color-psychology / data-visualization / narrative-arc）+ README |
| `references/design-runtime/` | design-specs / css-weapons / data-type-visual-mapping |
| `references/blocks/` | 7 种组件原型（timeline / diagram / quote / comparison / people / image-hero / matrix-chart）+ card-styles + README |
| `references/page-templates/` | cover / toc / section / end |
| `references/layouts/` | 10 种版式 + README |

### 借鉴的概念

- **资源路由**：策划稿字段决定读取哪份参考文件（`layout_hint→layouts/`、`page_type→page-templates/`、`card_type→blocks/`、`chart_type→charts/`）
- **页面密度**（`density_label`）、**卡片角色**（`role`）与**卡片风格**（`card_style`）——现为策划稿的可选字段
- **失败模式目录**的 8 模式分类法与修复顺序（`references/principles/failure-modes.md`）
- **图审缺陷分级**（P0 / P1 / P2，`references/strict-mode.md` 第 4 节）
- 风格 JSON 的 `mood_keywords` / `design_soul` / `variation_strategy` / `decoration_dna` 字段
- 用脚本校验阶段产物、用冒烟测试守住文档与代码一致性的做法

### 曾经引入、后来移除的部分

2026-05 曾整体拷入该项目的子代理调度链（`references/prompts/`、`references/playbooks/`、`cli-cheatsheet.md` 及配套的 prompt_harness / subagent_logger / milestone_check / contract_validator / planning_validator / visual_qa / check_skill / smoke_skill 等脚本）。本项目以 SKILL.md 的 6 步流程为唯一入口后，这条链路未被使用，已于 2026-11 移除；其中的校验思路由 `scripts/validate.py` 重新实现。

需要多阶段子代理编排、更深的阶段合同的版本，请直接使用原项目。

### 本项目在此之上的工作

| 维度 | 内容 |
|------|------|
| 风格库 | 26 种预置风格，分 5 个板块，各有 1280×720 标杆 mock 与截图 |
| 图表库 | 18 种纯 HTML/CSS/SVG 图表，分基础 / 进阶 / 复杂三层 |
| 排版 | [`typography.md`](references/typography.md) 14 条 |
| 导出管线 | 选择性栅格化、完整仿射变换、卡片成组、字体映射与按宽度缩字号（`html2svg.py` / `svg2pptx.py`） |
| 动效 | 页间切换与卡片入场动画（`pptx_motion.py`） |
| 合同与校验 | `contracts.py` 单一真源、`validate.py` 严格模式、`smoke_test.py` |
| 展示 | 风格预览画廊（`gallery.py`）、README 拼图（`build_hero.py`）、架构图 |

---

## 字体（Google Fonts，OFL/Apache 2.0）

各风格的 mock 通过 Google Fonts CDN 引入 Web 字体：

- **Inter / Inter Tight** ([rsms/inter](https://github.com/rsms/inter), OFL)
- **Source Serif 4** (Adobe, OFL)
- **Instrument Serif** (Instrument Studio, OFL)
- **Fraunces** (Undercase Type, OFL)
- **Playfair Display** (Claus Eggers Sørensen, OFL)
- **Noto Serif SC / JP、Noto Sans SC** (Google, OFL)
- **JetBrains Mono** (JetBrains, OFL)、**IBM Plex Mono** (IBM, OFL)
- **Quicksand** (Andrew Paglinawan, OFL)、**Nunito** (Vernon Adams, OFL)
- **Orbitron** (Matt McInerney, OFL)
- **Bagel Fat One / Bowlby One** (OFL)

导出的 PPTX 默认不依赖这些字体（映射到 Office 自带字体）。

## 导出依赖

- [dom-to-svg](https://github.com/felixfbecker/dom-to-svg) (MIT) — DOM 转 SVG
- [Puppeteer](https://github.com/puppeteer/puppeteer) (Apache 2.0) — 无头浏览器
- [python-pptx](https://github.com/scanny/python-pptx) (MIT)、[lxml](https://lxml.de) (BSD)、[Pillow](https://python-pillow.org) (MIT-CMU)

---

## 设计参照

排版做法来自对实际品牌官网 CSS 的阅读（**不参与代码授权，仅作设计灵感**）：

Linear / Anthropic / Stripe / Apple / OpenAI / Vercel / NYT Magazine / Pitch / Mercury / Arc / Tom Ford / Notion / Patagonia / National Geographic / Mayo Clinic / Suisse Int'l / Bauhaus / Cyberpunk 2077 / iOS 26 / Wes Anderson / 北京冬奥开幕式 / Apple Keynote 等。

---

## License

本项目采用 [MIT License](LICENSE)。来自 sunbigfly 的文件保留其原始 MIT 许可。
