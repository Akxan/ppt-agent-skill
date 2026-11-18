# PPT 设计原则

> 这些是演示设计领域公认的底层原则。理解"为什么"才能在没有具体规则覆盖时做出正确判断。

## 原则索引

| 文件 | 核心原则 | 来源/理论 | 策划时的一句话准则 |
|------|---------|----------|------------------|
| `visual-hierarchy.md` | 视觉层级与 CRAP | Robin Williams《写给大家看的设计书》 | 一页只能有一个视觉锚点，闭眼再睁开第一个看到的必须是最重要的信息 |
| `cognitive-load.md` | 认知负荷与信息密度 | Miller's Law / Mayer 多媒体学习理论 | 每页能用一句话总结核心信息，如果需要两句就该拆页 |
| `composition.md` | 构图与留白 | 三分法 / 格式塔心理学 | 留白不是浪费空间，微观间距 < 中观间距 < 宏观间距才能建立层级感 |
| `color-psychology.md` | 色彩心理与运用 | 60-30-10 法则 / 色彩情感映射 | 强调色是调味料不是主菜，同页最多 2 种 accent，大面积使用 = 不再是强调 |
| `data-visualization.md` | 数据可视化原则 | Edward Tufte / Stephen Few | 可视化的目标是让观众 3 秒内理解结论，不是展示数据 |
| `narrative-arc.md` | 叙事结构与节奏 | 金字塔原理 / SCQA / 故事弧线 | 禁止连续 3 页高密度或连续 3 页低密度，波浪形节奏才能维持注意力 |

## 何时读取

- **Step 4 写策划稿时**：拿不准一页放多少内容、主次怎么分，读 `cognitive-load.md` 与 `visual-hierarchy.md`
- **Step 5a 选风格时**：`color-psychology.md`
- **Step 5c 写 HTML 时**：遇到版式犹豫读 `composition.md`；图表主导的页面读 `data-visualization.md`
- **自检与返工时**：`failure-modes.md` 的 8 种失败模式与修复顺序

不需要每次全部读取，按当前卡住的问题挑对应的一份。

## 与具体规则的关系

```
原则层（principles/*.md）              = 为什么这样做   -> 没有具体规则覆盖时据此判断
规格层（design-runtime/、bento-grid）  = 具体数值与技法 -> 执行约束
组件层（layouts / blocks / charts）    = 用什么版式、组件、图表
```
