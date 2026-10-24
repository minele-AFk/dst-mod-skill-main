# 世界系统模式

当任务涉及常见的世界端游戏系统而不是单个狭窄组件时，请使用此文件。

本页面关注官方高频系统，这些系统通常一起出现在预制件中：

- `fueled`
- `burnable`
- `freezable`
- `lootdropper`
- `trader`
- `hauntable`
- `corruption`（原版当前主要用于 King Cane 的腐化状态）
- `deployable`

如果任务主要涉及从 `scripts/standardcomponents.lua` 选择 `Make*` 辅助构造函数，还请阅读 `references/patterns/prefab/standard-helper-patterns.md`。

首先从官方组件文件中读取确切的签名。
然后检查以相同方式组合它们的最接近的官方预制件。

## 为什么存在此页面

这些系统非常常见，以至于 mod 任务通常听起来像：

- "这个结构应该接受燃料"
- "这个植物应该燃烧并掉落战利品"
- "这个生物应该正确冻结"
- "这个物体应该可以被附身"
- "这个物品应该部署成一个结构"
- "这个 NPC 应该接受交易物品"

官方模式通常依赖于组件组合，而不是单个组件。

## `fueled`

官方文件：

- `scripts/components/fueled.lua`

高频方法：

- `SetSectionCallback(fn)`
- `SetDepletedFn(fn)`
- `SetSections(num)`
- `CanAcceptFuelItem(item)`
- `SetCanTakeFuelItemFn(fn)`
- `SetTakeFuelItemFn(fn)`
- `TakeFuelItem(item, doer)`
- `SetUpdateFn(fn)`
- `GetPercent()`
- `SetPercent(amount)`
- `StartConsuming()`
- `StopConsuming()`
- `DoDelta(amount, doer)`

使用场景：

- 存储和消耗燃料的结构或物品
- 具有可见燃料状态的机器
- 电池状或燃烧时间游戏系统

重要区别：

- `fuel`
  - 作为燃料消耗的物品
- `fueled`
  - 接受和消耗燃料的目标

观察到的官方模式：

- `winona_battery_low.lua`
  - 具有分段视觉状态和更新的 fueled 目标

常见陷阱：

- 不要混淆 `fuel` 和 `fueled`
- 如果 fueled 物品也有可见状态，也要检查其 `AnimState` 或 netvar 路径
- 如果燃料可以通过物品使用添加，除了组件本身，动作路由也很重要

## `burnable`

官方文件：

- `scripts/components/burnable.lua`

高频方法：

- `SetOnSmolderingFn(fn)`
- `SetOnStopSmolderingFn(fn)`
- `SetOnIgniteFn(fn)`
- `SetOnBurntFn(fn)`
- `SetOnExtinguishFn(fn)`
- `SetBurnTime(time)`
- `IsBurning()`
- `IsSmoldering()`
- `Ignite(immediate, source, doer)`
- `SmotherSmolder(smotherer)`
- `Extinguish(resetpropagator, heatpct, smotherer)`
- `AddBurnFX(prefab, offset, followsymbol, followaschild, scale, followlayered)`

来自 `scripts/standardcomponents.lua` 的高频辅助函数：

- `MakeSmallBurnable(...)`
- `MakeMediumBurnable(...)`
- `MakeLargeBurnable(...)`
- 角色特定的 burnable 辅助函数

使用场景：

- 可燃物品或结构
- 阴燃和点火流程
- 火焰特效和燃烧完成回调

观察到的官方组合：

- `backpack.lua`
  - `container` + `burnable` + propagator + hauntable 掉落行为
- `treasurechest.lua`
  - `container` + `workable` + `lootdropper` + burnable 结构处理

常见陷阱：

- 优先使用 `MakeSmallBurnable` 或其兄弟函数，而不是手动构建设置
- 结构通常需要与松散物品不同的燃烧行为
- 燃烧经常改变战利品、打开的容器或视觉状态，因此也要检查预制件回调

## `freezable`

官方文件：

- `scripts/components/freezable.lua`

高频方法：

- `SetResistance(resist)`
- `SetDefaultWearOffTime(wearofftime)`
- `AddShatterFX(prefab, offset, followsymbol)`
- `SpawnShatterFX()`
- `IsFrozen()`
- `IsThawing()`
- `AddColdness(coldness, freezetime, nofreeze)`
- `Freeze(freezetime)`
- `Unfreeze()`
- `Thaw(thawtime)`

来自 `scripts/standardcomponents.lua` 的高频辅助函数：

- `MakeTinyFreezableCharacter(...)`
- `MakeSmallFreezableCharacter(...)`
- `MakeMediumFreezableCharacter(...)`
- `MakeLargeFreezableCharacter(...)`

使用场景：

- 可以被冻结或解冻的生物
- 寒冷积累
- 冻结特定特效和消退时间

观察到的官方模式：

- `spiderden.lua`
  - 冻结和解冻行为与 `AnimState`、声音和符号覆盖绑定

常见陷阱：

- 冻结行为通常包括 SG、声音和动画后果，而不仅仅是组件调用
- 尽可能使用适合尺寸的辅助函数

## `lootdropper`

官方文件：

- `scripts/components/lootdropper.lua`

高频方法：

- `SetChanceLootTable(name)`
- `SetLoot(loots)`
- `SetLootSetupFn(fn)`
- `AddRandomLoot(prefab, weight)`
- `AddChanceLoot(prefab, chance)`
- `GenerateLoot()`
- `SpawnLootPrefab(lootprefab, pt, linked_skinname, skin_id, userid)`
- `DropLoot(pt, prefabs)`

使用场景：

- 生物死亡掉落
- 结构破坏掉落
- 随机掉落表

观察到的官方模式：

- `treasurechest.lua`
  - `container` + `workable` + `lootdropper` 用于锤子和破坏流程

常见陷阱：

- 如果破坏或工作完成也应该掉落存储的内容，也要检查容器拆除流程
- 掉落回调通常属于预制件级别的破坏逻辑，而不仅仅是 `lootdropper`

## `trader`

官方文件：

- `scripts/components/trader.lua`

高频方法：

- `Enable()`
- `Disable()`
- `SetAcceptTest(fn)`
- `SetAbleToAcceptTest(fn)`
- `SetOnAccept(fn)`
- `SetOnRefuse(fn)`
- `SetAcceptStacks()`
- `AbleToAccept(item, giver, count)`
- `WantsToAccept(item, giver, count)`
- `AcceptGift(giver, item, count)`

使用场景：

- 接受礼物或交易物品的 NPC 或结构
- 自定义接受规则
- 接受时和拒绝时的行为

常见陷阱：

- 接受流程通常还取决于 `GIVE` 等动作路由
- 如果交易目标有对话或特效，也要检查 `talker`、`lootdropper` 或预制件回调

## `hauntable`

官方文件：

- `scripts/components/hauntable.lua`

高频方法：

- `SetOnHauntFn(fn)`
- `SetOnUnHauntFn(fn)`
- `SetHauntValue(val)`
- `Panic(panictime)`
- `DoHaunt(doer)`

来自 `scripts/standardcomponents.lua` 的高频辅助函数：

- `MakeHauntable(...)`
- `MakeHauntableLaunch(...)`
- `MakeHauntableWork(...)`
- `MakeHauntableIgnite(...)`
- `MakeHauntableLaunchAndDropFirstItem(...)`
- 其他 `MakeHauntable*` 组合

使用场景：

- 幽灵交互
- 恐慌、发射、点燃、工作或变形附身效果

观察到的官方组合：

- `backpack.lua`
  - `MakeHauntableLaunchAndDropFirstItem(inst)`
- `berrybush.lua`
  - `MakeHauntableIgnite(inst)` 加上自定义附身反应

常见陷阱：

- 如果标准辅助函数已经匹配预期的附身行为，请优先使用它
- 在当前的 `scripts/standardcomponents.lua` 中，`MakeHauntableWork(...)` 和 `MakeHauntableIgnite(...)` 保持其 `#HAUNTFIX` 逻辑被注释并返回 `false`
- 不要假设辅助函数名称本身保证了有效的工作或点燃行为
- 仅当官方辅助函数系列不够时才使用自定义附身回调
- `haunted` 事件只在 `onhaunt` 返回真后推送；失败回调不会推统一事件，但仍会把 `haunted` 字段置真以启动冷却/表现，供 `StopHaunt` 收尾
- `itemmimic` 会在 `DoHaunt` 中提前转为敌对并返回，不经过统一的 `haunted` 事件分支；不要用该事件监听所有附身结果

## `corruption`

官方文件：

- `scripts/components/corruption.lua`

高频方法：

- `IsCorrupted()`
- `GetCurrent()`
- `SetCurrent(current)`
- `DoDelta(delta)`
- `SetOnCurrentFn(fn)`
- `SetOnCorruptedFn(fn)`
- `SetOnUncorruptedFn(fn)`
- `MakeCorrupted()`
- `MakeUncorrupted()`
- `OnTargetCorruptable(target, doer)`
- `OnUntargetCorruptable(target, doer)`
- `CorruptEnt(target, doer)`

当前原版实现把“已腐化”的阈值绑定到 `TUNING.KING_CANE_MAX_CORRUPTION`，并新增 fissure 与 chesspiece 的即时事件分支。它适合参考通用状态、目标关系与移除顺序，不是可直接改名为任意“诅咒值”的通用组件。

- 达到阈值时 `MakeCorrupted` 添加 `corrupted` tag、把当前值置为上限、停止周期更新并调用腐化回调。
- `SetCurrent` 在已腐化后忽略写入；值降为 0 时清除衰减计时并停止更新。
- `MakeUncorrupted` 只在当前已腐化时执行：移除 tag、清零当前值与衰减计时，再调用回调；已经未腐化时不会重复回调。
- 移除组件先解除当前腐化目标，再尝试退出腐化，因此目标事件与自身状态要分别验证。
- `OnTargetCorruptable` 对带 `chess_moonevent` 的目标推送 `forcechessstruggle=true`，解除目标关系时推送 false。这个布尔与目标事件成对维护；目标已失效时不能补推事件，但组件仍应清掉自己的目标引用。
- Fissure 分支只有 `shadowthrallmanager:ControlFissure(target)` 返回成功后，才登记矿井冷却并放电；失败必须返回 false 且不消耗冷却。成功门控、目标控制事件和资源冷却的顺序应作为一个事务检查。

若项目要复用组件名，先评估它是否与官方 King Cane 依赖和数值共享；更稳妥的做法是复制协议到自己的组件，使用项目 namespace、独立阈值和持久化 schema，而不是直接改共享 TUNING。

## `deployable`

官方文件：

- `scripts/components/deployable.lua`

高频方法：

- `SetDeployMode(mode)`
- `GetDeployMode()`
- `SetDeploySpacing(spacing)`
- `SetUseGridPlacer(usegridplacer)`
- `SetDeployTossSymbolOverride(data)`
- `IsDeployable(deployer)`
- `CanDeploy(pt, mouseover, deployer, rot)`
- `Deploy(pt, deployer, rot)`

使用场景：

- 放置结构或世界对象的物品
- 部署间距和部署模式规则
- 物品到世界的转换

常见陷阱：

- 可部署物品逻辑通常还需要配方或放置器对齐
- 预览行为通常取决于 `MakePlacer(...)` 或放置配置，而不仅仅是 deployable 组件

## 常见世界系统组合

- 可燃存储结构
  - `container` + `workable` + `lootdropper` + `burnable`
- 可穿戴可燃容器
  - `inventoryitem` + `equippable` + `container` + `burnable`
- 可收获世界植物
  - `pickable` + `inspectable` + 通常 `workable` + `lootdropper` + `burnable`
- 燃料驱动机器
  - `fueled` + 可见动画/状态更新 + 通常 `inspectable`
- 可被附身物品或结构
  - 正常游戏组件集 + 匹配所需幽灵效果的 `hauntable` 辅助函数
- 可部署放置物品
  - `inventoryitem` + `deployable` + 放置器/配方对齐

## 实用阅读顺序

1. 阅读确切的组件文件。
2. 如果可能存在辅助函数，阅读 `scripts/standardcomponents.lua`。
3. 阅读组合相同系统的最接近的官方预制件。
4. 如果视觉效果重要，也要检查动画或特效处理。
5. 如果玩家交互重要，也要检查动作路由。

当前源码锚点：`components/hauntable.lua:82-115`（事件与字段不同步），`components/corruption.lua:1-199`（状态、目标关系和回调）。源码只证明当前顺序与分支，未运行附身或腐化测试。

## 经验法则

- 对于 burnable、freezable 和 hauntable 行为，优先使用官方辅助构造函数。
- 使用组件组合作为推理单位，而不是孤立的组件。
- 当破坏、燃烧或收获改变存储内容或战利品时，完整检查预制件拆除路径。
