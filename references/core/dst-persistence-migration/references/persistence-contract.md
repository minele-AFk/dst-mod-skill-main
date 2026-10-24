---
name: dst-persistence-contract
description: 存档契约规范。定义 OnSave、OnLoad、LoadPostPass 和 OnLongUpdate 的数据边界与迁移策略。
---

# 存档契约

## Component 存档签名

Component 的 `OnSave()` 返回数据和可选 GUID 列表；Prefab 的保存回调则写入传入表。两者不能共用一套参数签名。以下仅展示保存契约，`MyComp` 和字段由实际组件提供。

```lua
function MyComp:OnSave()
    local data = {
        schema_version = 1,
    }
    local refs
    if self.target ~= nil and self.target:IsValid() then
        data.target_guid = self.target.GUID
        refs = { self.target.GUID } -- GUID 值列表，不放 EntityScript
    end
    return data, refs
end

function MyComp:OnLoad(data, newents)
    -- 先处理 nil、缺字段、旧枚举和 schema 迁移；不依赖其他组件加载顺序。
end

function MyComp:LoadPostPass(newents, data)
    local record = data ~= nil and data.target_guid ~= nil and newents[data.target_guid] or nil
    self.target = record ~= nil and record.entity or nil
end

function MyComp:LongUpdate(dt)
    -- 按引擎传入 dt 补算本机制；不等于自动按现实离线秒数推进。
end
```

## Prefab 存档签名

```lua
local function OnSave(inst, data)
    data.schema_version = 1
    data.custom = inst.my_data
    -- 若有外部实体引用，写入 GUID 后 return { target.GUID }；不要返回 data。
end

local function OnLoad(inst, data, newents)
    if data ~= nil then
        inst.my_data = data.custom -- 实际功能另做字段检查与迁移
    end
end

local function OnLoadPostPass(inst, newents, data)
    -- 需要外部引用时在这里用 newents 恢复。
end

-- 在 Prefab 构造函数中赋值；这些回调第一个参数就是 inst，不另加隐式 self。
inst.OnSave = OnSave
inst.OnLoad = OnLoad
inst.OnLoadPostPass = OnLoadPostPass
```

## 迁移策略

- schema_version 递增，OnLoad 检查版本并迁移
- 旧字段保留兼容读取，新字段提供默认值
- 不要假设新字段一定存在
- `OnPreLoad` 在组件加载前；各组件的 `OnLoad` 使用 `pairs` 遍历，无固定先后；Prefab 的 `OnLoad` 在其后，实体引用统一留给 postpass。
- 可从真实实体重建的注册表/显示缓存通常从其 Owner 恢复，避免把两份副本都当权威保存；不可重建的玩法状态仍需保存。
- `OnSave` 返回空表或 `nil` 时，保存器不会为该组件写入条目，因此 `OnLoad` 不会被调用。构造阶段必须先建立合法默认值，不能靠“读档回调总会执行”初始化。

2026-10-17 核对当前安装 `scripts.zip`：`entityscript.lua:GetPersistData/SetPersistData/LoadPostPass`，组件 refs 的值由引擎收集。较完整的生命周期和保存链路见 [恢复说明](../../../engineering/dst-mod-engineering/lifecycle-save.md)；上述核对只证明调用契约，不是存档实机验收。

## 生命周期与保存形式选择

当前 EntityScript 的调用顺序：GetPersistData 先组件 OnSave，再 Prefab OnSave；SetPersistData 按保存请求补组件、Prefab OnPreLoad、各组件 OnLoad、Prefab OnLoad；LoadPostPass 先组件再 Prefab；LongUpdate 先 Prefab OnLongUpdate 再组件 LongUpdate。组件间遍历不保证固定顺序。

### 完整生命周期顺序

以下顺序来自当前安装版 `entityscript.lua`，用于定位状态丢失和补组件问题：

```text
保存 GetPersistData
  -> 各组件的 OnSave
  -> Prefab OnSave

读档 SetPersistData
  -> 按 add_component_if_missing 补组件
  -> Prefab OnPreLoad
  -> 各组件 OnLoad
  -> Prefab OnLoad

引用恢复 LoadPostPass
  -> 各组件 LoadPostPass
  -> Prefab OnLoadPostPass

离线补算 LongUpdate
  -> Prefab OnLongUpdate
  -> 各组件 LongUpdate
```

组件遍历使用 `pairs`，不能依赖 A 组件先于 B 组件完成。`OnSave` 返回 `{}` 或 `nil` 时，`GetPersistData` 不会写入该组件的数据，`SetPersistData` 也就不会调用其 `OnLoad`；默认值应在构造阶段建立。`OnPreLoad` 可能早于组件 `OnLoad`，不要在这里假设组件状态已经恢复。

| 保存对象 | 入口与参考 |
|---|---|
| 本地标量、模式、等级 | OnSave/OnLoad；glommer、armor、fueled 为参考 |
| 外部实体链接 | 保存 GUID 并返回 refs，postpass 用 newents 恢复；childspawner 等 |
| 父实体拥有完整子实体 | GetSaveRecord/SpawnSaveRecord；inventory、container、player_common |
| 代码已创建的辅助实体内部数据 | GetPersistData/SetPersistData，并传递其 refs；slingshotmods |
| 引擎传入的时间补算 | LongUpdate(dt)；timer、pickable、perishable、childspawner |
| 跨存档本地配置/缓存 | [Persistent String](../../../patterns/persistence/persistent-string-patterns.md)，不冒充世界存档 |

外部引用不存在时安全降级，Prefab 的 postpass 可用于重新连接邻居、AI 与显示；参考 winona_battery_low、daywalker、spiderden。LongUpdate 不代替普通帧更新，也不自动代表现实离线时长。任务、效果与回滚策略见 [生命周期与恢复](../../../engineering/dst-mod-engineering/lifecycle-save.md)。

## 拥有的子实体与辅助数据模板

下面两个模板分别面向完整子实体与已由代码创建的辅助实体，不能同时保存同一个子实体两份。MyComponent、CreateHelper 与字段由宿主提供。

```lua
local function OnSave(inst, data)
    if inst._child ~= nil and inst._child:IsValid() then
        data.child = inst._child:GetSaveRecord()
    end
end

local function OnLoad(inst, data)
    if data ~= nil and data.child ~= nil then
        local child = SpawnSaveRecord(data.child)
        if child ~= nil then
            inst._child = child
        end
    end
end
```

```lua
function MyComponent:OnSave()
    if self.helper ~= nil and self.helper:IsValid() then
        local helper_data, refs = self.helper:GetPersistData()
        return { helper = helper_data }, refs
    end
end

function MyComponent:OnLoad(data, newents)
    if data ~= nil and data.helper ~= nil then
        self:CreateHelper()
        if self.helper ~= nil then
            self.helper:SetPersistData(data.helper, newents)
        end
    end
end
```

如辅助实体保存了外部 GUID，还必须把自己的 postpass 转给该辅助实体；SetPersistData 不会代替后续引用修复。构造阶段若已生成子实体，恢复前定义复用/替换与清理策略，避免读档生成双份。

## 时间补算与补组件迁移

```lua
function MyComponent:LongUpdate(dt)
    if self.cooldown > 0 then
        self.cooldown = math.max(0, self.cooldown - dt)
        if self.cooldown == 0 then
            self.inst:PushEvent("cooldownfinished")
        end
    end
end
```

只有该玩法选择时间补算时使用，并避免与正常更新对同段时间重复计算。保存剩余时间、读档重建和是否死亡/离线继续计时属于玩法约定。

当前保存器会汇总组件返回数据的 add_component_if_missing 标记；加载器可据此补缺失组件，再进入 preload/load。这只恢复存档里已经带标记的数据，不能让旧档自动拥有从未保存的新组件。新版本要给旧实体新增组件，仍需 Prefab 装配或显式迁移。

该标记的补组件路径会执行 `require("components/<name>")`。如果存档保存了模组自定义组件，而读档时该模组被关闭或文件缺失，补组件可能直接报错并阻止存档进入。不要把 `add_component_if_missing = true` 当成跨模组卸载的兼容层；原版组件相对安全，自定义组件必须先验证模组可用性、缺失回退和失败日志。

```lua
function MyComponent:OnSave()
    return { value = self.value, add_component_if_missing = true }
end
```

本段于 2026-10-21 对照安装版 entityscript.lua:GetPersistData/SetPersistData/LoadPostPass/LongUpdate；模板只说明合同，未执行实际存档重启测试。

2026-10-22 补充核对同一安装版 `entityscript.lua:1903-1914,1954-1981`：保存/加载顺序与补组件风险已按源码确认；未执行关闭模组读档、真实存档重启或联机验证。
