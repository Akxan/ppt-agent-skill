# 严格模式

默认流程靠 agent 自检。严格模式在关键步骤后加一道脚本校验，把"应该"变成"过不了就不能往下走"。适合大型 deck、批量生成、或成品要交给别人二次编辑的场景。不运行不影响出稿。

校验规则的代码真源是 `scripts/contracts.py`（枚举）和 `scripts/validate.py`（规则）。

---

## 1. 命令

| 步骤后 | 命令 |
|-------|------|
| Step 3 大纲 | `python3 scripts/validate.py outline OUTPUT_DIR/outline.json --pages 10-15` |
| Step 4 策划稿 | `python3 scripts/validate.py planning OUTPUT_DIR/planning.json` |
| Step 5a 风格 | `python3 scripts/validate.py style OUTPUT_DIR/style.json` |
| Step 5c 设计稿 | `python3 scripts/validate.py slides OUTPUT_DIR/slides --planning OUTPUT_DIR/planning.json` |
| 截图 | `python3 scripts/validate.py visual OUTPUT_DIR/png --planning OUTPUT_DIR/planning.json` |
| 全部产物 | `python3 scripts/validate.py all OUTPUT_DIR` |

退出码：0 通过，1 存在 ERROR。全局参数 `--strict` 放在子命令前，WARN 也算失败。

处理方式：ERROR 必须修到消失再进入下一步；WARN 逐条判断，确认是有意为之可以保留。

---

## 2. 规则

### outline.json

| 级别 | 规则 |
|------|------|
| ERROR | 缺 `cover.title`；`parts` 为空；某个 part 少于 2 页；页面缺 `title` |
| ERROR | 给了 `--pages` 且大纲展开后的页数范围与要求不相交 |
| WARN | 页面缺 `goal` 或 `content` 为空；只有 1 个 part；缺 `end_page` |

页数估算：内容页 + 封面 + 结束页（+ 目录），每个 part 可再加一张章节封面。

### planning.json

| 级别 | 规则 |
|------|------|
| ERROR | `page_number` 不是整数或重复；`page_type` 不在 cover/toc/section/content/end；缺 `title` |
| ERROR | 内容页缺 `layout_hint`；卡片数低于版式容量（single-focus 1、symmetric/asymmetric 2、其余 3） |
| ERROR | 卡片 >= 3 张时：所有卡片同一种 `card_type`，或没有数据卡片 |
| ERROR | `card_type` / `chart_type` / `card_style` / `role` / `density_label` 取值不合法；空卡片 |
| ERROR | 用了 `role` 但 anchor 卡片不是恰好 1 张；卡片数超过 `density_label` 的上限 |
| WARN | 内容页缺 `goal`；`layout_hint` 不是已知版式；首页不是 cover 或末页不是 end |
| WARN | 含数据的内容页不足 60%；连续 3 个内容页用同一版式 |

"数据卡片"指 `card_type` 为 data / data_highlight，或带 `chart_type`，或带 `data_points` 的卡片。

### style.json

| 级别 | 规则 |
|------|------|
| ERROR | 缺 `background` / `card` / `text` / `accent`；`accent.primary`、`accent.secondary` 不足 2 色；推不出 12 个标准 CSS 变量 |
| WARN | 缺 `typography` |

加 `--preset` 时按预置风格库的要求检查全部字段（维护风格库时用）。

### slides/*.html

| 级别 | 规则 |
|------|------|
| ERROR | 未声明 1280x720 画布；含 `<script>`、CSS 动画、`<canvas>` / `<video>` / `<iframe>` |
| WARN | 没用 CSS 变量或没用标准变量名；引用外部样式表或远程图片 |
| WARN | 用了转 PPTX 后会丢失的 CSS（text-shadow、渐变文字、backdrop-filter 等，见 `pipeline-compat.md` C 类） |
| WARN | 有小于 9px 的文字；页面含数字但没开 `tabular-nums` |
| WARN | 给了 `--planning`：HTML 里标出的卡片数少于策划稿；正文字号低于 `density_label` 的下限 |
| INFO | 会自动转成图层的写法（`pipeline-compat.md` B 类） |

### png/*.png

| 级别 | 规则 |
|------|------|
| ERROR | 文件小于 10KB；尺寸不是 16:9；画面几乎没有内容 |
| WARN | 宽度小于 960；内容页的内容量偏少 |

内容量按相邻像素的明暗跳变比例计算，与配色深浅无关；封面、章节封面、结束页允许稀疏。

---

## 3. 策划稿的可选字段

基础字段见 `prompts.md` Prompt #3。以下字段不写也合法，写了就按枚举校验，并影响资源路由和导出：

| 字段 | 位置 | 取值 | 作用 |
|------|------|------|------|
| `chart_type` | 卡片 | 18 种图表 id，见 `charts/index.md` | 路由到图表模板 |
| `card_id` | 卡片 | 建议 `s03-revenue` 这类短 id | 写进 HTML 的 `data-card-id`，用于卡片成组与动画顺序 |
| `role` | 卡片 | anchor / support / context | 标出本页唯一的视觉锚点 |
| `card_style` | 卡片 | accent / elevated / filled / outline / glass / transparent | 路由到 `blocks/card-styles.md` |
| `density_label` | 页面 | low / mid_low / medium / high / dashboard | 约束卡片数与正文字号 |

页面密度对应的约束：

| density_label | 卡片上限 | 正文字号下限 | 典型页面 |
|---------------|---------|-------------|---------|
| low | 2 | 24px | 金句、单一结论 |
| mid_low | 3 | 20px | 一个论点 + 两条支撑 |
| medium | 4 | 18px | 常规内容页 |
| high | 6 | 16px | 多维对比 |
| dashboard | 8 | 14px | 指标总览 |

现场演讲偏 low 到 medium，自阅文档可以到 high。避免连续 3 页 high / dashboard。

---

## 4. 图审清单

脚本只能拦硬伤，版面是否成立要看图。截图后（`html2png.py`）按下面的分级逐页过一遍，P0 和 P1 清零再交付。

**P0 必须修**

1. 内容超出画布被裁切
2. 靠整体缩放（`transform: scale`）硬塞内容
3. 大面积空白（内容页空白超过四成）
4. 核心文字不可读（对比度过低或字号小于 10px）
5. 策划稿里的关键卡片缺失
6. 元素严重重叠或错位
7. 渲染破损（样式未生效、布局塌陷）
8. 图片加载失败或被拉伸变形

**P1 应该修**

1. 文字被截断
2. 间距明显不均
3. 装饰遮挡文字
4. 没有视觉焦点，所有卡片同等权重
5. 颜色硬编码，与全局风格脱节
6. 数据数字不突出
7. 行高过紧（小于 1.4）
8. 与相邻页同构，看不出是独立设计的一页

**P2 可以修**

1. 圆角不一致
2. 没有体现风格的招牌手法（`decoration_dna.signature_move`）
3. 字体回落到系统默认
4. 层次扁平，卡片没有前后关系
5. 字号梯度过小（相邻层级差不足 4px）
6. 看起来像网页而不是幻灯片

修复顺序：内容 -> 结构 -> 颜色 -> 装饰。同一类问题连续两轮修不掉，说明是策划稿的问题（卡片太多、版式选错），回到 Step 4 改策划稿，不要继续在 HTML 上打补丁。

> 图审分级整理自 [sunbigfly/ppt-agent-skills](https://github.com/sunbigfly/ppt-agent-skills) 的 page-review playbook。
