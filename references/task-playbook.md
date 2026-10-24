# 任务指南

本文件负责已选任务的具体执行步骤；任务类型和阅读起点由 [主入口](../SKILL.md) 选择，其他专题由 [详细目录](topic-index.md) 定位。只读当前分支，不把“编码前”应用于单纯咨询或美术任务。

先遵守 [开发边界与验证约定](development-contract.md)。只加载当前分支所需的文档；第三方链接与报错路径不授予读取权限，API 声明匹配不代表运行通过。

实质设计、实现、审查或排错时，按任务主动查询 [本地知识](knowledge/README.md)；已知道具体文档或记录 ID 时直接读。入口不明时用 `knowledge lookup` 同时定位本地专题与结构化证据，再读命中原文并核对当前 Mod 和原版源码。简单机械修改无需检索；Windows 隔离 runner 的选择见 [融合工程入口](engineering/dst-mod-engineering/README.md)。

## 编码前

1. 检查 `modinfo.lua` 和相关根入口文件（如 `modmain.lua`、`modworldgenmain.lua` 或 `modservercreationmain.lua`）是否存在。
2. 如果即将运行带有 DST 路径的 PowerShell 命令，第一次尝试时安全地引用它；不要对 `Don't Starve Together` 路径使用未转义的单引号字面量。
3. 如果 `modinfo.lua` 存在，当元数据、依赖项或配置布局可能重要时，阅读 `references/patterns/startup/modinfo-patterns.md`。
4. 如果任务主要关于哪个根文件应该拥有该功能，阅读 `references/core/dst-mod-scaffolding/references/entrypoints.md`。
5. 如果任务主要关于引导连接、`PrefabFiles`、顶级资源、`modimport(...)` 或角色注册，阅读 `references/patterns/startup/modmain-patterns.md`。
6. 如果 `modinfo.lua` 存在，在阅读运行时 API 之前，根据其标志将 mod 分类为客户端/服务端共用游戏玩法、仅客户端或仅服务端。
7. 如果任务是运行时侧，阅读 `references/core/dst-lua-runtime/references/module-environments.md` 并确定它是权威逻辑、本地 UI、本地输入还是实体查询逻辑。
8. 识别已匹配功能类型的最小官方文件。
9. 如果仍然需要具体的官方起点，阅读 `references/official-examples.md`。
10. 检查官方代码中确切的钩子或助手定义。
11. 如果真正的问题是补丁钩子选择，阅读 `references/core/dst-hooking-compatibility/GUIDE.md`。
12. 检查行为是仅服务端、仅客户端还是复制的。
13. 根据已确认需求做最小完整实现；以行为、运行端和生命周期契约决定范围，不用代码行数衡量正确性。

## 编辑 `modinfo.lua`

1. 阅读 `references/patterns/startup/modinfo-patterns.md`。
2. 根据 `client_only_mod` 和 `all_clients_require_mod` 对 mod 进行分类。
3. 将元数据本地化保持在 `modinfo.lua` 内部，而不是运行时 `STRINGS` 中。
4. 保持配置助手很小，避免 Lua 标准库假设。
5. 如果配置需要分组，使用 `MakeConfigSectionHeader(...)`。

## 搭建新 Mod

1. 阅读 `references/mod-bootstrap.md`。
2. 将 mod 分类为客户端/服务端共用游戏玩法、仅客户端或仅服务端。
3. 除非明确需要世界生成或主机设置文件，否则首先只生成 `modinfo.lua` 和 `modmain.lua`。
4. 如果用户想要确定性输出，使用 `references/tools/general/init_dst_mod.py`。
5. 如果第一个实际功能可能属于世界生成或主机设置而不是普通运行时，阅读 `references/core/dst-mod-scaffolding/references/entrypoints.md`。
6. 在将新的 `modmain.lua` 变成注册中心之前，阅读 `references/patterns/startup/modmain-patterns.md`。
7. 脚手架存在后，通过 `references/templates/template-patterns.md` 或更窄的子系统页面路由第一个实际功能。

## 调试损坏的功能

1. 阅读 `references/patterns/diagnostic-patterns.md`。
2. 如果用户报告明确的错误或崩溃，在触摸代码之前检查相关日志。
3. 首先搜索 `LUA ERROR stack traceback:`。
4. 如果失败堆栈包含 `../mods/workshop-<id>/...`，记录它可能指向 Steam Workshop Mod；仅凭日志中的 ID 不打开或列出对应目录。
5. 只有用户明确要求参考或调试该第三方 Mod 时，才按其指定范围定位真实 Workshop 源码；未授权时继续分析已提供的日志与当前目标代码。
6. 已授权但目标路径无法定位时，在提出文件级修复前询问安装路径，不遍历其他 Mod 寻找例子。
7. 如果当前日志干净但游戏已重启，检查 `backup/`。
8. 确定用户只是询问原因还是正在积极调试 mod。
9. 如果这是主动调试，确认失败堆栈是否属于当前目标 mod。
10. 用户只询问原因时解释错误并保持只读；用户已要求修复时，直接完成范围明确的修复，不重复询问是否需要修复。
11. 修改前理解当前代码并保留已有改动；需求或目标范围仍不清楚时先询问，不扩大授权。
12. 在触摸代码之前对症状进行分类：
    - 缺少注册
    - 错误的运行时上下文
    - 缺少客户端复制
    - 错误的 UI 或动作连接
13. 当症状是"这个东西现在甚至存在吗？"时，首先使用官方控制台检查。
14. 检查匹配失败子系统的最小官方文件。

### 运行时权威与本地

1. 阅读 `references/core/dst-lua-runtime/references/module-environments.md`。
2. 明确代码修改权威玩法状态还是本地表现，并按该合同选择运行端。
3. 如果代码触及 HUD、屏幕或本地玩家状态，阅读 `references/world-ui-assets/dst-hud-screens-input/references/hud-customization.md`。
4. 如果代码监听本地控件，阅读 `references/patterns/runtime/input-patterns.md`。
5. 如果代码扫描附近实体，阅读 `references/patterns/runtime/entity-query-patterns.md`。

## 世界生成

1. 阅读 `references/patterns/world/worldgen-patterns.md`。
2. 确定任务属于 `modworldgenmain.lua` 还是 `modservercreationmain.lua`。
3. 如果任务是房间或任务，阅读 `scripts/map/rooms.lua`、`scripts/map/tasks.lua` 或 `scripts/map/tasksets.lua`。
4. 如果任务是主机自定义、预设 ID 或起始位置选择，阅读 `scripts/map/customize.lua`、`scripts/map/levels.lua` 和 `scripts/map/startlocations.lua`。
5. 如果任务是服务器创建屏幕行为，阅读 `scripts/widgets/redux/worldsettings/worldsettingstab.lua` 或匹配的屏幕/widget 文件。
6. 将世界生成时间逻辑与正常游戏玩法引导分开。

### 添加或移除世界自定义选项

1. 阅读 `references/patterns/world/worldgen-patterns.md`。
2. 首先阅读 `scripts/map/customize.lua`。
3. 确定选项属于 `LEVELCATEGORY.SETTINGS` 还是 `LEVELCATEGORY.WORLDGEN`。
4. 使用来自 `modutil.lua` 的 `AddCustomizeGroup(...)`、`AddCustomizeItem(...)`、`RemoveCustomizeGroup(...)` 或 `RemoveCustomizeItem(...)`。
5. 如果选项实际上是新的起始类型，也检查 `scripts/map/startlocations.lua`。
6. 如果任务提到预设，验证设置和世界生成两侧是否都需要更改。

### 补丁现有 Prefab

1. 阅读 `scripts/prefabs/<prefab>.lua`。
2. 阅读驱动目标行为的组件文件。
3. 如果钩子选择不明显，阅读 `references/core/dst-hooking-compatibility/GUIDE.md`。
4. 除非更改明显属于其他地方，否则使用 `AddPrefabPostInit`。
5. 仅添加缺失的行为，而不是完全替换 prefab。

如果唯一可行的补丁点是一个封闭的辅助函数，在复制大型外部函数之前阅读 `references/patterns/debug-techniques.md`。

### 添加玩家范围行为

1. 阅读 `references/patterns/player-patterns.md`。
2. 阅读 `scripts/prefabs/player_common.lua` 和任何涉及的组件。
3. 如果任务需要所有者专属玩家复制、HUD 同步或 `player_classified`，阅读 `references/patterns/network/player-network-patterns.md`。
4. 使用 `AddPlayerPostInit` 或组件钩子。
5. 明确保护主模拟和客户端逻辑。

### 使用标准助手构造函数

1. 阅读 `references/patterns/prefab/standard-helper-patterns.md`。
2. 阅读 `references/signatures/helper-signatures.md` 获取确切参数顺序。
3. 阅读 `scripts/standardcomponents.lua`。
4. 阅读已经使用相同助手家族的最接近官方 prefab。
5. 验证助手是否属于 `SetPristine()` 之前或仅在主路径上。
6. 不要假设每个助手名称都同样完整；在源代码中验证当前助手行为。

### 补丁生存、战斗、装备或容器行为

1. 阅读 `references/component-patterns.md`。
2. 打开 `scripts/components/` 下的确切官方组件文件。
3. 阅读使用相同组件模式的最接近官方 prefab。
4. 如果标签、动作、动画、输入或状态机流程很重要，也阅读匹配的窄参考页面。
5. 优先选择小的组件 post-init 或 prefab 本地设置更改，而不是重写系统。

### 添加或扩展组件

1. 阅读 `references/core/dst-prefab-authoring/references/prefab-contract.md` 获取基础加载路径。
2. 如果任务针对常见官方组件，阅读 `references/component-patterns.md`。
3. 阅读具有最接近生命周期和网络类型的官方组件。
4. 如果任务实际上是关于补丁钩子选择，阅读 `references/core/dst-hooking-compatibility/GUIDE.md`。
5. 使用 `AddComponentPostInit` 进行小扩展。
6. 如果组件有 replica，在编写网络代码之前检查 replica 和分类模式。
7. 在需要时使用 `AddReplicableComponent` 注册 replica 支持。

### 在保存或加载之间持久化状态

1. 阅读 `references/core/dst-persistence-migration/references/persistence-contract.md`。
2. 按合同选择数据类型和 Prefab/Component 回调，不重复加载同一文档。
3. 确定数据是纯标量状态、跨实体引用、嵌套拥有实体还是离线时间追赶。
4. 在发明自定义流程之前，阅读 `scripts/entityscript.lua` 获取生命周期顺序。
5. 按合同区分 Prefab OnLoadPostPass/OnLongUpdate 与 Component LoadPostPass/LongUpdate；跨实体恢复与时间推进分别核对，不把 dt 当作固定现实离线时长。
6. 保持保存的数据最小且规范。

### 持久化本地设置或跨保存配置文件数据

1. 阅读 `references/patterns/persistence/persistent-string-patterns.md`。
2. 确定数据是否真正是本地进程数据，而不是一个世界保存或一个实体。
3. 如果用户实际上想要主机可见的 mod 配置，停止并重新路由到 `references/patterns/startup/modinfo-patterns.md`。
4. 如果格式错误或旧负载是合理的，阅读 `references/patterns/network/protected-call-patterns.md`。
5. 首先将表序列化为字符串，通常使用 `json.encode(...)`。
6. 通过 `TheSim:GetPersistentString(...)` 的回调加载；不要将其视为同步返回。
7. 用稳定的 mod 命名空间前缀文件键。

### 保护序列化、反序列化或可选的 `require(...)`

1. 阅读 `references/patterns/network/protected-call-patterns.md`。
2. 保持保护边界狭窄：解码、编码或一个可选的 `require(...)`。
3. 默认优先使用 `pcall(...)`。
4. 仅当自定义错误处理程序实质性改善失败路径时，才使用 `xpcall(...)`。
5. 在保护调用后验证解码结果；`ok == true` 不够。

### 添加或修补 UI

1. 自有控件/布局读 [Widget 专题](world-ui-assets/dst-ui-widget-authoring/GUIDE.md)；HUD 挂载、屏幕或输入集成读 [HUD 专题](world-ui-assets/dst-hud-screens-input/GUIDE.md)，不默认同时加载全部基础页。
2. 所有权不明时读 [UI 补丁选择](patterns/ui/ui-patch-patterns.md)，再定位 scripts/widgets/ 或 scripts/screens/ 的实际类。
3. 输入选型读 [输入模式](patterns/runtime/input-patterns.md)，具体参数与句柄清理只查 [TheInput](systems/theinput.md)。
4. 自有 Widget/Screen 新建模块；小范围扩展现有类用 AddClassPostConstruct，保留生命周期和未消费路径。
5. UI 请求真实玩法时走 Action/RPC；为本功能的 handler、回调、任务和数据源定义退出与重建路径。

### 理解或重构 `modmain.lua`

1. 阅读 `references/patterns/startup/modmain-patterns.md`。
2. 当加载顺序、`modimport(...)`、`PrefabFiles` 或顶级 `Assets` 行为不清楚时，阅读 `scripts/mods.lua`。
3. 当任务依赖于暴露给 `modmain.lua` 的注册助手时，阅读 `scripts/modutil.lua`。
4. 确定哪些代码是真正的引导胶水，哪些代码应该移动到 prefabs、components、widgets、brains、SG 文件或辅助模块中。
5. 如果文件很大，将注册工作拆分为 `scripts/modmain/*.lua`，并保持根 `modmain.lua` 小而有序。

### 添加配方、动作或状态机更改

按实际需求选一条入口，不因配方任务预先加载 Action 和 SG：

| 变更 | 起点 |
|---|---|
| 配方/制作权限/placer | [制作专题](gameplay/dst-crafting-tech-prototypers/GUIDE.md)；具体步骤见下方“添加配方或放置器” |
| 候选动作/BufferedAction | [Action 链](core/dst-action-authoring/references/action-pipeline.md) |
| 状态、事件、时间线或玩家预测 | [StateGraph 合同](gameplay/dst-stategraph-authoring/references/stategraph-contract.md) |

读对应 modutil 注册与最相近的原版调用者。只有动作实际影响表演/预测时再联查 SG；本地面板行为按上述 UI 分支处理。

### 补丁常见世界系统

1. 阅读 `references/patterns/world-system-patterns.md`。
2. 打开 `scripts/components/` 下的确切官方组件文件。
3. 在手动滚动设置之前，检查 `scripts/standardcomponents.lua` 是否存在现有助手。
4. 阅读组合相同系统的最接近官方 prefab。
5. 如果涉及玩家交互或放置，也检查动作或配方路由。

### 添加配方或放置器

1. 阅读 `references/patterns/recipe/recipe-patterns.md`。
2. 除非任务明确需要遗留行为，否则使用 `AddRecipe2`。
3. 使用 `MakePlacer` 用于可放置结构或部署物。
4. 分别核对配方 ID、产物与 placer 的真实注册名；名称可显式不同，按配置保持引用一致。

### 添加或补丁大脑 AI

1. 阅读 `references/gameplay/dst-brain-authoring/references/brain-node-behaviour-quickref.md`。
2. 阅读最接近的官方 prefab 并注意它需要哪个大脑文件。
3. 阅读 `scripts/brains/` 下的匹配文件。
4. 也阅读匹配的状态机，因为 AI 选择和执行者执行是分离的层。
5. 如果更改很小，优先使用 `AddBrainPostInit`。
6. 如果 AI 类型是 mod 拥有的，在 `scripts/brains/` 下创建专用大脑文件。

### 添加字符串或本地化

1. 阅读 `references/patterns/runtime-i18n-patterns.md`。
2. 确定文本属于运行时 `STRINGS` 还是本地化的 `modinfo.lua` 元数据。
3. 在已读本地化页按少量字符串、语言表或运行时切换的实际需求选择组织方式。
4. 保持 prefab 和动作键与大写 `STRINGS` 条目对齐。
5. 如果艺术或图标问题混合在一起，单独检查 `references/patterns/asset/asset-patterns.md`，而不是将其视为字符串错误。

### 添加资源或图标

1. 阅读 `references/patterns/asset/asset-patterns.md`。
2. 确定资源属于 prefab 本地 `assets` 表还是顶级 mod `Assets`。
3. 当配方或 UI 元素依赖于图集和纹理路径时，保持它们明确。

### 打包、解包或调整纹理大小

1. 阅读 `references/patterns/asset/texture-patterns.md`。
2. 确定任务是官方图集解包、本地 TEX/XML 解包、图集打包还是 PNG 调整大小。
3. 使用 `references/tools/general/tex_atlas_tool.py` 进行图集打包或解包任务。
4. 当任务主要关于适配图标尺寸时，使用 `references/tools/general/resize_png.py`。
5. 如果任务还更改资源声明，阅读 `references/patterns/asset/asset-patterns.md`。

### 添加或补丁动画状态

1. 阅读 `references/patterns/asset/animstate-patterns.md`。
2. 识别任务是关于启动动画、状态机驱动流程、符号覆盖、层切换还是进度驱动 UI 动画。
3. 阅读已经使用相同模式的最接近官方 prefab、状态机、widget 或屏幕。
4. 在更改代码之前验证库、构建、动画、符号和层名称。
5. 保持动画补丁狭窄。

### 添加光照、特效或声音

1. 阅读 `references/patterns/asset/effects-patterns.md`。
2. 确定任务是发光游戏玩法 prefab、本地专用助手、网络代理、粒子效果还是状态机定时声音。
3. 阅读已经匹配该类型的最接近官方 prefab。
4. 如果交互或时序也更改，检查 `references/patterns/prefab/tag-patterns.md` 或 `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`。
5. 如果任务需要新纹理、着色器或声音资源，检查 `references/patterns/asset/asset-patterns.md`。

### 添加 RPC、Replica 或 Netvars

1. 阅读 `references/core/dst-networking-rpc/references/network-contract.md`。
2. 按已读合同选择 RPC 意图、复制状态或两者配合的最小实现。
3. 如果任务是玩家拥有或所有者专属，也阅读 `references/patterns/network/player-network-patterns.md`。
4. 确定需求是 RPC 意图、复制状态还是两者都需要。
5. 阅读 `scripts/networkclientrpc.lua` 获取 RPC 路由。
6. 在添加 replica 或分类逻辑之前，阅读 `scripts/entityreplica.lua` 和类似的官方 prefab 或组件。
7. 保持客户端读取在 replica 或 netvars 上，而不是仅服务端组件。

### 添加碎片感知运行时行为

1. 阅读 `references/patterns/network/shard-patterns.md`。
2. 确定功能是仅当前碎片、仅主碎片还是真正跨碎片。
3. 如果任务还保存碎片感知位置或迁移状态，阅读 `references/core/dst-persistence-migration/references/persistence-contract.md`。
4. 在发明新协议之前，使用现有的迁移、`worldmigrator` 或碎片聚合模式。
5. 仅当普通客户端/服务端 RPC 和保存的世界状态不够时，才使用碎片 mod RPC。

### 选择补丁钩子

1. 阅读 `references/core/dst-hooking-compatibility/GUIDE.md`。
2. 如果目标是一个 prefab，优先使用 `AddPrefabPostInit(...)`。
3. 如果目标是所有玩家，优先使用 `AddPlayerPostInit(...)`。
4. 如果目标是组件家族，优先使用 `AddComponentPostInit(...)`。
5. 如果目标是 widget 或屏幕类，优先使用 `AddClassPostConstruct(...)`。
6. 仅当更窄的钩子无法表达目标集时，才使用 `AddPrefabPostInitAny(...)`。

如果请求实际上是带有预测的内置世界交互，在默认使用自定义 RPC 之前检查动作和状态机流程。

### 添加新 Prefab 或物品

1. 阅读 `references/patterns/startup/modmain-patterns.md` 获取 `modmain.lua` 的注册侧。
2. 阅读 `references/core/dst-prefab-authoring/references/prefab-contract.md` 获取从 `modmain.lua` 到 `scripts/prefabs/*.lua` 的加载器路径。
3. 如果请求被表述为整个功能（如武器、容器、生物、结构或可玩角色），阅读 `references/feature-recipes.md`。
4. 如果 prefab 除了基本空闲剪辑之外还有自定义 `AnimState` 行为，阅读 `references/patterns/asset/animstate-patterns.md`。
5. 选择最接近的官方 prefab。
6. 阅读该 prefab 和 `scripts/standardcomponents.lua` 中的任何助手调用。
7. 重用可燃烧、可冻结、物理、可作祟、可浮动等设置的助手构造函数。
8. 在 PrefabFiles 登记文件模块，在返回值中登记实际 Prefab 名；资源路径按 mod 根目录配置。

如果 mod 拥有一系列几乎相同的 prefab 变体，优先使用共享工厂模式而不是重复的构造函数。使用 `scripts/prefabs/staff.lua` 作为官方类型参考。

如果 prefab 是生物或 NPC，也尽早通过大脑和状态机放置路由，而不是将其视为普通物品 prefab。

### 添加或重构可玩角色

1. 阅读 `references/patterns/character/character-patterns.md`。
2. 阅读 `references/patterns/startup/modmain-patterns.md` 获取角色注册和共享资源。
3. 在从头编写角色 prefab 之前，阅读 `scripts/prefabs/player_common.lua`。
4. 阅读最接近的官方角色 prefab，如 `scripts/prefabs/wilson.lua` 或 `scripts/prefabs/wormwood.lua`。
5. 将角色身份标签和客户端可见动画设置保持在 `common_postinit` 中。
6. 将属性调整、仅服务端组件和权威监听器保持在 `master_postinit` 中。
7. 如果角色需要进度，阅读 `scripts/prefabs/skilltree_defs.lua` 和最接近的 `scripts/prefabs/skilltree_<character>.lua`。
8. 仅当设计实际需要可解锁进度或技能门控配方时，才添加技能树。
9. 如果肖像、头像图标或自检艺术不正确，在更改不相关的游戏玩法代码之前，检查 `scripts/screens/lobbyscreen.lua`、`scripts/screens/redux/serverslotscreen.lua` 和 `scripts/widgets/inventorybar.lua`。
10. 如果衣柜或加载预览表单不正确，检查 `scripts/widgets/redux/loadoutselect.lua`、`scripts/widgets/skinspuppet.lua` 以及 `AddModCharacter(..., modes)` 是否使用与角色基础皮肤映射匹配的 `type` 名称。

### 添加或补丁官方皮肤数据

1. 阅读 `references/patterns/skin/skin-patterns.md`。
2. 确定任务是否真的需要官方皮肤系统，还是只需要预览模式或运行时构建交换。
3. 检查 `scripts/prefabskin.lua`、`scripts/prefabskins.lua` 和 `scripts/prefabs/skinprefabs.lua`。
4. 在承诺衣柜行为之前，检查 `scripts/widgets/redux/loadoutselect.lua` 和 `scripts/screens/redux/defaultskinselection.lua`。
5. 不要假设 mod 角色获得原版基础皮肤选择器。
6. 不要假设存在所有权，除非任务也补丁面向背包的选择流程。

### 调整数值或平衡

1. 从 `scripts/tuning.lua` 开始。
2. 如果涉及符号标识符，阅读 `scripts/constants.lua`。
3. 在值的使用位置不清楚之前，避免扫描不相关的 prefab 代码。

## 验证清单

- 检查所选根入口文件是否匹配执行阶段。
- 检查目标文件是否是正确的入口点。
- 检查 `PrefabFiles` 和 `Assets` 是否覆盖任何新 prefab 或资源。
- 检查服务端和客户端代码是否没有意外混合。
- 检查所选钩子是否是匹配目标的最窄钩子。
- 按持久化合同区分 Prefab/Component 的保存、加载后修复与时间推进回调。
- 检查数据应该是世界保存生命周期还是 `TheSim` 持久字符串存储。
- 检查脆弱的解码、编码或可选 `require(...)` 边界是否适当使用了 `pcall(...)` 或 `xpcall(...)`。
- 检查碎片感知逻辑是否区分当前碎片、主碎片和跨碎片行为。
- 检查本地 UI 补丁是否针对正确的层：`controls`、`playerhud`、瞬时 widget、弹出屏幕或 `frontend`。
- 检查 UI 处理程序、监听器和任务在关闭或销毁时是否被清理。
- 检查 RPC 命名空间和名称对在两侧是否匹配。
- 检查仅 replica 读取是否不调用仅服务端组件。
- 检查引擎全局变量（如 `GLOBAL`、`TheSim`、`TheNet`、`TheShard`、`TheInput`、`TheFrontEnd`、`TheWorld` 和 `ThePlayer`）是否未被覆盖或重新绑定。
- 检查共享注册表（如 `TUNING`、`STRINGS`、`ACTIONS` 和 mod RPC 注册表）是否被窄扩展而不是完全替换。
- 检查最终实现是否仍然匹配您检查的官方模式。
- 不要运行本地 `lua`、`luac` 或通用 Lua 语法编译器进行 DST mod 验证。
- 不要将缺少本地 `lua/luac` 报告为跳过的验证步骤；DST 使用 Klei 修改的 Lua 运行时，因此改用 DST 日志、游戏内检查、目标源代码检查和仓库检查进行验证。
- 在文档或辅助脚本重构后，从 skill 根目录运行 `& ./references/tools/engineering/run.ps1 check_skill --strict`，由统一入口选择项目解释器。
