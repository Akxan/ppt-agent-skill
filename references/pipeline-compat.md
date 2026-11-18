# HTML -> SVG -> PPTX 管线兼容性

写 HTML 设计稿时要知道：哪些效果进 PPTX 后仍是可编辑的形状和文字，哪些会变成图片，哪些会丢。本文件的结论都来自用真实 PowerPoint 渲染对照浏览器截图的实测，规则的代码真源是 `scripts/contracts.py` 里的 `COMPAT_RULES`。

预览页（`preview.html`）和像素级保真版（`presentation-hd.pptx`）不经过这条管线，任何 CSS 都原样保留。以下只针对可编辑的 `presentation.pptx`。

---

## 1. 管线怎么处理一页

1. `html2svg.py` 用 Puppeteer 打开 HTML，先把 dom-to-svg 画不出来的绘制**截成图层**嵌回页面，再调用 dom-to-svg 输出 SVG（文字是 `<text>`）
2. `svg2pptx.py` 把 SVG 逐元素翻成 PowerPoint 原生形状、文本框和图片，卡片打成组合，写入切换与动画

---

## 2. 三类结果

### A. 保持矢量（PPT 里可编辑）

| 写法 | 进 PPTX 后 |
|------|-----------|
| 纯色 / `linear-gradient` 背景的块、边框、圆角 | 矩形 / 圆角矩形，渐变填充 |
| 文字：字号、字重、斜体、字距、颜色、透明度、竖排（`writing-mode`） | 文本框，逐行定位 |
| `::before` / `::after`（纯色块、文字内容） | 与普通元素相同 |
| 内联 SVG：`rect` `circle` `ellipse` `line` `polygon` `polyline` `path`（含弧线 A 与曲线 C/S/Q/T） | 对应形状或自定义路径 |
| SVG 环形进度：`fill="none"` + `stroke-dasharray="弧长 周长"` | 弧形，起始角按 `rotate` 换算 |
| `<img>`（本地路径或 data URI），`object-fit` | 图片，cover 时居中裁剪 |
| `opacity`（元素或祖先） | 形状/图片透明度 |
| CSS border 三角形（宽高为 0） | 三角形路径 |

### B. 自动转图层（外观保真，但这一块在 PPT 里是图片）

| 写法 | 说明 |
|------|------|
| `radial-gradient` / `conic-gradient` / `repeating-*-gradient` / 多层背景 | 最常见：页面氛围背景、光晕、纹理 |
| CSS `background-image: url(...)` | |
| `filter`（blur 等）、`mask-image`、`clip-path`、`mix-blend-mode` | |
| `transform` 含旋转或斜切 | 印章、倾斜徽标 |
| 被祖先 `overflow: hidden` 裁掉一部分的装饰元素 | PPT 没有裁剪，只能整体入图 |
| 内联 SVG 含 `filter` `pattern` `mask` `clipPath` `use`，或描边用了带透明色标的渐变 | 整个 `<svg>` 入图 |

怎么入图取决于元素里有没有文字：

- **没有文字的装饰元素**：整棵子树截成一张透明图
- **有文字的容器**（如带径向背景的卡片、`body`）：只把背景、边框和伪元素烘焙成图，里面的文字仍是可编辑文本框
- **旋转的元素**：连文字一起入图

想强制把某个元素整体转成图片（比如特别复杂的图表），给它加 `data-pptx="raster"`。

### C. 会丢失或退化

| 写法 | 结果 | 建议 |
|------|------|------|
| `text-shadow` | 丢失 | 不要靠辉光保证文字可读 |
| `background-clip: text` 渐变文字 | 变成渐变的第一个颜色 | 关键标题直接用 `color` |
| `backdrop-filter` | 模糊丢失，半透明填充保留 | 玻璃卡片可用，但别依赖模糊做对比 |
| `box-shadow` | 丢失（元素本身被转图层时除外） | |
| `::first-letter` / `::first-line` / `::marker` | 样式丢失 | 首字下沉用独立 `<span>` |
| 带文字的容器上的 `filter` / `mask` / `mix-blend-mode` | 效果丢失，文字与背景保留 | 把效果放到没有文字的子元素上 |
| `overflow: hidden` 对文字的裁剪 | 不裁剪，文字完整显示 | 控制字数，不要靠裁剪藏文字 |
| `stroke-dashoffset` | 被忽略 | 环形图用 `stroke-dasharray="弧长 周长"` |
| 内联 SVG 里的 `<text>` | 可编辑，但位置可能偏 3-5px | 标注用 HTML 元素叠在 SVG 上 |
| 网页字体 | 默认映射到 Office 自带字体并按宽度缩字号 | 见第 4 节 |

### D. 禁止

| 写法 | 原因 |
|------|------|
| `<script>` | 幻灯片必须是静态 HTML；预览页的沙箱 iframe 不执行脚本 |
| `@keyframes` / `animation` | 转换只取静态一帧。动效用 `svg2pptx.py --animate` |
| `<canvas>` / `<video>` / `<iframe>` | 不会被转换 |
| 远程图片（`http://...`） | 不会嵌入 PPTX，先下载到 `images/` |

---

## 3. 写法约定

**卡片根节点打标记**——导出时据此打成组合、做入场动画：

```html
<div class="card" data-card-id="s03-revenue">...</div>
```

没写 `data-card-id` 时，退而识别 class 以 `card` 结尾的最外层元素（`card`、`stat-card`、`glass-card`）。

**环形图**——SVG 只画弧，中心文字用 HTML 叠加：

```html
<div style="position:relative; width:120px; height:120px;">
  <svg viewBox="0 0 120 120" style="width:100%; height:100%;">
    <circle cx="60" cy="60" r="50" fill="none" stroke="var(--card-border)" stroke-width="8"/>
    <!-- 弧长 = 2πr × 百分比，周长 = 2πr；rotate(-90) 让起点在 12 点钟 -->
    <circle cx="60" cy="60" r="50" fill="none" stroke="var(--accent-1)" stroke-width="8"
            stroke-dasharray="235 314" stroke-linecap="round" transform="rotate(-90 60 60)"/>
  </svg>
  <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center;">
    <div style="font-size:22px; font-weight:700;">75%</div>
  </div>
</div>
```

**图表的轴标签、图例、数据标注**——用 HTML `<span>` / `<div>` 绝对定位叠在 SVG 上，不写 SVG `<text>`。

**配图**——用 `<img>` 加 `object-fit: cover`；渐隐用盖在图上的 `linear-gradient` 遮罩 `<div>`。

---

## 4. 字体

PowerPoint 只能用打开文件那台机器上装了的字体，Google Fonts 多数人没装。`svg2pptx.py` 的两种策略：

| `--fonts` | 行为 | 适用 |
|-----------|------|------|
| `safe`（默认） | 按字体栈的类别映射到 Office 自带字体：无衬线 -> Arial，衬线 -> Georgia，等宽 -> Courier New，粗黑展示体 -> Arial Black；中文 -> 微软雅黑 / 宋体 / 楷体。替换后比网页字体宽时自动缩字号，避免相邻文字相撞 | 要发给别人的文件 |
| `design` | 保留字体栈里的第一个字体名 | 放映机器上装了设计字体 |

---

## 5. 切换与动画

| 能力 | 参数 | 说明 |
|------|------|------|
| 页间切换 | `--transition fade`（默认）`push` `wipe` `cover` `split` `zoom` `dissolve` `none` | 写入每页的进入效果 |
| 自动翻页 | `--advance-after 秒数` | 默认仅点击翻页 |
| 卡片入场 | `--animate fade` `wipe` `rise` `zoom`（默认 `none`） | 按卡片在 HTML 里的先后顺序 |
| 触发方式 | `--animate-trigger click`（默认）/ `auto` | 每点一下出一张 / 进入页面后依次自动出现 |

入场动画作用在卡片组合上，所以页面必须有带标记的卡片。动画在 PowerPoint 里验证过；WPS、Keynote、Google Slides 对动画的支持不完整。

---

## 6. 写完一页后的检查

- [ ] 画布 1280x720，没有 `<script>`、CSS 动画、`<canvas>`
- [ ] 卡片根节点带 `class="card"` 和 `data-card-id`
- [ ] 关键文字不依赖 text-shadow、渐变填充或 `overflow` 裁剪
- [ ] 图表标注是 HTML 元素，环形图用 `stroke-dasharray` 两值写法
- [ ] 图片是本地文件

机器检查：`python3 scripts/validate.py slides OUTPUT_DIR/slides`。ERROR 对应 D 类，WARN 对应 C 类，INFO 列出会转图层的 B 类写法。
