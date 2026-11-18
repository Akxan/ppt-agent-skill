# 世界级排版铁律 (Typography Bible)

> 本文件汇总所有 26 风格共享的排版规则。**每张 HTML 设计稿生成前必读**。
>
> 灵感来源：Linear / Anthropic / Stripe / Apple / Vercel / NYT Magazine / Tom Ford / Pitch / Mercury / Arc / Notion 等品牌的实际排版做法。

---

## 1. 字距铁律（Letter-Spacing）

字距按字号分级，**绝对不能"一刀切"**：

| 层级 | 字号 | letter-spacing | 用途 |
|------|------|----------------|------|
| **Display** | ≥ 48px | `-0.025em ~ -0.045em` | 封面主标题 / 大数据 |
| **Headline** | 28-44px | `-0.015em` | 页面主标题 |
| **Title** | 20-24px | `-0.01em` | 卡片标题 |
| **Body** | 13-16px | `-0.005em` 微收 | 正文段落 |
| **Caption** | 11-12px | `+0.05em` | 辅助标注 / 脚注 |
| **Overline** | 10-12px | `+0.15em ~ +0.3em` | PART 标识 / 小标 |
| **Maison label** | 10-11px | `+0.4em ~ +0.65em` | 奢华品牌签名 |

> 经验法则：字号越大字距越紧，字号越小字距越拉开。这是 Apple / Linear / Tom Ford 共同遵守的铁律。

---

## 2. 数字必须 Tabular-Nums

**所有数据数字都必须**等宽对齐，否则在 PPT 中数字跳来跳去看着廉价：

```css
.data-number {
  font-variant-numeric: tabular-nums proportional-nums;
}
```

适用范围：所有 `card_type=data` 卡片、KPI 指标、对比数据、年份/日期、价格、百分比、ID 等一切数字。

---

## 3. OpenType 特性必开

每个风格的字体调用都必须开启高级排版特性：

```css
.world-class {
  font-feature-settings: "kern", "liga", "ss01", "cv11", "calt", "ccmp";
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

| 特性 | 作用 |
|------|------|
| `kern` | 字距对（Kerning） |
| `liga` | 标准连字（fi, fl, ffi）|
| `ss01` ~ `ss20` | Stylistic Sets（不同字体支持不同集） |
| `cv01` ~ `cv99` | Character Variants（如 Inter cv11 是更现代的字母 g） |
| `calt` | 上下文替代（如箭头连字 -> →） |
| `ccmp` | 字形组合 |

---

## 4. Sans + Serif Italic 混排（签名手法）

**Linear / Stripe / Apple 都在用的隐藏招式**：标题的关键词用 serif italic 替换，瞬间提升档次。

```html
<h1 class="headline">
  Built for <em>the future.</em>
</h1>
```

```css
.headline { font-family: 'Inter Tight', sans-serif; font-weight: 600; }
.headline em {
  font-family: 'Instrument Serif', 'Fraunces', serif;
  font-style: italic;
  font-weight: 400;
  letter-spacing: -0.02em;
}
```

适用：所有暗色专业风格 + 浅色高级风格。

---

## 5. 首字下沉（Drop Cap）

杂志感、编辑感的招牌排版。适用于 `mocha_editorial` / `minimal_gray` / `noir_film` 等长正文场景。`::first-letter` 的样式进可编辑 PPTX 后会丢失，要保留首字下沉就把首字写成独立的 `<span class="drop-cap">`，用同样的规则：

```css
.body-text::first-letter, .drop-cap {
  float: left;
  font-size: 60px;
  line-height: 0.85;
  padding: 6px 10px 0 0;
  font-weight: 600;
  font-family: 'Fraunces', 'Source Serif 4', serif;
  color: var(--text-primary);
}
```

---

## 6. 不对称网格

**避免总是 50/50 居中布局**。世界级网站常用：

| 比例 | 适用 |
|------|------|
| `1fr / 1.5fr` | 标题在左，正文在右（编辑感） |
| `2fr / 3fr` | 主图在右，文字在左 |
| `1fr / 2fr / 1fr` | 三栏，中间承担主信息 |
| `auto / 1fr` | 大数字 + 解读，自适应宽度 |

留白要主动让位给主信息，不能均分。

---

## 7. 小标锚线（Label Anchor）

label 前面加 `::before` 短横线 / 小圆点，建立视觉锚点。**这是 Linear / Stripe 的招牌**：

```html
<div class="label">— Research · 2026</div>
```

```css
.label {
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--accent-1);
  font-weight: 600;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.label::before {
  content: '';
  width: 24px;
  height: 1px;
  background: currentColor;
}
```

或圆点带辉光（`dot_pulse`）：

```css
.label::before {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent-1);
  box-shadow: 0 0 8px currentColor;
}
```

---

## 8. 字体栈三层降级

每个风格的字体调用都遵循三层兜底：

```
[商业字体（用户若有授权）]
  → [Google Fonts 等价物]
  → [系统字体兜底]
```

**实战例子**：

| 角色 | 商业 | Google Fonts | 系统兜底 |
|------|------|--------------|---------|
| 现代 sans | Söhne / GT America / ABC Diatype | Inter / Inter Tight | -apple-system, BlinkMacSystemFont, sans-serif |
| 编辑器 serif | Tiempos Text / SangBleu OG | Source Serif 4 / Fraunces | Iowan Old Style, Georgia, serif |
| 显示 serif italic | Editorial New | Instrument Serif | Georgia italic |
| 时尚 serif | Didot | Playfair Display | Bodoni Moda, serif |
| Monospace | Söhne Mono / Geist Mono | JetBrains Mono / DM Mono | Courier New, monospace |
| 中文 serif | 思源宋体 | Noto Serif SC | STSong, SimSun, serif |
| 中文 sans | 苹方 / 微软雅黑（系统字体） | — | PingFang SC, Microsoft YaHei, sans-serif |

写法：

```css
font-family:
  'Söhne',                                     /* 商业 */
  'Inter Tight', 'Inter',                      /* Google */
  -apple-system, BlinkMacSystemFont,           /* 系统 */
  'Segoe UI', sans-serif;                      /* fallback */
```

---

## 9. 微妙的纹理（不能纯色无质感）

| 风格类型 | 纹理 |
|---------|------|
| 暗色 | 网格点阵 (40-80px) + 极光辉光（多层 radial-gradient） |
| 浅色高级 | 微噪点（SVG turbulence 或低 opacity 点阵） |
| 杂志 | 纸张米色背景 + 内框线 |
| 复古 | 颗粒感 + 半透明色块 |

实现：

```css
/* 暗色网格点阵 */
.dark-bg {
  background-image:
    radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 80px 80px;
}

/* 极光辉光 */
.aurora-glow::before {
  content: '';
  position: absolute; inset: 0;
  background:
    radial-gradient(circle at 80% 30%, rgba(99, 102, 241, 0.35) 0%, transparent 40%),
    radial-gradient(circle at 20% 70%, rgba(34, 211, 238, 0.25) 0%, transparent 35%);
  filter: blur(60px);
  pointer-events: none;
}
```

---

## 10. 统一的页脚系统（Footer）

每页（封面和章节封面除外）底部必须有统一页脚。**字号 11px，opacity 0.5，letter-spacing 1px**，极其低调不抢内容视线：

```html
<div class="footer">
  <span class="part-label">PART 01 — 章节名称</span>
  <span class="page-info">07 / 15  |  品牌名</span>
</div>
```

```css
.footer {
  position: absolute; bottom: 20px; left: 40px; right: 40px;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 11px;
  color: var(--text-secondary);
  opacity: 0.5;
  letter-spacing: 0.1em;
  font-family: 'Inter', sans-serif;
}
```

---

## 11. 字体导入（Font Imports）

每个风格只 `@import` 它实际用到的字体，避免每页都加载所有 Google Fonts。在 HTML `<head>` 中：

```html
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');
</style>
```

---

## 12. 中英文混排规则

- 中文和英文/数字之间**自动加一个半角空格**（如：「增长率达到 47.3%」）
- 数字推荐用 `font-variant-numeric: tabular-nums` 让数字等宽对齐
- 大号数据数字（36px+）建议用 `font-family: 'Inter Tight', 'DIN', var(--font-family)` 让数字更有冲击力
- 中文 punctuation 用全角（。，；：）
- 英文 punctuation 用半角 + 后置空格

---

## 13. 对比度安全规则

文字颜色必须与其直接背景形成足够对比度：

| 背景类型 | 文字颜色要求 |
|---------|------------|
| 深色（亮度 < 40%） | 标题用 white，正文用 70% white |
| 浅色（亮度 > 60%） | 标题用 dark，正文用 60-70% gray |
| 卡片内部 | 跟随卡片背景明暗选择 |
| accent 色文字 | 仅用于标题/标签/数据数字 |

**禁止**：
- 深色背景 + 深色文字
- 浅色背景 + 白色文字
- 硬编码颜色值（必须用 CSS 变量）

---

## 14. 排版自检 Checklist

每页 HTML 生成完，对照以下 7 条自检：

- [ ] 大字（≥48px）letter-spacing 在 -0.025em ~ -0.045em
- [ ] 小标 letter-spacing ≥ 0.15em
- [ ] 所有数字开 `font-variant-numeric: tabular-nums`
- [ ] OpenType 特性 (kern, liga) 至少开启
- [ ] 字体栈三层降级齐全（商业/Google/系统）
- [ ] 标题中关键词用 serif italic 混排（如适用）
- [ ] 页脚统一（封面/章节封面除外）
