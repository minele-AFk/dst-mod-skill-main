---
name: dst-network-contract
description: 网络契约规范。定义 netvar、Replica 和 Mod RPC 的使用边界，以及服务器权威原则。
---

# 网络契约

以下是注册与声明片段，不是完整功能实现。接口定位：当前安装的 `scripts/netvars.lua`、`scripts/networkclientrpc.lua`、`scripts/entityreplica.lua` 与 `scripts/entityscript.lua`；游戏更新后重新核对。

## netvar 声明

```lua
-- 网络 Prefab 构造中，entity:AddNetwork() 之后、SetPristine() 之前
inst._my_field = net_float(inst.GUID, "mymod.my_field", "my_field_dirty")
inst:ListenForEvent("my_field_dirty", function(inst)
    local value = inst._my_field:value()
    -- 仅更新本地表现/缓存；允许 UI 依赖尚未初始化。
end)
inst.entity:SetPristine()

if not TheWorld.ismastersim then
    return inst
end
inst._my_field:set(0) -- 权威状态由服务器写入
```

- 直接挂在实体上的 netvar 在所有端声明，并在 `SetPristine` 前完成；类型按实际范围选择。
- 客户端用 `:value()` 读值，监听声明时指定的 dirty 事件；加入时的初始展示也要读取现值，不能只等后续事件。
- 服务器和客户端必须使用相同的 netvar 名称和类型；声明不一致可能导致实体反序列化失败。
- `set_local` 只改本地副本，不同步也不触发 dirty；下一次服务器 `set` 会重新标脏。
- `net_event` 是一次性信号，不能承担初始快照或可重放状态。

数组网络变量（`net_bytearray`、`net_smallbytearray`、`net_ushortarray`）最多 31 个元素且开销较高；优先使用最小标量或拆分为确实需要同步的字段。Replica 的内部标签 `_<component>` / `__<component>` 由复制系统维护，业务代码不要手动增删。客户端依赖其他 Replica 的初始化放在 `OnEntityReplicated` 中，并允许依赖暂缺或稍后附着。

## Replica

```lua
-- modmain.lua 中注册
AddReplicableComponent("mycomponent")
```

- 对应文件为 `scripts/components/mycomponent_replica.lua`，注册的是组件名，不是 `_replica` 文件名。
- 在相关实体实例化前注册；不要把创建时序概括为“所有 Replica 都在 SetPristine 之后创建”。
- `EntityScript:AddComponent` 会先调用 `ReplicateComponent`；Replica 构造可创建其自身 netvar。直接实体字段和 Replica 内部字段的初始化路径要分开分析。
- 主组件与 Replica 的方法不互通，分别查对应源码；客户端接口须容忍组件或数据暂缺。

## Mod RPC

```lua
-- modmain.lua 注册服务器接收器；具体业务逻辑另行实现
AddModRPCHandler("mymod", "my_rpc", function(player, arg)
    if player == nil or not player:IsValid() then
        return
    end
    -- 在这里重新校验 arg 类型、数值范围、距离、权限和冷却。
    -- 本示例没有游戏状态修改，不可直接当成完整业务处理器。
end)
-- 客户端发送；先确保双方均已注册同一 namespace/name
SendModRPCToServer(MOD_RPC["mymod"]["my_rpc"], arg)
```

## 安全原则

1. 永远不信任客户端传来的实体或数值
2. 服务端必须重新验证权限和范围
3. 使用 Entity 参数而非 GUID 字符串
4. Server、Client、Shard RPC 分别使用对应的注册和发送函数；不要从服务器处理器首参推断其他方向的参数契约。
5. 声明存在不代表参数、运行端或生命周期正确；按 [联机专题](../GUIDE.md) 验证主机、远端客户端、专服和洞穴。

## 主机与远端的业务入口

若主机本地操作走快路径，核对它与远端请求执行同一套材料、权限、距离和冷却检查；允许传输路径不同，不能把主机跳过 RPC 等同于跳过业务校验。UI 的“可用”或乐观数量只是客户端视图，提交时仍从服务端真实状态计算结果。已有 Action/Builder 链路适用时优先复用，不因案例采用 RPC 就另建一套。

此项吸收自 [RULE-NET-002](../../../knowledge/dst-engineering-kb/rules/net.md#rule-net-002) 的审查思路，原记录为 E1 单案例静态候选。验证时分别尝试主机和远端的非法参数、材料不足与重复请求，结论以当前项目调用链及实际测试为准。

## 同步载体、受众与数值范围

| 需求 | 载体与合同 |
|---|---|
| 所有观察者和加入中玩家读取当前状态 | 实体 netvar 或 Replica；提供初值和后续 dirty |
| 客户端组件式只读接口 | 主组件保存权威事实，Replica 提供 getter/setter 与实际 netvar |
| 所属玩家私有状态、附着/分离与所有权 | 对照同类 classified；受众、父子关系与可见性分别确认 |
| 一次操作请求 | 优先原版 Action/Builder；确需时 Mod RPC，主机快路径同样校验 |
| 瞬时表现通知 | 先考虑由复制状态推导，再用事件；事件不能替代初始快照 |

当前 netvars.lua：net_bool 为 1 bit；net_tinybyte 0–7；net_smallbyte 0–63；net_byte 0–255；net_shortint 为有符号 16 bit，net_ushortint 0–65535；net_int/net_uint 为 32 bit；net_float 为 32-bit 浮点。0–100 整数进度可用 net_byte，不能用 net_smallbyte；编码范围、玩法上限和收发缩放分别检查。字符串不直接 set(table)，多字段也不构成事务。

主组件通过引擎已创建的 Replica setter 写值，不在两边各建同 GUID、同名 netvar，也不手动 new/赋值 inst.replica。Class 属性 setter 只有确实写网络值才同步。绑定时读现值，再监听实际 dirty；set_local/set 的 force-dirty 是特定通知语义，不是每次赋值的通用要求。相关依赖可尚未齐全，允许延迟附着并安全重绑。

classified 不是“字段多就必须加”的框架。inventory_replica:AttachClassified 等是具体组件合同，不是所有实体通用 API；目标受众可由 Network:SetClassifiedTarget 控制，实际流程按同类原版核对。移除或换绑时撤销旧监听；不假设所有观察者能读私有 player_classified。

## 最小实体 netvar 与初始表现

以下为 Prefab 构造片段，未提供资源、Prefab 返回与业务触发：

```lua
local function OnEnabledDirty(inst)
    local enabled = inst._my_enabled:value()
    -- 只更新本地表现；具体可视对象由项目提供。
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddNetwork()
    inst._my_enabled = net_bool(inst.GUID, "mymod.enabled", "mymod_enabled_dirty")
    inst.entity:SetPristine()

    if not TheNet:IsDedicated() then
        inst:ListenForEvent("mymod_enabled_dirty", OnEnabledDirty)
        OnEnabledDirty(inst)
    end
    if not TheWorld.ismastersim then
        return inst
    end
    inst._my_enabled:set(false)
    if not TheNet:IsDedicated() then
        OnEnabledDirty(inst)
    end
    return inst
end
```

完整主组件/Replica 例子维护在 [组件案例](../../../cases/case-custom-component.md)，不复制第二套不完整组件。OnEntityReplicated 可作为依赖复制对象的客户端挂载点，但不能保证私有 classified 或 HUD 都就绪；以真实复制/附着事件补绑定，参考 [玩家复制](../../../patterns/network/player-network-patterns.md)。

## RPC 方向、重建与排错

| 方向 | 注册与句柄 | 接收参数 |
|---|---|---|
| 客户端到服务端 | AddModRPCHandler / GetModRPC | handler 隐式获得请求玩家，客户端不额外传 ThePlayer 充当可信身份 |
| 服务端到客户端 | AddClientModRPCHandler / GetClientModRPC | 收件 userid 与 payload 分开，不能沿用服务端 player 首参假设 |
| 分片之间 | AddShardModRPCHandler / GetShardModRPC | 分片身份与业务载荷分开核对 |

实体参数须是接收端可映射的合法网络实体；跨端/分片不共用 GUID/Ents 命名空间。发送前确认实体可见，引用迟到或移除时降级。服务端拒绝需让预测临时状态可靠退出，不能由预览或客户端 UI 重复结算资源、伤害与奖励。

按“注册 → 创建/net 类型 → 初始复制 → getter → 实际事件 source → UI 绑定”排查。服务端打印设置值不证明远端收到；持续读取一个未同步的普通字段也无法修复传输。控制数据量、精度、发送频率和 UI 刷新频率，离散变化走事件，连续动画本地插值。

加入中、重连、Controls 重建、幽灵入场、换分片、父实体晚复制均从当前快照重建，旧监听/输入/FX 先解绑。验证非法参数、资源/权限/距离/物品归属/冷却、重复请求和服务器拒绝，并分别报告主机、真实远端与专服结果。可变上限值见 [数值案例](../../../cases/case-custom-stat.md)，HUD 初值见 [HUD 合同](../../../world-ui-assets/dst-hud-screens-input/references/hud-customization.md)。
