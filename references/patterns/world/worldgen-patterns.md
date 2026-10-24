# 世界生成模式

当任务涉及世界预设、关卡生成、任务、场景组件或服务器创建自定义时，请使用此文件。

当任务仍在 `modmain.lua`、`modworldgenmain.lua` 和 `modservercreationmain.lua` 之间做出选择时，请先阅读 `references/core/dst-mod-scaffolding/references/entrypoints.md`。

## 四个常见的 Mod 入口文件

官方 mod 加载识别这些根级入口文件：

- `modinfo.lua`
- `modmain.lua`
- `modworldgenmain.lua`
- `modservercreationmain.lua`

根据执行上下文选择入口文件，而不是按功能名称。

## 官方加载行为

在 `scripts/mods.lua` 中观察到：

- 前端服务器创建流程初始化 `modservercreationmain.lua`，然后是 `modworldgenmain.lua`
- 游戏世界生成初始化也运行 `modworldgenmain.lua`
- 正常游戏运行时仍使用 `modmain.lua`

相关官方代码行：

- `scripts/mods.lua:442-443`
- `scripts/mods.lua:577`

这意味着 `modworldgenmain.lua` 不仅用于主机 UI。它是实际的世界生成侧入口点。

## 入口文件路由

- `modmain.lua`
  - 正常运行时游戏代码
  - 预制件后初始化、组件、小部件、RPC 处理器、动作、SG 钩子、副本
- `modworldgenmain.lua`
  - 生成时注册和突变
  - 房间、任务、任务集、关卡、起始位置、场景组件/世界生成数据
- `modservercreationmain.lua`
  - 主机设置和预设面向的前端自定义
  - 世界存在之前需要的选项或预设描述

## 添加新内容与补丁现有内容

当引入新的命名对象时，使用 `Add...` 函数。
当修改已经存在的内置对象时，使用 `...PreInit` 函数。

高频配对：

- `AddRoom(name, data)`
  - 添加全新的房间定义
- `AddRoomPreInit(roomname, fn)`
  - 在世界生成消耗之前补丁现有房间
- `AddTask(name, data)`
  - 添加全新的任务定义
- `AddTaskPreInit(taskname, fn)`
  - 补丁现有任务定义
- `AddTaskSet(name, data)`
  - 添加全新的任务集
- `AddTaskSetPreInit(tasksetname, fn)`
  - 补丁一个现有任务集
- `AddTaskSetPreInitAny(fn)`
  - 补丁所有任务集
- `AddLevel(id, data)`
  - 添加新的关卡定义
- `AddLevelPreInit(levelid, fn)`
  - 补丁一个现有关卡
- `AddLevelPreInitAny(fn)`
  - 补丁所有关卡
- `AddStartLocation(name, data)`
  - 注册新的起始位置

这些 API 的官方辅助注册位于 `scripts/modutil.lua:237-309`。

## 主机自定义和预设数据

并非每个世界生成任务都是"添加房间"或"补丁任务"。
有些任务实际上是关于主机可见的世界自定义选项或预设组合。

关键官方文件：

- `scripts/map/customize.lua`
  - 自定义组和项目
  - `LEVELCATEGORY.SETTINGS` 与 `LEVELCATEGORY.WORLDGEN`
  - 起始位置选项连接
- `scripts/map/levels.lua`
  - 预设查找、预设 ID、预设名称和描述
  - 设置和世界生成之间的组合预设行为
- `scripts/widgets/redux/worldsettings/worldsettingstab.lua`
  - 服务器创建 UI 流程
  - 分别收集世界生成和设置选项，然后合并它们
- `scripts/map/startlocations.lua`
  - 起始位置注册和前端刷新

来自 `scripts/modutil.lua` 的高频自定义辅助函数：

- `AddCustomizeGroup(category, name, text, desc, atlas, order)`
- `RemoveCustomizeGroup(category, name)`
- `AddCustomizeItem(category, group, name, itemsettings)`
- `RemoveCustomizeItem(category, name)`

## `LEVELCATEGORY.SETTINGS` 与 `LEVELCATEGORY.WORLDGEN`

官方 `scripts/map/customize.lua` 将世界自定义项目分配到两个主要类别之一：

- `LEVELCATEGORY.SETTINGS`
  - 世界设置，如模拟或季节行为
- `LEVELCATEGORY.WORLDGEN`
  - 地图生成选项，如生成内容分布

如果任务是关于主机自定义屏幕中显示的内容，请在添加之前确认选项属于哪个类别。
不要默认将所有选项都放入世界生成。

## 起始位置也是一个自定义选项

官方 `scripts/map/customize.lua` 将 `start_location` 连接到 `startlocations.GetGenStartLocations`。
这意味着自定义起始位置不仅是生成数据。
它还影响主机在世界自定义屏幕中可以选择的内容。

实际后果：

- 使用 `AddStartLocation(...)` 注册位置
- 然后验证 `scripts/map/customize.lua` 中的主机面向选择流程
- 如果任务是关于设置 UI 中的显示或分组，也要检查 `modservercreationmain.lua`

## 预设组合

官方 `scripts/map/levels.lua` 和 `scripts/widgets/redux/worldsettings/worldsettingstab.lua` 保持设置预设和世界生成预设分开，然后在需要时组合它们。

实际后果：

- "预设"实际上可能涉及 `LEVELCATEGORY.SETTINGS` 和 `LEVELCATEGORY.WORLDGEN` 两者
- 更改一侧不会自动重写另一侧
- 如果用户说"自定义预设"，确认他们的意思是仅世界生成、仅设置还是组合行为

## 为什么重复名称会失败

官方地图模块拒绝重复的房间/任务名称：

- `scripts/map/rooms.lua`
  - 重复房间添加建议使用 `AddRoomPreInit(...)` 替代
- `scripts/map/tasks.lua`
  - 重复任务添加建议使用 `AddTaskPreInit(...)` 替代

如果用户说"调整 `BGForest`"或"更改 `Make a pick` 起始任务流程"，不要注册同名的第二个对象。
补丁现有的那个。

## 意图索引

将此用作从用户意图到文件和 API 的快速路由。

- "添加新房间"
  - `modworldgenmain.lua`
  - 检查 `scripts/map/rooms.lua`
  - 通常使用 `AddRoom(...)`
- "调整现有房间"
  - `modworldgenmain.lua`
  - 通常使用 `AddRoomPreInit(...)`
- "添加新任务"
  - `modworldgenmain.lua`
  - 检查 `scripts/map/tasks.lua`
  - 通常使用 `AddTask(...)`
- "调整现有任务"
  - `modworldgenmain.lua`
  - 通常使用 `AddTaskPreInit(...)`
- "补丁预设或任务集"
  - `modworldgenmain.lua`
  - 通常使用 `AddTaskSetPreInit(...)` 或 `AddTaskSetPreInitAny(...)`
- "补丁关卡设置或覆盖关卡数据"
  - `modworldgenmain.lua`
  - 通常使用 `AddLevelPreInit(...)` 或 `AddLevelPreInitAny(...)`
- "添加或替换起始位置"
  - `modworldgenmain.lua`
  - 检查 `scripts/map/startlocations.lua`
  - 通常使用 `AddStartLocation(...)`
- "更改主机在世界设置屏幕中看到的内容"
  - 从 `modservercreationmain.lua` 开始
  - 然后验证实际数据突变是否仍属于 `modworldgenmain.lua`
- "添加世界自定义选项"
  - 检查 `scripts/map/customize.lua`
  - 通常使用 `AddCustomizeGroup(...)` 和 `AddCustomizeItem(...)`
  - 明确选择 `LEVELCATEGORY.SETTINGS` 或 `LEVELCATEGORY.WORLDGEN`
- "隐藏或移除一个原版自定义选项"
  - 检查 `scripts/map/customize.lua`
  - 通常使用 `RemoveCustomizeItem(...)` 或 `RemoveCustomizeGroup(...)`
- "添加新的主机可选起始类型"
  - 检查 `scripts/map/startlocations.lua` 和 `scripts/map/customize.lua`
  - 通常使用 `AddStartLocation(...)`
- "补丁预设 ID、描述或组合预设行为"
  - 检查 `scripts/map/levels.lua`
  - 检查 `scripts/widgets/redux/worldsettings/worldsettingstab.lua`

## 常见失败点

- 错误的入口文件。
  - `modmain.lua` 中的世界生成代码在生成时通常什么都不做。
- 前端和世界生成混合在一起。
  - `modservercreationmain.lua` 可以准备主机面向的设置，但实际生成的内容通常仍属于 `modworldgenmain.lua`。
- 重复的房间或任务名称。
  - 当目标已经存在时，优先使用 `...PreInit`。
- 假设世界生成期间存在运行时全局变量。
  - 来自 `modmain.lua` 的许多正常游戏假设不属于世界生成引导。
- 主机设置更改被误认为是生成世界的更改。
  - 预设面板文本和实际世界内容相关，但它们不是同一个步骤。
- 错误的自定义类别。
  - `LEVELCATEGORY.SETTINGS` 和 `LEVELCATEGORY.WORLDGEN` 不可互换。
- 起始位置被视为纯后端数据。
  - 它也为前端自定义选择器提供数据。
- 组合预设假设过于宽泛。
  - 设置预设和世界生成预设可以分别解析，然后合并。

## 最小经验法则

- 使用 `modmain.lua` 进行游戏运行时。
- 使用 `modworldgenmain.lua` 进行世界生成内容。
- 使用 `modservercreationmain.lua` 进行主机设置和预设面向的前端工作。
- 当补丁内置房间、任务、任务集或关卡时，优先使用匹配的 `PreInit` 辅助函数。