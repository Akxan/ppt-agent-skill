# quote（引用/金句块）-- 灵魂的锚点

> 适用数据类型：expert_quotes / user_testimonials。大引号+金句独立悬浮。
> 结构：quote_text + attribution(name, title, organization)。
> 设计要点：超大装饰引号(font-size:120px, opacity:0.1)、引文 font-size:28-36px、来源 font-size:14px。
> 推荐 card_style：transparent（文字靠自身重力撑住画面），1页最多1个 quote 卡。

## JSON 结构
```json
{
  "card_type": "quote",
  "content": "引用内容（50-150字）",
  "attribution": {"name": "人名", "title": "职位/机构"},
  "avatar": true
}
```

## 设计灵魂

### 金句的视觉重量
- 引用文字用 24-28px，font-weight:500，line-height:1.6 -- 让每个字都有份量
- 引号装饰用超大 div（80-120px 的 `"` 字符），accent 色极低透明度（10-15%），像一个巨大的水印衬托在文字背后
- 金句周围需要大量留白 -- 留白就是"请静听"的无声邀请

### 灵动表达的变奏
- **左侧竖线式**：3px accent 竖线贯穿引用文字左侧，来源信息在下方。庄重、权威
- **居中悬浮式**：引用文字居中排布，周围大面积留白，巨大引号在背后偏移。诗意、感性
- **偏心张力式**：引用文字贴靠画面某一侧，另一侧大面积留白 + 来源人物信息。不对称的灵动

### 来源信息
- 头像（48px 圆形裁切） + 姓名（16px 700） + 职位（13px secondary）
- 来源信息要明显弱于引用文字 -- 观众先读金句，再看是谁说的

### card_style
- 推荐 `transparent` card_style -- 金句裸露在虚空中，靠文字自身的重力撑住画面
