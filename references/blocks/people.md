# people（人物组块）-- 面孔的力量

> 适用数据类型：team_profiles / user_testimonials。
> 结构：persons[]({name, title, avatar_desc, quote?})，3-6人一组。
> 设计要点：圆形头像占位+姓名+职位，引述用斜体+小字号。无真实照片时用渐变色块+首字母。
> 推荐 card_style：filled/outline。推荐布局：symmetric / three-column。

## JSON 结构
```json
{
  "card_type": "people",
  "title": "核心团队",
  "members": [
    {"name": "姓名", "title": "职位", "bio": "简介（30字内）", "avatar": true}
  ]
}
```

## 设计灵魂

### 人物展示的灵动手法
- **不要做成通讯录**：3-4 人一行等距排列 + 相同尺寸头像 + 相同格式的姓名职位 = 最无聊的人物展示
- **制造主次**：如果有核心人物（如 CEO/创始人），让其头像明显大于其他成员（120px vs 80px），位置偏离中心或独占一侧
- **参差排列**：人物可以交错排列（非严格等距），某些人物卡片稍高/稍大，制造自然的呼吸感
- **背景故事化**：头像背后可以叠加极淡的渐变色块/光晕，暗示每个人物的"个人色彩"

### 头像处理
- 圆形裁切 (border-radius:50% + overflow:hidden)
- 有头像时：3px accent 色边框，制造"被选中"的感觉
- 无头像时：首字母占位圆（accent 背景 + 白色大号字母）

### 信息层级
- 姓名 16px 700 居中 -- 最重要
- 职位 13px accent 色 -- 身份标识
- 简介 12px secondary -- 最次要，可以在空间不足时省略

### card_style
- 推荐 `transparent` card_style -- 人物组件靠面孔和排列本身构成视觉结构
