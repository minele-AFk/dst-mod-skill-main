# DST 模组 API 映射

将此文件用作紧凑的路由映射。
在编写代码前，从官方源代码读取确切的签名。

## `scripts/modutil.lua` 中的注册 API

- `AddPrefabPostInit`
  - 在构建后修补一个预制件。
- `AddPrefabPostInitAny`
  - 修补每个预制件，通常用于广泛的检测或标记。
- `AddPlayerPostInit`
  - 在不硬编码特定角色预制件的情况下修补玩家实例。
- `AddComponentPostInit`
  - 在组件类加载后扩展它。
- `AddBrainPostInit`
  - 修补 brain 定义。
- `AddStategraphPostInit`
  - 在状态图加载后修补它。
- `AddStategraphState`
  - 添加完整的 SG 状态对象。
- `AddStategraphEvent`
  - 添加 SG 事件处理程序。
- `AddClassPostConstruct`
  - 通过包装其构造函数来修补所需的类（如 widget 或屏幕类）。
- `AddGlobalClassPostConstruct`
  - 当类名除了包路径之外还很重要时，修补全局暴露的类。
- `AddAction`
  - 注册自定义动作。
- `AddComponentAction`
  - 将组件连接到动作收集器。
- `AddStategraphActionHandler`
  - 为状态图注册动作处理程序。
- `AddRecipe2`（推荐）
  - 注册具有现代过滤器支持的配方。
- `AddRecipe`（已弃用）
  - 旧版配方注册，建议改用 `AddRecipe2`。
- `Recipe`（已弃用）
  - 旧版配方构造函数，建议改用 `AddRecipe2`。
- `AddRecipeToFilter`
  - 将配方附加到制作过滤器。
- `AddIngredientValues`
  - 注册食材的烹饪价值（如肉、蔬菜分类）。
- `AddCookerRecipe`
  - 注册烹饪锅配方。
- `AddSimPostInit`
  - 模拟器初始化后回调，在 `TheWorld` 和 `ThePlayer` 已存在时触发。
- `AddReplicableComponent`
  - 注册 replica 端组件。
- `AddModRPCHandler`
  - 注册服务器端模组 RPC 处理程序。
- `AddClientModRPCHandler`
  - 注册客户端模组 RPC 处理程序。
- `AddModCharacter`
  - 注册模组角色及其元数据。
- `AddMinimapAtlas`
  - 显式注册小地图图集路径。
- `LoadPOFile`
  - 通过模组环境加载运行时 `.po` 翻译数据。
- `AddCustomizeGroup`
  - 注册主机可见的世界自定义组。
- `RemoveCustomizeGroup`
  - 隐藏或移除自定义组。
- `AddCustomizeItem`
  - 注册一个世界设置或世界生成自定义选项。
- `RemoveCustomizeItem`
  - 隐藏或移除一个自定义选项。

## `scripts/modutil.lua` 中的世界生成注册 API

当任务属于 `modworldgenmain.lua` 或 `modservercreationmain.lua` 而非正常游戏玩法引导时使用这些 API。

- `AddRoom`
  - 注册新的房间定义。
- `AddRoomPreInit`
  - 修补一个现有的房间定义。
- `AddTask`
  - 注册新的任务定义。
- `AddTaskPreInit`
  - 修补一个现有的任务定义。
- `AddTaskSet`
  - 注册新的任务集。
- `AddTaskSetPreInit`
  - 修补一个现有的任务集。
- `AddTaskSetPreInitAny`
  - 修补所有任务集。
- `AddLevel`
  - 注册新的关卡定义。
- `AddLevelPreInit`
  - 修补一个现有的关卡定义。
- `AddLevelPreInitAny`
  - 修补所有关卡。
- `AddStartLocation`
  - 注册世界生成的起始位置。
- `AddLocation`
  - 注册生成侧数据使用的位置条目。

自定义侧路由：

- `AddCustomizeGroup` 和 `AddCustomizeItem`
  - 通过 `scripts/map/customize.lua` 路由
  - 通常影响主机设置 UI 和预设数据
- `AddStartLocation`
  - 通过 `scripts/map/startlocations.lua` 路由
  - 也通过 `startlocations.GetGenStartLocations` 出现在世界自定义 UI 中

## `scripts/entityscript.lua` 中的实例方法

当模式依赖于运行时行为而非加载器 API 时，使用 `EntityScript` 方法。

- Tags 和组件
  - `AddTag`
  - `RemoveTag`
  - `HasTag`
  - `AddComponent`
  - `RemoveComponent`
- 事件和任务
  - `ListenForEvent`
  - `PushEvent`
  - `PushEventImmediate`
  - `DoTaskInTime`
  - `DoPeriodicTask`
- 子实体和所有权
  - `SpawnChild`
  - `AddChild`
  - `RemoveChild`
- Brains 和 SG
  - `SetBrain`
  - `RestartBrain`
  - `StopBrain`
  - `SetStateGraph`
  - `ClearStateGraph`
- 动作
  - `PushBufferedAction`
  - `PerformBufferedAction`
  - `SetInherentSceneAction`
  - `SetInherentSceneAltAction`

## `scripts/standardcomponents.lua` 中的设置助手

在手动编写常见预制件设置之前，先阅读此文件。

- 燃烧和火焰传播
  - `MakeSmallBurnable`
  - `MakeMediumBurnable`
  - `MakeLargeBurnable`
  - `MakeSmallPropagator`
  - `MakeMediumPropagator`
  - `MakeLargePropagator`
- 冰冻助手
  - `MakeTinyFreezableCharacter`
  - `MakeSmallFreezableCharacter`
  - `MakeMediumFreezableCharacter`
  - `MakeLargeFreezableCharacter`
- 物理助手
  - `MakeInventoryPhysics`
  - `MakeProjectilePhysics`
  - `MakeCharacterPhysics`
  - `MakeFlyingCharacterPhysics`
  - `MakeObstaclePhysics`
  - `MakeHeavyObstaclePhysics`
- 闹鬼助手
  - `MakeHauntable`
  - `MakeHauntableLaunch`
  - `MakeHauntableWork`
  - `MakeHauntableIgnite`
  - `MakeHauntableChangePrefab`
- 杂项助手
  - `MakeInventoryFloatable`
  - `MakeDeployableFertilizer`
  - `MakeForgeRepairable`
  - `MakeWaxablePlant`

## 加载器和元数据文件

- `scripts/mods.lua`
  - 用于加载顺序、`PrefabFiles`、`Assets` 和 `modmain.lua` 执行流程。
- `scripts/modindex.lua`
  - 用于 `modinfo.lua` 期望，如 API 版本、兼容性标志和配置选项。
- `scripts/mainfunctions.lua`
  - 用于预制件注册和资源路径解析。

## 经验法则

- 如果任务以"修补现有事物"开头，从 `modutil.lua` 和具体的官方目标文件开始。
- 如果任务以"为什么此实例表现如此"开头，从 `entityscript.lua` 和相关组件文件开始。
- 如果任务以"设置新预制件"开头，从类似的官方预制件和 `standardcomponents.lua` 开始。
- 如果任务依赖于服务器或客户端上下文，在编写代码前阅读 `references/core/dst-lua-runtime/references/module-environments.md`。
- 如果任务依赖于世界生成、预设或主机设置，也请阅读 `references/patterns/world/worldgen-patterns.md`。
- 如果任务主要关于 SG 路由、预测或执行器状态，也请阅读 `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`。
- 如果任务主要关于复制实现形式，也请阅读 `references/core/dst-networking-rpc/references/network-contract.md`。
- 如果任务主要关于光照、特效预制件、粒子或声音助手，也请阅读 `references/patterns/asset/effects-patterns.md`。

## 高频官方组件

当任务以其中一个组件为中心时，首先阅读确切的组件文件：

- `inspectable`
  - `scripts/components/inspectable.lua`
- `inventoryitem`
  - `scripts/components/inventoryitem.lua`
- `stackable`
  - `scripts/components/stackable.lua`
- `finiteuses`
  - `scripts/components/finiteuses.lua`
- `inventory`
  - `scripts/components/inventory.lua`
- `container`
  - `scripts/components/container.lua`
- `edible`
  - `scripts/components/edible.lua`
- `cookable`
  - `scripts/components/cookable.lua`
- `fuel`
  - `scripts/components/fuel.lua`
- `tool`
  - `scripts/components/tool.lua`
- `pickable`
  - `scripts/components/pickable.lua`
- `workable`
  - `scripts/components/workable.lua`
- `timer`
  - `scripts/components/timer.lua`
- `talker`
  - `scripts/components/talker.lua`
- `health`
  - `scripts/components/health.lua`
- `hunger`
  - `scripts/components/hunger.lua`
- `sanity`
  - `scripts/components/sanity.lua`
- `combat`
  - `scripts/components/combat.lua`
- `equippable`
  - `scripts/components/equippable.lua`
- `armor`
  - `scripts/components/armor.lua`
- `weapon`
  - `scripts/components/weapon.lua`

也请阅读 `references/component-patterns.md` 获取实用路由和常见组合。