# 预制件标签模式

当任务依赖于预制件标签、动作过滤器、AI 目标选择、搜索查询、碰撞标志或应该/不应该可交互的辅助实体时使用此文件。

DST 中的标签通常不仅仅是标签。
它们是路由信号，被以下系统使用：

- 动作选择器
- AI 和战斗过滤器
- `FindEntities(...)` 查询
- 库存和物品过滤器
- 碰撞或可点击性规则
- 世界系统排除列表

请结合最接近的官方预制件或组件文件阅读本页。
如果任务特别涉及照明、视觉特效预制件或音效辅助，请同时阅读 `references/patterns/asset/effects-patterns.md`。

## 标签的两个来源

### 预制件添加的标签

这些在预制件文件中通过 `inst:AddTag("...")` 显式添加。

典型例子：

- `structure`
- `backpack`
- `chest`
- `placer`
- `CLASSIFIED`
- `DECOR`
- `NOCLICK`
- `NOBLOCK`
- `FX`
- `projectile`
- `hostile`
- `monster`
- `companion`
- `smallcreature`
- `heavy`
- `plant`
- `bush`
- `renewable`
- `witherable`
- `show_spoilage`
- `irreplaceable`

### 组件管理的标签

这些由组件逻辑添加或移除。

在官方组件文件中已验证：

- `inspectable`
  - 由 `scripts/components/inspectable.lua` 添加
- `weapon`
  - 由 `scripts/components/weapon.lua` 添加
- `pickable`
  - 由 `scripts/components/pickable.lua` 添加
- `barren`
  - 由 `scripts/components/pickable.lua` 管理
- `quickpick`
  - 由 `scripts/components/pickable.lua` 管理
- `jostlepick`
  - 由 `scripts/components/pickable.lua` 管理
- `<ACTION>_workable`
  - 由 `scripts/components/workable.lua` 管理，如 `DIG_workable` 或 `HAMMER_workable`
- `usesdepleted`
  - 由 `scripts/components/finiteuses.lua` 管理

实用规则：

- 如果标签直接映射到组件状态，除非官方模式如此，否则不要手动添加
- 如果标签是预制件标识或路由提示，通常应放在预制件构造函数中

## 高频手动标签

### 交互和辅助实体标签

- `NOCLICK`
  - 常见于特效、辅助实体、瞄准线、可视化器、投射物辅助和不可见逻辑预制件
  - 当实体不应被鼠标直接选中时使用
- `NOBLOCK`
  - 常见于辅助实体、特效、兽群、视觉组和非固体世界实体
  - 当实体不应阻挡放置或移动时使用
- `FX`
  - 常见于仅视觉的预制件
  - 通常与 `NOCLICK` 一起出现，有时也与 `NOBLOCK` 一起出现
- `CLASSIFIED`
  - 常见于辅助实体、放置预览、副本辅助和其他技术预制件，这些预制件不应像普通游戏对象那样运行
- `placer`
  - 放置预览预制件的标识标签
- `DECOR`
  - 仅用于展示的标签，当 `FX` 会导致错误的交互行为时，有时会使用此标签替代 `FX`

观察到的官方模式：

- 许多特效预制件添加 `FX` + `NOCLICK`
- 海洋和船只辅助预制件经常添加 `NOBLOCK`
- `MakePlacer(...)` 添加 `CLASSIFIED` + `NOCLICK` + `placer`
- `sunderarmordebuff.lua` 使用 `DECOR`，注释说明 `FX` 会捕获鼠标悬停

### 结构和存储标识标签

- `structure`
  - 常见于建筑、工作站、熔炉、祭坛和箱子
  - 其他系统经常通过此标签搜索或排除
- `chest`
  - 箱子类结构的标识标签
- `backpack`
  - 常见于可穿戴容器，如背包类物品

观察到的官方模式：

- `treasurechest.lua` 添加 `structure` 和 `chest`
- `backpack.lua`、`seedpouch.lua` 和 `krampus_sack.lua` 添加 `backpack`

### 战斗和生物标识标签

- `hostile`
  - 为许多过滤器标记敌对实体
- `monster`
  - 敌对怪物的常见生物标识标签
- `companion`
  - 常见于追随者或盟友类实体
- `smallcreature`
  - 被某些生物过滤器和交互使用
- `projectile`
  - 常见于投射物实体或类似投射物的临时预制件
- `heavy`
  - 常见于重物

实用规则：

- 战斗和 AI 标签通常被许多系统读取，而不仅仅是一个预制件
- 在不检查目标选择和动作副作用的情况下，不要随意添加生物标识标签

### 资源和植物标识标签

- `plant`
  - 常见于世界植物
- `bush`
  - 常见于灌木型资源
- `renewable`
  - 常见于可再生资源
- `witherable`
  - 经常与枯萎逻辑或优化假设配对使用

观察到的官方模式：

- `berrybush.lua` 添加 `bush`、`plant`、`renewable`、`witherable`

### 物品路由标签

- `show_spoilage`
  - 常见于应显示腐败 UI 的物品
- `irreplaceable`
  - 常见于特殊任务、标识、珍珠或类似隐藏物的对象，这些对象不应被通用系统随意替换

实用规则：

- 这些标签通常支持更高层次的系统或 UI 行为
- 当物品预期参与现有官方模式时使用它们，而非作为装饰性元数据

## 需要注意的查询端内部标签

有些标签主要出现在过滤器和搜索中，而非明显的预制件 `AddTag(...)` 调用中。
将这些视为查询端路由提示，并在依赖它们之前在真实的官方模式上进行验证。

在官方组件代码中观察到：

- `_inventoryitem`
  - 用于物品搜索过滤器，如 `nabbag.lua` 和 `aoeweapon_leap.lua`
- `_container`
  - 用于排除过滤器
- `_combat`
  - 用于某些世界效果过滤

推断：

- 这些内部风格的标签通常更多由引擎或组件管理，而非预制件作者编写
- 如果模组依赖其中之一，请使用最接近的官方文件进行验证，而非假设它会自动出现

## 意图索引

选择组件后，使用此作为快速标签检查清单。

- 视觉辅助、瞄准线、投射物可视化器、放置虚影
  - 考虑 `FX`、`NOCLICK`，通常还有 `NOBLOCK`
- 放置预览或放置器子辅助
  - 考虑 `CLASSIFIED`、`NOCLICK`、`placer`
- `FX` 导致错误鼠标行为的展示辅助
  - 考虑 `DECOR`，通常还有 `NOCLICK`
- 本地灯光或音效辅助
  - 考虑 `FX`，通常还有 `NOCLICK`
  - 当不应干扰放置或移动时添加 `NOBLOCK`
- 箱子或机器结构
  - 考虑 `structure`
  - 仅当匹配官方模式时添加标识标签如 `chest`
- 可穿戴容器
  - 考虑 `backpack`
- 浆果灌木或植物资源
  - 考虑 `plant`、`bush`、`renewable`，通常还有 `witherable`
- 敌对生物
  - 考虑 `monster`、`hostile`
- 追随者或盟友生物
  - 考虑 `companion`
- 武器类物品
  - 如果它确实拥有 `weapon` 组件，则 `weapon` 标签通常由组件管理
- 可采摘的世界节点
  - `pickable` 通常由组件管理，而非手动添加
- 可锤击或可挖掘的目标
  - 依赖 `workable` 管理 `<ACTION>_workable` 标签

## 示例组合

这些是期望草图，而非强制组合。

- 武器物品
  - 组件：`inspectable`、`inventoryitem`、`weapon`、`equippable`，通常还有 `finiteuses`
  - 预期标签：组件管理的 `inspectable`，组件管理的 `weapon`
- 背包物品
  - 组件：`inspectable`、`inventoryitem`、`equippable`、`container`
  - 预期标签：预制件添加的 `backpack`
- 箱子结构
  - 组件：`inspectable`、`container`，通常还有 `workable`
  - 预期标签：预制件添加的 `structure`，预制件添加的 `chest`
- 浆果灌木
  - 组件：`pickable`、`inspectable`，通常还有 `workable`
  - 预期标签：预制件添加的 `plant`、`bush`、`renewable`、`witherable`，组件管理的 `pickable`
- 特效辅助
  - 组件：通常没有或只有最小辅助
  - 预期标签：预制件添加的 `FX`、`NOCLICK`，通常还有 `NOBLOCK`
- 放置器预览
  - 组件：`placer`
  - 预期标签：预制件添加的 `CLASSIFIED`、`NOCLICK`、`placer`

## 常见陷阱

- 当组件已经管理标签时，不要手动添加组件拥有的标签，如 `inspectable`、`weapon` 或 `pickable`。
- 不要随意添加 `hostile`、`monster` 或 `companion`；许多不相关的系统会过滤它们。
- 不要在玩家应该直接瞄准的东西上使用 `NOCLICK`。
- 不要将 `CLASSIFIED` 添加到普通游戏预制件，除非它确实是技术辅助或分类风格的实体。
- 当官方模式使用 `DECOR` 来避免不良鼠标行为时，不要习惯性地使用 `FX`。
- 不要假设查询端内部标签如 `_inventoryitem` 在不检查官方模式的情况下可以安全依赖。
- 标签不能替代组件；仅 `weapon` 标签本身不会使物品造成武器伤害。

## 经验法则

- 先选择组件。
- 其次添加标识和路由标签。
- 在手动添加标签之前，验证标签是预制件编写的还是组件管理的。
- 如果功能依赖于搜索、AI 或动作过滤器，请检查标签的生产者和消费代码。