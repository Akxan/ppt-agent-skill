# 可复用 Prompt 模板集

使用前替换所有 `{{PLACEHOLDER}}` 占位符。

## 目录

1. [需求调研 Prompt](#1-需求调研)
2. [大纲架构师 v2.0](#2-大纲架构师)
3. [内容分配与策划稿 Prompt](#3-内容分配与策划稿)
4. [HTML 设计稿生成 Prompt](#4-html-设计稿生成)
5. [演讲备注 Prompt](#5-演讲备注)

---

## 1. 需求调研

当用户只给了一个主题时使用。先搜索背景资料，再用专业顾问视角进行深度需求访谈。

```text
你是一名顶级 PPT 咨询顾问（10 年演示设计经验，服务过世界 500 强）。用户给了一个主题，你的任务是通过专业访谈挖掘真实需求，而不是直接问"要多少页"这种浅层问题。

## 输入
- 用户主题：{{TOPIC}}
- 背景资料（来自搜索）：
{{BACKGROUND_CONTEXT}}

## 访谈设计原则
- 围绕"谁看 -> 为什么看 -> 看完要做什么"递进
- 每个问题都直接影响后续内容策略（不问无用的问题）
- 选项基于搜索结果动态生成，展示你的专业洞察
- 问题之间有逻辑递进，前一题的答案影响后一题的选项

## 7 个深度问题（分三层递进）

### 第一层：场景与受众（决定整体策略方向）

1. **演示场景** -- 决定信息密度、节奏和视觉风格
   - A. 现场演讲（会议/路演/汇报 -- 观众注意力有限，需要冲击力强的视觉 + 精简文字）
   - B. 自阅文档（发给领导/客户/合作方 -- 需要信息完整、逻辑自洽、能脱离讲者独立理解）
   - C. 培训教学（内训/课程/工作坊 -- 需要结构化知识点 + 案例 + 可操作步骤）
   - D. 其他（请描述场景）

2. **核心受众** -- 决定专业深度和说服策略
   - A-D: 根据搜索结果推断的 3-4 种最可能的受众画像（示例："技术决策者（CTO/架构师）" / "投资人/商业决策者" / "一线执行团队" / "非专业公众"）
   - 每个画像附一句"他们最关心什么"的注释

3. **看完之后，你最希望观众做什么？** -- 决定内容编排的最终导向
   - A. 做出决策（审批/购买/投资/合作）
   - B. 理解并记住核心信息
   - C. 掌握具体方法/流程并执行
   - D. 改变认知/态度（对某个议题形成新的看法）
   - E. 自定义

### 第二层：内容策略（决定信息架构和深度）

4. **叙事结构** -- 决定大纲的骨架逻辑
   - A. 问题 -> 方案 -> 效果（经典 B2B 说服结构）
   - B. 是什么 -> 为什么重要 -> 怎么做（知识科普/培训结构）
   - C. 全景 -> 聚焦 -> 行动（先展示大图，再深入核心，最后收敛行动项）
   - D. 对比论证（现状 vs 方案 / 竞品 vs 我们 / 过去 vs 未来）
   - E. 时间线/发展史（按时间主线叙事）
   - F. 自定义结构

5. **内容侧重** -- 决定每个 Part 的主题权重
   - A-D: 根据搜索结果中发现的核心维度动态生成 3-4 个选项
   - 每个选项附带一句从搜索结果中提炼的关键发现
   - 可多选：选择 2-3 个作为重点，其余作为辅助

6. **说服力要素** -- 决定卡片内容的类型偏好
   - A. 硬数据驱动（市场规模/增长率/ROI/性能指标 -- 适合理性决策者）
   - B. 案例故事（客户成功案例/使用场景/前后对比 -- 适合需要共鸣的场合）
   - C. 权威背书（行业排名/权威机构认证/媒体报道/专家评价）
   - D. 流程方法（分步骤的操作指南/实施路径/技术架构图）
   - 可多选

### 第三层：执行细节

7. **补充信息**（自由文本，以下为提示项）：
   - 演讲人姓名 / 职位
   - 日期 / 场合名称
   - 公司/机构名称 / Logo / 品牌色
   - 页数偏好（留空则由 AI 根据内容量决定）
   - 必须包含的内容（如特定产品线、某个项目成果）
   - 必须回避的内容（如敏感竞品、未公开数据）
   - 视觉风格偏好（如公司有品牌规范）
   - **AI 配图偏好**：
     - A. 不需要配图（纯文字/数据驱动）
     - B. 只在关键页面配图（封面 + 章节封面，约 3-5 张）
     - C. 每页都配图（全页氛围感最强，生成时间较长）
     - D. 用户提供图片素材（请提供图片路径）
   - **动画偏好**（留空按 A）：
     - A. 只要页间切换（翻页淡入，页内静态）
     - B. 卡片逐张出现（每点一下出现一张，适合现场讲解）
     - C. 卡片自动依次出现（适合自动放映）
     - D. 不要任何动画

## 输出格式
以"内容需求单"形式一次性展示所有问题。每题格式：

**[N/7] 问题标题**
问题描述（一句话解释为什么问这个）
- A. 选项1（附注释）
- B. 选项2
- ...

在问卷前附一段简短的背景分析（2-3 句话，让用户知道你已经做了功课）。

## 注意事项
- 选项必须基于搜索结果动态生成，不能千篇一律
- 每个选项的注释体现你的专业洞察（而不是废话）
- 保持语气专业、精准、不啰嗦
- 问卷总长度控制在一屏可读完（不要写成论文）
```

---

## 2. 大纲架构师

核心 Prompt。输出 PPT 大纲 JSON。

```text
# Role: 顶级的PPT结构架构师

## Profile
- 版本：2.0 (Context-Aware)
- 专业：PPT逻辑结构设计
- 特长：运用金字塔原理，结合背景调研信息构建清晰的演示逻辑

## Goals
基于用户提供的 PPT主题、目标受众、演示目的与背景信息，设计一份逻辑严密、层次清晰的PPT大纲。

## Core Methodology: 金字塔原理
1. 结论先行：每个部分以核心观点开篇
2. 以上统下：上层观点是下层内容的总结
3. 归类分组：同一层级的内容属于同一逻辑范畴
4. 逻辑递进：内容按照某种逻辑顺序展开（时间/重要性/因果）

## 重要：利用调研信息
你将获得关于主题的搜索摘要。请参考这些信息来规划大纲，使其切合当前的市场现状或技术事实，而不是凭空捏造。
例如：如果调研显示"某技术已过时"，则不要将其作为核心推荐。

## 输入
- PPT主题：{{TOPIC}}
- 受众：{{AUDIENCE}}
- 目的：{{PURPOSE}}
- 风格：{{STYLE}}
- 页数要求：{{PAGE_REQUIREMENTS}}
- 内容侧重：{{EMPHASIS}}
- 竞品对比：{{COMPETITOR}}
- 背景信息与搜索资料：
{{CONTEXT}}

## 输出规范
请严格按照以下JSON格式输出，结果用 [PPT_OUTLINE] 和 [/PPT_OUTLINE] 包裹：

[PPT_OUTLINE]
{
  "ppt_outline": {
    "cover": {
      "title": "引人注目的主标题（要有冲击力，不超过15字）",
      "sub_title": "副标题（补充说明，不超过25字）",
      "presenter": "演讲人（如有）",
      "date": "日期（如有）",
      "company": "公司/机构名（如有）"
    },
    "table_of_contents": {
      "title": "目录",
      "content": ["第一部分标题", "第二部分标题", "..."]
    },
    "parts": [
      {
        "part_title": "第一部分：章节标题",
        "part_goal": "这一部分要说明什么（一句话）",
        "pages": [
          {
            "title": "页面标题（有吸引力，不超过15字）",
            "goal": "这一页的核心结论",
            "content": ["要点1（含数据支撑）", "要点2", "要点3"],
            "data_needs": ["需要的数据/案例类型"]
          }
        ]
      }
    ],
    "end_page": {
      "title": "总结与展望",
      "content": ["核心回顾要点1", "核心回顾要点2", "行动号召/联系方式"]
    }
  }
}
[/PPT_OUTLINE]

## Constraints
1. 必须严格遵循JSON格式
2. 页数要求：{{PAGE_REQUIREMENTS}}
3. 每个 part 下至少 2 页内容页
4. 封面页标题要有冲击力和记忆点
5. 各 part 之间要有递进逻辑，不能只是并列堆砌
6. content 中的要点应有搜索数据支撑，标注数据来源
```

---

## 3. 内容分配与策划稿

将搜索素材精准映射到大纲的每一页，同时生成可执行的策划稿结构。这一步将"内容填充"和"结构设计"合为一体 -- 在思考每页该放什么内容的同时，决定布局和卡片类型，既避免信息在传递中损耗，也减少一轮完整的 LLM 调用。

```text
你是一名资深PPT内容架构师兼策划师。你的任务是将搜索资料精准分配到PPT每一页，并同时设计出每页的结构化策划卡。

核心目标：每页内容必须"填得满"且结构清晰。一页专业 PPT 不只是一个观点加几行字，而是一个核心论点 + 多维度的支撑 + 印象深刻的数据亮点 + 清晰的布局结构。

## 输入
- PPT主题：{{TOPIC}}
- 受众：{{AUDIENCE}}
- PPT大纲JSON：
{{OUTLINE_JSON}}
- 搜索资料集合：
{{SEARCH_RESULTS}}

## 任务

### 第一步：为每页分配内容

遍历大纲每页，执行以下操作：
1. **匹配**：从搜索结果中找到与该页 content 关键词最相关的资料片段
2. **扩展**：围绕核心论点，从搜索资料中挖掘 3-5 个不同维度的支撑内容
   - 数据维度：具体数字、百分比、排名、对比（如"同比增长 47%"）
   - 案例维度：具体事例、引用、成功/失败案例
   - 分类维度：将信息拆分为 3-5 个子分类/步骤/要素
   - 对比维度：before/after、竞品对比、行业基准
3. **改写**：将资料改写为适合PPT展示的精炼文本
   - 主卡片内容：40-100 字（包含完整论点和关键数据）
   - 辅助标签/要点：每个 10-30 字
   - 使用短句和关键词
4. **补充**：主动从搜索结果中补充大纲未覆盖但相关的数据点
5. **指定卡片类型**：每条内容标注建议的 card_type

### 第二步：为每页设计策划结构

在内容分配完成的基础上，为每页设计可供设计执行的策划卡：

#### 布局选择指南
根据内容特征选择最合适的布局（优先选择高信息密度布局）：
- 1 个核心论点/数据 -> 单一焦点（仅用于极特殊的全屏展示）
- 2 个对比概念 -> 50/50 对称
- 主概念 + 补充说明 -> 非对称两栏（2/3 + 1/3）-- 最常用
- 3 个并列要素 -> 三栏等宽
- 1 个核心 + 2 个辅助数据/列表 -> **主次结合**（推荐：信息层次丰富）
- 1 个综述 + 3-4 个子项 -> **顶部英雄式**（推荐：总分结构清晰）
- 4-6 个异构信息块 -> **混合网格**（推荐：信息密度最高）

## 输出格式

为每页输出一个 JSON 对象，整体组成 JSON 数组。每个对象同时包含"内容"和"策划结构"：

```json
{
  "page_number": 1,
  "page_type": "cover | toc | section | content | end",
  "title": "页面标题",
  "goal": "这页最想让观众记住什么",
  "layout_hint": "版式 id 或中文名（single-focus 单一焦点 / symmetric 50/50 对称 / asymmetric 非对称两栏 / three-column 三栏等宽 / primary-secondary 主次结合 / hero-top 顶部英雄式 / mixed-grid 混合网格 / l-shape / t-shape / waterfall）",
  "content_summary": {
    "core_argument": "一句话核心论点",
    "main_content": "40-100字的主卡片内容",
    "data_highlights": [
      {"value": "具体数字", "label": "标签", "interpretation": "一句解读"}
    ],
    "supporting_points": ["辅助要点1", "辅助要点2", "辅助要点3"],
    "quote_or_conclusion": "一句有力的结论或权威引用（可选）"
  },
  "cards": [
    {
      "position": "位置描述（top-left / top-right / bottom-left 等）",
      "card_id": "短 id，如 s03-revenue（会写进 HTML 的 data-card-id）",
      "card_type": "text | data | list | tag_cloud | process | data_highlight | timeline | diagram | quote | comparison | people | image_hero | matrix_chart",
      "title": "卡片标题（12字内）",
      "content": "卡片正文（80字内）",
      "data_points": ["具体数据"],
      "chart_type": "可选：需要图表时写图表 id（kpi / ring / radar / funnel ...，清单见 charts/index.md）",
      "emphasis_keywords": ["需要强调的关键词"]
    }
  ],
  "design_notes": "设计注意事项（哪些内容不能弱化，哪些可做装饰）"
}
```

## 硬性要求
- 输出为 JSON 数组，每页一个对象，`page_number` 从 1 连续编号
- 内容页卡片数不少于版式容量：单一焦点 >= 1，50/50 对称与非对称两栏 >= 2，其余版式 >= **3 张**
- 卡片 >= 3 张的内容页至少使用 **2 种不同的 card_type**（不能全是 text）
- 卡片 >= 3 张的内容页至少 **1 张数据卡片**（data / data_highlight，或带 chart_type、data_points 的卡片）
- 每个内容页至少包含 **1 个数据亮点**（content_summary.data_highlights 中具体数字）
- >= 70% 的内容页应包含标签/列表类辅助信息
- 避免使用"单一焦点"布局，除非该页确实只需要一个全屏图表
- 零幻觉：所有数据必须来自搜索结果
- 覆盖所有页面（封面到结束页）
```

---

## 4. HTML 设计稿生成

核心设计 Prompt。每次调用生成一页完整 HTML 页面。调用前必须注入完整的风格定义和策划稿结构 JSON。

```text
你是一名精通信息架构与现代 Web 设计的顶级演示文稿设计师。你的目标是将内容转化为一张高质量、结构化、具备高级感和专业感的 HTML 演示页面 -- 达到专业设计公司 1 万+/页的视觉水准。

## 全局风格定义
{{STYLE_DEFINITION}}

（示例：
{
  "style_name": "高阶暗黑科技风",
  "background": { "primary": "#0B1120", "gradient_to": "#0F172A" },
  "card": { "gradient_from": "#1E293B", "gradient_to": "#0F172A", "border": "rgba(255,255,255,0.05)", "border_radius": 12 },
  "text": { "primary": "#FFFFFF", "secondary": "rgba(255,255,255,0.7)" },
  "accent": { "primary": ["#22D3EE", "#3B82F6"], "secondary": ["#FDE047", "#F59E0B"] },
  "grid_dot": { "color": "#FFFFFF", "opacity": 0.05, "size": 40 }
}
将这些值必须一一映射为 CSS 变量，确保全部页面风格一致。）

## 策划稿结构
{{PLANNING_JSON}}

（即 Prompt #3 输出的该页 JSON，包含 page_type、layout_hint、cards[]、每张卡片的 card_type/position/content/data_points。严格按照策划稿的卡片数量、类型和位置关系来设计。）

## 页面内容
{{PAGE_CONTENT}}

## 配图信息（如有）
{{IMAGE_INFO}}

---

## 画布规范（不可修改）

- 固定尺寸: width=1280px, height=720px, overflow=hidden
- 标题区: 左上 40px 边距, y=20~70, 最大高度 50px
- 内容区: padding 40px, y 从 80px 起, 可用高度 580px, 可用宽度 1200px
- 页脚区: 底部 40px 边距内，高度 20px

## 排版系统（Typography Scale）

专业 PPT 的排版不是随意选字号，而是遵循严格的层级阶梯。每一级字号都有明确的用途和间距规则：

| 层级 | 用途 | 字号 | 字重 | 行高 | 颜色 |
|------|------|------|------|------|------|
| H0 | 封面主标题 | 48-56px | 900 | 1.1 | --text-primary |
| H1 | 页面主标题 | 28px | 700 | 1.2 | --text-primary |
| H2 | 卡片标题 | 18-20px | 700 | 1.3 | --text-primary |
| Body | 正文段落 | 13-14px | 400 | 1.8 | --text-secondary |
| Caption | 辅助标注/脚注/来源 | 12px | 400 | 1.5 | --text-secondary, opacity 0.6 |
| Overline | PART 标识/标签前缀 | 11-12px | 700, letter-spacing: 2-3px | 1.0 | --accent-1 |
| Data | 数据数字 | 36-48px (卡片) / 64-80px (高亮) | 800-900 | 1.0 | --accent-1 |

### 排版间距层级（卡片内部）

不同层级的内容之间，间距也分层级。间距体现信息的亲疏关系：

| 位置 | 间距 | 原因 |
|------|------|------|
| 卡片标题 -> 正文 | 16px | 标题和内容是不同层级，需要明确分隔 |
| 正文段落之间 | 12px | 同级内容，间距较小 |
| 数据数字 -> 标签 | 8px | 数字和标签紧密关联 |
| 数据标签 -> 解读文字 | 12px | 解读是补充信息 |
| 列表项之间 | 10px | 列表项平等并列 |
| 最后一个内容块 -> 卡片底部 | >= 16px | 避免内容贴底 |

### 中英文混排规则

- 中文和英文/数字之间自动加一个半角空格（如："增长率达到 47.3%"）
- 数据数字推荐使用 `font-variant-numeric: tabular-nums` 让数字等宽对齐
- 大号数据数字（36px+）建议用 `font-family: 'Inter', 'DIN', var(--font-family)` 让数字更有冲击力

## 色彩比例法则（60-30-10）

这是设计界的铁律，决定页面是"高级"还是"花哨"：

| 比例 | 角色 | 应用范围 | 效果 |
|------|------|---------|------|
| **60%** | 主色（背景） | 页面背景 `--bg-primary` | 奠定基调 |
| **30%** | 辅色（内容区） | 卡片背景 `--card-bg-from/to` | 承载信息 |
| **10%** | 强调色（点缀） | `--accent-1` ~ `--accent-4` | 引导视线 |

### accent 色使用约束

强调色是"调味料"，用多了就毁了整道菜：

- **允许使用 accent 色的元素**：标题下划线/竖线（3-4px）、数据数字颜色、标签边框/文字、进度条填充、PART 编号、圆点/节点、图标背景
- **禁止使用 accent 色的元素**：大面积卡片背景、正文段落文字、大面积色块填充
- **同页限制**：同一页面最多同时使用 2 种 accent 色（--accent-1 和 --accent-2），不要 4 个全用
- **每个卡片**：最多使用 1 种 accent 色作为主题色

## Bento Grid 布局系统

根据 layout_hint 选择布局，用 CSS Grid 精确实现。所有坐标基于内容区(40px padding)。

### 布局映射表

| layout_hint | CSS grid-template | 卡片尺寸 |
|-------------|------------------|---------|
| 单一焦点 | 1fr / 1fr | 1200x580 |
| 50/50 对称 | 1fr 1fr / 1fr | 各 590x580 |
| 非对称两栏 (2/3+1/3) | 2fr 1fr / 1fr | 790+390 x 580 |
| 三栏等宽 | repeat(3, 1fr) / 1fr | 各 387x580 |
| 主次结合 | 2fr 1fr / 1fr 1fr | 790x580 + 390x280x2 |
| 英雄式+3子 | 1fr / auto 1fr 然后 repeat(3,1fr) | 1200x260 + 387x300x3 |
| 混合网格 | 自定义 grid-row/column span | 尺寸由内容决定 |

间距: gap=20px | 圆角: border-radius=12px | 内边距: padding=24px

## 6 种卡片类型的 HTML 实现

### text（文本卡片）
- 标题: h3, font-size=18-20px, font-weight=700, color=text-primary
- 正文: p, font-size=13-14px, line-height=1.8, color=text-secondary
- 关键词: 用 <strong> 或 <span class="highlight"> 包裹（背景 accent-primary 10% 透明度）

### data（数据卡片）
- 核心数字: font-size=36-48px, font-weight=800, **直接用 `color: var(--accent-1)`**
  - 不要用 `background-clip: text` 渐变文字：转 PPTX 后退化为渐变的第一个颜色
- 单位/标签: font-size=14-16px, color=text-secondary 或 color=accent-2
- 补充说明: font-size=13px, 在数字下方

### list（列表卡片）
- 列表项: display=flex, gap=10px
- 圆点: min-width=6-8px, height=6-8px, border-radius=50%, background=accent-primary
- 文字: font-size=13px, color=text-secondary, line-height=1.6
- 交替使用不同 accent 色的圆点增加层次感

### tag_cloud（标签云）
- 容器: display=flex, flex-wrap=wrap, gap=8px
- 标签: display=inline-block, padding=4px 12px, border-radius=9999px
- 标签边框: border=1px solid accent-primary 30%透明, color=accent-primary, font-size=12px

### process（流程卡片）
- 步骤: display=flex 水平排列，或垂直排列
- 节点: width/height=32px, border-radius=50%, background=accent-primary, 居中显示步骤数字
- 连线: 节点之间用 `<div>` 作为连接线（height=2px, background=accent-color）
- 箭头: 用内联 `<svg>` 三角形（`<polygon>` 或 `<path>`）
- 标签: font-size=12-13px, margin-top=8px

### data_highlight（大数据高亮区）
- 用于封面或重点页的超大数据展示
- 数字: font-size=64-80px, font-weight=900
- 用 accent 颜色直接上色（渐变文字转 PPTX 后会退化为纯色）

## 视觉设计原则

### 渐变使用约束（慎用渐变）
渐变用不好比纯色更丑。遵循以下限制：
- **允许渐变的场景**：页面背景（大面积微妙过渡）、强调色竖线/横线（3-4px 窄条）、进度条填充
- **禁止渐变的场景**：正文文字颜色、小尺寸图标填充、卡片背景（除非暗色系微妙过渡）、按钮
- **渐变方向**：同一页面内所有渐变方向保持一致（统一 135deg 或 180deg）
- **渐变色差**：两端颜色色相差不超过 60 度（如蓝-青可以，蓝-橙禁止），亮度差不超过 20%
- **首选纯色**：当不确定渐变效果时，用 accent 纯色（`var(--accent-1)`）替代

### 层次感
- 页面标题(H1): 28px, 700 weight, 左上固定位，搭配 accent 色的标题下划线或角标
- Overline 标记(如"PART 0X"): 11-12px, 700 weight, letter-spacing=2-3px, accent 色
- 卡片标题(H2) > 数据数字(Data) > 正文(Body) > 辅助标注(Caption) -- 严格遵循排版阶梯

### 装饰元素词汇表

以下是专业 PPT 中常用的装饰元素。每页至少使用 2-3 种装饰元素，但不要过度堆砌。

#### 基础装饰（所有风格通用）

| 装饰 | 实现方式 | 使用时机 |
|------|---------|--------|
| 背景网格点阵 | radial-gradient(circle, dot-color dot-size, transparent dot-size), background-size=grid-size | grid_pattern.enabled=true 的风格 |
| 标题下划线 | `<div>` 4px 高, 40-60px 宽, accent 渐变, 在标题下方 4px 处 | 每页标题 |
| 卡片左侧强调线 | `<div>` 3-4px 宽, 100% 高, accent 色, position=absolute, left=0 | 文本卡片/引用 |
| 编号气泡 | `<div>` 32-40px 圆形, accent 色背景, 白色数字 | 步骤/列表序号 |
| 分隔渐隐线 | `<div>` 1px 高, linear-gradient(90deg, accent 30%, transparent) | 卡片内区域分隔 |

#### 深色风格专用

| 装饰 | 实现方式 | 效果 |
|------|---------|------|
| 角落装饰线 | `<div>` L 形边框（只显示两条边: border-top + border-left），accent 色 20% 透明度 | 页面四角层次感 |
| 光晕效果 | `<div>` radial-gradient 超大半透明圆(400-600px)，accent 色 5-8% 透明度 | 关键区域背后的辉光 |
| 半透明数字水印 | `<div>` 超大号数字(120-160px), accent 色, opacity 0.03-0.05 | 页面层次感/章节标识 |
| 卡片分隔线 | `<div>` 1px solid rgba(255,255,255,0.05) | 卡片间微妙分界 |

#### 浅色风格专用

| 装饰 | 实现方式 | 效果 |
|------|---------|------|
| 渐变色块 | `<div>` 大面积弧形色块, accent 色 5-10% 透明度, border-radius 50% | 卡片一角的活泼感 |
| 细边框卡片 | border: 1px solid var(--card-border) | 清晰的区域划分 |
| 圆形图标底 | `<div>` 48px 圆形, accent 色 10% 透明度背景 + 内联 SVG 图标 | 替代纯文字列表 |

#### 统一页脚系统

每页（封面和章节封面除外）底部必须有统一页脚：

```html
<div style="position:absolute; bottom:20px; left:40px; right:40px;
            display:flex; justify-content:space-between; align-items:center;">
  <!-- 左侧：章节信息 -->
  <span style="font-size:11px; color:var(--text-secondary); opacity:0.5;
               letter-spacing:1px;">
    PART 01 - 章节名称
  </span>
  <!-- 右侧：页码 + 品牌 -->
  <span style="font-size:11px; color:var(--text-secondary); opacity:0.5;">
    07 / 15  |  品牌名
  </span>
</div>
```

页脚规则：
- 字号 11px, text-secondary 色, opacity 0.5（极其低调，不抢内容视线）
- 左侧显示当前 PART 编号 + 章节名
- 右侧显示 当前页/总页数 + 品牌名（如有）
- **封面页、章节封面不显示页脚**

### 配图融入设计（根据用户偏好决定是否配图）

配图是可选项，在需求调研阶段由用户决定：
- **不配图**: 跳过本节
- **只关键页**: 仅封面、章节封面、结束页配图
- **每页配图**: 所有页面都有图片融入

当需要配图时，图片不能像贴纸一样硬塞在页面里。必须通过**视觉融入技法**让图片与内容浑然一体。

**核心原则**：图片是**氛围的一部分**，不是独立的内容块。

> **导出说明**：下面的技法用 `linear-gradient` 遮罩 `<div>` 叠在图片上实现渐隐，图片和遮罩进 PPTX 后各自独立、可单独调整。也可以直接用 CSS `mask-image`，导出时那张图会连同遮罩效果一起转成图层（外观一致，但不能再单独调遮罩）。

#### 5 种融入技法

##### 1. 渐隐融合 -- 封面页/章节封面的首选

图片占页面右半部分，左侧边缘用渐变遮罩渐隐到背景色，让图片"消融"在背景中。

```html
<div style="position:absolute; right:0; top:0; width:55%; height:100%; overflow:hidden;">
  <img src="..." style="width:100%; height:100%; object-fit:cover; opacity:0.35;">
  <!-- 左侧渐隐遮罩(真实div) -->
  <div style="position:absolute; left:0; top:0; width:60%; height:100%;
              background:linear-gradient(90deg, var(--bg-primary) 0%, transparent 100%);"></div>
</div>
```

##### 2. 色调蒙版 -- 内容页大卡片

图片上覆盖半透明色调层，让图片染上主题色，同时降低视觉干扰。

```html
<div style="position:relative; overflow:hidden; border-radius:var(--card-radius);">
  <img src="..." style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0;">
  <!-- 主题色蒙版 -->
  <div style="position:absolute; top:0; left:0; width:100%; height:100%;
              background:linear-gradient(135deg, rgba(11,17,32,0.85), rgba(15,23,42,0.6));"></div>
  <!-- 内容在蒙版之上 -->
  <div style="position:relative; z-index:1; padding:24px;">
    <!-- 文字内容 -->
  </div>
</div>
```

##### 3. 氛围底图 -- 章节封面/数据页

图片作为整页超低透明度背景，营造氛围感。

```html
<img src="..." style="position:absolute; top:0; left:0; width:100%; height:100%;
     object-fit:cover; opacity:0.08; pointer-events:none;">
```

##### 4. 裁切视窗 -- 小卡片顶部

图片作为卡片头部的"窗口"，用圆角裁切，底部渐隐到卡片背景。

```html
<div style="position:relative; height:120px; overflow:hidden;
            border-radius:var(--card-radius) var(--card-radius) 0 0;">
  <img src="..." style="width:100%; height:100%; object-fit:cover;">
  <div style="position:absolute; bottom:0; left:0; width:100%; height:50%;
              background:linear-gradient(0deg, var(--card-bg-from), transparent);"></div>
</div>
```

##### 5. 圆形/异形裁切 -- 数据卡片辅助

图片裁切为圆形或其他形状，作为装饰元素。

```html
<img src="..." style="width:80px; height:80px; border-radius:50%;
     object-fit:cover; border:3px solid var(--accent-1);">
```

#### 按页面类型选择技法

| 页面类型 | 推荐技法 | opacity 范围 |
|---------|---------|-------------|
| 封面页 | 渐隐融合 | 0.25-0.40 |
| 章节封面 | 氛围底图 或 渐隐融合 | 0.05-0.15 |
| 英雄卡片 | 色调蒙版 | 图片0.3 + 蒙版0.7 |
| 大卡片(>=50%宽) | 色调蒙版 或 裁切视窗 | 0.15-0.30 |
| 小卡片(<400px) | 裁切视窗 或 圆形裁切 | 0.8-1.0 |
| 数据页 | 氛围底图 | 0.05-0.10 |

#### 图片 HTML 规范
- 优先用 `<img>` 标签（进 PPTX 后是独立图片，可替换）；CSS `background-image` 也能导出，但会连同容器背景烘焙成一张图层
- `object-fit: cover`，`border-radius` 与容器一致
- 图片用本地路径（相对 HTML 文件或绝对路径），不要引用远程 URL
- 底层氛围图的 opacity 必须足够低（0.05-0.15），避免遮挡前景内容

**禁止**：
- 禁止图片直接裸露在卡片角落（无融入效果）
- 禁止图片占据整个卡片且无蒙版（文字不可读）
- 禁止图片与背景色有明显的矩形边界线

#### 内联 SVG 的写法（详见 `pipeline-compat.md` 第 3 节）

1. **文字标注不写 SVG `<text>`**：数据标注、x 轴标签、图例、环形图中心文字都用 HTML `<div>` / `<span>` 绝对定位叠在 SVG 上方（SVG `<text>` 进 PPTX 后位置可能偏 3-5px）
2. **数字与单位字号不同时**用 flex 排成独立元素（`display:flex; align-items:baseline; gap:4px`）
3. **环形进度用 `stroke-dasharray="弧长 周长"` 两值写法**，不用 `stroke-dashoffset`（会被忽略）

## 对比度安全规则（必须遵守）

文字颜色必须与其直接背景形成足够对比度，否则用户看不清：

| 背景类型 | 文字颜色要求 |
|---------|------------|
| 深色背景 (--bg-primary 亮度 < 40%) | 标题用 --text-primary（白色/浅色）, 正文用 --text-secondary（70%白） |
| 浅色背景 (--bg-primary 亮度 > 60%) | 标题用 --text-primary（深色/黑色）, 正文用 --text-secondary（灰色） |
| 卡片内部 | 跟随卡片背景明暗选择文字色 |
| accent 色文字 | 只能用于标题/标签/数据数字，不能用于大段正文 |

**禁止行为**：
- 禁止深色背景 + 深色文字（如黑底黑字、深蓝底深灰字）
- 禁止浅色背景 + 白色文字
- 禁止硬编码颜色值，所有颜色必须通过 CSS 变量引用

## 纯 CSS 数据可视化（推荐使用）

数据卡片不要只放一个大数字。用纯 CSS/SVG 实现轻量数据可视化，让数字更有冲击力。以下是 8 种可视化类型，根据数据特征选择：

### 1. 进度条（表示百分比/完成度）
```css
.progress-bar {
  height: 8px; border-radius: 4px;
  background: var(--card-bg-from);
  overflow: hidden;
}
.progress-bar .fill {
  height: 100%; border-radius: 4px;
  background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
  /* width 用内联 style 设置百分比 */
}
```

### 2. 对比柱（两项对比）
```css
.compare-bar {
  display: flex; gap: 4px; align-items: flex-end;
  height: 60px;
}
.compare-bar .bar {
  flex: 1; border-radius: 4px 4px 0 0;
  /* height 用内联 style 设置百分比 */
}
```

### 3. 环形百分比（内联 SVG 画弧，中心文字用 HTML 叠加）
```html
<div style="position:relative; width:80px; height:80px;">
  <svg width="80" height="80" viewBox="0 0 80 80">
    <circle cx="40" cy="40" r="32" fill="none"
            stroke="var(--card-bg-from)" stroke-width="10"/>
    <circle cx="40" cy="40" r="32" fill="none"
            stroke="var(--accent-1)" stroke-width="10"
            stroke-dasharray="180.96 201.06" stroke-linecap="round"
            transform="rotate(-90 40 40)"/>
  </svg>
  <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
              font-size:16px; font-weight:700; color:var(--text-primary);">90%</div>
</div>
```
计算公式: dasharray 第一个值 = 2 * PI * r * (百分比/100), 第二个值 = 2 * PI * r

### 4. 指标行（数字+标签+进度条 组合）
```html
<div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
  <span style="font-size:24px; font-weight:800; color:var(--accent-1);
               font-variant-numeric:tabular-nums; min-width:60px;">87%</span>
  <div style="flex:1;">
    <div style="font-size:12px; color:var(--text-secondary); margin-bottom:4px;">用户满意度</div>
    <div class="progress-bar"><div class="fill" style="width:87%"></div></div>
  </div>
</div>
```

### 5. 迷你折线图 Sparkline（趋势方向）
```html
<svg width="120" height="40" viewBox="0 0 120 40">
  <!-- 面积填充 -->
  <path d="M0,35 L20,28 L40,30 L60,20 L80,15 L100,10 L120,5 L120,40 L0,40 Z"
        fill="var(--accent-1)" opacity="0.1"/>
  <!-- 折线 -->
  <polyline points="0,35 20,28 40,30 60,20 80,15 100,10 120,5"
            fill="none" stroke="var(--accent-1)" stroke-width="2" stroke-linecap="round"/>
  <!-- 终点圆点 -->
  <circle cx="120" cy="5" r="3" fill="var(--accent-1)"/>
</svg>
```
用在数据数字旁边，占位小但信息量大。数据点坐标根据实际趋势调整 y 值（高=好 -> y 值小）。

### 6. 点阵图 Waffle Chart（百分比直觉化）
```html
<div style="display:grid; grid-template-columns:repeat(10,1fr); gap:3px; width:100px;">
  <!-- 67 个填充点 + 33 个空点 = 67% -->
  <div style="width:8px; height:8px; border-radius:2px; background:var(--accent-1);"></div>
  <!-- 重复填充点... -->
  <div style="width:8px; height:8px; border-radius:2px; background:var(--card-bg-from);"></div>
  <!-- 重复空点... -->
</div>
```
10x10 = 100 格，填充数量 = 百分比值。比进度条更直觉。

### 7. KPI 指标卡（数字+趋势箭头+标签）
```html
<div style="display:flex; align-items:baseline; gap:8px;">
  <span style="font-size:40px; font-weight:800; color:var(--accent-1);
               font-variant-numeric:tabular-nums;">2.4M</span>
  <!-- 上升箭头（绿色=好） -->
  <svg width="16" height="16" viewBox="0 0 16 16">
    <polygon points="8,2 14,10 2,10" fill="#16A34A"/>
  </svg>
  <span style="font-size:14px; color:#16A34A; font-weight:600;">+12.3%</span>
</div>
<div style="font-size:12px; color:var(--text-secondary); margin-top:4px;">月活跃用户数</div>
```
趋势箭头颜色：上升用绿色 #16A34A，下降用红色 #DC2626，持平用 text-secondary。

### 8. 评分指示器（5分制）
```html
<div style="display:flex; gap:6px;">
  <!-- 4 个实心圆 + 1 个空心圆 = 4/5 分 -->
  <div style="width:12px; height:12px; border-radius:50%; background:var(--accent-1);"></div>
  <div style="width:12px; height:12px; border-radius:50%; background:var(--accent-1);"></div>
  <div style="width:12px; height:12px; border-radius:50%; background:var(--accent-1);"></div>
  <div style="width:12px; height:12px; border-radius:50%; background:var(--accent-1);"></div>
  <div style="width:12px; height:12px; border-radius:50%; border:2px solid var(--accent-1); background:transparent;"></div>
</div>
```

### 可视化选择指南

| 数据类型 | 推荐可视化 |
|---------|----------|
| 百分比/完成度 | 进度条 或 环形百分比 |
| 两项对比 | 对比柱 |
| 时间趋势 | 迷你折线图 |
| 比例直觉化 | 点阵图 |
| 核心 KPI | KPI 指标卡 |
| 多指标并排 | 指标行（多行堆叠） |
| 评级/评分 | 评分指示器 |

## 内容密度要求

每张卡片不能只有一个标题和一句话，必须信息充实：

| 卡片类型 | 最低内容要求 |
|---------|------------|
| text | 标题 + 至少 2 段正文（每段 30-50 字）或 标题 + 3-5 条要点 |
| data | 核心数字 + 单位 + 变化趋势(升/降/持平) + 一句解读 + 进度条/对比可视化 |
| list | 至少 4 条列表项，每条 15-30 字 |
| process | 至少 3 个步骤，每步有标题+一句描述 |
| tag_cloud | 至少 5 个标签 |
| data_highlight | 1 个超大数字 + 副标题 + 补充数据行 |

**禁止**：空白卡片、只有标题没有内容的卡片、只有一句话的卡片

## 特殊字符与单位符号处理（必须遵守）

专业内容中大量使用特殊字符、单位符号、上下标。这些符号必须正确输出，否则在 SVG/PPTX 中会乱码或丢失：

| 类型 | 正确写法 | 错误写法 | 说明 |
|------|----------|----------|------|
| 温度 | `25–40 °C` 或 `25–40&nbsp;°C` | `25-40 oC` | 用 Unicode 度符号而不是字母 o |
| 百分比 | `99.9%` | `99.9 %`（前面加空格） | 数字和 % 之间不加空格 |
| ppm | `100 ppm` | `100ppm` | 数字和单位之间加空格 |
| 化学式下标 | `H₂O` 或 `H<sub>2</sub>O` | `H2O` | 用 Unicode 下标数字或 sub 标签 |
| 化学式上标 | `m²` 或 `m<sup>2</sup>` | `m2` | 用 Unicode 上标或 sup 标签 |
| 大于等于 | `≥ 99.9%` 或 `>=99.9%` | `> =99.9%` | 不要在 > 和 = 之间加空格 |
| 微米 | `0.22 μm` | `0.22 um` | 用 Unicode mu 而不是字母 u |

### 规则
1. **优先用 Unicode 直接字符**（° ² ³ μ ≥ ≤ ₂ ₃），而不是 HTML 实体，因为 Unicode 在 SVG/PPTX 中渲染最可靠
2. **数字与单位之间**：英文单位前加一个半角空格（`100 ppm`），符号单位紧跟（`99.9%`、`25°C`）
3. **化学式中的下标数字**：必须用 `<sub>` 标签或 Unicode 下标字符（₀₁₂₃₄₅₆₇₈₉），绝对不能用普通数字代替

## 页面级情感设计

不同页面类型有不同的情感目标：

| 页面类型 | 情感目标 | 设计要求 |
|---------|---------|---------|
| 封面页 | 视觉冲击、专业信赖 | 大标题+配图、装饰元素要丰富、品牌感要强 |
| 目录页 | 清晰导航、预期管理 | 每章有图标/色块标识、章节编号醒目 |
| 章节封面 | 过渡、呼吸感 | PART 编号大号显示、引导语、留白充分 |
| 内容页 | 信息传递、数据说服 | 卡片密度高、数据可视化、要点清晰 |
| 结束页 | 总结回顾、行动号召 | 3-5 条核心要点回顾 + 明确的 CTA（联系方式/下一步） |

## 导出约束（必须遵守）

本 HTML 会被转成可编辑的 PowerPoint：文字变成文本框，色块和 SVG 图形变成原生形状，dom-to-svg 画不出的效果自动截成图层。完整规则见 `pipeline-compat.md`，写的时候记住四条：

1. **静态 HTML**：禁止 `<script>`、`@keyframes` / `animation`、`<canvas>` / `<video>` / `<iframe>`。页间切换和卡片入场动画在导出时添加，不写在 HTML 里
2. **卡片根节点打标记**：`<div class="card" data-card-id="...">`（id 取策划稿的 `card_id`）。导出时据此把卡片打成组合、按顺序做入场动画
3. **关键信息不依赖会退化的效果**：`text-shadow`、渐变文字（`background-clip:text`）、`box-shadow`、`backdrop-filter`、`::first-letter` 进 PPTX 后会丢失或变样，只能用作锦上添花
4. **装饰可以放开用**：径向/锥形渐变、`filter: blur()`、`mask-image`、`clip-path`、旋转的印章——只要放在**没有文字的装饰元素**上，导出时原样保真（转成图层）

## CSS 变量模板

所有颜色值必须通过 CSS 变量引用，禁止硬编码 hex/rgb 值（唯一例外：transparent 和白色透明度 rgba(255,255,255,0.x)）。

```css
:root {
  --bg-primary: {{background.primary}};
  --bg-secondary: {{background.gradient_to}};
  --card-bg-from: {{card.gradient_from}};
  --card-bg-to: {{card.gradient_to}};
  --card-border: {{card.border}};
  --card-radius: {{card.border_radius}}px;
  --text-primary: {{text.primary}};
  --text-secondary: {{text.secondary}};
  --accent-1: {{accent.primary[0]}};
  --accent-2: {{accent.primary[1]}};
  --accent-3: {{accent.secondary[0]}};
  --accent-4: {{accent.secondary[1]}};
  --grid-dot-color: {{grid_dot.color}};
  --grid-dot-opacity: {{grid_dot.opacity}};
  --grid-size: {{grid_dot.size}}px;
}
```

## 输出要求
- 输出完整 HTML 文件（含 <!DOCTYPE html>、<head>、<style> 全内嵌）
- body 固定 width=1280px, height=720px
- 不使用外部 CSS/JS（全部内嵌）
- 不添加任何解释性文字
- 确保每张卡片的内容完整填充（不留空卡片）
- 数据卡片的数字要醒目突出（最大视觉权重）
- 所有颜色都通过 var(--xxx) 引用，不硬编码
- 浅色背景的卡片内文字必须是深色，深色背景的卡片内文字必须是浅色
- 数据卡片至少配一个 CSS 可视化元素（进度条/对比柱/环形图）
- 每张卡片根节点带 `class="card"` 与 `data-card-id`
```

---

## 5. 演讲备注

为每页生成演讲提示（可选步骤）。

```text
你是一名演讲教练。请为以下 PPT 页面生成简洁的演讲备注。

## 页面标题
{{SLIDE_TITLE}}

## 页面内容
{{SLIDE_CONTENT}}

## 演讲备注要求
1. 每页 3-5 句话的演讲提示
2. 包括：开场过渡语、核心要传达的信息、可以用的比喻/故事/互动
3. 标注关键数据的口述表达（如："这个数字意味着..."）
4. 提示与下一页的衔接语
5. 整体风格：自然、自信、有节奏感
```

---

## Prompt 使用流程

```
Step 1 -> 使用 Prompt #1（需求调研）
Step 2 -> 搜索（不需要专门 Prompt，直接使用搜索工具）
Step 3 -> 使用 Prompt #2（大纲架构师）
Step 4 -> 使用 Prompt #3（内容分配与策划稿）
Step 5a -> 按 styles/index.md 选择风格
Step 5b -> 如有 generate_image，为每页生成配图
Step 5c -> 使用 Prompt #4（HTML 设计稿），逐页生成，遵守 `pipeline-compat.md`
后处理 -> scripts/html_packager.py 合并预览 + scripts/html2svg.py 转 SVG + scripts/svg2pptx.py 转 PPTX（按动画偏好加 --animate / --transition）
可选 -> 使用 Prompt #5（演讲备注）
```
