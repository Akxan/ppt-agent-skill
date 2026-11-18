---
name: ppt-agent
description: 专业 PPT 演示文稿全流程 AI 生成助手。模拟顶级 PPT 设计公司的完整工作流（需求调研 -> 资料搜集 -> 大纲策划 -> 策划稿 -> 设计稿），输出高质量 HTML 格式演示文稿。当用户提到制作 PPT、做演示文稿、做 slides、做幻灯片、做汇报材料、做培训课件、做路演 deck、做产品介绍页面时触发此技能。即使用户只说"帮我做个关于 X 的介绍"或"我要给老板汇报 Y"，只要暗示需要结构化的多页演示内容，都应该触发。也适用于用户说"帮我把这篇文档做成 PPT"、"把这个主题做成演示"等需要将内容转化为演示格式的场景。
---

# PPT Agent -- 专业演示文稿全流程生成

## 核心理念

模仿专业 PPT 设计公司（报价万元/页级别）的完整工作流，而非"给个大纲套模板"：

1. **先调研后生成** -- 用真实数据填充内容，不凭空杜撰
2. **策划与设计分离** -- 先验证信息结构，再做视觉包装
3. **内容驱动版式** -- Bento Grid 卡片式布局，每页由内容决定版式
4. **全局风格一致** -- 先定风格再逐页生成，保证跨页统一
5. **智能配图** -- 利用图片生成能力为每页配插图（绝大多数环境都有此能力）

---

## 环境感知

开始工作前自省 agent 拥有的工具能力：

| 能力 | 降级策略 |
|------|---------|
| **信息获取**（搜索/URL/文档/知识库） | 全部缺失 -> 依赖用户提供材料 |
| **图片生成**（绝大多数环境都有） | 缺失 -> 纯 CSS 装饰替代 |
| **文件输出** | 必须有 |
| **脚本执行**（Python >= 3.10 / Node.js >= 18） | 缺失 -> 跳过 SVG 与 PPTX 导出，只交付 HTML |

**原则**：检查实际可调用的工具列表，有什么用什么。

---

## 路径约定

| 变量 | 含义 | 获取方式 |
|------|------|---------|
| `SKILL_DIR` | 本 SKILL.md 所在目录的绝对路径 | 即触发 Skill 时读取 SKILL.md 的目录 |
| `OUTPUT_DIR` | 产物输出根目录 | 用户当前工作目录下的 `ppt-output/`（首次使用时 `mkdir -p` 创建） |

后续所有路径均基于这两个变量。

---

## 输入模式与复杂度判断

### 入口判断

| 入口 | 示例 | 从哪步开始 |
|------|------|-----------|
| 纯主题 | "做一个 Dify 企业介绍 PPT" | Step 1 完整流程 |
| 主题 + 需求 | "15 页 AI 安全 PPT，暗黑风" | Step 1（跳部分已知问题）|
| 源材料 | "把这篇报告做成 PPT" | Step 1（材料为主）|
| 已有大纲 | "我有大纲了，生成设计稿" | Step 4 或 5 |

### 跳步规则

跳过前置步骤时，必须补全对应依赖产物：

| 起始步骤 | 缺失依赖 | 补全方式 |
|---------|---------|---------|
| Step 4 | 每页内容文本 | 先用 Prompt #3 为每页生成内容分配 |
| Step 5 | 策划稿 JSON | 用户提供或先执行 Step 4 |

### 复杂度自适应

| 规模 | 页数 | 调研 | 搜索 | 策划 | 生成 |
|------|------|------|------|------|------|
| **轻量** | <= 8 页 | 3 题精简版（场景+受众+补充信息） | 3-5 个查询 | Step 3 可与 Step 4 合并一步完成 | 逐页生成 |
| **标准** | 9-18 页 | 完整 7 题 | 8-12 个查询 | 完整流程 | 按 Part 分批，每批 3-5 页 |
| **大型** | > 18 页 | 完整 7 题 | 10-15 个查询 | 完整流程 | 按 Part 分批，每批 3-5 页，批间确认 |

---

## 6 步 Pipeline

### Step 1: 需求调研 [STOP -- 必须等用户回复]

> **禁止跳过。** 无论主题多简单，都必须提问并等用户回复后才能继续。不替用户做决定。

**执行**：使用 `references/prompts.md` Prompt #1
1. 搜索主题背景资料（3-5 条）
2. 根据复杂度选择完整 7 题或精简 3 题，一次性发给用户。环境提供结构化提问工具（如 `AskUserQuestion`）时优先使用，否则用分组清晰的文本问卷
3. **等待用户回复**（阻断点）
4. 整理为需求 JSON

**7 题三层递进结构**（轻量模式只问第 1、2、7 题）：

| 层级 | 问题 | 决定什么 |
|------|------|---------|
| 场景层 | 1. 演示场景（现场/自阅/培训） | 信息密度和视觉风格 |
| 场景层 | 2. 核心受众（动态生成画像） | 专业深度和说服策略 |
| 场景层 | 3. 期望行动（决策/理解/执行/改变认知） | 内容编排的最终导向 |
| 内容层 | 4. 叙事结构（问题->方案/科普/对比/时间线） | 大纲骨架逻辑 |
| 内容层 | 5. 内容侧重（搜索结果动态生成，可多选） | 各 Part 主题权重 |
| 内容层 | 6. 说服力要素（数据/案例/权威/方法，可多选） | 卡片内容类型偏好 |
| 执行层 | 7. 补充信息（演讲人/品牌色/必含/必避/页数/配图偏好/**动画偏好**） | 具体执行细节 |

**动画偏好**（第 7 题里问，默认 A）：

| 选项 | 含义 | Step 6 的参数 |
|------|------|--------------|
| A. 只要页间切换 | 翻页淡入，页内静态 | 默认，不加参数 |
| B. 卡片逐张出现 | 每点一下出现一张卡片，适合现场讲解 | `--animate fade` |
| C. 卡片自动依次出现 | 进入页面后自动播放，适合自动放映 | `--animate rise --animate-trigger auto` |
| D. 不要任何动画 | 翻页也不要过渡 | `--transition none` |

**产物**：需求 JSON（topic + requirements）-> `OUTPUT_DIR/requirements.json`

---

### Step 2: 资料搜集

> 盘点所有信息获取能力，全部用上。

**执行**：
1. 根据主题规划查询（数量参考复杂度表）
2. 用所有可用的信息获取工具并行搜索
3. 每组结果摘要总结

**产物**：搜索结果集合 JSON

---

### Step 3: 大纲策划

**执行**：使用 `references/prompts.md` Prompt #2（大纲架构师 v2.0）

**方法论**：金字塔原理 -- 结论先行、以上统下、归类分组、逻辑递进

**自检**：页数符合要求 / 每 part >= 2 页 / 要点有数据支撑

**产物**：`[PPT_OUTLINE]` JSON -> `OUTPUT_DIR/outline.json`

---

### Step 4: 内容分配 + 策划稿 [建议等用户确认]

> 将内容分配和策划稿生成合为一步。在思考每页应该放什么内容的同时，决定布局和卡片类型，更自然高效。

**执行**：使用 `references/prompts.md` Prompt #3（内容分配与策划稿）

**要点**：
- 将搜索素材精准映射到每页
- 为每页设计多层次内容结构（主卡片 40-100 字 + 数据亮点 + 辅助要点）
- 同时确定 page_type / layout_hint / cards[] 结构
- **内容页卡片数不少于版式容量**：单一焦点 >= 1、对称/非对称两栏 >= 2、其余版式 >= 3；卡片 >= 3 张时至少 2 种 card_type 且至少 1 张数据卡片
- 布局选择参考 `references/bento-grid.md` 的决策矩阵；需要图表时在卡片上写 `chart_type`
- 可用的版式、组件、图表、风格清单：`python3 SKILL_DIR/scripts/resource_loader.py menu`

向用户展示策划稿概览，建议等用户确认后再进入 Step 5。

**产物**：每页策划卡 JSON 数组 -> `OUTPUT_DIR/planning.json`

---

### Step 5: 风格决策 + 设计稿生成

分三个子步骤，**顺序不可颠倒**：

#### 5a. 风格决策

**执行**：阅读 `references/styles/index.md`（含决策矩阵），按主题关键词匹配 26 种预置风格之一；都不合适时按同一 JSON 结构自定义（方法见 index.md "自定义风格"）

**26 风格按 5 板块分组**（完整 JSON 在板块文件中）：

| 板块 | 数量 | 风格 ID | 板块文件 |
|------|------|--------|---------|
| 暗色专业 | 7 | dark_tech / xiaomi_orange / luxury_purple / nocturne_violet / cyberpunk_neon / chrome_y2k / noir_film | `references/styles/dark.md` |
| 浅色高级 | 8 | blue_white / fresh_green / minimal_gray / mocha_editorial / medical_pulse / earth_concrete / champagne_gold / liquid_glass | `references/styles/light.md` |
| 活力鲜明 | 4 | vibrant_rainbow / kindergarten_pop / bauhaus_block / candy_pastel | `references/styles/vibrant.md` |
| 东方文化 | 3 | royal_red / sakura_wabi / ink_jade | `references/styles/cultural.md` |
| 自然/复古 | 4 | botanic_forest / safari_savanna / retro_70s / gov_authority | `references/styles/natural.md` |

**风格预览**：`SKILL_DIR/ppt-output/style-gallery/index.html` 是 26 风格的卡片墙，用户拿不定主意时让其打开对比。

**也必读**：`references/typography.md`（字距分级 / tabular-nums / OpenType / serif italic 混排 / 字体栈三层降级）

**产物**：选定风格的完整 JSON -> `OUTPUT_DIR/style.json`

#### 5b. 智能配图（根据用户偏好）

> 在需求调研（Step 1 第 7 题）中确认用户的配图偏好后执行。如果用户选择"不需要配图"则跳过。

在生成每页 HTML **之前**，先为该页生成配图，保存到 `OUTPUT_DIR/images/`。封面页、章节封面必须有。

**提示词构造公式**：`[内容主题] + [视觉风格] + [画面构图] + [技术约束]`

| 维度 | 说明 | 示例 |
|------|------|------|
| 内容主题 | 从该页策划稿的核心概念提炼，具体到场景/对象 | "DMSO molecular purification process, crystallization flask with clear liquid" |
| 视觉风格 | 与 style.json 的 `mood_keywords` 和配色对齐 | 暗黑科技 -> "deep blue dark tech background, subtle cyan glow, futuristic" |
| 画面构图 | 根据图片在页面中的放置方式决定 | 右侧渐隐 -> "clean composition, main subject on left, fade to transparent on right" |
| 技术约束 | 固定后缀 | "no text, no watermark, high quality, professional illustration" |

**按页面类型追加关键词**：

| 页面类型 | 图片特征 | 追加关键词 |
|---------|---------|-----------|
| 封面页 | 主题概览，视觉冲击 | "hero image, wide composition, dramatic lighting" |
| 章节封面 | 该章主题的象征性视觉 | "symbolic, conceptual, centered composition" |
| 内容页 | 辅助说明，不喧宾夺主 | "supporting illustration, subtle, background-suitable" |
| 数据页 | 抽象数据可视化氛围 | "abstract data visualization, flowing lines, tech" |

**禁止**：图片中出现文字 / 与页面配色冲突（暗色主题配暗色图，亮色主题配亮色图）/ 与内容无关的装饰图 / 多页重复使用同一 prompt。

**产物**：`OUTPUT_DIR/images/` 下的配图文件

#### 5c. 逐页 HTML 设计稿生成

**执行**：使用 `references/prompts.md` Prompt #4 + `references/bento-grid.md`

> **禁止跳过策划稿直接生成。** 每页必须先有 Step 4 的结构 JSON。

**每页 Prompt 组装公式**：
```
Prompt #4 模板
+ 风格定义 JSON（5a 产物）[必须]
+ 该页策划稿 JSON（Step 4 产物）[必须]
+ 该页用到的版式/组件/图表说明 [按需，见下方"资源路由"]
+ 配图路径（5b 产物）[可选 -- 无配图时省略 IMAGE_INFO 块]
```

**核心设计约束**（完整清单见 Prompt #4 与 `references/pipeline-compat.md`）：
- 画布 1280x720px，`overflow:hidden`，静态 HTML（不写 `<script>`、不写 CSS 动画）
- 颜色通过标准 CSS 变量引用（`--bg-primary` / `--text-primary` / `--accent-1` ...），图表模板依赖这些变量名
- 每张卡片的根节点写 `class="card"` 和 `data-card-id`，导出时据此成组、做入场动画
- 文字不要用渐变填充、text-shadow 承载关键信息（转 PPTX 后退化）；径向渐变、模糊光晕、遮罩等装饰可以放心用，导出时自动转成图层

**分批策略**：按 Part 为单位分批生成，每批 3-5 页，写入 `OUTPUT_DIR/slides/`（文件名用零填充或 `slide-N.html` 均可，导出按自然顺序排序）。

**跨页视觉叙事**：

| 策略 | 规则 | 原因 |
|------|------|------|
| **密度交替** | 高密度页（混合网格/英雄式）后面跟低密度页（章节封面/单一焦点） | 连续 3+ 页高密度内容会导致视觉疲劳 |
| **章节色彩递进** | Part 1 卡片主用 accent-1，Part 2 用 accent-2，依次轮换 | 通过颜色让受众无意识感知章节切换 |
| **封面-结尾呼应** | 结束页的视觉元素与封面页形成呼应 | 首尾呼应给出完整闭环感 |
| **渐进揭示** | 同一概念跨多页展开时，视觉复杂度递增 | 引导观众逐步深入理解 |

**产物**：每页一个 HTML 文件 -> `OUTPUT_DIR/slides/`

---

### Step 6: 后处理 [必做 -- HTML 生成完后立即执行]

> **禁止跳过。** 不要停在 HTML 就结束。

```
slides/*.html --> preview.html --> svg/*.svg --> presentation.pptx
```

**依赖**（首次运行）：
```bash
pip install python-pptx lxml Pillow
# Node.js >= 18；puppeteer 与 dom-to-svg 在首次运行 html2svg.py 时自动装到 SKILL_DIR/node_modules
```

**依次执行**：

1. **合并预览**（做了卡片动画时加上与步骤 3 相同的 `--animate` / `--animate-trigger`，浏览器里就能预览动效，用户没有 PowerPoint 也能看）
   ```bash
   python3 SKILL_DIR/scripts/html_packager.py OUTPUT_DIR/slides/ -o OUTPUT_DIR/preview.html
   ```

2. **SVG 转换**（文字保留为可编辑 `<text>`；dom-to-svg 画不出的效果自动截成图层）
   ```bash
   python3 SKILL_DIR/scripts/html2svg.py OUTPUT_DIR/slides/ -o OUTPUT_DIR/svg/
   ```

3. **PPTX 生成**（原生形状 + 可编辑文字；按 Step 1 的动画偏好加参数）
   ```bash
   python3 SKILL_DIR/scripts/svg2pptx.py OUTPUT_DIR/svg/ -o OUTPUT_DIR/presentation.pptx
   #   默认：页间淡入切换，页内静态
   #   卡片逐张出现：   --animate fade
   #   卡片自动依次出现：--animate rise --animate-trigger auto
   #   不要任何动画：   --transition none
   #   换切换效果：     --transition push|wipe|cover|split|zoom|dissolve
   ```

4. **（可选）像素级保真版**：用户更看重"和预览一模一样"而不需要编辑时追加
   ```bash
   python3 SKILL_DIR/scripts/html2png.py OUTPUT_DIR/slides/ -o OUTPUT_DIR/png/
   python3 SKILL_DIR/scripts/png2pptx.py OUTPUT_DIR/png/ -o OUTPUT_DIR/presentation-hd.pptx
   ```

5. **通知用户** -- 告知产物位置和使用方式：
   - `preview.html` -- 浏览器打开，方向键翻页；带动画预览时点击画面或按 → 逐张出现卡片
   - `presentation.pptx` -- 文字与形状可直接编辑；卡片是组合，可整体移动
   - 字体：PPTX 默认映射到 Office 自带字体（Arial / Georgia / 微软雅黑等）。机器上装了设计字体时可加 `--fonts design` 重新导出
   - 做了动画时说明触发方式（点击 / 自动）

**降级**：Node.js 不可用或依赖安装失败时，步骤 2-4 无法执行，只交付 `preview.html`，并告知用户装好 Node.js 后可重新运行。

**产物**：preview.html + svg/*.svg + presentation.pptx

---

## 输出目录结构

```
ppt-output/
  requirements.json       # 需求
  outline.json            # 大纲
  planning.json           # 策划稿
  style.json              # 风格定义
  images/                 # AI 配图
  slides/                 # 每页 HTML
  preview.html            # 可翻页预览
  svg/                    # 矢量 SVG
  presentation.pptx       # 可编辑 PPTX（含切换/动画）
  png/                    # 截图（可选）
  presentation-hd.pptx    # 像素级保真版（可选）
```

---

## 质量自检

| 维度 | 检查项 |
|------|-------|
| 内容 | 每页 >= 2 信息卡片 / >= 60% 内容页含数据 / 章节有递进 |
| 视觉 | 全局风格一致 / 配图风格统一 / 卡片不重叠 / 文字不溢出 |
| 技术 | 使用标准 CSS 变量 / 卡片带 `data-card-id` / 无 `<script>` 与 CSS 动画 / PPTX 能正常打开 |

按 `references/principles/failure-modes.md` 的修复顺序处理问题：先补内容，再调版式，最后才动装饰。

---

## 严格模式（可选）

需要更高的交付确定性时（大型 deck、交给他人二次编辑、批量生成），在对应步骤后运行校验脚本，把自检变成硬门槛。不运行也不影响出稿。

| 时机 | 命令 | 拦什么 |
|------|------|-------|
| Step 3 后 | `python3 SKILL_DIR/scripts/validate.py outline OUTPUT_DIR/outline.json --pages 10-15` | part 少于 2 页、缺标题、页数不符 |
| Step 4 后 | `python3 SKILL_DIR/scripts/validate.py planning OUTPUT_DIR/planning.json` | 卡片不足、类型单一、无数据卡片、枚举值写错、版式连续重复 |
| Step 5a 后 | `python3 SKILL_DIR/scripts/validate.py style OUTPUT_DIR/style.json` | 生成不出 CSS 变量的残缺风格 |
| Step 5c 后 | `python3 SKILL_DIR/scripts/validate.py slides OUTPUT_DIR/slides --planning OUTPUT_DIR/planning.json` | 画布尺寸、`<script>`/动画、卡片缺失、会退化的 CSS |
| Step 6 后 | `python3 SKILL_DIR/scripts/validate.py all OUTPUT_DIR` | 以上全部 + 截图空白页 + 产物数量 |

退出码 0 通过、1 有 ERROR；加 `--strict` 时 WARN 也算失败。规则与可选字段（`role` / `card_style` / `density_label`）见 `references/strict-mode.md`。

---

## 资源路由

策划稿字段决定 Step 5c 该读哪些参考文件。手动查表，或让脚本一次取齐：

```bash
python3 SKILL_DIR/scripts/resource_loader.py resolve --planning OUTPUT_DIR/planning.json --page 3
```

- 字段路由：`layout_hint→layouts/`、`page_type→page-templates/`、`card_type→blocks/`、`chart_type→charts/`

| 字段 | 取值 | 路由到 |
|------|------|-------|
| `layout_hint` | single-focus / symmetric / asymmetric / three-column / primary-secondary / hero-top / mixed-grid / l-shape / t-shape / waterfall（也接受"主次结合"等中文叫法） | `references/layouts/<版式>.md` |
| `page_type` | cover / toc / section / end（content 页没有模板） | `references/page-templates/<类型>.md` |
| `card_type` | text / data / list / tag_cloud / process / data_highlight | `references/bento-grid.md` "6 种卡片内容类型" |
| `card_type` | timeline / diagram / quote / comparison / people / image_hero / matrix_chart | `references/blocks/<组件>.md`（下划线换成连字符） |
| `chart_type` | progress_bar / comparison_bar / ring / sparkline / waffle / kpi / metric_row / rating | `references/charts/basic.md` 对应小节 |
| `chart_type` | radar / timeline / funnel / gauge / grouped_bar / simple_map | `references/charts/advanced.md` 对应小节 |
| `chart_type` | world_choropleth / network_graph / sankey_flow / heatmap_calendar | `references/charts/complex.md` 对应小节 |
| `card_style`（可选） | accent / elevated / filled / outline / glass / transparent | `references/blocks/card-styles.md` |

---

## Reference 文件索引

| 文件 | 何时阅读 | 关键内容 |
|------|---------|---------|
| `references/prompts.md` | 每步生成前 | 5 套 Prompt 模板（调研/大纲/策划/设计/备注）|
| `references/method.md` | 初次了解 | 核心理念与方法论 |
| `references/bento-grid.md` | Step 4 / 5c | 7 种布局精确坐标 + 6 种卡片类型 + 决策矩阵 |
| `references/styles/index.md` | **Step 5a** | 26 种预置风格索引 + 决策矩阵 + JSON 结构 + 自定义风格 |
| `references/styles/{dark,light,vibrant,cultural,natural}.md` | Step 5a 选定风格后 | 该板块所有风格的完整 JSON |
| `references/typography.md` | **Step 5c** | 排版铁律 14 条 |
| `references/charts/index.md` | Step 4 / 5c 涉及数据可视化时 | 18 种图表索引 + 决策矩阵 |
| `references/charts/{basic,advanced,complex}.md` | 选定图表后 | 完整 HTML 模板（基础 8 / 进阶 6 / 复杂 4）|
| `references/layouts/*.md` | Step 5c，按 layout_hint | 10 种版式的重力结构与禁忌 |
| `references/blocks/*.md` | Step 5c，按 card_type / card_style | 7 种组件原型 + card-styles |
| `references/page-templates/*.md` | Step 5c，按 page_type | cover / toc / section / end |
| `references/principles/*.md` | Step 4-5 自检 | 6 条设计原则 + failure-modes（8 种失败模式与修复顺序）|
| `references/design-runtime/*.md` | Step 5c 进阶 | design-specs（画布与排版规格）/ css-weapons（12 种 CSS 技法）/ data-type-visual-mapping（数据类型 -> 卡片/版式/图表）|
| `references/pipeline-compat.md` | **Step 5c** | 哪些 CSS 保持矢量、哪些转图层、哪些会丢 |
| `references/strict-mode.md` | 启用严格模式时 | 校验规则、可选字段、图审缺陷分级 |

## 维护

合同的单一真源是 `scripts/contracts.py`（页面类型、版式、卡片类型、图表注册表、风格字段、兼容规则）。新增风格、图表或改枚举后运行：

```bash
python3 scripts/smoke_test.py            # 风格 / mock / 图表 / 校验器 / 资源路由 / 文档引用
python3 scripts/smoke_test.py --export   # 追加真实导出管线（约 1 分钟，需 Node.js）
```
