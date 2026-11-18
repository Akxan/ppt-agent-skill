# 复杂图表 (Complex Charts) — 4 种 ECharts 级可视化

> 本文档收录 4 种**世界级复杂图表**：世界地图 choropleth、关系网络、桑基图、热力日历。这些是 ECharts、D3、Datawrapper 的招牌图，但本项目要求**纯 SVG/HTML/CSS 实现，禁止 JavaScript 运行时**——以保持 `html2svg → svg2pptx` 管线零偏移。
>
> 复杂度通过**手工预算的几何 + SVG path + 大量 HTML 绝对定位标签**达成。每张图都是一次性数据快照（static），不支持交互/动画。
>
> **共同约束**（来自 [`pipeline-compat.md`](../pipeline-compat.md)）：
>
> - SVG 内**禁止 `<text>` 元素**——所有标签均用 HTML `<div>` / `<span>` 绝对定位叠加
> - 颜色全部 CSS 变量（`--accent-1` / `--accent-2` / `--card-border` ...），不硬编码
> - 数字开 `font-variant-numeric: tabular-nums`
> - 禁止 `conic-gradient` / `mask-image` / `mix-blend-mode` / `filter: blur()`（光栅化）
> - 禁止 JavaScript / `<script>` 标签
>
> 每张图的 HTML 模板可直接粘贴到任何风格（dark_tech / royal_red / minimal_gray ...），CSS 变量自动适配。

---

## 目录

| # | 图表 | chart_id | 何时用 |
|---|------|---------|-------|
| 15 | 世界地图 choropleth | `world_choropleth` | 全球数据可视化（按国家上色） |
| 16 | 关系网络 | `network_graph` | 节点 + 连线（组织架构 / 知识图谱） |
| 17 | 桑基图 | `sankey_flow` | 流量 / 转化路径 / 预算分配 |
| 18 | 热力日历 | `heatmap_calendar` | 365 天数据密度（贡献度 / DAU 历史） |

---

## 15. 世界地图 choropleth (`world_choropleth`)

**何时用**：

- 按国家展示一项指标（用户数 / 销售额 / GDP / 渗透率）
- 强调"全球"叙事（融资路演、年度报告、市场扩张计划）
- 数据点 ≥ 8 个国家、且分布在 ≥ 3 个大洲时（少于 3 个洲请用 KPI 卡组）

**数据格式**：

```json
{
  "metric": "月活跃用户 (MAU)",
  "unit": "万",
  "max": 4800,
  "regions": [
    {"id": "usa",       "name": "美国",   "value": 4800, "intensity": 1.00},
    {"id": "canada",    "name": "加拿大", "value":  720, "intensity": 0.18},
    {"id": "mexico",    "name": "墨西哥", "value":  410, "intensity": 0.12},
    {"id": "brazil",    "name": "巴西",   "value": 1850, "intensity": 0.42},
    {"id": "europe",    "name": "欧洲",   "value": 3200, "intensity": 0.72},
    {"id": "russia",    "name": "俄罗斯", "value":  280, "intensity": 0.10},
    {"id": "china",     "name": "中国",   "value": 4200, "intensity": 0.92},
    {"id": "india",     "name": "印度",   "value": 2400, "intensity": 0.55},
    {"id": "japan",     "name": "日本",   "value":  980, "intensity": 0.24},
    {"id": "sea",       "name": "东南亚", "value":  870, "intensity": 0.22},
    {"id": "australia", "name": "澳洲",   "value":  340, "intensity": 0.10},
    {"id": "africa",    "name": "非洲",   "value":  520, "intensity": 0.14}
  ]
}
```

`intensity` ∈ [0, 1] 是把 `value / max` 后**手工调过的**视觉强度（线性映射会让小国全部"灰掉"，常用 `Math.pow(value/max, 0.6)` 提亮中段）。

**HTML 模板**（完整可运行）：

```html
<div class="chart-world-choropleth" style="position:relative; width:100%; aspect-ratio: 16/9; padding: 24px 28px 56px;">

  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 8px;">
    <div>
      <div style="font-size:11px; letter-spacing:0.18em; text-transform:uppercase; color:var(--accent-1); font-weight:600;">— GLOBAL DISTRIBUTION</div>
      <div style="font-size:20px; font-weight:600; letter-spacing:-0.01em; color:var(--text-primary); margin-top:6px;">月活跃用户 (MAU)</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:32px; font-weight:700; letter-spacing:-0.02em; color:var(--text-primary); font-variant-numeric: tabular-nums;">2.46<span style="font-size:14px; color:var(--text-secondary); font-weight:500; margin-left:4px;">亿 / 月</span></div>
      <div style="font-size:11px; color:var(--text-secondary); letter-spacing:0.05em; margin-top:2px;">合计 12 个区域 · 2026Q1</div>
    </div>
  </div>

  <div style="position:relative; width:100%; height:78%;">
    <svg viewBox="0 0 1000 500" preserveAspectRatio="xMidYMid meet" style="width:100%; height:100%; display:block;">
      <defs>
        <pattern id="wm-grid" x="0" y="0" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="var(--card-border)" stroke-width="0.4" opacity="0.18"/>
        </pattern>
      </defs>
      <rect x="0" y="0" width="1000" height="500" fill="url(#wm-grid)"/>

      <path d="M 60 110 L 120 92 L 200 96 L 260 108 L 280 142 L 240 178 L 180 196 L 130 184 L 95 168 L 70 144 Z"
            fill="var(--accent-1)" fill-opacity="1.00" stroke="var(--card-border)" stroke-width="0.8"/>
      <path d="M 70 60 L 180 48 L 290 52 L 320 78 L 280 104 L 200 92 L 130 88 L 80 92 L 60 78 Z"
            fill="var(--accent-1)" fill-opacity="0.18" stroke="var(--card-border)" stroke-width="0.8"/>
      <path d="M 130 200 L 200 196 L 250 218 L 232 252 L 178 268 L 138 248 L 122 220 Z"
            fill="var(--accent-1)" fill-opacity="0.12" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 270 280 L 320 268 L 360 290 L 380 340 L 372 396 L 332 420 L 290 412 L 268 372 L 254 326 Z"
            fill="var(--accent-1)" fill-opacity="0.42" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 460 100 L 510 88 L 560 96 L 588 116 L 580 142 L 530 152 L 480 144 L 452 126 Z"
            fill="var(--accent-1)" fill-opacity="0.72" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 580 70 L 720 60 L 850 70 L 920 92 L 880 122 L 760 118 L 660 110 L 590 96 Z"
            fill="var(--accent-1)" fill-opacity="0.10" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 720 152 L 800 142 L 858 168 L 870 210 L 832 244 L 776 240 L 728 218 L 712 184 Z"
            fill="var(--accent-1)" fill-opacity="0.92" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 660 230 L 720 224 L 752 252 L 740 296 L 692 308 L 660 282 L 650 252 Z"
            fill="var(--accent-1)" fill-opacity="0.55" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 870 178 L 906 172 L 920 198 L 906 220 L 878 218 L 866 198 Z"
            fill="var(--accent-1)" fill-opacity="0.24" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 780 270 L 832 264 L 858 290 L 842 320 L 800 322 L 776 298 Z"
            fill="var(--accent-1)" fill-opacity="0.22" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 838 360 L 900 350 L 932 374 L 916 408 L 868 416 L 838 392 Z"
            fill="var(--accent-1)" fill-opacity="0.10" stroke="var(--card-border)" stroke-width="0.8"/>

      <path d="M 480 200 L 540 192 L 590 208 L 612 252 L 600 320 L 562 372 L 520 388 L 478 364 L 458 312 L 462 252 Z"
            fill="var(--accent-1)" fill-opacity="0.14" stroke="var(--card-border)" stroke-width="0.8"/>
    </svg>

    <div style="position:absolute; left:14.5%; top:30%; transform:translate(-50%,-50%); text-align:center; pointer-events:none;">
      <div style="font-size:11px; font-weight:700; color:var(--text-primary); letter-spacing:0.04em; text-shadow:0 1px 2px rgba(0,0,0,0.4);">USA</div>
      <div style="font-size:13px; font-weight:700; color:var(--accent-1); font-variant-numeric: tabular-nums; letter-spacing:-0.01em; margin-top:1px;">4 800</div>
    </div>
    <div style="position:absolute; left:17%; top:14%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:10px; color:var(--text-secondary); letter-spacing:0.04em;">Canada</div>
      <div style="font-size:11px; font-weight:600; color:var(--text-primary); font-variant-numeric: tabular-nums;">720</div>
    </div>
    <div style="position:absolute; left:18.5%; top:46%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:10px; color:var(--text-secondary);">Mexico</div>
      <div style="font-size:11px; font-weight:600; color:var(--text-primary); font-variant-numeric: tabular-nums;">410</div>
    </div>

    <div style="position:absolute; left:32.5%; top:69%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:11px; font-weight:700; color:var(--text-primary); letter-spacing:0.04em;">Brazil</div>
      <div style="font-size:12px; font-weight:700; color:var(--accent-1); font-variant-numeric: tabular-nums;">1 850</div>
    </div>

    <div style="position:absolute; left:52%; top:24%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:11px; font-weight:700; color:var(--text-primary); letter-spacing:0.04em;">Europe</div>
      <div style="font-size:13px; font-weight:700; color:var(--accent-1); font-variant-numeric: tabular-nums;">3 200</div>
    </div>

    <div style="position:absolute; left:74%; top:18%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:10px; color:var(--text-secondary);">Russia</div>
      <div style="font-size:11px; font-weight:600; color:var(--text-primary); font-variant-numeric: tabular-nums;">280</div>
    </div>

    <div style="position:absolute; left:79%; top:39%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:11px; font-weight:700; color:var(--text-primary); letter-spacing:0.04em;">China</div>
      <div style="font-size:13px; font-weight:700; color:var(--accent-1); font-variant-numeric: tabular-nums;">4 200</div>
    </div>

    <div style="position:absolute; left:70.5%; top:54%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:11px; font-weight:700; color:var(--text-primary);">India</div>
      <div style="font-size:12px; font-weight:700; color:var(--accent-1); font-variant-numeric: tabular-nums;">2 400</div>
    </div>

    <div style="position:absolute; left:89%; top:39%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:10px; color:var(--text-secondary);">Japan</div>
      <div style="font-size:11px; font-weight:600; color:var(--text-primary); font-variant-numeric: tabular-nums;">980</div>
    </div>

    <div style="position:absolute; left:81%; top:59%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:10px; color:var(--text-secondary);">SEA</div>
      <div style="font-size:11px; font-weight:600; color:var(--text-primary); font-variant-numeric: tabular-nums;">870</div>
    </div>

    <div style="position:absolute; left:88.5%; top:78%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:10px; color:var(--text-secondary);">Australia</div>
      <div style="font-size:11px; font-weight:600; color:var(--text-primary); font-variant-numeric: tabular-nums;">340</div>
    </div>

    <div style="position:absolute; left:53%; top:58%; transform:translate(-50%,-50%); text-align:center;">
      <div style="font-size:10px; color:var(--text-secondary);">Africa</div>
      <div style="font-size:11px; font-weight:600; color:var(--text-primary); font-variant-numeric: tabular-nums;">520</div>
    </div>
  </div>

  <div style="position:absolute; left:28px; bottom:14px; right:28px; display:flex; align-items:center; gap:14px;">
    <span style="font-size:10px; letter-spacing:0.12em; color:var(--text-secondary); text-transform:uppercase;">Less</span>
    <div style="display:flex; flex:1; height:8px; border-radius:2px; overflow:hidden;">
      <div style="flex:1; background:var(--accent-1); opacity:0.10;"></div>
      <div style="flex:1; background:var(--accent-1); opacity:0.28;"></div>
      <div style="flex:1; background:var(--accent-1); opacity:0.50;"></div>
      <div style="flex:1; background:var(--accent-1); opacity:0.75;"></div>
      <div style="flex:1; background:var(--accent-1); opacity:1.00;"></div>
    </div>
    <span style="font-size:10px; letter-spacing:0.12em; color:var(--text-secondary); text-transform:uppercase;">More</span>
    <span style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums; margin-left:8px;">0 — 4 800 万</span>
  </div>

</div>
```

**实现要点**：

- **路径数据是手工简化的多边形**（每个区域 6-12 个点），目的不是地理精度而是视觉可识别度。如果需要真实 GeoJSON，建议用 Natural Earth Low Res + `topojson-simplify` 离线生成 path 后内联。本模板的 viewBox 是 `1000 × 500`（Equirectangular 风格），便于经纬度的线性映射。
- **`fill-opacity` 即数据值**——直接把 `intensity ∈ [0, 1]` 写到 `fill-opacity` 属性。所有 path 用同一个 `fill="var(--accent-1)"`，颜色随风格自动切换。
- **标签是 HTML 绝对定位**（百分比坐标），不在 SVG 内。重要国家（intensity ≥ 0.4）显示数字；次要国家只显示名字 + 数字。中国 / 美国 / 巴西 / 印度 / 欧洲 5 个 hero 标签**字号加大、颜色用 accent**——剩下的退到 secondary，避免视觉过载。
- **网格底**用 `<pattern id="wm-grid">` 做经纬线，50×50 单位、stroke 0.4 / opacity 0.18，给地图垫一层"地理感"，否则光看色块像马赛克。
- **图例 5 段**对应 `[0.10, 0.28, 0.50, 0.75, 1.00]`——这些不是均分的而是感知校准过的（人眼对 opacity < 0.3 的差异不敏感，所以低段密集、高段稀疏）。

**自检**：

- [ ] 12 个 path 的 `fill-opacity` 与数据 `intensity` 一一对应
- [ ] 所有标签都是 HTML `<div>`，**SVG 内零 `<text>`**
- [ ] 数字开 `font-variant-numeric: tabular-nums`
- [ ] 标签的 `left` / `top` 是百分比（响应式），不是 px
- [ ] 图例 5 段 + Less/More + 数值范围都齐全
- [ ] hero 国家（数值最大的 4-5 个）字号大一档、颜色用 `--accent-1`

**未来扩展（v2）**：

- 真实国家轮廓：写一个离线脚本从 Natural Earth GeoJSON 简化（`topojson-simplify -s 0.5`）后批量生成 path，替换内联的 12 个简化形状
- 双色映射（如"增长 vs 下滑"用 `--accent-1` / `--accent-3` 分流）
- Bubble overlay：在 choropleth 上叠加按城市的圆点（用 SVG `<circle>` + HTML 数字标签）

---

## 16. 关系网络 (`network_graph`)

**何时用**：

- 组织架构图（CEO → C-suite → 团队）
- 知识图谱 / 概念关系（5-12 个节点最佳）
- 投资组合关系网（基金 → 被投公司 → 退出渠道）
- 数据血缘（source → ETL → mart → BI）

**节点数 > 12 时不要用本模板**——人眼解析连线的极限就是 12 个节点 / 18 条边。改用桑基图或层级树。

**数据格式**：

```json
{
  "title": "组织架构 · 2026Q2",
  "nodes": [
    {"id": "ceo",  "label": "CEO",         "x": 50, "y": 16, "size": "lg", "tier": 1},
    {"id": "cto",  "label": "CTO",         "x": 22, "y": 42, "size": "md", "tier": 2},
    {"id": "cfo",  "label": "CFO",         "x": 50, "y": 42, "size": "md", "tier": 2},
    {"id": "cmo",  "label": "CMO",         "x": 78, "y": 42, "size": "md", "tier": 2},
    {"id": "eng1", "label": "Platform",    "x": 10, "y": 74, "size": "sm", "tier": 3},
    {"id": "eng2", "label": "AI / ML",     "x": 28, "y": 80, "size": "sm", "tier": 3},
    {"id": "fin",  "label": "FP & A",      "x": 46, "y": 76, "size": "sm", "tier": 3},
    {"id": "ops",  "label": "Ops",         "x": 60, "y": 80, "size": "sm", "tier": 3},
    {"id": "grw",  "label": "Growth",      "x": 74, "y": 76, "size": "sm", "tier": 3},
    {"id": "br",   "label": "Brand",       "x": 90, "y": 80, "size": "sm", "tier": 3}
  ],
  "edges": [
    {"from": "ceo", "to": "cto"}, {"from": "ceo", "to": "cfo"}, {"from": "ceo", "to": "cmo"},
    {"from": "cto", "to": "eng1"}, {"from": "cto", "to": "eng2"},
    {"from": "cfo", "to": "fin"}, {"from": "cfo", "to": "ops"},
    {"from": "cmo", "to": "grw"}, {"from": "cmo", "to": "br"}
  ]
}
```

`x` / `y` 是 0-100 百分比坐标，**手工预算**（模拟 force-directed 收敛后的稳定布局）——把它当成"静态截图"，没有 JS 跑物理模拟。

**HTML 模板**（完整可运行）：

```html
<div class="chart-network" style="position:relative; width:100%; aspect-ratio: 16/9; padding: 28px 32px; overflow:hidden;">

  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 12px;">
    <div>
      <div style="font-size:11px; letter-spacing:0.18em; text-transform:uppercase; color:var(--accent-1); font-weight:600;">— ORG STRUCTURE</div>
      <div style="font-size:20px; font-weight:600; letter-spacing:-0.01em; color:var(--text-primary); margin-top:6px;">组织架构图 · 10 个核心节点</div>
    </div>
    <div style="display:flex; gap:14px; align-items:center; font-size:11px; color:var(--text-secondary); letter-spacing:0.04em;">
      <span style="display:inline-flex; align-items:center; gap:6px;"><span style="width:14px;height:14px;border-radius:50%;background:var(--accent-1);box-shadow:0 0 8px var(--accent-1);"></span>Tier 1</span>
      <span style="display:inline-flex; align-items:center; gap:6px;"><span style="width:11px;height:11px;border-radius:50%;background:var(--accent-2);"></span>Tier 2</span>
      <span style="display:inline-flex; align-items:center; gap:6px;"><span style="width:8px;height:8px;border-radius:50%;background:var(--text-secondary); opacity:0.6;"></span>Tier 3</span>
    </div>
  </div>

  <div style="position:relative; width:100%; height:88%;">

    <svg viewBox="0 0 1000 500" preserveAspectRatio="none" style="position:absolute; inset:0; width:100%; height:100%;">
      <line x1="500" y1="80"  x2="220" y2="210" stroke="var(--accent-1)" stroke-width="1.6" stroke-opacity="0.55"/>
      <line x1="500" y1="80"  x2="500" y2="210" stroke="var(--accent-1)" stroke-width="1.6" stroke-opacity="0.55"/>
      <line x1="500" y1="80"  x2="780" y2="210" stroke="var(--accent-1)" stroke-width="1.6" stroke-opacity="0.55"/>

      <line x1="220" y1="210" x2="100" y2="370" stroke="var(--accent-2)" stroke-width="1.2" stroke-opacity="0.40"/>
      <line x1="220" y1="210" x2="280" y2="400" stroke="var(--accent-2)" stroke-width="1.2" stroke-opacity="0.40"/>

      <line x1="500" y1="210" x2="460" y2="380" stroke="var(--accent-2)" stroke-width="1.2" stroke-opacity="0.40"/>
      <line x1="500" y1="210" x2="600" y2="400" stroke="var(--accent-2)" stroke-width="1.2" stroke-opacity="0.40"/>

      <line x1="780" y1="210" x2="740" y2="380" stroke="var(--accent-2)" stroke-width="1.2" stroke-opacity="0.40"/>
      <line x1="780" y1="210" x2="900" y2="400" stroke="var(--accent-2)" stroke-width="1.2" stroke-opacity="0.40"/>

      <circle cx="500" cy="80"  r="34" fill="var(--accent-1)" fill-opacity="0.10" stroke="var(--accent-1)" stroke-width="0.6" stroke-opacity="0.4"/>
      <circle cx="220" cy="210" r="26" fill="var(--accent-2)" fill-opacity="0.08" stroke="var(--accent-2)" stroke-width="0.5" stroke-opacity="0.4"/>
      <circle cx="500" cy="210" r="26" fill="var(--accent-2)" fill-opacity="0.08" stroke="var(--accent-2)" stroke-width="0.5" stroke-opacity="0.4"/>
      <circle cx="780" cy="210" r="26" fill="var(--accent-2)" fill-opacity="0.08" stroke="var(--accent-2)" stroke-width="0.5" stroke-opacity="0.4"/>
    </svg>

    <div style="position:absolute; left:50%; top:16%; transform:translate(-50%,-50%); width:64px; height:64px; border-radius:50%; background:linear-gradient(135deg, var(--accent-1), var(--accent-2)); display:flex; align-items:center; justify-content:center; box-shadow: 0 6px 24px rgba(0,0,0,0.18), 0 0 0 4px var(--card-bg-from);">
      <div style="text-align:center;">
        <div style="font-size:12px; font-weight:700; color:#fff; letter-spacing:0.05em;">CEO</div>
        <div style="font-size:9px; color:rgba(255,255,255,0.85); letter-spacing:0.08em; margin-top:1px;">Tier 1</div>
      </div>
    </div>

    <div style="position:absolute; left:22%; top:42%; transform:translate(-50%,-50%); width:48px; height:48px; border-radius:50%; background:var(--card-bg-from); border:1.5px solid var(--accent-2); display:flex; align-items:center; justify-content:center;">
      <span style="font-size:11px; font-weight:700; color:var(--text-primary); letter-spacing:0.04em;">CTO</span>
    </div>
    <div style="position:absolute; left:50%; top:42%; transform:translate(-50%,-50%); width:48px; height:48px; border-radius:50%; background:var(--card-bg-from); border:1.5px solid var(--accent-2); display:flex; align-items:center; justify-content:center;">
      <span style="font-size:11px; font-weight:700; color:var(--text-primary); letter-spacing:0.04em;">CFO</span>
    </div>
    <div style="position:absolute; left:78%; top:42%; transform:translate(-50%,-50%); width:48px; height:48px; border-radius:50%; background:var(--card-bg-from); border:1.5px solid var(--accent-2); display:flex; align-items:center; justify-content:center;">
      <span style="font-size:11px; font-weight:700; color:var(--text-primary); letter-spacing:0.04em;">CMO</span>
    </div>

    <div style="position:absolute; left:10%; top:74%; transform:translate(-50%,-50%); display:flex; flex-direction:column; align-items:center; gap:4px;">
      <div style="width:32px; height:32px; border-radius:50%; background:var(--card-bg-to); border:1px solid var(--card-border);"></div>
      <span style="font-size:10px; color:var(--text-secondary); letter-spacing:0.04em;">Platform</span>
    </div>
    <div style="position:absolute; left:28%; top:80%; transform:translate(-50%,-50%); display:flex; flex-direction:column; align-items:center; gap:4px;">
      <div style="width:32px; height:32px; border-radius:50%; background:var(--card-bg-to); border:1px solid var(--card-border);"></div>
      <span style="font-size:10px; color:var(--text-secondary);">AI / ML</span>
    </div>
    <div style="position:absolute; left:46%; top:76%; transform:translate(-50%,-50%); display:flex; flex-direction:column; align-items:center; gap:4px;">
      <div style="width:32px; height:32px; border-radius:50%; background:var(--card-bg-to); border:1px solid var(--card-border);"></div>
      <span style="font-size:10px; color:var(--text-secondary);">FP &amp; A</span>
    </div>
    <div style="position:absolute; left:60%; top:80%; transform:translate(-50%,-50%); display:flex; flex-direction:column; align-items:center; gap:4px;">
      <div style="width:32px; height:32px; border-radius:50%; background:var(--card-bg-to); border:1px solid var(--card-border);"></div>
      <span style="font-size:10px; color:var(--text-secondary);">Ops</span>
    </div>
    <div style="position:absolute; left:74%; top:76%; transform:translate(-50%,-50%); display:flex; flex-direction:column; align-items:center; gap:4px;">
      <div style="width:32px; height:32px; border-radius:50%; background:var(--card-bg-to); border:1px solid var(--card-border);"></div>
      <span style="font-size:10px; color:var(--text-secondary);">Growth</span>
    </div>
    <div style="position:absolute; left:90%; top:80%; transform:translate(-50%,-50%); display:flex; flex-direction:column; align-items:center; gap:4px;">
      <div style="width:32px; height:32px; border-radius:50%; background:var(--card-bg-to); border:1px solid var(--card-border);"></div>
      <span style="font-size:10px; color:var(--text-secondary);">Brand</span>
    </div>

  </div>
</div>
```

**实现要点**：

- **节点位置全部手工预算**——本模板没有 JS 跑 d3-force。把节点想象成"已经收敛好的截图"，把 x/y 直接编进 HTML。规则：tier 1 居中靠上、tier 2 横向均分中部、tier 3 散布底部。每个节点之间至少留 8% 横向间距，否则视觉拥挤。
- **连线是 SVG `<line>`**（不是 `<path>`），因为直线没必要 Bezier。坐标系用固定 viewBox `1000 × 500`，节点中心点要换算成 viewBox 单位（HTML 用 50% / SVG 用 500），所以 SVG 用 `preserveAspectRatio="none"` 让坐标线性拉伸——HTML 节点（百分比定位）和 SVG 连线（绝对坐标）才能精确对齐。
- **节点视觉分层**：
  - Tier 1（CEO）：64px gradient 圆 + 4px 光晕外环（用 `box-shadow: 0 0 0 4px`，**不用 filter:blur**）
  - Tier 2（C-suite）：48px 边框圆 + 文字
  - Tier 3（团队）：32px 半透明圆 + 下方文字标签（避免文字挤进小圆）
- **连线分两层**：tier1→tier2 用 `--accent-1` 1.6px 粗、tier2→tier3 用 `--accent-2` 1.2px 细，并降 opacity——视觉自然形成"主干粗、支干细"的层级。
- **不用箭头标记**（`<marker>`）——svg2pptx 对 marker 支持差，组织架构靠位置上下关系暗示流向就够了。

**自检**：

- [ ] 节点之间无重叠（横向 ≥ 8%、纵向 ≥ 12% 间距）
- [ ] 连线的 SVG 坐标 = HTML 百分比 × viewBox 尺寸（500/250 = 50%）
- [ ] SVG 用 `preserveAspectRatio="none"` 才能和 HTML 百分比对齐
- [ ] SVG 内零 `<text>`，所有标签是 HTML
- [ ] tier 1 / 2 / 3 视觉层级清晰（大小、颜色、粗细全都有差异）

**未来扩展（v2）**：

- 节点数 > 8 时建议用 Python 的 `networkx.spring_layout()` **离线**算一遍 force-directed，再把收敛后的坐标 dump 到 JSON、模板里读。
- 加入"边权重"——`<line stroke-width>` 与边的 weight 成正比
- 双向边用 SVG `<path>` 微弯（控制点偏移 8-12 单位），避免双向箭头视觉重叠

---

## 17. 桑基图 (`sankey_flow`)

**何时用**：

- SaaS 转化漏斗（Marketing → Trial → Paid → Renewed），需要看每一步的**多分支流向**而非单一漏斗
- 预算分配（总预算 → 部门 → 项目）
- 用户来源 → 落地页 → 行为路径
- 能源流向、流量构成

漏斗图（Funnel）只能表达单线性收窄；桑基图能表达**多入多出**且每条流的宽度都按数值精确分配。

**数据格式**：

```json
{
  "title": "SaaS 转化路径 · 2026Q1",
  "unit": "用户数",
  "columns": [
    {"id": "src", "label": "Source", "nodes": [
      {"id": "paid",   "label": "付费广告",  "value": 12000},
      {"id": "organic","label": "自然搜索",  "value":  8000},
      {"id": "referral","label":"推荐",     "value":  4000}
    ]},
    {"id": "trial", "label": "Trial", "nodes": [
      {"id": "trial7",  "label": "7-day Trial",  "value": 14000},
      {"id": "demo",    "label": "Demo Booked",  "value":  6000},
      {"id": "drop1",   "label": "未激活",       "value":  4000}
    ]},
    {"id": "paid_stage", "label": "Paid", "nodes": [
      {"id": "starter", "label": "Starter $29",  "value":  6800},
      {"id": "pro",     "label": "Pro $99",      "value":  3200},
      {"id": "drop2",   "label": "Trial 流失",   "value": 10000}
    ]},
    {"id": "outcome", "label": "12-mo Outcome", "nodes": [
      {"id": "renew",   "label": "续约",         "value":  7600},
      {"id": "churn",   "label": "流失",         "value":  2400}
    ]}
  ],
  "flows": [
    {"from":"paid",     "to":"trial7",  "value": 8000},
    {"from":"paid",     "to":"demo",    "value": 3000},
    {"from":"paid",     "to":"drop1",   "value": 1000},
    {"from":"organic",  "to":"trial7",  "value": 4500},
    {"from":"organic",  "to":"demo",    "value": 2500},
    {"from":"organic",  "to":"drop1",   "value": 1000},
    {"from":"referral", "to":"trial7",  "value": 1500},
    {"from":"referral", "to":"demo",    "value":  500},
    {"from":"referral", "to":"drop1",   "value": 2000},

    {"from":"trial7",   "to":"starter", "value": 4800},
    {"from":"trial7",   "to":"pro",     "value": 2200},
    {"from":"trial7",   "to":"drop2",   "value": 7000},
    {"from":"demo",     "to":"starter", "value": 2000},
    {"from":"demo",     "to":"pro",     "value": 1000},
    {"from":"demo",     "to":"drop2",   "value": 3000},

    {"from":"starter",  "to":"renew",   "value": 5000},
    {"from":"starter",  "to":"churn",   "value": 1800},
    {"from":"pro",      "to":"renew",   "value": 2600},
    {"from":"pro",      "to":"churn",   "value":  600}
  ]
}
```

**HTML 模板**（完整可运行 · 4 列简化版）：

```html
<div class="chart-sankey" style="position:relative; width:100%; aspect-ratio: 16/9; padding: 28px 36px;">

  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 14px;">
    <div>
      <div style="font-size:11px; letter-spacing:0.18em; text-transform:uppercase; color:var(--accent-1); font-weight:600;">— CONVERSION FLOW</div>
      <div style="font-size:20px; font-weight:600; letter-spacing:-0.01em; color:var(--text-primary); margin-top:6px;">SaaS 用户转化路径 · Q1 2026</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:28px; font-weight:700; letter-spacing:-0.02em; color:var(--text-primary); font-variant-numeric: tabular-nums;">24 000<span style="font-size:13px; color:var(--text-secondary); font-weight:500; margin-left:6px;">访客 → 7 600 续约</span></div>
      <div style="font-size:11px; color:var(--text-secondary); letter-spacing:0.05em; margin-top:2px;">总转化率 31.7%</div>
    </div>
  </div>

  <div style="position:relative; width:100%; height:80%;">

    <div style="position:absolute; top:-18px; left:0; right:0; display:grid; grid-template-columns: repeat(4, 1fr); font-size:10px; letter-spacing:0.15em; color:var(--text-secondary); text-transform:uppercase; font-weight:600;">
      <div style="text-align:left; padding-left:4px;">— Source</div>
      <div style="text-align:center;">— Trial</div>
      <div style="text-align:center;">— Paid</div>
      <div style="text-align:right; padding-right:4px;">12-mo Outcome —</div>
    </div>

    <svg viewBox="0 0 1000 500" preserveAspectRatio="none" style="position:absolute; inset:0; width:100%; height:100%;">

      <path d="M 80,40 C 280,40 100,150 320,150" stroke="var(--accent-1)" stroke-width="62" stroke-opacity="0.42" fill="none" stroke-linecap="butt"/>
      <path d="M 80,135 C 280,135 100,255 320,255" stroke="var(--accent-1)" stroke-width="22" stroke-opacity="0.42" fill="none"/>
      <path d="M 80,180 C 280,180 100,360 320,360" stroke="var(--accent-2)" stroke-width="8" stroke-opacity="0.30" fill="none"/>

      <path d="M 80,260 C 280,260 100,170 320,170" stroke="var(--accent-1)" stroke-width="35" stroke-opacity="0.42" fill="none"/>
      <path d="M 80,315 C 280,315 100,275 320,275" stroke="var(--accent-1)" stroke-width="20" stroke-opacity="0.42" fill="none"/>
      <path d="M 80,355 C 280,355 100,365 320,365" stroke="var(--accent-2)" stroke-width="8" stroke-opacity="0.30" fill="none"/>

      <path d="M 80,420 C 280,420 100,200 320,200" stroke="var(--accent-1)" stroke-width="12" stroke-opacity="0.42" fill="none"/>
      <path d="M 80,438 C 280,438 100,290 320,290" stroke="var(--accent-1)" stroke-width="4" stroke-opacity="0.42" fill="none"/>
      <path d="M 80,455 C 280,455 100,375 320,375" stroke="var(--accent-2)" stroke-width="16" stroke-opacity="0.30" fill="none"/>

      <path d="M 360,135 C 540,135 380,80  600,80"  stroke="var(--accent-1)" stroke-width="36" stroke-opacity="0.42" fill="none"/>
      <path d="M 360,170 C 540,170 380,180 600,180" stroke="var(--accent-1)" stroke-width="18" stroke-opacity="0.42" fill="none"/>
      <path d="M 360,225 C 540,225 380,335 600,335" stroke="var(--accent-3)" stroke-width="56" stroke-opacity="0.28" fill="none"/>

      <path d="M 360,275 C 540,275 380,128 600,128" stroke="var(--accent-1)" stroke-width="16" stroke-opacity="0.42" fill="none"/>
      <path d="M 360,300 C 540,300 380,210 600,210" stroke="var(--accent-1)" stroke-width="9"  stroke-opacity="0.42" fill="none"/>
      <path d="M 360,330 C 540,330 380,395 600,395" stroke="var(--accent-3)" stroke-width="24" stroke-opacity="0.28" fill="none"/>

      <path d="M 640,80  C 820,80  660,90  880,90"  stroke="var(--accent-1)" stroke-width="40" stroke-opacity="0.45" fill="none"/>
      <path d="M 640,135 C 820,135 660,200 880,200" stroke="var(--accent-3)" stroke-width="16" stroke-opacity="0.32" fill="none"/>
      <path d="M 640,180 C 820,180 660,135 880,135" stroke="var(--accent-1)" stroke-width="22" stroke-opacity="0.45" fill="none"/>
      <path d="M 640,210 C 820,210 660,225 880,225" stroke="var(--accent-3)" stroke-width="6"  stroke-opacity="0.32" fill="none"/>

      <rect x="68" y="14"  width="14" height="56" rx="2" fill="var(--accent-1)" fill-opacity="0.85"/>
      <rect x="68" y="120" width="14" height="42" rx="2" fill="var(--accent-1)" fill-opacity="0.7"/>
      <rect x="68" y="172" width="14" height="22" rx="2" fill="var(--accent-1)" fill-opacity="0.6"/>

      <rect x="318" y="100" width="14" height="100" rx="2" fill="var(--accent-1)" fill-opacity="0.85"/>
      <rect x="318" y="220" width="14" height="48"  rx="2" fill="var(--accent-1)" fill-opacity="0.7"/>
      <rect x="318" y="320" width="14" height="80"  rx="2" fill="var(--accent-3)" fill-opacity="0.55"/>

      <rect x="598" y="40"  width="14" height="80"  rx="2" fill="var(--accent-1)" fill-opacity="0.85"/>
      <rect x="598" y="150" width="14" height="46"  rx="2" fill="var(--accent-1)" fill-opacity="0.7"/>
      <rect x="598" y="280" width="14" height="120" rx="2" fill="var(--accent-3)" fill-opacity="0.55"/>

      <rect x="878" y="50"  width="14" height="100" rx="2" fill="var(--accent-1)" fill-opacity="0.85"/>
      <rect x="878" y="180" width="14" height="68"  rx="2" fill="var(--accent-3)" fill-opacity="0.55"/>
    </svg>

    <div style="position:absolute; left:0; top:6%; font-size:11px;"><div style="font-weight:600; color:var(--text-primary);">付费广告</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">12 000</div></div>
    <div style="position:absolute; left:0; top:26%; font-size:11px;"><div style="font-weight:600; color:var(--text-primary);">自然搜索</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">8 000</div></div>
    <div style="position:absolute; left:0; top:42%; font-size:11px;"><div style="font-weight:600; color:var(--text-primary);">推荐</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">4 000</div></div>

    <div style="position:absolute; left:34%; top:18%; font-size:11px; transform:translateX(-50%); text-align:center;"><div style="font-weight:600; color:var(--text-primary);">7-day Trial</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">14 000</div></div>
    <div style="position:absolute; left:34%; top:46%; font-size:11px; transform:translateX(-50%); text-align:center;"><div style="font-weight:600; color:var(--text-primary);">Demo Booked</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">6 000</div></div>
    <div style="position:absolute; left:34%; top:70%; font-size:11px; transform:translateX(-50%); text-align:center;"><div style="font-weight:600; color:var(--text-secondary); opacity:0.7;">未激活</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">4 000</div></div>

    <div style="position:absolute; left:64%; top:8%;  font-size:11px; transform:translateX(-50%); text-align:center;"><div style="font-weight:600; color:var(--text-primary);">Starter $29</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">6 800</div></div>
    <div style="position:absolute; left:64%; top:28%; font-size:11px; transform:translateX(-50%); text-align:center;"><div style="font-weight:600; color:var(--text-primary);">Pro $99</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">3 200</div></div>
    <div style="position:absolute; left:64%; top:60%; font-size:11px; transform:translateX(-50%); text-align:center;"><div style="font-weight:600; color:var(--text-secondary); opacity:0.7;">Trial 流失</div><div style="font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">10 000</div></div>

    <div style="position:absolute; right:0; top:12%; font-size:12px; text-align:right;"><div style="font-weight:700; color:var(--accent-1);">续约</div><div style="font-size:11px; color:var(--text-primary); font-variant-numeric:tabular-nums; font-weight:600;">7 600</div></div>
    <div style="position:absolute; right:0; top:38%; font-size:12px; text-align:right;"><div style="font-weight:700; color:var(--text-secondary);">流失</div><div style="font-size:11px; color:var(--text-primary); font-variant-numeric:tabular-nums; font-weight:600;">2 400</div></div>

  </div>
</div>
```

**实现要点**：

- **流条用 SVG `<path>` 不是 `<polygon>`**——桑基的招牌是平滑 S 曲线（cubic Bezier），写法 `M startX,startY C cp1X,cp1Y cp2X,cp2Y endX,endY`，两个控制点 X 都设在两端 X 的 30%/70% 处，Y 与端点齐。
- **流条宽度 = `stroke-width`**——把 path 当宽线条画，**不**用闭合多边形 fill。stroke-width 直接 = value × scale（本例 scale ≈ 0.005，12000 → ~60px）。这是桑基图最优雅的实现方式。
- **流条颜色双轨**：成功流（trial → paid → renew）用 `--accent-1`；流失/放弃流（drop1 / drop2 / churn）用 `--accent-3` 或同色低 opacity。视觉一眼区分"健康路径"vs"流失"。
- **节点用窄 `<rect>`**（14px 宽 × 节点 value 高度），紧贴流条起点/终点。节点 fill 与流条同色但 opacity 高一档（0.85 vs 0.42），形成"实柱 + 透明流"的桑基标志性外观。
- **节点高度 = sum(出流) = sum(入流)**——这是桑基的守恒定律。手算 value 时一定要平衡上下游，否则视觉错位。本例：trial7 (14000) = 8000+4500+1500（in） = 4800+2200+7000（out）。
- **`stroke-linecap="butt"`**（默认即可）——`round` 会让流条端头超出节点矩形，破坏对齐。

**自检**：

- [ ] 每个节点的入流总和 = 出流总和（守恒）
- [ ] 流条 stroke-width 与 value 成线性比例
- [ ] 成功 vs 流失流的颜色区分明显（accent-1 vs accent-3）
- [ ] 节点矩形高度与该节点的 value 成比例
- [ ] SVG 用 `preserveAspectRatio="none"` + 固定 viewBox 才能和 HTML 标签对齐
- [ ] SVG 内零 `<text>`

**未来扩展（v2）**：

- 5+ 列：增加列数时，把 viewBox 改成 1400×500、列间距均分。可另写离线布局脚本，输入 nodes/flows JSON、输出每条 path 的 d 值
- 流条 hover 高亮：本管线不支持交互，只能在静态截图选定一条主路径加粗 + 高 opacity
- 数值标注在流条上：本管线不能跟随曲线，只能在最宽段用 HTML div 叠加数字（仅最大的 1-2 条）

---

## 18. 热力日历 (`heatmap_calendar`)

**何时用**：

- 365 天的活跃度 / 提交数 / DAU 历史（GitHub contributions 经典款）
- 全年事件密度（运营活动、Bug 报告、销售记录）
- 季节性洞察（哪几个月密、哪几周冷）

数据点 < 100 时不要用本模板（用迷你折线就够了）。本图的强项是**让 365 个数据点同时在一屏可读**。

**数据格式**：

```json
{
  "year": 2026,
  "metric": "代码提交数",
  "total": 1843,
  "max_per_day": 24,
  "days": [
    {"date": "2026-01-01", "value": 0,  "level": 0},
    {"date": "2026-01-02", "value": 3,  "level": 1},
    {"date": "2026-01-03", "value": 8,  "level": 2}
  ],
  "month_labels": ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]
}
```

`level` ∈ {0, 1, 2, 3, 4, 5} 是离散的强度桶（GitHub 用 5 桶；本模板用 6 桶以匹配项目数据范围）。映射建议：

| level | value 范围 | opacity |
|-------|----------|---------|
| 0 | 0 | 0.06 |
| 1 | 1-3 | 0.22 |
| 2 | 4-7 | 0.40 |
| 3 | 8-12 | 0.60 |
| 4 | 13-18 | 0.80 |
| 5 | 19+ | 1.00 |

**HTML 模板**（完整可运行）：

```html
<div class="chart-heatmap-calendar" style="position:relative; width:100%; aspect-ratio: 16/5; padding: 24px 32px 28px 56px;">

  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 18px;">
    <div>
      <div style="font-size:11px; letter-spacing:0.18em; text-transform:uppercase; color:var(--accent-1); font-weight:600;">— 365-DAY ACTIVITY</div>
      <div style="font-size:20px; font-weight:600; letter-spacing:-0.01em; color:var(--text-primary); margin-top:6px;">代码提交日历 · 2026</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:28px; font-weight:700; letter-spacing:-0.02em; color:var(--text-primary); font-variant-numeric: tabular-nums;">1 843<span style="font-size:13px; color:var(--text-secondary); font-weight:500; margin-left:6px;">次提交 · 全年</span></div>
      <div style="font-size:11px; color:var(--text-secondary); letter-spacing:0.05em; margin-top:2px;">最长连续 47 天 · 平均 5.05 / 日</div>
    </div>
  </div>

  <div style="position:relative; padding-top:16px;">

    <div style="position:absolute; top:0; left:0; right:0; display:grid; grid-template-columns: repeat(53, 1fr); font-size:9px; color:var(--text-secondary); letter-spacing:0.04em; pointer-events:none;">
      <div style="grid-column: 1 / 6;">Jan</div>
      <div style="grid-column: 6 / 10;">Feb</div>
      <div style="grid-column: 10 / 14;">Mar</div>
      <div style="grid-column: 14 / 19;">Apr</div>
      <div style="grid-column: 19 / 23;">May</div>
      <div style="grid-column: 23 / 27;">Jun</div>
      <div style="grid-column: 27 / 32;">Jul</div>
      <div style="grid-column: 32 / 36;">Aug</div>
      <div style="grid-column: 36 / 41;">Sep</div>
      <div style="grid-column: 41 / 45;">Oct</div>
      <div style="grid-column: 45 / 49;">Nov</div>
      <div style="grid-column: 49 / 54;">Dec</div>
    </div>

    <div style="position:absolute; top:18px; left:-44px; display:grid; grid-template-rows: repeat(7, 1fr); height:calc(7 * (100% / 7) - 0px); gap:2px; font-size:9px; color:var(--text-secondary); align-items:center;">
      <div></div>
      <div>Mon</div>
      <div></div>
      <div>Wed</div>
      <div></div>
      <div>Fri</div>
      <div></div>
    </div>

    <div style="display:grid; grid-template-columns: repeat(53, 1fr); grid-template-rows: repeat(7, 1fr); gap:2px; aspect-ratio: 53 / 7;">

      <div style="grid-column:1; grid-row:1; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      <div style="grid-column:1; grid-row:2; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      <div style="grid-column:1; grid-row:3; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:1; grid-row:4; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:1; grid-row:5; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:1; grid-row:6; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      <div style="grid-column:1; grid-row:7; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>

      <div style="grid-column:2; grid-row:1; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      <div style="grid-column:2; grid-row:2; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:2; grid-row:3; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
      <div style="grid-column:2; grid-row:4; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:2; grid-row:5; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
      <div style="grid-column:2; grid-row:6; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:2; grid-row:7; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>

      <div style="grid-column:3; grid-row:1; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:3; grid-row:2; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
      <div style="grid-column:3; grid-row:3; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
      <div style="grid-column:3; grid-row:4; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div>
      <div style="grid-column:3; grid-row:5; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
      <div style="grid-column:3; grid-row:6; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:3; grid-row:7; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>

      <div style="grid-column:4; grid-row:1; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:4; grid-row:2; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
      <div style="grid-column:4; grid-row:3; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div>
      <div style="grid-column:4; grid-row:4; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div>
      <div style="grid-column:4; grid-row:5; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
      <div style="grid-column:4; grid-row:6; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:4; grid-row:7; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>

      <div style="grid-column:5; grid-row:1; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:5; grid-row:2; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:5; grid-row:3; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
      <div style="grid-column:5; grid-row:4; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:5; grid-row:5; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:5; grid-row:6; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      <div style="grid-column:5; grid-row:7; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>

      <div style="grid-column:6; grid-row:1; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      <div style="grid-column:6; grid-row:2; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:6; grid-row:3; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
      <div style="grid-column:6; grid-row:4; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
      <div style="grid-column:6; grid-row:5; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div>
      <div style="grid-column:6; grid-row:6; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:6; grid-row:7; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>

      <div style="grid-column:7; grid-row:1; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:7; grid-row:2; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div>
      <div style="grid-column:7; grid-row:3; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div>
      <div style="grid-column:7; grid-row:4; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
      <div style="grid-column:7; grid-row:5; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
      <div style="grid-column:7; grid-row:6; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:7; grid-row:7; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>

      <div style="grid-column:8; grid-row:1; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:8; grid-row:2; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
      <div style="grid-column:8; grid-row:3; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
      <div style="grid-column:8; grid-row:4; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
      <div style="grid-column:8; grid-row:5; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:8; grid-row:6; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
      <div style="grid-column:8; grid-row:7; aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>

      <div style="grid-column:9 / 13; grid-row:1 / 8; display:grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(7, 1fr); gap:2px;">
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      </div>

      <div style="grid-column:13 / 27; grid-row:1 / 8; display:grid; grid-template-columns: repeat(14, 1fr); grid-template-rows: repeat(7, 1fr); gap:2px;">
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      </div>

      <div style="grid-column:27 / 41; grid-row:1 / 8; display:grid; grid-template-columns: repeat(14, 1fr); grid-template-rows: repeat(7, 1fr); gap:2px;">
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      </div>

      <div style="grid-column:41 / 54; grid-row:1 / 8; display:grid; grid-template-columns: repeat(13, 1fr); grid-template-rows: repeat(7, 1fr); gap:2px;">
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:1.00;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.80;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.60;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
        <div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.40;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.22;"></div><div style="aspect-ratio:1; border-radius:2px; background:var(--accent-1); opacity:0.06;"></div>
      </div>

    </div>
  </div>

  <div style="margin-top:14px; display:flex; align-items:center; justify-content:flex-end; gap:8px;">
    <span style="font-size:10px; letter-spacing:0.12em; color:var(--text-secondary); text-transform:uppercase;">Less</span>
    <span style="display:inline-block; width:11px; height:11px; border-radius:2px; background:var(--accent-1); opacity:0.06;"></span>
    <span style="display:inline-block; width:11px; height:11px; border-radius:2px; background:var(--accent-1); opacity:0.22;"></span>
    <span style="display:inline-block; width:11px; height:11px; border-radius:2px; background:var(--accent-1); opacity:0.40;"></span>
    <span style="display:inline-block; width:11px; height:11px; border-radius:2px; background:var(--accent-1); opacity:0.60;"></span>
    <span style="display:inline-block; width:11px; height:11px; border-radius:2px; background:var(--accent-1); opacity:0.80;"></span>
    <span style="display:inline-block; width:11px; height:11px; border-radius:2px; background:var(--accent-1); opacity:1.00;"></span>
    <span style="font-size:10px; letter-spacing:0.12em; color:var(--text-secondary); text-transform:uppercase;">More</span>
  </div>

</div>
```

**实现要点**：

- **53 列 × 7 行 grid**——一年 ≤ 366 天，53 周列足够覆盖。每个 cell 用 `aspect-ratio: 1` 保证正方形，跟容器宽度自适应。
- **本模板用嵌套 grid 分组生成**：开头 8 列是单元格手写演示（让你看清结构），剩余 45 列分成 4 个**子 grid 块**（9-12 / 13-26 / 27-40 / 41-53）批量填充——避免 371 个独立 div 把模板撑到 5000 行。生产用法：用 Python 模板引擎（Jinja）循环生成 371 个 div 即可。
- **每个 cell 只有一个属性变化**：`opacity`。`background: var(--accent-1)` 全部相同。这是热力日历的灵魂——**单变量映射**，最大化色彩信号。
- **6 个 opacity 桶**（0.06 / 0.22 / 0.40 / 0.60 / 0.80 / 1.00）是感知校准的——0.06 让"无活动"日子仍可见但很弱（区分于背景），1.00 是峰值。GitHub 用 5 桶，本模板加一档便于范围更宽的数据。
- **月份标签用 `grid-column: N / M` 跨多列**——1 月 = `1 / 6`（5 列）、2 月 = `6 / 10`（4 列）...精确对齐每月第一周。注意不同年份首日星期不同，模板里需根据 `year` 参数偏移第一列的起始 row。
- **左侧周标签**只显示 Mon / Wed / Fri（隔行），跟 GitHub 一样——避免 7 行全部标签把视觉撑乱。

**自检**：

- [ ] 53 列 × 7 行 = 371 cell（覆盖 365-366 天）
- [ ] 所有 cell 用 `aspect-ratio: 1` 保持正方形
- [ ] 单一颜色（`--accent-1`），仅 opacity 变化
- [ ] 6 个 opacity 桶离散（0.06 / 0.22 / 0.40 / 0.60 / 0.80 / 1.00）
- [ ] 月份标签的 grid-column 跨度 = 该月对应的周数
- [ ] 图例 6 段 + Less / More 文字
- [ ] 数字（total / max）开 tabular-nums

**未来扩展（v2）**：

- Python 模板：另写离线脚本，输入 `{date: value}` JSON、年份起始星期，输出 371 个 div 字符串
- 月份分隔：在每月的最后一列右侧加 1px 透明分隔（用 `grid-column-gap` 不行，可在该列 cell 上加 `border-right: 1px solid var(--card-border)`）
- 突出周末：周六/周日（行 1 / 7）整体降一档 opacity 或加 0.5px 内边框，强化"工作日 vs 周末"差异
- 多年对比：连续画 2-3 张本模板上下堆叠，每张占 1/3 高度

---

## 共同实施清单

生成任何复杂图表前，请对照：

- [ ] **数据先行**：所有 value 已经映射到 `intensity` / `level` / `opacity` 桶。**不要让模板做计算**——模板只负责渲染
- [ ] **颜色 100% CSS 变量**——禁止 `#22D3EE` 等硬编码
- [ ] **SVG 内零 `<text>`**——所有标签是 HTML 元素，绝对定位叠加
- [ ] **数字开 tabular-nums**——尤其大数（`total`, `max`, KPI）
- [ ] **配合 viewBox 用 `preserveAspectRatio="none"`**（network、sankey）才能让 SVG 几何与 HTML 百分比标签对齐
- [ ] **不引 JS、不用 conic-gradient / mask-image / mix-blend-mode / filter:blur()**
- [ ] **响应式**：所有定位用百分比 / aspect-ratio，不用绝对 px——便于贴到 1280×720 PPT 内任意尺寸卡片

## 升级路径

| 现状 | 触发升级条件 | v2 方案 |
|------|------------|---------|
| 12 个简化国家 path | 超过 20 国 / 客户要求真实地图 | 离线 GeoJSON → topojson-simplify → 内联 path |
| 手工预算 network 坐标 | 节点 > 12 / 边 > 20 | Python `networkx.spring_layout()` 离线计算坐标 |
| 4 列桑基手工 path | 5+ 列 / 流条数 > 25 | Python `sankey_layout.py` 自动计算 path d 值 |
| 371 cell 嵌套 grid | 数据动态 / 多年 | Jinja 模板循环生成 371 div |

每条升级路径都**不引入运行时 JS**——离线计算 + 模板生成 = 管线兼容。
