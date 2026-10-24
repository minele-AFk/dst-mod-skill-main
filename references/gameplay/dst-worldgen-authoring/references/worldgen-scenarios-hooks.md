# 世界生成 Hook、Scenario 与静态布局

## 注册对象与回调

Mod 入口使用 modutil 注入的 AddRoom/AddTask/AddTaskSet/AddLevel/AddStartLocation。底层 AddMod* 还可能接收显式 modname，不与环境包装当作同签名别名。

新增使用独立命名对象，修改现有对象使用限定名称的 AddRoomPreInit/AddTaskPreInit/AddTaskSetPreInit/AddLevelPreInit。ModManager:GetPostInitFn 是内部查询，不是注册回调的替代 API。

例如以下是给已存在房间补计数的完整接入函数；房间、Prefab 和数量由已确认的设计传入：

```lua
local function AddPrefabCount(roomname, prefabname, count)
    AddRoomPreInit(roomname, function(room)
        room.contents = room.contents or {}
        room.contents.countprefabs = room.contents.countprefabs or {}
        room.contents.countprefabs[prefabname] = count
    end)
end
```

计数按生成节点处理，不保证世界总量。多个房间实例、过滤、空间不足都会影响结果；distributeprefabs 是分布权重，不是严格计数。改生成设置不会自动给旧存档补内容。

## 静态布局链

Tiled 导出的、当前 loader 可 require 的 Lua 表 → StaticLayout.Get("map/static_layouts/my_mod_layout", props) → 唯一 Layouts 表项 → room/taskset 等实际放置入口。文件通常位于 scripts/map/static_layouts；不要把未经转换的 JSON 当成当前 require 可直接执行的模块。

BG_TILES 是地面层，FG_OBJECTS 是对象层。Tiled 的数字是 tileset 索引，经 static_layout.lua 的 GROUND_TYPES 映射，不等于 WORLD_TILES 数值。tilewidth、对象坐标、旋转、预留空间、地形与依赖 Prefab 都要检查。

ocean_prefill_setpieces 的 count 当前兼容数字、count 表或函数，不能把数字形式误报成类型错。放置计划数量不等于实际成功数量。精确结构与消费者见 [世界与空间](../../../engineering/dst-mod-engineering/worldgen-spatial.md)。

## Scenario 持久化

生成记录的 scenario 字段在 SpawnSaveRecord 链添加 scenariorunner；SetScript(name) require("scenarios/" .. name)，对应 scripts/scenarios/name.lua。

- 首次 Run：有 OnCreate 则执行，再记录 hasrunonce。
- 每次 Run：有 OnLoad 则执行，否则 ClearScenario。
- ClearScenario 移除 runner，并调用脚本 OnDestroy；它不是“保存任意自定义状态”的接口。
- runner 只保存 scriptname/hasrunonce；自定义进度保存到明确的组件或实体存档数据。
- OnDestroy 的存在不自动证明任何宿主移除路径都会调用；跟踪实际 ClearScenario/Reset/移除调用者，任务和监听仍明确所属者。

```lua
local function OnCreate(inst, runner)
    -- 仅首次执行的、可重复进入防护后的初始化。
end

local function OnLoad(inst, runner)
    -- 根据持久状态幂等恢复监听或表现。
end

local function OnDestroy(inst)
    -- 撤销本 Scenario 的外部资源；允许重复调用。
end

return { OnCreate = OnCreate, OnLoad = OnLoad, OnDestroy = OnDestroy }
```

这不是完整奖励/陷阱机制；奖励发放、异常重试和读档恢复需要自己的状态合同，不能靠 OnCreate 字面含义承诺永久仅发一次。

## 验证

本轮核对 modutil.lua:238-305、map/static_layout.lua:27-65、components/scenariorunner.lua:8-61；[快照记录](../../../core/dst-source-research/references/source-research.md#2026-10-17-知识内容复核)。

至少区分数据/Lua 检查、多 seed 新世界实际数量、Scenario 首次/读档/清除、服务器存档与真实客户端显示。Scenario 运行日志不能替代世界布局可达性检查。
