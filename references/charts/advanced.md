# 进阶图表（6 种）

> 本文件覆盖 6 种 NEW 进阶图表。**所有模板均符合 [pipeline-compat.md](../pipeline-compat.md)**：SVG 内零 `<text>`、所有标签 HTML 叠加、所有数字 `tabular-nums`、所有颜色用 CSS 变量。
>
> 复制即用。每个模板都内置假数据，只需替换数据即可。

---

## 图表索引

| # | 图表 | chart_id | 何时用 |
|---|------|----------|-------|
| 1 | 雷达图 | `radar` | 多维度对比（5-8 维） |
| 2 | 时间线 | `timeline` | 历史 / 路线图 / 流程 |
| 3 | 漏斗图 | `funnel` | 转化率 / 流失分析 |
| 4 | 仪表盘 | `gauge` | KPI 评级 / 健康度 |
| 5 | 多组对比柱 | `grouped_bar` | 多类别 × 多组对比 |
| 6 | 简单地理 | `simple_map` | 城市点 / 区域分布 |

---

## 1. 雷达图 (radar)

**何时用**：5-8 个维度的多面对比，比如产品能力评估、候选人能力雷达、品牌健康度。维度数低于 5 用「指标行」，超过 8 个维度时拆成两张雷达图。

**数据格式**：

```json
{
  "dimensions": ["性能", "续航", "拍照", "屏幕", "做工", "系统"],
  "series": [
    { "name": "Pro 版", "values": [88, 72, 95, 90, 85, 80], "color": "var(--accent-1)" },
    { "name": "标准版", "values": [70, 80, 78, 75, 72, 78], "color": "var(--accent-3)" }
  ],
  "max": 100
}
```

**HTML 模板**（6 维 × 2 系列，220×220 视图，半径 90，5 圈刻度）：

```html
<div class="chart-radar" style="position:relative; width:340px; height:280px; font-family:var(--body-font);">
  <svg viewBox="0 0 220 220" style="position:absolute; left:60px; top:20px; width:220px; height:220px; overflow:visible;">
    <polygon points="110,20 187.94,65 187.94,155 110,200 32.06,155 32.06,65"
             fill="none" stroke="var(--card-border)" stroke-width="1" opacity="0.55"/>
    <polygon points="110,38 172.35,74 172.35,146 110,182 47.65,146 47.65,74"
             fill="none" stroke="var(--card-border)" stroke-width="1" opacity="0.4"/>
    <polygon points="110,56 156.76,83 156.76,137 110,164 63.24,137 63.24,83"
             fill="none" stroke="var(--card-border)" stroke-width="1" opacity="0.3"/>
    <polygon points="110,74 141.18,92 141.18,128 110,146 78.82,128 78.82,92"
             fill="none" stroke="var(--card-border)" stroke-width="1" opacity="0.22"/>
    <polygon points="110,92 125.59,101 125.59,119 110,128 94.41,119 94.41,101"
             fill="none" stroke="var(--card-border)" stroke-width="1" opacity="0.15"/>

    <line x1="110" y1="110" x2="110" y2="20"   stroke="var(--card-border)" stroke-width="1" opacity="0.25"/>
    <line x1="110" y1="110" x2="187.94" y2="65"  stroke="var(--card-border)" stroke-width="1" opacity="0.25"/>
    <line x1="110" y1="110" x2="187.94" y2="155" stroke="var(--card-border)" stroke-width="1" opacity="0.25"/>
    <line x1="110" y1="110" x2="110" y2="200" stroke="var(--card-border)" stroke-width="1" opacity="0.25"/>
    <line x1="110" y1="110" x2="32.06" y2="155" stroke="var(--card-border)" stroke-width="1" opacity="0.25"/>
    <line x1="110" y1="110" x2="32.06" y2="65"  stroke="var(--card-border)" stroke-width="1" opacity="0.25"/>

    <polygon points="110,30.8 166.05,72.6 184.04,150.5 110,134.0 47.78,82.7 60.84,73.4"
             fill="var(--accent-3)" fill-opacity="0.18"
             stroke="var(--accent-3)" stroke-width="1.6" stroke-linejoin="round"/>

    <polygon points="110,29.2 173.13,69.05 175.62,140.45 110,182 64.66,131.3 47.65,74"
             fill="var(--accent-1)" fill-opacity="0.22"
             stroke="var(--accent-1)" stroke-width="1.8" stroke-linejoin="round"/>

    <circle cx="110" cy="29.2"  r="3" fill="var(--accent-1)"/>
    <circle cx="173.13" cy="69.05"  r="3" fill="var(--accent-1)"/>
    <circle cx="175.62" cy="140.45" r="3" fill="var(--accent-1)"/>
    <circle cx="110" cy="182" r="3" fill="var(--accent-1)"/>
    <circle cx="64.66" cy="131.3"  r="3" fill="var(--accent-1)"/>
    <circle cx="47.65" cy="74"   r="3" fill="var(--accent-1)"/>
  </svg>

  <span class="radar-axis" style="position:absolute; left:170px; top:0px;   transform:translateX(-50%);">性能</span>
  <span class="radar-axis" style="position:absolute; left:288px; top:74px;">续航</span>
  <span class="radar-axis" style="position:absolute; left:288px; top:166px;">拍照</span>
  <span class="radar-axis" style="position:absolute; left:170px; top:236px; transform:translateX(-50%);">屏幕</span>
  <span class="radar-axis" style="position:absolute; right:288px; top:166px; transform:translateX(-100%);">做工</span>
  <span class="radar-axis" style="position:absolute; right:288px; top:74px;  transform:translateX(-100%);">系统</span>

  <div class="radar-legend" style="position:absolute; left:0; bottom:-4px; display:flex; gap:18px;">
    <span style="display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--text-secondary); letter-spacing:0.08em;">
      <span style="width:10px; height:10px; border-radius:2px; background:var(--accent-1);"></span>Pro 版
    </span>
    <span style="display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--text-secondary); letter-spacing:0.08em;">
      <span style="width:10px; height:10px; border-radius:2px; background:var(--accent-3);"></span>标准版
    </span>
  </div>

  <style>
    .chart-radar .radar-axis {
      font-size: 11px;
      color: var(--text-secondary);
      letter-spacing: 0.08em;
      font-weight: 600;
      text-transform: uppercase;
      white-space: nowrap;
    }
  </style>
</div>
```

**坐标计算公式**（如需调整 N 维或半径 r，复用此公式生成 polygon points）：

```
每个轴角度  θ_i = -90° + i * (360° / N)
顶点坐标    (cx + r * cos(θ_i), cy + r * sin(θ_i))
数据顶点    r_data = r * (value / max)
```

6 维示例：圆心 (110, 110)，r=90，scale=value/100。

**变体**：
- **单系列雷达**：删掉 `<polygon>` 第二条 + legend 的第二项即可。
- **8 维**：把 polygon 的 6 个顶点改为 8 个，按公式重算。

**自检**：
- [ ] SVG 内无 `<text>`，所有维度名是 HTML span
- [ ] 背景刻度 5 圈（0/25/50/75/100），便于读数
- [ ] 数据多边形半透明填充（fill-opacity 0.18-0.25）
- [ ] 用 `var(--accent-X)`，不硬编码颜色
- [ ] 数字虽不显式标注，若加角标则需 `font-variant-numeric: tabular-nums`

---

## 2. 时间线 (timeline)

**何时用**：4-6 个里程碑的横向叙事，比如公司发展史、产品路线图、项目阶段。超过 8 个里程碑改用「垂直时间线」（变体）。

**数据格式**：

```json
{
  "milestones": [
    { "year": "2021", "title": "公司成立",       "side": "top",    "highlight": false },
    { "year": "2022", "title": "完成 A 轮融资",   "side": "bottom", "highlight": false },
    { "year": "2023", "title": "首款产品上市",   "side": "top",    "highlight": false },
    { "year": "2024", "title": "用户突破 1000 万","side": "bottom", "highlight": true  },
    { "year": "2025", "title": "出海东南亚",     "side": "top",    "highlight": false },
    { "year": "2026", "title": "IPO 上市",       "side": "bottom", "highlight": true  }
  ]
}
```

**HTML 模板**（横向，6 节点，上下交替排版）：

```html
<div class="chart-timeline" style="position:relative; width:920px; height:200px; font-family:var(--body-font); padding:0 40px;">
  <div style="position:absolute; left:40px; right:40px; top:50%; height:2px; background:linear-gradient(90deg, var(--card-border) 0%, var(--accent-1) 50%, var(--card-border) 100%); transform:translateY(-50%);"></div>

  <div style="position:absolute; left:40px; right:40px; top:50%; height:0; transform:translateY(-50%); display:flex; justify-content:space-between;">
    <div class="tl-node" data-side="top"></div>
    <div class="tl-node" data-side="bottom"></div>
    <div class="tl-node" data-side="top"></div>
    <div class="tl-node" data-side="bottom" data-hl="1"></div>
    <div class="tl-node" data-side="top"></div>
    <div class="tl-node" data-side="bottom" data-hl="1"></div>
  </div>

  <div style="position:absolute; left:40px; right:40px; top:0; bottom:0; display:flex; justify-content:space-between; pointer-events:none;">
    <div class="tl-cell" data-side="top">
      <div class="tl-year">2021</div>
      <div class="tl-title">公司成立</div>
    </div>
    <div class="tl-cell" data-side="bottom">
      <div class="tl-year">2022</div>
      <div class="tl-title">完成 A 轮融资</div>
    </div>
    <div class="tl-cell" data-side="top">
      <div class="tl-year">2023</div>
      <div class="tl-title">首款产品上市</div>
    </div>
    <div class="tl-cell" data-side="bottom" data-hl="1">
      <div class="tl-year">2024</div>
      <div class="tl-title">用户突破 1000 万</div>
    </div>
    <div class="tl-cell" data-side="top">
      <div class="tl-year">2025</div>
      <div class="tl-title">出海东南亚</div>
    </div>
    <div class="tl-cell" data-side="bottom" data-hl="1">
      <div class="tl-year">2026</div>
      <div class="tl-title">IPO 上市</div>
    </div>
  </div>

  <style>
    .chart-timeline .tl-node {
      position: relative;
      width: 14px; height: 14px; border-radius: 50%;
      background: var(--bg-primary, #0a0a0a);
      border: 2px solid var(--accent-1);
      box-shadow: 0 0 0 4px rgba(255,255,255,0.04);
      flex-shrink: 0;
    }
    .chart-timeline .tl-node[data-hl="1"] {
      background: var(--accent-1);
      box-shadow: 0 0 12px var(--accent-1), 0 0 0 4px rgba(255,255,255,0.06);
    }
    .chart-timeline .tl-cell {
      position: relative;
      width: 0;
      display: flex; flex-direction: column; align-items: center;
      text-align: center;
    }
    .chart-timeline .tl-cell[data-side="top"]    { justify-content: flex-start; padding-top: 16px; }
    .chart-timeline .tl-cell[data-side="bottom"] { justify-content: flex-end;   padding-bottom: 16px; flex-direction: column-reverse; }
    .chart-timeline .tl-cell[data-side="top"]    { transform: translateY(0); }
    .chart-timeline .tl-cell[data-side="bottom"] { transform: translateY(100px); }
    .chart-timeline .tl-year {
      font-family: var(--display-font, var(--body-font));
      font-size: 22px; font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--accent-1);
      font-variant-numeric: tabular-nums proportional-nums;
      margin-bottom: 4px;
      white-space: nowrap;
    }
    .chart-timeline .tl-cell[data-side="bottom"] .tl-year { margin-bottom: 0; margin-top: 4px; }
    .chart-timeline .tl-title {
      font-size: 12px;
      color: var(--text-secondary);
      letter-spacing: 0.04em;
      line-height: 1.3;
      max-width: 130px;
      white-space: nowrap;
    }
    .chart-timeline .tl-cell[data-hl="1"] .tl-title {
      color: var(--text-primary);
      font-weight: 600;
    }
  </style>
</div>
```

**变体**：
- **垂直时间线**：将外层 flex 由横向改纵向（`flex-direction: column`），主线变 width:2px 居中竖线。适合 8+ 节点。
- **阶段块时间线**：节点之间用 `flex:1` 的色块连接（每段 +1 颜色），适合"阶段"而非"瞬时"事件。

**自检**：
- [ ] 节点用真实 div，不用 `::before`
- [ ] 上下交替排版避免文字撞车
- [ ] 高亮节点 (`data-hl="1"`) 用 `--accent-1` 实心 + 辉光
- [ ] 年份 `font-variant-numeric: tabular-nums`
- [ ] 主线两端用 `--card-border`，中段用 `--accent-1` 渐变

---

## 3. 漏斗图 (funnel)

**何时用**：4-5 层转化路径，每层都"流失了一部分"。例：访问→注册→付费→续费。流失点超过 6 层或多分支路径用「桑基图」（complex.md）。

**数据格式**：

```json
{
  "stages": [
    { "name": "网站访问", "value": 100000, "rate": "100.0%" },
    { "name": "注册账号", "value":  42000, "rate": "42.0%"  },
    { "name": "首次付费", "value":  18500, "rate": "44.0%"  },
    { "name": "续费用户", "value":  11200, "rate": "60.5%"  },
    { "name": "年度会员", "value":   6800, "rate": "60.7%"  }
  ]
}
```

`rate` 是相对于上一层的转化率；首层固定 100%。

**HTML 模板**（5 层梯形，每层 1 个 SVG polygon）：

```html
<div class="chart-funnel" style="position:relative; width:680px; height:380px; font-family:var(--body-font);">
  <svg viewBox="0 0 400 380" preserveAspectRatio="none" style="position:absolute; left:0; top:0; width:400px; height:380px;">
    <defs>
      <linearGradient id="funnelGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%"   stop-color="var(--accent-1)" stop-opacity="0.95"/>
        <stop offset="100%" stop-color="var(--accent-3)" stop-opacity="0.7"/>
      </linearGradient>
    </defs>

    <polygon points="40,8 360,8 332,68 68,68"     fill="url(#funnelGrad)" fill-opacity="0.95"/>
    <polygon points="68,76 332,76 304,144 96,144" fill="url(#funnelGrad)" fill-opacity="0.78"/>
    <polygon points="96,152 304,152 276,220 124,220" fill="url(#funnelGrad)" fill-opacity="0.62"/>
    <polygon points="124,228 276,228 248,296 152,296" fill="url(#funnelGrad)" fill-opacity="0.48"/>
    <polygon points="152,304 248,304 220,372 180,372" fill="url(#funnelGrad)" fill-opacity="0.36"/>
  </svg>

  <div class="fn-row" style="top:18px;">
    <span class="fn-name">网站访问</span>
    <span class="fn-num">100,000</span>
    <span class="fn-rate">100.0%</span>
  </div>
  <div class="fn-row" style="top:96px;">
    <span class="fn-name">注册账号</span>
    <span class="fn-num">42,000</span>
    <span class="fn-rate">42.0%</span>
  </div>
  <div class="fn-row" style="top:174px;">
    <span class="fn-name">首次付费</span>
    <span class="fn-num">18,500</span>
    <span class="fn-rate">44.0%</span>
  </div>
  <div class="fn-row" style="top:252px;">
    <span class="fn-name">续费用户</span>
    <span class="fn-num">11,200</span>
    <span class="fn-rate">60.5%</span>
  </div>
  <div class="fn-row" style="top:330px;">
    <span class="fn-name">年度会员</span>
    <span class="fn-num">6,800</span>
    <span class="fn-rate">60.7%</span>
  </div>

  <div class="fn-side-axis" style="position:absolute; left:420px; top:8px; bottom:8px; width:6px; border-left:1px dashed var(--card-border);"></div>
  <div class="fn-legend" style="position:absolute; left:436px; top:18px; display:flex; flex-direction:column; gap:62px;">
    <div class="fn-arrow"><span class="fn-arrow-num">-58.0%</span><span class="fn-arrow-lbl">流失</span></div>
    <div class="fn-arrow"><span class="fn-arrow-num">-56.0%</span><span class="fn-arrow-lbl">流失</span></div>
    <div class="fn-arrow"><span class="fn-arrow-num">-39.5%</span><span class="fn-arrow-lbl">流失</span></div>
    <div class="fn-arrow"><span class="fn-arrow-num">-39.3%</span><span class="fn-arrow-lbl">流失</span></div>
  </div>

  <style>
    .chart-funnel .fn-row {
      position: absolute;
      left: 50%; transform: translateX(-50%);
      width: 320px;
      display: flex; align-items: center; justify-content: space-between;
      gap: 16px; padding: 0 12px;
      pointer-events: none;
    }
    .chart-funnel .fn-name {
      font-size: 13px; font-weight: 600;
      color: var(--text-primary);
      letter-spacing: 0.04em;
    }
    .chart-funnel .fn-num {
      font-family: var(--display-font, var(--body-font));
      font-size: 20px; font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums proportional-nums;
    }
    .chart-funnel .fn-rate {
      font-family: var(--mono-font, var(--body-font));
      font-size: 11px;
      color: rgba(255,255,255,0.85);
      background: rgba(0,0,0,0.25);
      border-radius: 999px;
      padding: 3px 8px;
      letter-spacing: 0.04em;
      font-variant-numeric: tabular-nums;
    }
    .chart-funnel .fn-arrow {
      display: flex; flex-direction: column; gap: 2px;
    }
    .chart-funnel .fn-arrow-num {
      font-family: var(--mono-font, var(--body-font));
      font-size: 12px; font-weight: 600;
      color: var(--accent-3);
      font-variant-numeric: tabular-nums;
      letter-spacing: -0.01em;
    }
    .chart-funnel .fn-arrow-lbl {
      font-size: 10px; color: var(--text-secondary);
      letter-spacing: 0.12em; text-transform: uppercase;
    }
  </style>
</div>
```

**梯形 polygon 坐标计算**：viewBox 400×380，5 层每层高 68，间隔 8。对每层 i：

```
top_y    = 8 + i * 76
bot_y    = top_y + 60
top_half = 160 - i * 32      (顶宽的一半)
bot_half = 160 - (i+1) * 28  (底宽的一半，注意收窄不同)
```

实际写时手算粘贴即可（已在模板内写好）。

**变体**：
- **左对齐漏斗（瀑布感）**：所有梯形左边垂直对齐，只右边收窄，更像 step 流失瀑布。
- **横向漏斗**：旋转 90°，从左到右收窄，适合横屏看板。

**自检**：
- [ ] 5 层梯形用 `<polygon>`，绝不用 CSS border 三角形
- [ ] fill-opacity 从 0.95 递减到 0.36（视觉收窄感）
- [ ] 数字 `font-variant-numeric: tabular-nums`
- [ ] 转化率 pill 用 `rgba(0,0,0,0.25)` 半透明，对深浅色都安全
- [ ] 流失箭头单独画在漏斗外侧（不挤占图形）

---

## 4. 仪表盘 (gauge)

**何时用**：单一 KPI 的"等级感"，比如健康度 78/100、信用分、NPS、风险等级。仅 1 个数字、需"绿/黄/红"分段时首选。

**数据格式**：

```json
{
  "value": 78,
  "max": 100,
  "label": "系统健康度",
  "rating": "良好",
  "thresholds": [
    { "from":  0, "to":  40, "color": "var(--accent-3)", "label": "需关注" },
    { "from": 40, "to":  70, "color": "var(--accent-4)", "label": "中等" },
    { "from": 70, "to": 100, "color": "var(--accent-1)", "label": "优秀" }
  ]
}
```

**HTML 模板**（半圆 180°，三色分段 + 指针 + 中心 KPI）：

```html
<div class="chart-gauge" style="position:relative; width:320px; height:220px; font-family:var(--body-font);">
  <svg viewBox="0 0 220 130" style="position:absolute; left:50%; top:0; transform:translateX(-50%); width:280px; height:auto; overflow:visible;">
    <path d="M 20 110 A 90 90 0 0 1 110 20"
          fill="none" stroke="var(--accent-3)" stroke-width="14" stroke-linecap="butt"/>
    <path d="M 110 20 A 90 90 0 0 1 173.64 46.36"
          fill="none" stroke="var(--accent-4)" stroke-width="14" stroke-linecap="butt"/>
    <path d="M 173.64 46.36 A 90 90 0 0 1 200 110"
          fill="none" stroke="var(--accent-1)" stroke-width="14" stroke-linecap="butt"/>

    <path d="M 20 110 A 90 90 0 0 1 200 110"
          fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>

    <line x1="20"  y1="110" x2="32"  y2="110" stroke="var(--text-secondary)" stroke-width="1" opacity="0.5"/>
    <line x1="46"  y1="46"  x2="55"  y2="53"  stroke="var(--text-secondary)" stroke-width="1" opacity="0.5"/>
    <line x1="110" y1="20"  x2="110" y2="32"  stroke="var(--text-secondary)" stroke-width="1" opacity="0.5"/>
    <line x1="174" y1="46"  x2="165" y2="53"  stroke="var(--text-secondary)" stroke-width="1" opacity="0.5"/>
    <line x1="200" y1="110" x2="188" y2="110" stroke="var(--text-secondary)" stroke-width="1" opacity="0.5"/>

    <g transform="rotate(50.4 110 110)">
      <line x1="110" y1="110" x2="110" y2="32"
            stroke="var(--text-primary)" stroke-width="2.4" stroke-linecap="round"/>
      <circle cx="110" cy="32" r="4" fill="var(--text-primary)"/>
    </g>
    <circle cx="110" cy="110" r="9" fill="var(--bg-primary, #0a0a0a)" stroke="var(--text-primary)" stroke-width="2"/>
    <circle cx="110" cy="110" r="3" fill="var(--text-primary)"/>
  </svg>

  <div style="position:absolute; left:0; right:0; top:120px; text-align:center;">
    <div style="font-family:var(--display-font, var(--body-font)); font-size:54px; font-weight:700; line-height:1; letter-spacing:-0.04em; color:var(--text-primary); font-variant-numeric:tabular-nums proportional-nums;">
      78<span style="font-size:22px; color:var(--text-secondary); font-weight:500; letter-spacing:0; margin-left:4px;">/100</span>
    </div>
    <div style="margin-top:10px; display:inline-flex; align-items:center; gap:6px; padding:4px 12px; border-radius:999px; background:rgba(255,255,255,0.06); border:1px solid var(--card-border);">
      <span style="width:6px; height:6px; border-radius:50%; background:var(--accent-1); box-shadow:0 0 8px var(--accent-1);"></span>
      <span style="font-size:11px; color:var(--text-primary); font-weight:600; letter-spacing:0.12em;">优秀</span>
    </div>
    <div style="margin-top:6px; font-size:11px; color:var(--text-secondary); letter-spacing:0.16em; text-transform:uppercase;">系统健康度</div>
  </div>

  <span style="position:absolute; left:18px; bottom:50px; font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums; letter-spacing:0.06em;">0</span>
  <span style="position:absolute; left:50%; top:0px; transform:translateX(-50%); font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums; letter-spacing:0.06em;">50</span>
  <span style="position:absolute; right:18px; bottom:50px; font-size:10px; color:var(--text-secondary); font-variant-numeric:tabular-nums; letter-spacing:0.06em;">100</span>
</div>
```

**指针角度计算**：

```
半圆从 -90° (左) 到 +90° (右)，整段 180°
角度 = -90 + (value / max) * 180
SVG 内 transform="rotate(angle 110 110)"
示例：value=78, max=100 -> -90 + 0.78 * 180 = 50.4°
```

**圆弧分段（A 命令）**：圆心 (110, 110)，半径 90，每个分段 SVG path 计算：

```
点 (x, y) at 角度 θ (0°指 12 点钟，顺时针):
  x = 110 + 90 * sin(θ - 90°) [from -90° start]
  实际写法：用 path "M x1 y1 A 90 90 0 0 1 x2 y2"
0%   -> ( 20, 110)   100% -> (200, 110)
40%  -> (110,  20)   该点是顶端
70%  -> (173.64, 46.36)
```

**变体**：
- **单色仪表（无分段）**：删 3 段 path，换 1 整段 + 一段填充弧（dasharray 控制进度）。
- **双指针对比**：第二根指针用 `var(--accent-3)` + opacity 0.6，对比"目标 vs 实际"。

**自检**：
- [ ] 半圆 3 段用 SVG path，绝不用 conic-gradient
- [ ] 指针是 SVG `<line>` + `transform="rotate()"`，不用 CSS 旋转
- [ ] 中心 KPI 大数字 + "/100" 用 flex baseline 对齐（嵌入 span 已加 `margin-left`）
- [ ] 数字 `font-variant-numeric: tabular-nums`
- [ ] 等级 pill 颜色对应 threshold（指针落在哪段就用那段色）

---

## 5. 多组对比柱 (grouped_bar)

**何时用**：3-4 个类别 × 2-3 个组的对比，比如「3 款产品 × 3 个年度」「5 个区域 × 2 种产品」。仅 1 组用「对比柱」（basic.md）。

**数据格式**：

```json
{
  "categories": ["产品 A", "产品 B", "产品 C"],
  "groups": [
    { "name": "2024", "color": "var(--accent-3)", "values": [320, 410, 280] },
    { "name": "2025", "color": "var(--accent-2)", "values": [480, 520, 360] },
    { "name": "2026", "color": "var(--accent-1)", "values": [620, 580, 510] }
  ],
  "max": 700,
  "unit": "万元"
}
```

**HTML 模板**（3 类别 × 3 组，纯 div + flex，无 SVG）：

```html
<div class="chart-grouped-bar" style="position:relative; width:680px; height:340px; font-family:var(--body-font); display:flex; flex-direction:column; gap:14px;">

  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div style="display:flex; gap:18px;">
      <span class="gb-leg"><span class="gb-sw" style="background:var(--accent-3);"></span>2024</span>
      <span class="gb-leg"><span class="gb-sw" style="background:var(--accent-2);"></span>2025</span>
      <span class="gb-leg"><span class="gb-sw" style="background:var(--accent-1);"></span>2026</span>
    </div>
    <span style="font-size:11px; color:var(--text-secondary); letter-spacing:0.12em; text-transform:uppercase;">单位：万元</span>
  </div>

  <div style="position:relative; flex:1; display:flex; align-items:flex-end; gap:64px; padding:0 24px 32px; border-bottom:1px solid var(--card-border);">

    <div style="position:absolute; left:24px; right:24px; top:8px; bottom:32px; pointer-events:none;">
      <div class="gb-grid" style="top:0%;"></div>
      <div class="gb-grid" style="top:25%;"></div>
      <div class="gb-grid" style="top:50%;"></div>
      <div class="gb-grid" style="top:75%;"></div>
    </div>

    <span class="gb-yax" style="top:8px;">700</span>
    <span class="gb-yax" style="top:25%;">525</span>
    <span class="gb-yax" style="top:50%;">350</span>
    <span class="gb-yax" style="top:75%;">175</span>
    <span class="gb-yax" style="bottom:32px; transform:translateY(50%);">0</span>

    <div class="gb-cluster">
      <div class="gb-bars">
        <div class="gb-bar" style="height:45.7%; background:var(--accent-3);"><span class="gb-num">320</span></div>
        <div class="gb-bar" style="height:68.6%; background:var(--accent-2);"><span class="gb-num">480</span></div>
        <div class="gb-bar" style="height:88.6%; background:var(--accent-1);"><span class="gb-num">620</span></div>
      </div>
      <div class="gb-cat">产品 A</div>
    </div>

    <div class="gb-cluster">
      <div class="gb-bars">
        <div class="gb-bar" style="height:58.6%; background:var(--accent-3);"><span class="gb-num">410</span></div>
        <div class="gb-bar" style="height:74.3%; background:var(--accent-2);"><span class="gb-num">520</span></div>
        <div class="gb-bar" style="height:82.9%; background:var(--accent-1);"><span class="gb-num">580</span></div>
      </div>
      <div class="gb-cat">产品 B</div>
    </div>

    <div class="gb-cluster">
      <div class="gb-bars">
        <div class="gb-bar" style="height:40.0%; background:var(--accent-3);"><span class="gb-num">280</span></div>
        <div class="gb-bar" style="height:51.4%; background:var(--accent-2);"><span class="gb-num">360</span></div>
        <div class="gb-bar" style="height:72.9%; background:var(--accent-1);"><span class="gb-num">510</span></div>
      </div>
      <div class="gb-cat">产品 C</div>
    </div>

  </div>

  <style>
    .chart-grouped-bar .gb-leg {
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 12px; color: var(--text-secondary);
      letter-spacing: 0.04em;
      font-variant-numeric: tabular-nums;
    }
    .chart-grouped-bar .gb-sw {
      width: 12px; height: 12px; border-radius: 2px;
      display: inline-block;
    }
    .chart-grouped-bar .gb-grid {
      position: absolute; left: 0; right: 0; height: 1px;
      background: var(--card-border); opacity: 0.35;
    }
    .chart-grouped-bar .gb-yax {
      position: absolute; left: 0;
      font-size: 10px; color: var(--text-secondary);
      letter-spacing: 0.04em;
      font-variant-numeric: tabular-nums;
      transform: translateY(-50%);
    }
    .chart-grouped-bar .gb-cluster {
      flex: 1;
      display: flex; flex-direction: column; align-items: center; gap: 10px;
      height: 100%;
      padding-left: 28px;
    }
    .chart-grouped-bar .gb-bars {
      flex: 1;
      display: flex; align-items: flex-end; gap: 6px;
      width: 100%;
    }
    .chart-grouped-bar .gb-bar {
      flex: 1;
      position: relative;
      border-radius: 3px 3px 0 0;
      min-height: 6px;
      box-shadow: inset 0 -2px 0 rgba(0,0,0,0.18);
    }
    .chart-grouped-bar .gb-num {
      position: absolute;
      left: 50%; top: -18px;
      transform: translateX(-50%);
      font-family: var(--display-font, var(--body-font));
      font-size: 11px; font-weight: 600;
      color: var(--text-primary);
      letter-spacing: -0.01em;
      font-variant-numeric: tabular-nums proportional-nums;
      white-space: nowrap;
    }
    .chart-grouped-bar .gb-cat {
      font-size: 12px; font-weight: 600;
      color: var(--text-primary);
      letter-spacing: 0.04em;
    }
  </style>
</div>
```

**柱高百分比计算**：

```
height% = (value / max) * 100
示例 max=700, value=320 -> 45.7%
```

**变体**：
- **横向多组对比**：把 cluster 改 `flex-direction: row`，柱子用 `width:N%`（适合类别名超长场景）。
- **堆叠（stacked）**：每个 cluster 内的柱子 `flex-direction: column`，每段 `height:N%` 占自身比例（适合「合计 + 拆解」）。

**自检**：
- [ ] 用 flex + div，零 SVG，便于响应式
- [ ] 数据标签放柱顶 (`top:-18px`)，绝不挡柱子
- [ ] 数字 `font-variant-numeric: tabular-nums`
- [ ] Y 轴刻度线用 `var(--card-border) opacity:0.35`，不抢主图
- [ ] 图例 + Y 轴单位都齐（"单位：万元"放右上）
- [ ] 柱子底部 `inset box-shadow` 制造一点立体感（可选）

---

## 6. 简单地理 (simple_map)

**何时用**：5-12 个城市点 / 区域强调，配合一句洞察（如"覆盖 9 个一线城市"）。需精确边界 / choropleth 改用「世界地图 choropleth」（complex.md）。

**数据格式**：

```json
{
  "country": "中国",
  "points": [
    { "city": "北京", "x": 612, "y": 178, "value": 4200, "highlight": true  },
    { "city": "上海", "x": 658, "y": 308, "value": 5600, "highlight": true  },
    { "city": "广州", "x": 568, "y": 446, "value": 3100, "highlight": false },
    { "city": "深圳", "x": 580, "y": 462, "value": 3850, "highlight": true  },
    { "city": "成都", "x": 432, "y": 332, "value": 1850, "highlight": false },
    { "city": "西安", "x": 488, "y": 268, "value": 1240, "highlight": false },
    { "city": "杭州", "x": 632, "y": 332, "value": 2680, "highlight": false },
    { "city": "武汉", "x": 540, "y": 332, "value": 1980, "highlight": false }
  ],
  "unit": "万用户"
}
```

**HTML 模板**（简化中国轮廓 + 8 城市 HTML 圆点）：

```html
<div class="chart-map" style="position:relative; width:720px; height:520px; font-family:var(--body-font);">

  <svg viewBox="0 0 800 560" style="position:absolute; left:0; top:0; width:100%; height:100%; overflow:visible;">
    <defs>
      <linearGradient id="mapFill" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%"   stop-color="var(--accent-1)" stop-opacity="0.10"/>
        <stop offset="100%" stop-color="var(--accent-3)" stop-opacity="0.04"/>
      </linearGradient>
    </defs>

    <path d="M 220 120 L 300 80 L 420 90 L 520 70 L 640 110 L 700 170 L 720 240 L 690 310 L 660 360 L 640 410 L 600 460 L 540 490 L 460 500 L 400 470 L 360 480 L 300 460 L 240 430 L 200 380 L 170 320 L 150 250 L 170 180 Z"
          fill="url(#mapFill)"
          stroke="var(--accent-1)"
          stroke-width="1.5"
          stroke-opacity="0.55"
          stroke-linejoin="round"/>

    <path d="M 540 490 L 560 510 L 580 504 L 590 514 L 580 530 L 555 525 Z"
          fill="url(#mapFill)"
          stroke="var(--accent-1)"
          stroke-width="1.2"
          stroke-opacity="0.45"
          stroke-linejoin="round"/>
  </svg>

  <div class="mp-pt" data-hl="1" style="left:76.5%; top:31.8%;">
    <span class="mp-dot" style="width:22px; height:22px;"></span>
    <span class="mp-pulse" style="width:22px; height:22px;"></span>
    <div class="mp-card" data-side="right">
      <div class="mp-city">北京</div>
      <div class="mp-val">4,200<span class="mp-unit">万用户</span></div>
    </div>
  </div>

  <div class="mp-pt" data-hl="1" style="left:82.2%; top:55.0%;">
    <span class="mp-dot" style="width:24px; height:24px;"></span>
    <span class="mp-pulse" style="width:24px; height:24px;"></span>
    <div class="mp-card" data-side="right">
      <div class="mp-city">上海</div>
      <div class="mp-val">5,600<span class="mp-unit">万用户</span></div>
    </div>
  </div>

  <div class="mp-pt" style="left:71.0%; top:79.6%;">
    <span class="mp-dot" style="width:18px; height:18px;"></span>
    <div class="mp-card" data-side="left">
      <div class="mp-city">广州</div>
      <div class="mp-val">3,100<span class="mp-unit">万用户</span></div>
    </div>
  </div>

  <div class="mp-pt" data-hl="1" style="left:72.5%; top:82.5%;">
    <span class="mp-dot" style="width:20px; height:20px;"></span>
    <span class="mp-pulse" style="width:20px; height:20px;"></span>
    <div class="mp-card" data-side="right">
      <div class="mp-city">深圳</div>
      <div class="mp-val">3,850<span class="mp-unit">万用户</span></div>
    </div>
  </div>

  <div class="mp-pt" style="left:54.0%; top:59.3%;">
    <span class="mp-dot" style="width:14px; height:14px;"></span>
    <div class="mp-card" data-side="left">
      <div class="mp-city">成都</div>
      <div class="mp-val">1,850<span class="mp-unit">万用户</span></div>
    </div>
  </div>

  <div class="mp-pt" style="left:61.0%; top:47.9%;">
    <span class="mp-dot" style="width:12px; height:12px;"></span>
    <div class="mp-card" data-side="right">
      <div class="mp-city">西安</div>
      <div class="mp-val">1,240<span class="mp-unit">万用户</span></div>
    </div>
  </div>

  <div class="mp-pt" style="left:79.0%; top:59.3%;">
    <span class="mp-dot" style="width:16px; height:16px;"></span>
    <div class="mp-card" data-side="right">
      <div class="mp-city">杭州</div>
      <div class="mp-val">2,680<span class="mp-unit">万用户</span></div>
    </div>
  </div>

  <div class="mp-pt" style="left:67.5%; top:59.3%;">
    <span class="mp-dot" style="width:15px; height:15px;"></span>
    <div class="mp-card" data-side="left">
      <div class="mp-city">武汉</div>
      <div class="mp-val">1,980<span class="mp-unit">万用户</span></div>
    </div>
  </div>

  <div class="mp-legend" style="position:absolute; left:24px; bottom:24px; display:flex; flex-direction:column; gap:8px; padding:14px 18px; background:linear-gradient(180deg, var(--card-bg-from), var(--card-bg-to)); border:1px solid var(--card-border); border-radius:var(--card-radius, 6px);">
    <div style="font-size:10px; color:var(--text-secondary); letter-spacing:0.16em; text-transform:uppercase;">用户规模</div>
    <div style="display:flex; align-items:center; gap:14px;">
      <span style="display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">
        <span style="width:10px; height:10px; border-radius:50%; background:var(--accent-1); opacity:0.7;"></span>1,000+
      </span>
      <span style="display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">
        <span style="width:16px; height:16px; border-radius:50%; background:var(--accent-1); opacity:0.85;"></span>3,000+
      </span>
      <span style="display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--text-secondary); font-variant-numeric:tabular-nums;">
        <span style="width:22px; height:22px; border-radius:50%; background:var(--accent-1);"></span>5,000+
      </span>
    </div>
  </div>

  <style>
    .chart-map .mp-pt {
      position: absolute;
      transform: translate(-50%, -50%);
    }
    .chart-map .mp-dot {
      position: relative;
      display: block;
      border-radius: 50%;
      background: var(--accent-1);
      opacity: 0.55;
      box-shadow: 0 0 12px var(--accent-1);
    }
    .chart-map .mp-pt[data-hl="1"] .mp-dot {
      opacity: 0.95;
      box-shadow: 0 0 18px var(--accent-1), 0 0 0 2px rgba(255,255,255,0.4);
    }
    .chart-map .mp-pulse {
      position: absolute;
      left: 50%; top: 50%;
      transform: translate(-50%, -50%);
      border-radius: 50%;
      border: 1.5px solid var(--accent-1);
      opacity: 0.4;
    }
    .chart-map .mp-card {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      padding: 6px 10px;
      background: linear-gradient(180deg, var(--card-bg-from), var(--card-bg-to));
      border: 1px solid var(--card-border);
      border-radius: 4px;
      white-space: nowrap;
      backdrop-filter: blur(4px);
    }
    .chart-map .mp-card[data-side="right"] { left: calc(100% + 14px); }
    .chart-map .mp-card[data-side="left"]  { right: calc(100% + 14px); }
    .chart-map .mp-city {
      font-size: 11px; font-weight: 600;
      color: var(--text-primary);
      letter-spacing: 0.06em;
      line-height: 1;
      margin-bottom: 4px;
    }
    .chart-map .mp-val {
      font-family: var(--display-font, var(--body-font));
      font-size: 14px; font-weight: 700;
      color: var(--accent-1);
      letter-spacing: -0.01em;
      font-variant-numeric: tabular-nums proportional-nums;
      line-height: 1;
    }
    .chart-map .mp-unit {
      font-family: var(--body-font);
      font-size: 10px;
      color: var(--text-secondary);
      font-weight: 500;
      letter-spacing: 0.04em;
      margin-left: 3px;
    }
    .chart-map .mp-pt[data-hl="1"] .mp-card {
      border-color: var(--accent-1);
      box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
  </style>
</div>
```

**SVG path 说明**：
- 主轮廓 path 是**简化示意**（约 21 个点），传达"中国大致形状"，**不是地理精确边界**。
- 海南岛是第二个独立 path。
- 需要按区域上色（choropleth）→ 见 complex.md 的「世界地图」；需要精确省界时，离线把 GeoJSON 简化成 path 再内联。

**点位定位说明**：
- 数据点用 HTML div + `position:absolute; left:N%; top:N%` 定位，**不用 SVG circle**，便于未来加 hover / 跳转 / 弹窗。
- `transform:translate(-50%, -50%)` 保证 left/top 是点中心（不是左上角）。
- 圆点尺寸映射数据量：14px (1,000-) / 16-18px (1,500-2,500) / 20-22px (3,000-4,500) / 24px+ (5,000+)。

**变体**：
- **世界地图简化版**：换 path 为简化的世界轮廓（所有大陆轮廓合并为 1 path），点位换为各大洲城市。
- **省份热力（无点）**：`<path>` 列表（每省一个），fill 由 value 映射 `var(--accent-1)` opacity。需离线把 GeoJSON 转成 path。

**自检**：
- [ ] 国家轮廓用 1 个 SVG `<path>`，简化坐标 (~50-100 字符)
- [ ] 数据点用 HTML div + `left:N%; top:N%`，不用 SVG circle
- [ ] 点尺寸映射数据量（dot diameter ∝ sqrt(value)）
- [ ] 卡片用 `data-side="right|left"` 防遮挡
- [ ] 高亮点 (`data-hl="1"`) 加 pulse 圈 + 白色 ring
- [ ] 数字 `font-variant-numeric: tabular-nums`
- [ ] Legend 在左下角说明圆点尺寸-数据量映射
- [ ] 复杂边界场景（省界 / 国界精确）→ 转用 complex.md

---

## 通用调整建议

### 颜色映射快速参考

| 角色 | 变量 | 用途 |
|------|------|------|
| 主数据 | `var(--accent-1)` | 主系列、高亮、KPI 数字 |
| 对比 | `var(--accent-3)` | 对照系列、流失、反向 |
| 中性 | `var(--accent-2)` | 第三系列、过渡色 |
| 警示 | `var(--accent-4)` 或 `var(--accent-3)` | 黄色警告 / 红色风险 |
| 网格 | `var(--card-border)` | 刻度线、分隔线 |
| 卡背景 | `var(--card-bg-from)` → `var(--card-bg-to)` | tooltip / 图例底框 |

### 通用排版 token

所有图表已遵守：

- 数字 `font-family: var(--display-font, var(--body-font))` + `font-variant-numeric: tabular-nums proportional-nums`
- 维度名 / 类别名 `letter-spacing: 0.04-0.08em` (正文) 或 `0.12-0.18em` (大写小标)
- 数据标签 `font-size: 11-13px`（次要）/ `16-22px`（主要）
- 单位 `font-size: 10-11px`，`color: var(--text-secondary)`

### 排错速查

| 问题 | 原因 | 修复 |
|------|------|------|
| PPT 中数字偏移 | 用了 SVG `<text>` | 改 HTML span 叠加 |
| 数字宽度跳变 | 漏写 `tabular-nums` | 加上 `font-variant-numeric` |
| 颜色不随风格切换 | 硬编码颜色 | 全部换 `var(--accent-X)` |
| 仪表盘弧不显示 | 用了 conic-gradient | 改 SVG path A 命令 |
| 漏斗梯形消失 | 用了 CSS border 三角形 | 改 SVG `<polygon>` |
| 地图点位漂移 | 用了 SVG circle + viewBox 缩放 | 改 HTML div + `left:N%` |

---

> 见 [basic.md](basic.md)（8 种基础图表）和 [complex.md](complex.md)（4 种复杂图表）。
