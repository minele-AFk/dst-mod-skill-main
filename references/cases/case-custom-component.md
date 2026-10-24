# 示例：可保存、可查询的自定义资源组件

本例只展示组件/Replica 的构造、写入和保存合同，不是已运行的角色或 Buff 成品。旧案例依赖项目私有工具、动画和输入组件，且含错误的网络类型及手动 Replica 构造；这些内容不再作为通用模板。

示例保留 0–800 的资源范围，允许小数，使用 net_float。当前 net_smallbyte 仅 0–63、net_byte 仅 0–255，不能容纳该范围；整数资源可另核对 net_ushortint。上限、恢复、攻击返还、激活消耗、死亡政策由具体玩法定义，不由本文替用户决定。

## 1. Replica 模块

保存为 scripts/components/my_mod_counter_replica.lua：

```lua
local CounterReplica = Class(function(self, inst)
    self.inst = inst
    self._current = net_float(inst.GUID, "my_mod_counter.current", "my_mod_counterdirty")
end)

function CounterReplica:GetCurrent()
    return self._current:value()
end

function CounterReplica:SetCurrent(value)
    self._current:set(value)
end

return CounterReplica
```

SetCurrent 由主组件调用；客户端展示只读取。该命名并不创建权限控制，不能因为公开了 setter 就在客户端结算玩法。

## 2. 主组件模块

保存为 scripts/components/my_mod_counter.lua：

```lua
local MAX_VALUE = 800
local Counter = Class(function(self, inst)
    self.inst = inst
    self.max = MAX_VALUE
    self.current = 100
    inst.replica.my_mod_counter:SetCurrent(self.current)
end)

function Counter:GetCurrent()
    return self.current
end

function Counter:SetCurrent(value)
    if type(value) ~= "number" or value ~= value then
        return false
    end
    self.current = math.max(0, math.min(self.max, value))
    self.inst.replica.my_mod_counter:SetCurrent(self.current)
    return true
end

function Counter:DoDelta(delta)
    if type(delta) ~= "number" or delta ~= delta then
        return false
    end
    return self:SetCurrent(self.current + delta)
end

function Counter:OnSave()
    return { version = 1, current = self.current }
end

function Counter:OnLoad(data)
    if data ~= nil and type(data.current) == "number" then
        self:SetCurrent(data.current)
    end
end

return Counter
```

这里用集中 setter，Class 第三参不是必须。若改用属性 setter，它必须显式调用 Replica；普通赋值本身不联网。未来增加可配置最大值、激活状态或跨字段迁移时分别保存依据，不能仅存 current 后声称完整 Buff 已恢复。

## 3. 注册与装配

在 modmain 注册 AddReplicableComponent("my_mod_counter")，早于目标实体生成。然后在已授权目标的主机初始化中 inst:AddComponent("my_mod_counter")；角色优先使用现有 MakePlayerCharacter 的 master 回调，不为示例重造一个不完整玩家 Prefab。

AddComponent 会先构造已注册的 Replica，再构造主组件，因此主组件构造器可以调用它。构造期间 inst.components.my_mod_counter 尚未指向自身。客机由 ReplicateEntity 创建自己的 Replica；不要手动给 inst.replica 赋值或重复 new 一个实例。

HUD 在复制接口就绪后主动 GetCurrent 一次，再监听宿主的 my_mod_counterdirty 事件。没有真实传输时，服务端 PushEvent 不能替代这条复制链。

## 4. 扩展到激活效果时

资源扣除与效果激活属于同一次服务端业务：验证请求者、资源、冷却、目标和当前状态，成功后结算一次。需要重复激活时先定义刷新/叠加，再管理任务和 modifier。

任务句柄保存在组件，RemoveComponent 对应 OnRemoveFromEntity，宿主移除对应 OnRemoveEntity；清理可重复。活动效果另外保存恢复依据和剩余时间，不能让一个零延迟 Init 猜其他组件已经加载。

快捷键是客户端输入层，使用真实输入注册与动作/RPC 请求；不存在可由教程默认提供的 inputcontroller:AddActionListener 合同。所有世界扫描、FX、持续恢复按具体需求另接入，不复制旧案例的全玩家高频扫描。

## 5. 静态证据与待验收

本轮核对 entityscript.lua:610-645、entityreplica.lua:34-84、netvars.lua:6-14；示例仅做 Lua 语法检查。仍待游戏验证首次生成、服务端写入、真实客机初值/变化、0/800/小数边界、旧档缺字段、保存重启和组件移除。

- [组件合同](../core/dst-component-authoring/references/component-contract.md)。
- [网络合同](../core/dst-networking-rpc/references/network-contract.md)。
- [HUD 接入](../world-ui-assets/dst-hud-screens-input/references/hud-customization.md)。
- [Buff 生命周期](../gameplay/dst-status-buffs-survival/GUIDE.md)。
