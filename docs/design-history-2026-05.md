# PPT Agent Skill 世界级重做设计文档

**日期**：2026-05-10
**作者**：与用户共同确定（基于 brainstorming + visual companion 全程对齐）
**状态**：已实施（历史记录）

> 这是 2026-05 那次重做动工前的设计文档，保留用于追溯决策。其中的文件路径、脚本名和测试方案与现状已有出入，当前实现以 SKILL.md、`scripts/contracts.py` 和代码为准。

---

## 1. 目标与动机

### 1.1 当前状态
[ppt-agent-skill](../../../) 现有 8 种预置风格 + 8 种纯 CSS/SVG 数据可视化。质量已经超出大多数同类工具，但与 Linear / Anthropic / Stripe / Apple / Vercel / NYT / Tom Ford 等世界级品牌的实际排版水准对比，仍有明显差距：

- 字距未按显示尺寸分级（大字应负字距，小标应正字距）
- 数字未统一使用 `font-variant-numeric: tabular-nums`
- OpenType 特性（kern/liga/ss01/calt）未启用
- 缺乏 sans + serif italic 混排（Linear/Stripe/Apple 的签名手法）
- 缺乏首字下沉、masthead 刊号、不对称网格等编辑级排版
- 部分风格（vibrant_rainbow, luxury_purple）的视觉品味偏俗

### 1.2 目标
将 PPT Agent Skill 升级为**世界级演示文稿生成系统**：
- 风格库从 8 → **26** 种，覆盖 5 个情绪板块
- 所有风格按世界级标杆（Linear / Anthropic / Stripe / Apple / NYT / Tom Ford / Pitch / Mercury / Arc / Notion 等品牌的实际排版做法）执行
- 图表系统从 8 → **18-20** 种，含 ECharts 级复杂图表（世界地图、关系网络、3D 立体柱、桑基、热力等）
- 新增「风格预览画廊」功能（gallery.py）让用户直观选风格
- 全程**向后兼容**：原 8 个 style_id 保留并升级，老用户不受影响

### 1.3 非目标（Out of Scope）

明确不做的：
- 不做 PDF/视频/Keynote 输出（本次专注风格 + 图表 + 画廊）
- 不做 Markdown 输入支持
- 不做模板继承（用户自带 PPTX/Logo 取色）
- 不引入实际的 ECharts 运行时（保持纯 SVG/CSS，否则破坏 svg2pptx 管线）
- 不做用户自定义风格 JSON 加载（YAGNI，等真有需求再加）
- 不重写 SKILL.md 的 6 步 pipeline 主架构（仅 Step 5 内部调整）

---

## 2. 范围概览

| 模块 | 当前 | 目标 | 增量 |
|------|------|------|------|
| 预置风格 | 8 | 26 | +18 新增 + 8 升级 |
| 数据可视化 | 8 | 18-20 | +10-12 新增 + 8 升级 |
| 字体栈策略 | 单一 | 三层降级（商业/Google/系统） | 新增 |
| 排版铁律文档 | 散落在 prompts.md | 独立 typography.md | 新增 |
| 风格预览画廊 | 无 | gallery.py + style-gallery/ | 新增 |
| README 视觉资产 | 5 张 PNG（小米示例） | 26 风格预览 + 4 板块象限图 | 新增 |

---

## 3. 详细设计

### 3.1 26 风格列表（按 5 板块）

**保留原 ID 升级（8 个）**：仅视觉/字体/排版按世界级标杆重做，ID 完全不变以保兼容。

| ID | 板块 | 升级方向 | 灵感来源 |
|----|------|---------|---------|
| `dark_tech` | 暗色专业 | 极光辉光 + 网格底纹 + Inter Tight 紧凑字距 + serif italic 混排 | Linear.app |
| `xiaomi_orange` | 暗色专业 | 产品光球 + 点燃感辐射 + 电影级光感 | Apple Keynote (硬件版) |
| `blue_white` | 浅色高级 | Apple 级极简白 + 雪松灰文本 + 内框线条 | Apple 企业页面 |
| `royal_red` | 东方文化 | 金箔角饰 + 印章元素 + 宋体居中 + 渐隐金线 | 北京冬奥开幕式 |
| `fresh_green` | 浅色高级 | 赭石+草绿 + serif 斜体 + Aesop 级高级自然感 | Aesop |
| `luxury_purple` | 暗色专业 | YSL/Tom Ford 级黑金 + Didot 衬线 + 菱形装饰 | Tom Ford |
| `minimal_gray` | 浅色高级 | 米纸底色 + serif 标题 + 三栏分割 + masthead 刊号风 | NYT Magazine |
| `vibrant_rainbow` | 活力鲜明 | Stripe 级渐变 + 玻璃球反光（带内阴影）+ 半透徽章 | Stripe Sessions |

**新增 18 个**（全部用诗意新名）：

| ID | 板块 | 适用场景 | 灵感来源 |
|----|------|---------|---------|
| `nocturne_violet` | 暗色专业 | 设计师 SaaS / 产品发布 | Linear（紫光版） |
| `cyberpunk_neon` | 暗色专业 | 电竞 / 游戏 / Web3 | Cyberpunk 2077 |
| `chrome_y2k` | 暗色专业 | Web3 / 千禧年复古 / 科幻 | Y2K 美学 |
| `noir_film` | 暗色专业 | 纪录片 / 影像艺术 / 记者 | 黑白电影 |
| `mocha_editorial` | 浅色高级 | AI 安全研究 / 学术 / 出版 | Anthropic / Pantone 2025 |
| `medical_pulse` | 浅色高级 | 医疗 / 医药 / 健康保险 | 纯白+医疗蓝+ECG 心电 |
| `earth_concrete` | 浅色高级 | 建筑 / 室内 / 工业 / 咖啡 | Suisse Int'l 风格 |
| `champagne_gold` | 浅色高级 | 婚庆 / 宴会 / 年终庆典 | 奢华香槟金 |
| `liquid_glass` | 浅色高级 | XR / AR / 苹果生态 | iOS 26 / visionOS |
| `kindergarten_pop` | 活力鲜明 | 儿童教育 / 亲子 / 启蒙 | Quicksand 圆润字体 |
| `bauhaus_block` | 活力鲜明 | 教育 / 创意品牌 / 独立设计 | Bauhaus / Swiss Design |
| `candy_pastel` | 活力鲜明 | 甜品 / 烘焙 / 儿童零食 | 马卡龙糖果色 |
| `sakura_wabi` | 东方文化 | 日系 / 茶道 / 酒店 / 侘寂 | 日本侘寂美学 |
| `ink_jade` | 东方文化 | 国潮 / 茶饮 / 古风文创 | 墨色+浅米+朱红 |
| `botanic_forest` | 自然/复古 | 户外品牌 / 可持续 / 林产 | 深绿森林秘境 |
| `safari_savanna` | 自然/复古 | 旅行 / 户外探险 / 纪录片 | 萨凡纳暖橙茶 |
| `retro_70s` | 自然/复古 | 独立咖啡 / 复古品牌 / 唱片 | 70 年代棕橙黄 |
| `gov_authority` | 自然/复古 | 党政机关 / 重大会议 / 严肃汇报 | 深红蓝 + 国徽感 |

**总计：8 + 18 = 26 个风格**

### 3.2 风格 JSON Schema 升级

参考 [sunbigfly/ppt-agent-skills](https://github.com/sunbigfly/ppt-agent-skills) 的成熟实践，引入 `mood_keywords` / `design_soul` / `variation_strategy` / `decoration_dna` 等高价值字段。每个风格在原有字段基础上扩展（新字段标 `[新]`）：

```json
{
  "style_name": "高阶暗黑科技风",
  "style_id": "dark_tech",
  "category": "dark_professional",          // [新] 5 板块之一
  "inspiration": "Linear.app",              // [新] 灵感来源
  "mood_keywords": ["深空冷寂", "精密仪器", "微光脉搏"],  // [新] 情绪标签数组
  "design_soul": "天文台穹顶内部，深蓝黑幕中冷青的仪器扫描光有节奏地划过 -- 精密、冷寂、但每一次扫描都暗含脉搏。",  // [新] 一句话灵魂
  "variation_strategy": "数据页用网格点阵+角标装饰线（紧张高密度），章节封面用大面积深空留白+单一光晕（释放），产品页用全屏暗底+中央悬浮发光数据面板（聚焦）",  // [新] 跨页节奏策略
  "decoration_dna": {                        // [新] 装饰 DNA
    "signature_move": "网格点阵底纹 + L 形角标装饰线 + 极光辉光",
    "forbidden": ["渐变色块", "叶片装饰", "波浪分隔线"],
    "recommended_combos": [
      "网格点阵 + 角标 + 大号水印数字",
      "光晕效果 + 脉冲圆点 + 半透明数字水印"
    ]
  },
  "background": {
    "primary": "#050b1f",
    "gradient_to": "#0a1f3d",
    "texture": {                    // [新] 微妙纹理
      "type": "grid_dot",
      "size": 80,
      "opacity": 0.015
    },
    "glow": [                       // [新] 辉光层（可多层）
      { "x": "80%", "y": "30%", "color": "#6366f1", "opacity": 0.35, "blur": 60 },
      { "x": "20%", "y": "70%", "color": "#22D3EE", "opacity": 0.25, "blur": 60 }
    ]
  },
  "card": {
    "gradient_from": "#1E293B",
    "gradient_to": "#0F172A",
    "border": "rgba(255,255,255,0.05)",
    "border_radius": 12,
    "backdrop_blur": 10              // [新] 玻璃态卡片
  },
  "text": {
    "primary": "#FFFFFF",
    "secondary": "rgba(255,255,255,0.7)",
    "title_size": 28,
    "body_size": 14,
    "card_title_size": 20
  },
  "accent": {
    "primary": ["#22D3EE", "#3B82F6"],
    "secondary": ["#FDE047", "#F59E0B"]
  },
  "typography": {                    // [新] 排版规则
    "display_font": "'Inter Tight', 'Inter', -apple-system, sans-serif",
    "body_font": "'Inter', -apple-system, sans-serif",
    "serif_italic_font": "'Instrument Serif', 'Fraunces', serif",  // 用于混排
    "mono_font": "'JetBrains Mono', 'Söhne Mono', monospace",
    "display_letter_spacing": "-0.045em",
    "body_letter_spacing": "-0.005em",
    "label_letter_spacing": "0.18em",
    "feature_settings": "'ss01', 'cv11', 'calt', 'kern', 'liga'",
    "tabular_nums": true
  },
  "decorations": {                   // [新] 签名手法清单
    "label_anchor": "dot_pulse",     // 小标前的圆点（带辉光）
    "title_serif_italic": true,      // 标题中关键词用 serif italic
    "corner_lines": false,
    "vertical_divider": false,
    "drop_cap": false,
    "masthead": false
  },
  "font_imports": [                  // [新] Google Fonts URL
    "https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap"
  ]
}
```

### 3.3 字体栈三层降级策略

每个风格的 `typography.*_font` 字段都遵循三层降级：

```
[商业字体]      → [Google Fonts 替代]      → [系统兜底]
Söhne          → Inter / Inter Tight      → -apple-system, BlinkMacSystemFont, sans-serif
Tiempos Text   → Source Serif 4           → Iowan Old Style, Georgia, serif
GT America     → Inter                    → SF Pro, sans-serif
Geist Sans     → Inter Tight              → -apple-system, sans-serif
ABC Diatype    → Inter                    → -apple-system, sans-serif
Camera         → Inter                    → -apple-system, sans-serif
Editorial New  → Instrument Serif         → Georgia, serif
Didot          → Playfair Display         → Bodoni Moda, serif
Söhne Mono     → JetBrains Mono           → 'Courier New', monospace
SangBleu       → Fraunces                 → Georgia, serif
Founders Grotesk → Inter Tight            → -apple-system, sans-serif
```

中文场景：`Source Han Serif SC` → `Noto Serif SC` → `STSong, SimSun, serif`

### 3.4 排版铁律（typography.md 内容）

**字距铁律**：
- Display (≥48px)：`letter-spacing: -0.025em ~ -0.045em`（收紧）
- Headline (28-44px)：`letter-spacing: -0.015em`
- Body (13-16px)：`letter-spacing: -0.005em`
- Caption (11-12px)：`letter-spacing: +0.05em`
- Overline / 小标：`letter-spacing: +0.15em ~ +0.65em`（拉开）

**数字必须 tabular-nums**：所有数据用 `font-variant-numeric: tabular-nums proportional-nums`，等宽对齐才有专业感。

**OpenType 特性必开**：`font-feature-settings: "kern", "liga", "ss01", "cv11", "calt", "ccmp"`

**渲染优化必开**：`-webkit-font-smoothing: antialiased`, `text-rendering: optimizeLegibility`

**Sans + Serif italic 混排**：标题中关键词用 serif italic（Instrument Serif / Fraunces / Playfair）。Linear / Stripe / Apple 实际都在用。

**首字下沉**：长正文段落用 `::first-letter { float: left; font-size: 56-72px; line-height: 0.85; padding: 4px 8px 0 0; }`

**不对称网格**：不要总是居中。常用 `1fr / 1.5fr` 或 `2fr / 3fr` 分栏，让留白主动让位给主信息。

**小标锚线**：label 前面加 `::before` 短横线/小圆点，建立视觉锚点。

**微妙纹理**：
- 深色：网格点阵 + 极光辉光
- 浅色：微噪点
- 杂志：纸张米色

**字体栈降级**：商业字体（用户若有）→ Google Fonts → 系统字体兜底。

### 3.5 图表系统升级（18-20 种）

**层级 1：基础升级（8 种，重做）**

| 图表 | 升级方向 |
|------|---------|
| 进度条 | 加渐变 + 圆角 + tabular-nums 数字 |
| 对比柱 | 多条对比 + 数据标签 + 颜色梯度 |
| 环形图 | 多环嵌套 + 中心 KPI + 渐变弧 |
| 迷你折线（sparkline） | 面积填充 + 端点高亮 + 趋势箭头 |
| 点阵图（Waffle） | 10×10 + 类别色块 |
| KPI 指标卡 | 大数字 + 趋势箭头 + 同比 + sparkline |
| 指标行 | 多指标堆叠 + 进度可视化 |
| 评分指示器 | 5 分制 + 半星支持 |

**层级 2：新增高频（6 种）**

| 图表 | 实现方式 |
|------|---------|
| 雷达图（Radar） | SVG `<polygon>` + 多边形网格 |
| 时间线（Timeline） | div 节点 + 真实连线 + 节点编号 |
| 漏斗图（Funnel） | div 梯形 + 渐变填充 + 转化率标注 |
| 仪表盘（Gauge） | SVG 弧线 + 指针 + 刻度 |
| 多组对比柱（Grouped Bar） | flex 多组 + 图例 |
| 简单地理（Simple Map） | SVG 中国/世界轮廓 + 数据点 |

**层级 3：ECharts 级复杂（4-6 种）**

| 图表 | 实现方式 |
|------|---------|
| 世界地图 choropleth | 内联 SVG world map paths + 数据驱动填色 |
| 中国省份地图 | 内联 SVG China provinces + 数据填色 |
| 关系网络（Network） | SVG 节点 + 连线 + 力导向布局静态版 |
| 3D 立体柱 | SVG `<polygon>` 模拟立体 + 透视 |
| 桑基图（Sankey） | SVG path 流 + 节点 |
| 热力日历（Heatmap） | div grid 365 格 + 颜色梯度 |

**关键约束**：所有图表纯 SVG/CSS 实现，不引入 ECharts 运行时（破坏 svg2pptx 管线）。所有图表遵守 `pipeline-compat.md` 防偏移规则（SVG 内不写 `<text>`，标签用 HTML div 叠加）。

### 3.6 风格预览画廊（gallery.py）

**功能**：
1. 读取 `references/styles/*.md` 中的 26 个风格 JSON
2. 为每个风格生成一个 1280×720 的 demo HTML（用统一的"标杆 mock 模板"）
3. 输出到 `ppt-output/style-gallery/<style_id>.html`
4. 生成统一索引 `ppt-output/style-gallery/index.html`（卡片墙）
5. 调用 puppeteer 截图 → `<style_id>.png`
6. 拼合 5 板块象限图 → `style-gallery/quadrants.png`（README 用）

**用法**：
```bash
python3 scripts/gallery.py [--out ppt-output/style-gallery/] [--screenshots]
```

**Agent 在 Step 1 调用**：当用户对风格选择犹豫时，agent 可以执行 gallery.py 后告诉用户"在 ppt-output/style-gallery/index.html 看效果"。

### 3.7 文件组织架构（确认 by-quadrant 切分）

```
ppt-agent-skill/
├── SKILL.md                          # 更新引用，主流程不变
├── README.md                         # 风格数 8→26，加 4 板块预览图
├── README_EN.md                      # 同步
├── references/
│   ├── styles/                       # [新目录]
│   │   ├── index.md                  # 26 风格索引 + JSON Schema + 决策矩阵
│   │   ├── dark.md                   # 7 暗色：dark_tech, xiaomi_orange, luxury_purple, nocturne_violet, cyberpunk_neon, chrome_y2k, noir_film
│   │   ├── light.md                  # 8 浅色：blue_white, fresh_green, minimal_gray, mocha_editorial, medical_pulse, earth_concrete, champagne_gold, liquid_glass
│   │   ├── vibrant.md                # 4 活力：vibrant_rainbow, kindergarten_pop, bauhaus_block, candy_pastel
│   │   ├── cultural.md               # 3 东方：royal_red, sakura_wabi, ink_jade
│   │   └── natural.md                # 4 自然/复古：botanic_forest, safari_savanna, retro_70s, gov_authority
│   ├── charts/                       # [新目录]
│   │   ├── index.md                  # 图表索引 + 决策矩阵
│   │   ├── basic.md                  # 8 种基础（升级版）
│   │   ├── advanced.md               # 6 种进阶
│   │   └── complex.md                # 4-6 种 ECharts 级
│   ├── principles/                   # [新目录，参考 sunbigfly]
│   │   └── failure-modes.md          # 8 种失败模式 + 修复顺序
│   ├── typography.md                 # [新] 排版铁律（共享）
│   ├── style-system.md               # [改造] 改为引导文件，redirect 到 styles/index.md
│   ├── bento-grid.md                 # 保留
│   ├── pipeline-compat.md            # 保留
│   ├── prompts.md                    # 更新引用 + 新增 charts.md 引用
│   └── method.md                     # 保留
├── scripts/
│   ├── html_packager.py              # 保留
│   ├── html2svg.py                   # 保留
│   ├── svg2pptx.py                   # 保留
│   ├── gallery.py                    # [新] 生成风格预览画廊
│   └── smoke_test.py                 # [新] 端到端测试 + 失败模式扫描
├── tests/
│   └── smoke-results/                # [新] smoke_test.py 输出
└── ppt-output/
    ├── style-gallery/                # [新] gallery.py 输出
    │   ├── index.html
    │   ├── <style_id>.html × 26
    │   ├── <style_id>.png × 26
    │   └── quadrants.png             # 5 板块拼图
    └── png/                          # 原小米示例保留
```

**板块分类与计数核对**：
- 暗色专业 (7)：dark_tech, xiaomi_orange, luxury_purple, nocturne_violet, cyberpunk_neon, chrome_y2k, noir_film
- 浅色高级 (8)：blue_white, fresh_green, minimal_gray, mocha_editorial, medical_pulse, earth_concrete, champagne_gold, liquid_glass
- 活力鲜明 (4)：vibrant_rainbow, kindergarten_pop, bauhaus_block, candy_pastel
- 东方文化 (3)：royal_red, sakura_wabi, ink_jade
- 自然/复古 (4)：botanic_forest, safari_savanna, retro_70s, gov_authority

**合计：7 + 8 + 4 + 3 + 4 = 26 ✓**

### 3.8 SKILL.md 更新点

主 6 步 pipeline 不变。具体调整：

- **Step 1（需求调研）**：第 7 题"补充信息"中"视觉风格偏好"的引导从"8 种预置风格"改为"26 种预置风格，可执行 gallery.py 预览"
- **Step 5a（风格决策）**：阅读 `references/styles/index.md` 而非 `style-system.md`；引入"5 板块决策矩阵"
- **Step 5c（HTML 设计稿）**：Prompt #4 必须注入新的 `typography` 字段；在画布规范前增加"排版铁律"小节，引用 `typography.md`；同时引用 `references/principles/failure-modes.md`
- **质量自检**：新增"字距/数字/OpenType 三检查" + 失败模式扫描

### 3.9 README.md 更新点

- 风格数：8 → 26
- 图表数：8 → 18-20
- 加 4-5 张 5 板块象限预览图（gallery.py 生成）
- 增加"风格预览"章节链接 `ppt-output/style-gallery/index.html`
- 工作流图保持不变

### 3.10 失败模式目录（参考 sunbigfly 的 runtime-failure-modes）

新建 `references/principles/failure-modes.md`，沉淀 Step 4 单页生产的失败模式。它定义合同违约和修复顺序，不定义某种审美风格、不压制创新。

**3 大类 8 种失败模式**：

| 类别 | 失败模式 | 触发条件 |
|------|---------|---------|
| 内容未完成 | underfill | 页面视觉成立，但 payload 明显不足；装饰远多于有效信息 |
| 内容未完成 | support_collapse | 支撑卡片没有承担解释/比较/证据/上下文 |
| 内容未完成 | payload_missing | planning 或 HTML 未完整执行本页应交付的信息 |
| 内容未完成 | source_overclaim | 页面结论强于资料支持力度 |
| 视觉失真 | launch_drift | 封面/章节页拉向与内容不匹配的发布会语气 |
| 视觉失真 | anchor_overexpansion | 锚点占据全部注意力，支撑内容失去存在空间 |
| 视觉失真 | deck_rhythm_clone | 多页同构布局/装饰/锚点关系，无节奏推进 |
| 视觉失真 | decorative_substitution | 用材质/光效/分隔线替代真实信息组织 |

**修复顺序铁律**：
1. 先补 payload
2. 再补 support 与 context
3. 再校正 anchor 比例与位置
4. 最后调材质装饰

不得跳过前两步，不能用装饰调整掩盖内容合同缺失。

### 3.11 测试体系（新增）

参考 sunbigfly 的 `smoke_skill.py`，新建 `scripts/smoke_test.py`：

**测试覆盖**：
1. **风格定义校验**：26 个风格 JSON 是否完整（必填字段、CSS 变量、字体栈）
2. **风格 mock HTML 校验**：每个风格的 demo HTML 在 Puppeteer 中能正确渲染（无控制台错误）
3. **pipeline-compat 检查**：26 个 mock 不含 CSS 禁止清单中的特性（mask-image / background-clip:text / 伪元素装饰 / conic-gradient / border 三角形）
4. **图表组件渲染校验**：18-20 种图表的 HTML 模板能正确渲染
5. **端到端 PPT 生成**：选 3 个代表风格（dark_tech / mocha_editorial / vermilion_court），生成 5 页 demo PPT，验证 preview.html / svg/ / pptx 三种产物正确性
6. **失败模式自动检测**：扫描生成的 HTML 是否触发任何失败模式（如 underfill, decorative_substitution）

**用法**：
```bash
python3 scripts/smoke_test.py [--style <id>] [--phase 1-5]
```

**输出**：`tests/smoke-results/<timestamp>/report.md` 含通过率 + 失败详情 + 截图证据。

### 3.12 向后兼容保证

| 兼容点 | 策略 |
|--------|------|
| 8 个原 style_id | 全部保留并升级，不改 ID |
| 老用户已生成的 PPT | HTML 自包含，不受影响 |
| `style-system.md` 文件路径 | 保留为引导文件，内部 redirect 到新结构 |
| `prompts.md` 中的 Prompt #4 | 增量加字段，旧字段全部保留可用 |
| `bento-grid.md` / `pipeline-compat.md` | 完全不动 |
| `scripts/*.py` 三脚本 | 不动接口，gallery.py 是新增 |

---

## 4. 实施路线（高层级，详细计划由 writing-plans 生成）

**Phase 1：基础设施（先做，可独立验证）**
1. 写 `references/typography.md`（排版铁律）
2. 写 `references/principles/failure-modes.md`（8 种失败模式 + 修复顺序）
3. 写 `references/styles/index.md`（Schema + 决策矩阵 + 26 风格元数据表）
4. 写 1 个 pilot 风格的完整定义（建议 `dark_tech`）+ 1 个标杆 mock HTML
5. 写 `scripts/smoke_test.py` 骨架（可执行 Phase 1 的校验）
6. 跑 smoke test 验证 Phase 1 通过

**Phase 2：风格批量产出（按板块分批）**
5. 暗色专业 7 个 → `references/styles/dark.md` + 7 个 mock
6. 浅色高级 8 个 → `references/styles/light.md` + 8 个 mock
7. 活力鲜明 4 个 → `references/styles/vibrant.md` + 4 个 mock
8. 东方文化 3 个 → `references/styles/cultural.md` + 3 个 mock
9. 自然/复古 4 个 → `references/styles/natural.md` + 4 个 mock

每批完成后用户验收，再开下一批。

**Phase 3：图表系统**
10. 写 `references/charts/index.md`（决策矩阵）
11. 写 `references/charts/basic.md`（8 种重做）
12. 写 `references/charts/advanced.md`（6 种新增）
13. 写 `references/charts/complex.md`（4-6 种 ECharts 级）

**Phase 4：画廊与集成**
14. 写 `scripts/gallery.py`
15. 运行 gallery.py 生成全套预览
16. 更新 `SKILL.md` 引用
17. 更新 `README.md` / `README_EN.md` 加预览图
18. 改造 `style-system.md` 为引导文件

**Phase 5：验证**
19. 用 6 步 pipeline 端到端跑通 1 个新风格的 PPT（如 mocha_editorial）
20. 验证 SVG/PPTX 转换无偏移

---

## 5. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 26 风格质量难以保持一致 | Pilot 验收 + 按板块分批 + 每批样品先确认 |
| Google Fonts @import 影响渲染速度 | 字体按需加载（每个风格只加自己用到的） + 系统字体兜底 |
| ECharts 级复杂图表（如世界地图）实现困难 | 优先做 4-5 种最高 ROI 的，其他作为 v2 |
| 风格选择心智负担（26 个太多） | gallery.py 解决（视觉选择） + 决策矩阵（关键词→风格） |
| 新增字段破坏老 prompt | 所有新字段标可选，老风格 JSON 不强制升级 |
| 工程量大（约 9600 行）一次性提交难审 | 严格按 Phase + 板块分批，每批 1-3 PR |

---

## 6. 成功标准

- [ ] 26 风格全部可用，每个有完整 JSON + 标杆 mock + 决策矩阵条目
- [ ] 18-20 图表全部可用，每个有 HTML 模板 + 何时用 + 数据格式
- [ ] gallery.py 能一键生成 26 风格预览页 + 5 板块象限图
- [ ] 端到端验证：用 mocha_editorial 风格生成一份 5 页测试 PPT，preview.html / svg / pptx 三种产物都正确
- [ ] 老 8 个 style_id 在新系统下可正常调用（向后兼容验证）
- [ ] README 4-5 张象限图能直观展示风格风貌
- [ ] SKILL.md 主流程不变，文件改动 ≤ 30 行

---

## 7. 参考资源

**世界级品牌**：linear.app · anthropic.com · stripe.com · apple.com · openai.com · vercel.com · nytimes.com/magazine · pitch.com · mercury.com · arc.net · tomfordbeauty.com · notion.so

**Google Fonts 等价物**：Inter / Inter Tight / Source Serif 4 / Fraunces / Instrument Serif / Playfair Display / JetBrains Mono / Noto Serif SC / Quicksand

**GitHub 高星参考**：shadcn-ui/ui ⭐78k · tailwindlabs/tailwindcss ⭐82k · rsms/inter ⭐18k · vercel/geist-ui ⭐4.4k · catppuccin/catppuccin ⭐15k · system-fonts/modern-font-stacks ⭐10k · slidevjs/slidev ⭐35k · hakimel/reveal.js ⭐67k

**直接借鉴**：
- [sunbigfly/ppt-agent-skills](https://github.com/sunbigfly/ppt-agent-skills) — 引入了：
  - 风格 JSON 的 `mood_keywords` / `design_soul` / `variation_strategy` / `decoration_dna` 字段（§3.2）
  - `runtime-failure-modes` 失败模式目录（§3.10）
  - `smoke_skill.py` 端到端测试理念（§3.11）

---

## 8. 决策日志

| 决策 | 选择 | 备选 | 理由 |
|------|------|------|------|
| 风格数 | 26 | 12 / 14 / 18 | 用户明确要求扩展到 26 |
| 命名策略 | 8 原 ID 保留 + 18 新 ID | 全部新名 / 双向别名 | 用户选择保留原 ID 不动 |
| 图表数 | 18-20 + ECharts 级 | 8 / 14 | 用户选择最大范围 |
| 文件组织 | 按 5 板块分文件 | monolithic / 1 风格 1 文件 | 单文件过大；1 风格 1 文件上下文消耗大 |
| 风格画廊 | gallery.py + README 象限图 | 仅文字描述 | 用户明确要求生成预览 |
| 用户自定义风格 | 不做（YAGNI） | 加 plugin 机制 | 当前没有此明确需求 |
