# 官方示例索引

当你已经了解子系统，但仍需要一个具体的官方 DST 示例作为起点时使用此文件。

本页面是一个快速示例路由器，不是更窄的模式页面的替代品。
选择一个接近的官方文件，阅读它，然后深入到解释底层模式的子系统页面。

## 物品和装备示例

- `scripts/prefabs/spear.lua`
  - 简单武器物品
- `scripts/prefabs/armor_grass.lua`
  - 简单可穿戴护甲
- `scripts/prefabs/backpack.lua`
  - 可穿戴容器
- `scripts/prefabs/treasurechest.lua`
  - 带容器和可加工流程的箱子结构
- `scripts/prefabs/berrybush.lua`
  - 可采摘世界植物
- `scripts/prefabs/coldfirepit.lua`
  - 带燃烧和燃料相关行为的发光结构
- `scripts/prefabs/winona_battery_low.lua`
  - 燃料驱动的机器、辅助实体、声音循环和更丰富的结构设置

接下来阅读：

- `references/component-patterns.md`
- `references/patterns/world-system-patterns.md`
- `references/patterns/asset/animstate-patterns.md`

## 引导和注册示例

- `scripts/mods.lua`
  - mod 环境设置、`modimport(...)`、`modmain.lua`、`PrefabFiles` 和 mod 级 `Assets` 的加载器流程
- `scripts/modutil.lua`
  - `modmain.lua` 通常调用的注册 API
- `scripts/prefabs/staff.lua`
  - 分组的 prefab 文件家族，展示引导后 `PrefabFiles` 可以指向的内容

接下来阅读：

- `references/core/dst-mod-scaffolding/references/entrypoints.md`
- `references/patterns/startup/modmain-patterns.md`
- `references/core/dst-prefab-authoring/references/prefab-contract.md`

## 生物、大脑和状态机示例

- `scripts/prefabs/glommer.lua`
  - 带大脑和状态机连接的生物 prefab
- `scripts/brains/glommerbrain.lua`
  - 紧凑的行为树示例
- `scripts/stategraphs/SGglommer.lua`
  - 匹配的执行侧状态机
- `scripts/prefabs/player_common.lua`
  - 玩家侧状态机和网络连接
- `scripts/stategraphs/SGwilson.lua`
  - 权威玩家动作状态
- `scripts/stategraphs/SGwilson_client.lua`
  - 预测玩家动作状态

接下来阅读：

- `references/gameplay/dst-brain-authoring/references/brain-node-behaviour-quickref.md`
- `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`
- `references/core/dst-networking-rpc/references/network-contract.md`

## 可玩角色和技能树示例

- `scripts/modutil.lua`
  - `AddModCharacter(...)` 注册和可选的 mod 角色模式存储
- `scripts/prefabs/player_common.lua`
  - 共享玩家角色构造函数、客户端/服务端分离和基线玩家系统
- `scripts/prefabs/wilson.lua`
  - 带 `common_postinit` 和 `master_postinit` 的紧凑原版角色示例
- `scripts/prefabs/wormwood.lua`
  - 带自定义资产和技能树资产注册的更丰富角色示例
- `scripts/prefabs/skilltree_defs.lua`
  - 中央技能树注册表、验证助手和 `CreateSkillTreeFor(...)`
- `scripts/prefabs/skilltree_wilson.lua`
  - 角色本地技能树数据模块
- `scripts/screens/lobbyscreen.lua`
  - `images/names_<character>.xml` 和 `bigportraits/...` 的前端消费者
- `scripts/screens/redux/serverslotscreen.lua`
  - mod 角色存档槽肖像查找
- `scripts/widgets/inventorybar.lua`
  - 自检头像查找
- `scripts/widgets/redux/loadoutselect.lua`
  - 通过 `MODCHARACTERMODES` 的 mod 角色预览模式路由
- `scripts/widgets/skinspuppet.lua`
  - 皮肤模式的衣柜木偶构建和动画选择
- `scripts/skinsutils.lua`
  - 默认 `GetSkinModes(...)` 数据和带皮肤角色助手
- `scripts/widgets/redux/skilltreewidget.lua`
  - 技能树背景图片契约
- `scripts/widgets/redux/skilltreebuilder.lua`
  - 技能树图标查找契约

接下来阅读：

- `references/patterns/character/character-patterns.md`
- `references/patterns/runtime-i18n-patterns.md`
- `references/patterns/recipe/recipe-patterns.md`

## 玩家范围补丁示例

- `scripts/modutil.lua`
  - `AddPlayerPostInit(...)` 通过 `AddPrefabPostInitAny(...)` 加上 `player` 标签实现
- `scripts/prefabs/player_common.lua`
  - 玩家基线设置、`common_postinit`、`master_postinit` 和玩家生命周期事件

接下来阅读：

- `references/patterns/player-patterns.md`
- `references/patterns/network/player-network-patterns.md`
- `references/core/dst-hooking-compatibility/GUIDE.md`
- `references/world-ui-assets/dst-hud-screens-input/references/hud-customization.md`
- `references/core/dst-lua-runtime/references/module-environments.md`

## 皮肤系统示例

- `scripts/prefabskin.lua`
  - `CreatePrefabSkin(...)` 和共享皮肤辅助函数
- `scripts/prefabskins.lua`
  - 生成的 `PREFAB_SKINS` 和 `PREFAB_SKINS_IDS`
- `scripts/prefabs/skinprefabs.lua`
  - 生成的基础皮肤和物品皮肤数据
- `scripts/skinsutils.lua`
  - 皮肤数据查找、构建名称解析、肖像命名和皮肤模式
- `scripts/widgets/redux/loadoutselect.lua`
  - mod 角色预览模式和原版角色基础皮肤 UI 行为
- `scripts/screens/redux/defaultskinselection.lua`
  - 所有权门控皮肤列表构建

接下来阅读：

- `references/patterns/skin/skin-patterns.md`
- `references/patterns/character/character-patterns.md`
- `references/core/dst-prefab-authoring/references/prefab-contract.md`

## 标准助手示例

- `scripts/standardcomponents.lua`
  - 官方 `Make*` 助手定义
- `scripts/prefabs/spear.lua`
  - `MakeInventoryPhysics(...)`、`MakeInventoryFloatable(...)` 和 `MakeHauntableLaunch(...)`
- `scripts/prefabs/backpack.lua`
  - `MakeInventoryFloatable(...)`、可燃烧或传播器助手，以及 `MakeHauntableLaunchAndDropFirstItem(...)`
- `scripts/prefabs/berrybush.lua`
  - 障碍物物理、积雪覆盖助手、季节性生长助手和作祟自定义反应
- `scripts/prefabs/treasurechest.lua`
  - 结构侧可燃烧设置和重型障碍物物理

接下来阅读：

- `references/patterns/prefab/standard-helper-patterns.md`
- `references/patterns/world-system-patterns.md`
- `references/signatures/helper-signatures.md`

## 特效、光照和声音示例

- `scripts/prefabs/moon_altar.lua`
  - 发光世界结构
- `scripts/prefabs/lighterfire_common.lua`
  - 带复制范围的子光照助手
- `scripts/prefabs/moose_nest_fx.lua`
  - 一次性 FX prefab 和代理式触发器
- `scripts/prefabs/deer_fx.lua`
  - 带可选光照和声音的共享 FX 工厂
- `scripts/prefabs/atrium_gate_pulsesfx.lua`
  - 仅声音代理模式
- `scripts/prefabs/torchfire_barber.lua`
  - `AddVFXEffect()` 粒子系统

接下来阅读：

- `references/patterns/asset/effects-patterns.md`
- `references/patterns/prefab/tag-patterns.md`
- `references/patterns/asset/asset-patterns.md`

## UI 和前端示例

- `scripts/widgets/controls.lua`
  - 持久 HUD 子所有权
- `scripts/screens/playerhud.lua`
  - 玩家 HUD 生命周期和屏幕拥有的 UI 流程
- `scripts/widgets/containerwidget.lua`
  - 带每次打开监听器和清理的瞬时打开或关闭 widget
- `scripts/screens/redux/popupdialog.lua`
  - 带 `default_focus`、`OnControl(...)` 和 `Close()` 的紧凑模态屏幕
- `scripts/widgets/screen.lua`
  - 基础屏幕生命周期、焦点恢复和 `OnBecomeActive()` 或 `OnBecomeInactive()`
- `scripts/screens/redux/servercreationscreen.lua`
  - 服务器设置屏幕流程
- `scripts/frontend.lua`
  - 屏幕堆栈、顶级输入管道、淡入淡出流程和前端声音助手

接下来阅读：

- `references/world-ui-assets/dst-ui-widget-authoring/GUIDE.md`
- `references/patterns/ui/ui-patch-patterns.md`
- `references/pitfalls/ui-pitfalls.md`
- `references/core/dst-hooking-compatibility/GUIDE.md`
- `references/patterns/runtime/input-patterns.md`
- `references/world-ui-assets/dst-hud-screens-input/references/hud-customization.md`

## 动作和交互示例

- `scripts/componentactions.lua`
  - 官方动作收集器和动作类型路由
- `scripts/stategraphs/SGwilson.lua`
  - 玩家执行者侧动作状态
- `scripts/stategraphs/SGwilson_client.lua`
  - 预测客户端执行者状态
- `scripts/modutil.lua`
  - mod 侧动作注册 API

接下来阅读：

- `references/core/dst-action-authoring/references/action-pipeline.md`
- `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`

## 网络和分类示例

- `scripts/entityreplica.lua`
  - replica 加载和 `AddReplicableComponent(...)` 路径
- `scripts/prefabs/player_common.lua`
  - 玩家侧网络和分类附加流程
- `scripts/prefabs/player_classified.lua`
  - 大型分类实体示例
- `scripts/components/inventory_replica.lua`
  - replica 侧 API 和分类附加模式
- `scripts/networkclientrpc.lua`
  - RPC 命名空间和 ID 路由

接下来阅读：

- `references/core/dst-networking-rpc/references/network-contract.md`
- `references/core/dst-networking-rpc/references/network-contract.md`
- `references/patterns/network/player-network-patterns.md`
- `references/core/dst-lua-runtime/references/module-environments.md`

## 保存、加载和离线进度示例

- `scripts/entityscript.lua`
  - 核心保存和加载生命周期：`GetPersistData()`、`SetPersistData()`、`LoadPostPass()`、`LongUpdate()`
- `scripts/components/childspawner.lua`
  - 保存引用加上 `LoadPostPass(...)` 引用修复
- `scripts/components/slingshotmods.lua`
  - 通过 `GetPersistData()` 和 `SetPersistData(...)` 的嵌套辅助持久数据
- `scripts/prefabs/player_common.lua`
  - 玩家上的特殊情况嵌套保存记录
- `scripts/prefabs/winona_battery_low.lua`
  - `OnLoadPostPass(...)` 用于加载后重新连接
- `scripts/components/timer.lua`
  - 计时器持久化加上 `LongUpdate(dt)`
- `scripts/components/pickable.lua`
  - 通过 `LongUpdate(dt)` 的再生追赶

接下来阅读：

- `references/core/dst-persistence-migration/references/persistence-contract.md`
- `references/core/dst-persistence-migration/references/persistence-contract.md`
- `references/patterns/diagnostic-patterns.md`

## 持久字符串和本地配置文件存储示例

- `scripts/mainfunctions.lua`
  - `SavePersistentString(...)` 和 `ErasePersistentString(...)` 包装 `TheSim`
- `scripts/util/savedata.lua`
  - 带脏标志、加载、保存和擦除流程的可重用持久文件包装器
- `scripts/generickv.lua`
  - 通过一个文件持久化的简单键值存储
- `scripts/craftingmenuprofile.lua`
  - 保存为 JSON 的本地制作 UI 首选项
- `scripts/plantregistrydata.lua`
  - 使用 `DataDumper(...)` 保存的较大本地注册表数据
- `scripts/skilltreedata.lua`
  - 在一个世界保存之外持久化的本地配置文件进度数据

接下来阅读：

- `references/patterns/persistence/persistent-string-patterns.md`
- `references/core/dst-persistence-migration/references/persistence-contract.md`
- `references/patterns/startup/modinfo-patterns.md`

## 保护调用和安全解码示例

- `scripts/craftingmenuprofile.lua`
  - 围绕 JSON 解码的 `pcall(...)`，用于持久本地 UI 配置文件数据
- `scripts/screens/modsscreen.lua`
  - 围绕远程 JSON 解码的 `pcall(...)`
- `scripts/screens/multiplayermainscreen.lua`
  - 围绕缓存 MOTD JSON 解码的 `pcall(...)`
- `scripts/screens/redux/multiplayermainscreen.lua`
  - 围绕来自通用 KV 的存储 JSON 的 `pcall(...)`
- `scripts/tools/getmissingstrings.lua`
  - `pcall(require, ...)` 用于可选语音文件
- `scripts/screens/worldgenscreen.lua`
  - 围绕带回退的 JSON 编码的 `xpcall(..., generic_error)`

接下来阅读：

- `references/patterns/network/protected-call-patterns.md`
- `references/patterns/persistence/persistent-string-patterns.md`
- `references/patterns/diagnostic-patterns.md`

## 世界碎片和迁移示例

- `scripts/prefabs/world.lua`
  - `TheWorld.ismastershard` 设置
- `scripts/prefabs/world_network.lua`
  - 世界侧碎片客户端运行时
- `scripts/prefabs/shard_network.lua`
  - 碎片侧运行时聚合对象
- `scripts/components/worldmigrator.lua`
  - 传送门可用性和迁移激活
- `scripts/components/playerspawner.lua`
  - 玩家迁移保存和生成流程
- `scripts/components/recallmark.lua`
  - 同一碎片与不同碎片标记存储
- `scripts/components/shard_players.lua`
  - 主碎片集群玩家计数聚合
- `scripts/components/shardtransactionsteps.lua`
  - 健壮的碎片到碎片传输参考

接下来阅读：

- `references/patterns/network/shard-patterns.md`
- `references/core/dst-persistence-migration/references/persistence-contract.md`
- `references/core/dst-networking-rpc/references/network-contract.md`

## 世界生成和预设示例

- `scripts/map/rooms.lua`
  - 房间注册和重复名称行为
- `scripts/map/tasks.lua`
  - 任务注册和重复名称行为
- `scripts/map/tasksets.lua`
  - 任务集定义
- `scripts/map/startlocations.lua`
  - 起始位置注册和前端刷新
- `scripts/map/customize.lua`
  - 主机可见的世界自定义项和类别
- `scripts/map/levels.lua`
  - 预设 ID、列表和组合预设组成
- `scripts/screens/redux/servercreationscreen.lua`
  - 主机面对的世界设置流程

接下来阅读：

- `references/patterns/world/worldgen-patterns.md`
- `references/task-playbook.md`

## 文本和本地化示例

- `scripts/strings.lua`
  - 全局 `STRINGS` 树形结构
- `scripts/stringutil.lua`
  - 运行时字符串查找行为
- `scripts/translator.lua`
  - `TranslateStringTable(...)`
- `scripts/languages/loc.lua`
  - 官方区域设置加载和翻译流程
- `scripts/modutil.lua`
  - mod 暴露的 `LoadPOFile(...)`

接下来阅读：

- `references/patterns/runtime-i18n-patterns.md`
- `references/patterns/runtime-i18n-patterns.md`
- `references/patterns/startup/modinfo-patterns.md`

## 实用规则

- 使用本页面选择最接近的官方起始文件。
- 然后切换到更窄的参考页面获取实际实现规则。
- 当一个接近的示例已经匹配请求的类型时，不要阅读五个官方示例。
