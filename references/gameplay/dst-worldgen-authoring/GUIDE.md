---
name: dst-worldgen-authoring
description: Create and modify Don't Starve Together world generation. Use when writing tiles and terrain (TileManager.AddTile / tiledefs), rooms, tasks, task sets, layouts (static or hand-written), levels, start locations, worldgen hooks (PreInit), the override density system, or scenario injection into worldgen.
---

# DST 世界生成编写

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

让世界生成内容在 `modworldgenmain.lua` 用 `Add...`/`...PreInit` 注册与挂接；地皮走模组环境 `AddTile` 动态注册；复杂结构用 Tiled 静态布局 + `StaticLayout.Get`；定向实体行为用 scenario 注入。

## 工作流

1. 先确认入口：世界生成内容放 `modworldgenmain.lua`（不是 `modmain.lua`，后者生成期不执行）。主机前端预设/选项属于 `modservercreationmain.lua`。
2. 新增命名对象使用环境 API AddRoom/AddTask/AddTaskSet/AddLevel/AddStartLocation；给内置对象打补丁用对应 PreInit。底层 AddMod* 有额外 modname 参数，不混用签名。
3. 地皮用环境 AddTile，优先集中到 modworldgenmain 并以稳定 WORLD_TILES 名防重入；当前普通运行也先执行该入口。不要在 modmain 无条件重复注册，也不直接改 TileManager 保护开关。
4. 房间 flower/任务/布局引用地皮时用 `WORLD_TILES.<name>`；TC 过滤用 `TERRAIN_FILTER` 或 `AddRoomPreInit`。
5. 复杂结构用当前 StaticLayout loader 可 require 的 Tiled Lua 表 + StaticLayout.Get，登记唯一 Layouts 名并接入实际放置入口；JSON 先转换，不当作 Lua 模块。
6. 要定向实体行为，在布局/房间给实体 save_data 加 `scenario = "<name>"`，并补 `scenarios/<name>.lua` 的 `{OnCreate, OnLoad, OnDestroy}`。
7. 密度控制：`level.overrides` + MULTIPLY 系统（`prefab名={count="rare"}` 等）；成簇生成用 `Bunches`。

## 源码锚点

- modutil.lua:AddTile 包装与 tilemanager.lua 验证；tiledefs.lua 只作原版定义参考，不复制其保护开关操作。
- `scripts/map/rooms.lua`、`tasks.lua`、`tasksets.lua`、`levels.lua`、`startlocations.lua`：注册 API 与数据结构。
- `scripts/map/layouts.lua`、`static_layout.lua`、`object_layout.lua`：布局定义与 LAYOUT_FUNCTIONS。
- `scripts/map/storygen.lua`、`network.lua`、`graphnode.lua`：世界结构生成内核。
- `scripts/mainfunctions.lua`、`components/scenariorunner.lua`：scenario 注入读取与运行时。
- 世界生成工作流相关（worldgen_main / forest_map / level）：生成管线总览。

## 不变量

- 地皮通过阶段入口在消费者初始化前注册，不在运行回调里动态造 ID，也不手改 WORLD_TILES。
- 不要用不存在的旧全局 API（`AddLayout`、`TopologySetUp`、`SetTiles`、`SetNode`），对应能力已被 Layouts 表 + Story/Graph/Node + WorldSim 取代。
- 布局导出数据的 tile 序号必须与 `GROUND_TYPES` 顺序一致（第 1 个是 IMPASSABLE，第 2 个是 ROAD…）。
- runner 保存 scriptname/hasrunonce；自定义持久状态写明确的组件/实体存档数据，ClearScenario 负责清除，不是保存接口。

## 验证

- 新地皮/房间/任务在世界生成设置里可选且能生成；`WORLD_TILES.<name>` 全局可用。
- 房间/任务 name 不重复（重复用 `PreInit` 打补丁）。
- 静态布局坐标、地皮矩阵、缩放与预期一致；scenario 在生成时被正确挂到实体。

## 虚拟房间集合（VirtualRoomSet）

当前安装版世界在主机端创建 `virtualroommanager` 与 `worldstaticlayouts`。虚拟房间集合只能存在于主机：`VirtualRoomSet` 的构造要求 `TheWorld.ismastersim`，并依赖世界已有的 `virtualroommanager`。每个集合必须先在 `VIRTUALROOM_BOUNDINGBOXES` 声明唯一名称和边界框；存在 mask 时长度必须等于 `(maxx-minx+1)*(maxy-miny+1)`。多个集合的边界不得碰撞。

`VirtualRoomSet:SetRoomDefinitions(defs)` 与项目定义层配合管理 `InitializeLayout`、`DeleteLayout`、房间连接、地皮批次和重置版本。房间内的 `virtualroomteleporter` 只负责方向、目标集合、投票、出发/到达回调和可选的落点覆盖；实际的隐藏/显示、玩家检测和轮换由集合管理。存档保留当前房间、房间数据和原始地皮等信息，版本升级可触发重置，不能把内部表当稳定公开 API。

传送是否允许必须走 `IsTeleportingPermittedFromPointToPoint`：它会检查 WagPunk 竞技场屏障和虚拟房间集合之间的移动规则。自定义传送、瞬移杖和回城效果若只查可通行地皮，可能把玩家送出封闭房间。验证空世界、重进存档、多人投票、连接中断、房间旋转、重置与主客机权限；本机未运行世界测试。

`FindNearestActiveTelebase` 当前在比较距离前先验证点到点传送许可，不能跨区或处于屏障限制中的传送台不会成为最近候选。自定义回城、传送台列表或目标排序应把资格检查放在候选筛选阶段，再应用距离和优先类型；否则会得到“最近但实际不能用”的目标。

地图显示使用 `IsVisibleRespectingVRSFromPointToPoint` 和 `MiniMapEntity:SetAlwaysOutsideVRS`，它与实际传送许可分开。`IsTeleportLinkingPermittedFromPoint` 还用于拒绝屏障开启区域、金库房间和 Charlie Boss 竞技场内的连接点。`VirtualRoomManager:WillBoundingBoxCollideAt`、`StaticLayoutPlacer.CreateVRSPositionFilter` 属于放置/碰撞预算，`VirtualRoomSet:SetKeepInventoryItemsthroughReset` 属于重置生命周期，不能混成同一条传送资格规则。

房间布局批量铺设地皮时，当前 `VirtualRoomSet:ApplyFloorTileBatch` 会在整批 `Map:SetTile` 前关闭 `Map:SetInstantPhysicsRebuild()`，结束后恢复原值，避免每格重复重建同一碰撞区域。自己的批量地形操作也应合并物理重建，并保证异常路径会恢复原设置；不要逐格修改后仍让每一格触发完整重建。

## 按需资源

- 需要**世界生成层级的整体视图**(Location→Level→TaskSet→Task→Room、扩展点总览、锁钥可达性、密度上限、环境限制)时读取 [worldgen-graph.md](references/worldgen-graph.md)。
- 需要**地皮/地形系统**（AddTile 签名、ground_tile_def、turf_def、TileRanges、旧 GROUND deprecated、新地皮五要素）时读取 [worldgen-tile-terrain.md](references/worldgen-tile-terrain.md)。
- 需要**注册 API + 数据结构**（Room/Task/Layout/Level 字段、AddMod* 全家、override 密度、Bunches）时读取 [worldgen-data-and-hooks.md](references/worldgen-data-and-hooks.md)。
- 需要**worldgen hook + scenario 注入 + Tiled 静态布局流程**时读取 [worldgen-scenarios-hooks.md](references/worldgen-scenarios-hooks.md)。
- 需要**overrides / worldsettings 全部合法取值词表**（never/rare/…/insane、task_set、season_start 等，写错会静默失效）时读取 [worldgen-overrides.md](references/worldgen-overrides.md) 与 [worldsettings-overrides.md](references/worldsettings-overrides.md)；重生成词表用 `tools/dump_options.lua`。
- 需要**世界设置选项、建服前端注册和 `AddLevelPreInitAny` / `AddTaskSetPreInitAny` 时机**时读取 [world-options-preinit.md](references/world-options-preinit.md)。
- 需要**裁剪世界是否仍能解锁 Boss 链**（天体英雄、远古织影者等前置实体/结构/系统）时读取 [boss-prerequisites.md](references/boss-prerequisites.md)；用 `tools/save_inspect.lua` 对照真实存档验证（见 [save-files.md](references/save-files.md)）。
- 需要入口文件路由与 Add/PreInit 意图索引时读取 `patterns/world/worldgen-patterns.md`（生成入口侧）。
- 需要地皮/turf 接入骨架（AddTile 六参，资源由项目提供）时读取 assets/turf-template.lua；需要世界生成整体骨架（Room/Task/TaskSet/静态布局）时复制 assets/worldgen-template.lua。
- 需要世界生成进阶模式（世界规则覆盖层 / 极坐标迷宫分帧 / 旧档 retrofit / Tiled 撒点 / 静态布局 areas 参数）时查阅 `references/mod-notes/` 下 [mod-fengyun.md](../../mod-notes/mod-fengyun.md)（丰耘秘境）与 [mod-daogui.md](../../mod-notes/mod-daogui.md)（道诡异仙）原始笔记。
