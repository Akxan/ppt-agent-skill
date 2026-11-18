# CSS 高级武器库（W1-W12）

> Step 5c 的进阶技法库，按需查阅。每页挑 2-3 种，相邻页的组合应该不同。
> 用之前先看下表：每种技法进可编辑 PPTX 后的结果不一样（规则见 `../pipeline-compat.md`）。

| 技法 | 进 PPTX 后 |
|------|-----------|
| W1 渐变文字 | **退化**为渐变首色，关键标题慎用 |
| W2 clip-path 裁剪 | 转图层（无文字元素整体入图；有文字的容器只烘焙背景） |
| W3 mask-image 遮罩 | 转图层 |
| W4 conic-gradient | 转图层；环形进度更推荐 SVG `stroke-dasharray`（保持矢量） |
| W5 backdrop-filter 毛玻璃 | **退化**：模糊丢失，半透明填充保留 |
| W6 mix-blend-mode | 转图层（仅对无文字元素有效） |
| W7 多层 box-shadow | **退化**：阴影丢失 |
| W8 伪元素 | 保持矢量 |
| W9 空间结构 | 9a/9e 保持矢量；9b/9c 斜切与 9d mask 转图层 |
| W10 表面材质 | 10a 噪点、10b 扫描线转图层；10c 拟态阴影丢失 |
| W11 HUD 边角 | 保持矢量 |
| W12 叙事化页脚 | 保持矢量 |

---

## W1. 渐变文字填充（标题/核心数字用）

```css
.gradient-text {
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```
**适用**：页面标题、核心 KPI 数字、封面主标题。视觉冲击力远超纯色文字。
**ADAPT**：渐变角度 90-180deg / 颜色组合 accent-1→accent-2 或 accent-1→accent-3 / 用于 text 或 data_highlight

---

## W2. clip-path 几何裁剪（卡片/色块用）

```css
/* 底部斜切 -- 制造"撕裂"动感 */
.card-sliced { clip-path: polygon(0 0, 100% 0, 100% 88%, 0 100%); }
/* 左侧斜入 -- 制造"侵入"感 */
.card-invade { clip-path: polygon(5% 0, 100% 0, 100% 100%, 0 100%); }
/* 菱形裁切 -- 装饰元素用 */
.diamond { clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); }
```
**适用**：对比页中推荐方案的卡片、章节封面的装饰色块、accent 色带。
**ADAPT**：斜切角度 / 裁切方向（底/左/右/对角） / 裁切比例 80%-95%

---

## W3. mask-image 穿孔遮罩（氛围层用）

```css
.mask-spotlight {
  background: var(--bg-primary);
  mask-image: radial-gradient(ellipse 300px 250px at 65% 40%, transparent 100%, black 101%);
  -webkit-mask-image: radial-gradient(ellipse 300px 250px at 65% 40%, transparent 100%, black 101%);
}
```
**适用**：封面/结束页的聚光灯效果，数据页的焦点穿孔。
**ADAPT**：椭圆尺寸 200-500px / 焦点位置 / 方向（径向/线性消融）

---

## W4. conic-gradient 锥形渐变（环形图/进度用）

```css
.ring-progress {
  width: 80px; height: 80px; border-radius: 50%;
  background: conic-gradient(var(--accent-1) 0% 20%, rgba(255,255,255,0.08) 20% 100%);
  mask: radial-gradient(circle 28px, transparent 100%, black 101%);
  -webkit-mask: radial-gradient(circle 28px, transparent 100%, black 101%);
}
```
**适用**：data 卡片中的百分比可视化、评分指示器。
**ADAPT**：环宽（mask circle 半径） / 填充百分比 / 颜色

---

## W5. backdrop-filter 毛玻璃（glass card_style 用）

```css
.card-glass {
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.06);
}
```
**适用**：配图页的文字覆盖层、封面/结束页的信息卡片。
**ADAPT**：blur 8-24px / saturate 120-200% / 背景透明度 0.02-0.08

---

## W6. mix-blend-mode 混合模式（水印/装饰用）

```css
.watermark-blend {
  mix-blend-mode: overlay; /* 或 soft-light / screen */
  color: var(--accent-1);
  opacity: 0.06;
}
```
**适用**：让水印/装饰元素与背景产生"化学反应"而非简单叠加。
**ADAPT**：blend 模式（overlay/soft-light/screen/multiply） / opacity 0.03-0.10

---

## W7. box-shadow 多层阴影（elevated 卡片用）

```css
.card-elevated {
  box-shadow:
    0 1px 2px rgba(0,0,0,0.1),
    0 4px 8px rgba(0,0,0,0.08),
    0 12px 24px rgba(0,0,0,0.12),
    0 24px 48px rgba(0,0,0,0.06);
  transform: translateY(-4px);
}
/* accent 卡片的发光阴影 */
.card-accent-glow {
  box-shadow:
    0 4px 12px rgba(245,197,24,0.15),
    0 12px 32px rgba(245,197,24,0.1),
    inset 0 1px 0 rgba(255,255,255,0.15);
}
```
**适用**：每页的 elevated/accent 卡片。4 层阴影比 1 层阴影质感提升 5 倍。
**ADAPT**：阴影层数 2-4 / 偏移方向 / accent 发光色跟随变量 / 深色底强化或弱化

---

## W8. 伪元素高级用法（装饰/标记/叠层）

```css
/* 卡片左上角的分类角标 */
.card::before {
  content: attr(data-label);
  position: absolute; top: -1px; left: 16px;
  font-size: 10px; font-weight: 700; letter-spacing: 1px;
  background: var(--accent-1); color: var(--bg-primary);
  padding: 2px 10px; border-radius: 0 0 6px 6px;
}
/* 引用标记的大引号 */
.quote-card::before {
  content: '\201C';
  position: absolute; top: -12px; left: 16px;
  font-size: 80px; line-height: 1; color: var(--accent-1);
  opacity: 0.15; font-family: Georgia, serif;
}
/* 卡片底部的渐隐分隔线 */
.card::after {
  content: '';
  position: absolute; bottom: 0; left: 10%; right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent-1), transparent);
  opacity: 0.2;
}
```
**适用**：角标标记、引用装饰、精致分隔线、装饰性几何形状。
**ADAPT**：伪元素用途（角标/引号/分隔线/形状） / 位置 / 颜色 / 透明度

---

## W9. 空间结构技法（让空间本身叙事）

> 作用于卡片/元素的形状和位置，而非装饰细节。从根本上打破"矩形盒子在 Grid 格子里排列"的结构平庸。

```css
/* 9a. 数字脱框——核心数据裸露在空间中，不在任何卡片容器内 */
.hero-number-naked {
  position: absolute;
  top: 100px; left: 60px;
  font-size: 120px; font-weight: 900;
  color: var(--accent-1);
  line-height: 0.85;
  text-shadow: 0 0 80px rgba(245,197,24,0.12);
  z-index: 4;
  /* 没有 background、没有 padding、没有 border-radius -- 数字裸露 */
}

/* 9b. 卡片斜切——clip-path 制造非矩形边缘 */
.card-slash-bottom { clip-path: polygon(0 0, 100% 0, 100% 88%, 0 100%); }
.card-slash-left { clip-path: polygon(6% 0, 100% 0, 100% 100%, 0 100%); }

/* 9c. 出血色带——冲出画布两侧边缘 */
.bleed-band {
  position: absolute;
  left: -40px; right: -40px;
  height: 64px;
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  clip-path: polygon(2% 0, 100% 20%, 98% 100%, 0 80%);
}

/* 9d. 消融边缘——卡片一侧渐隐消失而非硬切 */
.card-fade-right {
  mask-image: linear-gradient(90deg, black 60%, transparent 100%);
  -webkit-mask-image: linear-gradient(90deg, black 60%, transparent 100%);
}

/* 9e. 装饰做减法——一个大几何形状取代 N 个小点缀 */
.deco-mega-circle {
  position: absolute;
  top: -100px; right: -80px;
  width: 500px; height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--accent-1), transparent 70%);
  opacity: 0.05; z-index: 1;
}
```
**适用**：
- **9a 数字脱框**：含核心 KPI 的页面
- **9b-9d 斜切/出血/消融**：每 3-4 页至少 1 次非矩形元素
- **9e 装饰减法**：5+ 小装饰 → 换 1 个大几何形状
**ADAPT**：子技法自由组合 / 脱框数字字号 80-160px / 斜切角度 / 出血量 -20~-60px / 消融方向

---

## W10. 表面材质（让画面有触觉）

> 通过 CSS/SVG 制造材质纹理，让画面从"平面屏幕"变成"有物理存在的介质"。

```css
/* 10a. SVG 噪声纹理——宣纸/磨砂/胶片颗粒感 */
.texture-grain {
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch"/></filter><rect width="200" height="200" filter="url(%23n)" opacity="0.08"/></svg>');
  /* baseFrequency: 0.3=粗砂岩 / 0.8=细宣纸 / 1.5=胶片颗粒 */
  /* opacity: 0.04-0.12 */
}

/* 10b. 扫描线——CRT 显示器 / 仪表盘 */
.texture-scanlines::after {
  content: '';
  position: absolute; inset: 0;
  background: repeating-linear-gradient(0deg, transparent 0, rgba(0,0,0,0.15) 1px, transparent 2px);
  background-size: 100% 3px;
  opacity: 0.3; pointer-events: none; z-index: 1;
}

/* 10c. 拟态凹凸——从平面中压出/凸起形状 */
.neumorphic-raised {
  background: var(--bg-secondary); border-radius: 16px;
  box-shadow: 6px 6px 12px rgba(0,0,0,0.12), -6px -6px 12px rgba(255,255,255,0.08);
}
.neumorphic-inset {
  background: var(--bg-secondary); border-radius: 16px;
  box-shadow: inset 4px 4px 8px rgba(0,0,0,0.1), inset -4px -4px 8px rgba(255,255,255,0.06);
}
```
**适用**：10a 文化/学术/高端品牌 / 10b 科技/数据/监控 / 10c 极简设计增加微妙 Z 轴
**ADAPT**：材质类型选择 / baseFrequency 控制粗细 / 扫描线密度 / 凹凸方向和强度

---

## W11. HUD 边角框定（取景器/技术图纸/蓝图感）

```css
.hud-frame::before,
.hud-frame::after {
  content: '';
  position: absolute;
  width: 28px; height: 28px;
  border-color: var(--accent-1);
  border-style: solid;
  opacity: 0.4; z-index: 2;
}
.hud-frame::before {
  top: 20px; left: 20px;
  border-width: 2px 0 0 2px; /* 左上角 */
}
.hud-frame::after {
  bottom: 20px; right: 20px;
  border-width: 0 2px 2px 0; /* 右下角 */
}
```
**适用**：封面页、数据仪表盘页、结论页。边角线粗细/颜色/虚实跟随风格 DNA。
**ADAPT**：角线尺寸 20-40px / 线宽 1-3px / 虚线 dashed vs 实线 / 颜色跟随 accent / 2 角 vs 4 角 / 加 border-radius 弧形化

---

## W12. 叙事化页脚（让功能元素参与故事）

> 页码不只是数字，它可以是叙事的一部分。

```css
/* 12a. 终端状态栏 -- 科技/数据主题 */
.footer-terminal {
  position: absolute; bottom: 20px; left: 24px;
  font-size: 11px; font-family: 'Courier New', monospace;
  color: var(--accent-1); opacity: 0.6; letter-spacing: 1px;
  /* 内容：STATUS: ACTIVE | SECTION: 02 | PAGE: 03/12 */
}

/* 12b. 印章/徽记 -- 国风/文化/正式场合 */
.footer-seal {
  position: absolute; bottom: 24px; right: 32px;
  width: 56px; height: 24px;
  background: var(--accent-1); color: var(--bg-primary);
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--accent-2); border-radius: 2px; opacity: 0.8;
}

/* 12c. 刻度尺/进度条 -- 流程/时间线主题 */
.footer-progress {
  position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
  background: var(--bg-secondary);
}
.footer-progress::after {
  content: '';
  position: absolute; left: 0; top: 0; height: 100%;
  width: calc(var(--progress, 25) * 1%);
  background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
}
```
**适用**：根据 `design_soul` 自由选择页脚人格。把页码从"功能角落"变成"设计收尾笔触"。
**ADAPT**：页脚类型（终端/印章/进度条） / 位置 / 内容格式 / 颜色跟随 accent
