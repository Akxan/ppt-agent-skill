# References 索引

SKILL.md 的 6 步流程在各步按需读取这里的文件。枚举值、图表注册表等"机器要认"的定义以 `scripts/contracts.py` 为准，这里的文档负责解释怎么用。

## 目录

```
references/
  prompts.md            5 套 Prompt 模板（调研 / 大纲 / 策划 / 设计 / 演讲备注）
  method.md             核心方法论
  bento-grid.md         画布参数、7 种布局、6 种基础卡片
  typography.md         排版铁律 14 条
  pipeline-compat.md    哪些 CSS 保持矢量、哪些转图层、哪些会丢
  strict-mode.md        可选的脚本校验：规则、可选字段、图审清单
  styles/               26 种预置风格（index.md + 5 个板块文件）
  charts/               18 种图表（index.md + basic / advanced / complex）
  layouts/              10 种版式的重力结构与禁忌
  blocks/               7 种组件原型 + card-styles.md
  page-templates/       cover / toc / section / end
  principles/           6 条设计原则 + failure-modes.md
  design-runtime/       design-specs / css-weapons / data-type-visual-mapping
```

## 各步读什么

| 步骤 | 必读 | 按需 |
|------|------|------|
| Step 1 需求调研 | `prompts.md` #1 | |
| Step 3 大纲 | `prompts.md` #2 | `principles/narrative-arc.md` |
| Step 4 策划稿 | `prompts.md` #3、`bento-grid.md` | `charts/index.md`、`design-runtime/data-type-visual-mapping.md`、`principles/cognitive-load.md` |
| Step 5a 风格 | `styles/index.md`、选中的板块文件 | `principles/color-psychology.md` |
| Step 5c 设计稿 | `prompts.md` #4、`typography.md`、`pipeline-compat.md` | 资源路由取到的 `layouts/` `blocks/` `page-templates/` `charts/`；`design-runtime/css-weapons.md` |
| 自检 | `principles/failure-modes.md` | `strict-mode.md` |

## 资源路由

`scripts/resource_loader.py` 按策划稿字段取文件：

| 策划稿字段 | 取自 |
|-----------|------|
| `layout_hint` | `layouts/<版式>.md` |
| `page_type` | `page-templates/<类型>.md` |
| `card_type` | `blocks/<组件>.md`（基础卡片在 `bento-grid.md`） |
| `chart_type` | `charts/{basic,advanced,complex}.md` 的对应小节 |
| `card_style` | `blocks/card-styles.md` |

```bash
python3 scripts/resource_loader.py menu                                           # 全部可选项
python3 scripts/resource_loader.py resolve --planning ppt-output/planning.json --page 3
```

## 资源文件的格式约定

`layouts/`、`blocks/`、`page-templates/` 下的每个文件：第一个 `# 标题`，紧跟一段 `> 引用块`（适用数据、卡片数、禁忌——`menu` 只显示它的第一行），之后是正文（`resolve` 输出标题与正文）。新增文件放进对应目录即可被 `menu` 发现；新增版式、卡片类型或图表还要在 `scripts/contracts.py` 登记。

## 维护

```bash
python3 scripts/smoke_test.py    # 含 docs 套件：检查文档里引用的路径是否都存在
```
