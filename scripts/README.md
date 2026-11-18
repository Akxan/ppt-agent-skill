# Scripts 索引

## 导出（Step 6）

| 脚本 | 用途 |
|------|------|
| `html_packager.py` | 多页 HTML -> 单文件翻页预览 `preview.html` |
| `html2svg.py` | HTML -> SVG。文字保留为 `<text>`；dom-to-svg 画不出的效果先截成图层；给卡片打成组标记 |
| `svg2pptx.py` | SVG -> 可编辑 PPTX。原生形状、文本框、卡片组合、页间切换、卡片入场动画 |
| `pptx_motion.py` | 切换与动画的 PresentationML 构造（被 `svg2pptx.py` / `png2pptx.py` 调用） |
| `html2png.py` | HTML -> PNG 截图（图审、像素级保真版） |
| `png2pptx.py` | PNG -> 整页图片 PPTX（不可编辑，支持页间切换） |

## 合同与校验

| 脚本 | 用途 |
|------|------|
| `contracts.py` | 单一真源：页面类型、版式、卡片类型、页面密度、图表注册表、风格字段与 CSS 变量映射、管线兼容规则 |
| `validate.py` | 严格模式入口：`outline` / `planning` / `style` / `slides` / `visual` / `all` |
| `resource_loader.py` | 资源路由：`menu` 列出可选项，`resolve` 按策划稿取版式 / 组件 / 图表说明 |

## 维护工具

| 脚本 | 用途 |
|------|------|
| `smoke_test.py` | 冒烟测试：styles / mocks / charts / validators / resources / docs，`--export` 追加真实导出 |
| `gallery.py` | 生成 26 风格预览画廊 `ppt-output/style-gallery/index.html`，`--screenshots` 重新截图 |
| `build_hero.py` | 把风格截图拼成 README 用的 `assets/hero-*.png` |

## 依赖关系

```
contracts.py         -- 无依赖（标准库）
validate.py          -> contracts（visual 子命令需要 Pillow）
resource_loader.py   -> contracts, validate
smoke_test.py        -> contracts, validate, resource_loader（export 套件另需 python-pptx、Node.js）
html2svg.py          -- Node.js >= 18；首次运行把 puppeteer、dom-to-svg 装到 skill 根目录
html2png.py          -> html2svg（复用依赖目录与 node 调用）
pptx_motion.py       -- lxml
svg2pptx.py          -> pptx_motion；python-pptx、lxml、Pillow
png2pptx.py          -> pptx_motion, svg2pptx；python-pptx
gallery.py           -> contracts（--screenshots 时用 html2png / html2svg）
build_hero.py        -> contracts；Pillow
```

Python 依赖：`pip install python-pptx lxml Pillow`。
