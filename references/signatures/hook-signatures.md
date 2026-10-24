# Hook 签名

从 `scripts/modutil.lua` 复制的精确签名。
当真正的问题是哪个钩子应该负责补丁时，请使用 `references/core/dst-hooking-compatibility/GUIDE.md`。

```lua
AddCustomizeGroup(category, name, text, desc, atlas, order)
RemoveCustomizeGroup(category, name)
AddCustomizeItem(category, group, name, itemsettings)
RemoveCustomizeItem(category, name)
GetCustomizeDescription(description)

AddLevelPreInit(levelid, fn)
AddLevelPreInitAny(fn)
AddTaskSetPreInit(tasksetname, fn)
AddTaskSetPreInitAny(fn)
AddTaskPreInit(taskname, fn)
AddRoomPreInit(roomname, fn)
AddLocation(arg1, ...)
AddLevel(arg1, arg2, ...)
AddTaskSet(arg1, ...)
AddTask(arg1, ...)
AddRoom(arg1, ...)
AddStartLocation(arg1, ...)

AddClassPostConstruct(package, fn)
AddGlobalClassPostConstruct(package, classname, fn)
AddAction(id, str, fn)
AddComponentAction(actiontype, component, fn)
AddStategraphActionHandler(stategraph, handler)
AddStategraphPostInit(stategraph, fn)
AddComponentPostInit(component, fn)
AddPrefabPostInitAny(fn)
AddPlayerPostInit(fn)
AddPrefabPostInit(prefab, fn)
AddBrainPostInit(brain, fn)
AddModCharacter(name, gender, modes)
AddRecipeToFilter(recipe_name, filter_name)
AddRecipe2(name, ingredients, tech, config, filters)
AddMinimapAtlas(atlaspath)
AddReplicableComponent(name)
AddModRPCHandler(namespace, name, fn)
AddClientModRPCHandler(namespace, name, fn)
AddShardModRPCHandler(namespace, name, fn)
GetModRPC(namespace, name)
GetClientModRPC(namespace, name)
GetShardModRPC(namespace, name)
SendModRPCToServer(id_table, ...)
SendModRPCToClient(id_table, ...)
SendModRPCToShard(id_table, ...)
LoadPOFile(path, lang)
```

## 快速路由

- 世界自定义选项或预设面向的主机设置
  - `AddCustomizeGroup`、`AddCustomizeItem`、`RemoveCustomizeGroup`、`RemoveCustomizeItem`
- 修补现有的世界生成内容
  - `AddLevelPreInit`、`AddTaskSetPreInit`、`AddTaskPreInit`、`AddRoomPreInit`
- 注册新的房间、任务、任务集、关卡或起始位置
  - `AddRoom`、`AddTask`、`AddTaskSet`、`AddLevel`、`AddStartLocation`
- 修补运行时预制件、组件、状态图或 UI 类
  - `AddPrefabPostInit`、`AddComponentPostInit`、`AddStategraphPostInit`、`AddClassPostConstruct`、`AddGlobalClassPostConstruct`
- 修补每个带有玩家标签的实例
  - `AddPlayerPostInit`
- 注册一个可玩角色，可选地带有衣柜或装备预览模式
  - `AddModCharacter`
- 添加网络连接
  - `AddReplicableComponent`、`AddModRPCHandler`、`AddClientModRPCHandler`、`AddShardModRPCHandler`、`Get*RPC`、`SendModRPCTo*`
- 添加显式的小地图或运行时 `.po` 翻译支持
  - `AddMinimapAtlas`、`LoadPOFile`