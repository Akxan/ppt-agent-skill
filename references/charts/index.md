# 图表系统索引（18 种 / 3 层级）

> 所有图表纯 HTML/CSS/SVG 实现，**不引入 ECharts 等运行时**（幻灯片必须是静态 HTML）。模板只用保持矢量的写法，进 PPTX 后图形和数字都可编辑；标签用 HTML 元素叠在 SVG 上，不写 SVG `<text>`（见 [pipeline-compat.md](../pipeline-compat.md)）。

---

## 1. 18 种图表全景

策划稿里在卡片上写 `chart_type`，Step 5c 用 `scripts/resource_loader.py resolve` 取到对应模板。注册表在 `scripts/contracts.py` 的 `CHARTS`。

| # | 图表 | `chart_type` | 层级 | 文件 | 何时用 |
|---|------|--------------|------|------|-------|
| 1 | 进度条 | `progress_bar` | 基础 | [basic.md](basic.md) | 单一百分比 / 完成度 |
| 2 | 对比柱 | `comparison_bar` | 基础 | [basic.md](basic.md) | 2-6 项对比 |
| 3 | 环形图 | `ring` | 基础 | [basic.md](basic.md) | 百分比 + 中心 KPI |
| 4 | 迷你折线 | `sparkline` | 基础 | [basic.md](basic.md) | 趋势方向 |
| 5 | 点阵图 | `waffle` | 基础 | [basic.md](basic.md) | 比例直觉化（10×10）|
| 6 | KPI 指标卡 | `kpi` | 基础 | [basic.md](basic.md) | 大数字 + 趋势箭头 |
| 7 | 指标行 | `metric_row` | 基础 | [basic.md](basic.md) | 多指标垂直堆叠 |
| 8 | 评分指示器 | `rating` | 基础 | [basic.md](basic.md) | 5 分制 / 半星 |
| 9 | 雷达图 | `radar` | 进阶 | [advanced.md](advanced.md) | 多维度对比（5-8 维）|
| 10 | 时间线 | `timeline` | 进阶 | [advanced.md](advanced.md) | 历史 / 路线图 / 流程 |
| 11 | 漏斗图 | `funnel` | 进阶 | [advanced.md](advanced.md) | 转化率 / 流失分析 |
| 12 | 仪表盘 | `gauge` | 进阶 | [advanced.md](advanced.md) | KPI 评级 / 健康度 |
| 13 | 多组对比柱 | `grouped_bar` | 进阶 | [advanced.md](advanced.md) | 多类别 × 多组对比；堆叠变体写 `stacked_bar` 亦可 |
| 14 | 简单地理 | `simple_map` | 进阶 | [advanced.md](advanced.md) | 城市点 / 区域分布 |
| 15 | 世界地图 | `world_choropleth` | 复杂 | [complex.md](complex.md) | 全球数据可视化 |
| 16 | 关系网络 | `network_graph` | 复杂 | [complex.md](complex.md) | 节点 + 连线 |
| 17 | 桑基图 | `sankey_flow` | 复杂 | [complex.md](complex.md) | 流量 / 转化路径 |
| 18 | 热力日历 | `heatmap_calendar` | 复杂 | [complex.md](complex.md) | 365 天数据密度 |

模板标题里的旧叫法（`compare_bar` / `ring_chart` / `waffle_chart` / `kpi_card`）作为别名仍被接受。

---

## 2. 决策矩阵

按数据特征快速选图：

| 数据类型 | 推荐图表 | 备选 |
|---------|---------|------|
| 单一百分比 | 进度条 / 环形图 | KPI 指标卡 |
| 两项对比 | 对比柱 | 多组对比柱 |
| 3-8 个并列指标 | KPI 卡组 / 指标行 | 雷达图 |
| 多维度评估 | 雷达图 | 评分指示器 |
| 时间趋势 | 迷你折线 | 时间线 |
| 比例直觉化 | 点阵图 | 环形图 |
| 转化漏斗 | 漏斗图 | 桑基图 |
| KPI 评级（如健康度）| 仪表盘 | 评分指示器 |
| 多类别对比（如年度对比）| 多组对比柱 | — |
| 地理分布（中国/世界）| 简单地理 / 世界地图 | — |
| 关系网络（如组织架构）| 关系网络 | — |
| 复杂流量分析 | 桑基图 | 漏斗图 |
| 连续日期数据 | 热力日历 | 迷你折线 |

---

## 3. 图表通用规范

### 3.1 数据格式

所有图表的 HTML 模板都接受简单的 inline data，无运行时依赖。例如：

```html
<!-- 进度条 -->
<div class="chart-progress" data-value="87" data-label="完成度">
  <div class="bar"><div class="fill" style="width:87%"></div></div>
  <span class="value">87%</span>
</div>
```

### 3.2 颜色映射

所有图表必须用 CSS 变量 (`--accent-1`, `--accent-2`, etc.)，不硬编码颜色。这样 26 风格自动适配。

### 3.3 数字格式

所有数据数字必须 `font-variant-numeric: tabular-nums proportional-nums`。

### 3.4 SVG 内禁止 `<text>`

所有文字标注（数据标签、x 轴、图例、中心数字）用 HTML `<div>` / `<span>` 绝对定位叠加在 SVG 上方。

### 3.5 ECharts 兼容性

复杂图表（世界地图、关系网络、桑基图、热力日历）的实现策略：
- **不引入 ECharts 运行时**
- 用纯 SVG path 数据 + 静态计算
- 需要真实地理边界时，离线把 GeoJSON 简化成 SVG path 再内联

### 3.6 风格适配

每种图表在每个风格下应自动适配：
- 暗色风格：用 `--accent-1` 高亮主色，`--card-border` 做线条
- 浅色风格：用 `--accent-1` 描边，`--card-bg-from` 填充
- 文化风格（royal_red 等）：用 `--accent-1`（金色）+ `--accent-3`（朱红）双色调

### 3.7 自检清单

每个图表 HTML 模板自检：

- [ ] 用 CSS 变量，不硬编码颜色
- [ ] 数字 tabular-nums
- [ ] SVG 内无 `<text>`
- [ ] 不用 conic-gradient（环形图用 SVG circle + dasharray）
- [ ] 不用 mask-image / mix-blend-mode
- [ ] 至少有一个示例数据
