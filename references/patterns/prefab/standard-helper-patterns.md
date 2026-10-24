# 标准辅助函数模式

当任务主要涉及从 `scripts/standardcomponents.lua` 选择或应用 `Make*` 辅助构造函数时，请使用此文件。

阅读 `references/signatures/helper-signatures.md` 获取确切的参数顺序。
当任务主要涉及组件行为而非辅助函数选择时，阅读 `references/patterns/world-system-patterns.md`。

## 本页面存在的原因

许多 DST 预制件不仅仅由原始组件组装而成。
它们还依赖于辅助构造函数，例如：

- `MakeInventoryPhysics(...)`
- `MakeInventoryFloatable(...)`
- `MakeSmallBurnable(...)`
- `MakeObstaclePhysics(...)`
- `MakeSnowCoveredPristine(...)`

辅助函数的选择通常决定了标签、碰撞组、动画行为或隐藏默认值。

## 物理辅助函数

在 `scripts/standardcomponents.lua` 中观察到：

- `MakeInventoryPhysics(...)`
  - 物品碰撞组
  - 球体物理
  - 与世界、障碍物和小障碍物碰撞
- `MakeProjectilePhysics(...)`
  - 物品碰撞组
  - 仅地面碰撞掩码
- `MakeCharacterPhysics(...)`
  - 角色碰撞组
  - 胶囊物理
  - 也与角色和巨人碰撞
- `MakeObstaclePhysics(...)`
  - 添加 `blocker` 标签
  - 静态障碍物物理
- `MakeSmallObstaclePhysics(...)`
  - 添加 `blocker` 标签
  - 小障碍物碰撞组
- `MakeHeavyObstaclePhysics(...)`
  - 添加 `blocker` 标签
  - 用于重型可举起障碍物

实用后果：

- 不要仅仅因为两者都"需要碰撞"就对生物或建筑使用物品物理
- 障碍物辅助函数已经添加了高频 `blocker` 标签
- `MakeHeavyObstaclePhysics(...)` 不仅仅是"更强的障碍物物理"；官方注释说要将其与 `heavyobstaclephysics` 组件配对

观察到的官方示例：

- `scripts/prefabs/spear.lua`
  - `MakeInventoryPhysics(inst)`
- `scripts/prefabs/berrybush.lua`
  - `MakeSmallObstaclePhysics(inst, .1)`
- `scripts/prefabs/treasurechest.lua`
  - `MakeHeavyObstaclePhysics(inst, SUNKEN_PHYSICS_RADIUS)`

## `MakeInventoryFloatable(...)`

在 `scripts/standardcomponents.lua` 和 `scripts/components/floater.lua` 中观察到：

- 添加 `floater` 组件
- 配置大小、垂直偏移和缩放
- 可选的 `swap_bank` 在漂浮时启用特殊的 `floating_item` bank
- `float_index` 选择暂停帧和侧面
- 可选的 `swap_data` 控制漂浮时恢复或覆盖的 bank、动画和符号

实用后果：

- 此辅助函数不仅仅是"显示水花特效"
- 官方物品通常在 `SetPristine()` 之前调用它，因为 floater 也管理客户端可见行为
- 如果物品需要特殊的漂浮符号或返回时使用不同的默认 bank，请查看 `swap_data`

观察到的官方示例：

- `scripts/prefabs/spear.lua`
  - `MakeInventoryFloatable(inst, "med", 0.05, {1.1, 0.5, 1.1}, true, -9)`
- `scripts/prefabs/backpack.lua`
  - `MakeInventoryFloatable(inst, "small", 0.2, nil, nil, nil, swap_data)`

良好规则：

- 普通图标或拾取物使用简单的大小和偏移
- 当预制件从漂浮模式返回时需要特定的 bank 或符号时，使用 `swap_data`

## 可燃烧和传播器辅助函数

在 `scripts/standardcomponents.lua` 中观察到：

- 可燃烧辅助函数添加组件、燃烧特效级别、燃烧时间和默认的点燃/熄灭/烧毁回调
- 传播器辅助函数添加热量接受、闪点处理和默认传播数值

实用后果：

- 如果目标是普通的可燃烧物品或建筑，请从辅助函数开始，而不是重建整个燃烧回调链
- 建筑燃烧行为通过 `structure` 参数与松散物品燃烧行为不同

观察到的官方示例：

- `scripts/prefabs/backpack.lua`
  - `MakeSmallBurnable(inst)`
  - `MakeSmallPropagator(inst)`
- `scripts/prefabs/berrybush.lua`
  - `MakeLargeBurnable(inst)`
  - `MakeMediumPropagator(inst)`

## 雪和季节辅助函数

在 `scripts/standardcomponents.lua` 中观察到：

- `MakeSnowCoveredPristine(...)`
  - 覆盖 `snow` 符号
  - 添加 `SnowCovered` 标签
  - 隐藏雪层
- `MakeSnowCovered(...)`
  - 根据世界状态显示或隐藏雪层
  - 也可能在联网主模拟预制件上附加月雹堆积处理
- `MakeNoGrowInWinter(...)`
  - 监视 `iswinter`
  - 期望预制件已拥有 `pickable` 组件

实用后果：

- `MakeSnowCoveredPristine(...)` 和 `MakeSnowCovered(...)` 通常是一对
- 当雪符号必须在客户端上存在时，在 `SetPristine()` 之前调用 pristine 辅助函数
- 仅在 `pickable` 组件存在后调用 `MakeNoGrowInWinter(...)`

观察到的官方示例：

- `scripts/prefabs/berrybush.lua`
  - 在 `SetPristine()` 之前调用 `MakeSnowCoveredPristine(inst)`
  - 稍后在主路径上调用 `MakeSnowCovered(inst)` 和 `MakeNoGrowInWinter(inst)`

## 可闹鬼辅助函数现实

在当前 `scripts/standardcomponents.lua` 中观察到：

- `MakeHauntableLaunch(...)` 主动发射物品
- `MakeHauntableLaunchAndDropFirstItem(...)` 广泛用于容器
- `MakeHauntableWork(...)` 包含 `#HAUNTFIX` 注释逻辑，当前返回 `false`
- `MakeHauntableIgnite(...)` 包含 `#HAUNTFIX` 注释逻辑，当前返回 `false`

实用后果：

- 不要假设每个闹鬼辅助函数家族成员都同样"活跃"
- 发射式辅助函数是稳定的参考
- 工作或点燃辅助函数必须针对当前官方源代码和目标预制件进行验证
- 如果期望的幽灵交互必须肯定有效，请检查预制件是否还添加了自定义闹鬼反应或自定义 `hauntable` 回调

观察到的官方示例：

- `scripts/prefabs/backpack.lua`
  - `MakeHauntableLaunchAndDropFirstItem(inst)`
- `scripts/prefabs/berrybush.lua`
  - `MakeHauntableIgnite(inst)`
  - 加上 `AddHauntableCustomReaction(inst, OnHaunt, false, false, true)`

## 快速导航

- "这是一个松散的物品栏物品"
  - 从 `MakeInventoryPhysics(...)` 开始
- "这应该漂浮在海洋中"
  - 添加 `MakeInventoryFloatable(...)`
- "这在世界中阻挡移动"
  - 选择障碍物或重型障碍物物理，而不是物品物理
- "这应该正常燃烧"
  - 从可燃烧辅助函数加上匹配的传播器辅助函数开始
- "这应该对幽灵做出反应"
  - 验证确切的闹鬼辅助函数，而不是假设名称足够
- "这应该显示雪或在冬天停止生长"
  - 在与官方预制件相同的生命周期阶段使用雪或季节辅助函数