# 组件 Class 构造、网络与保存契约

## 构造与可用上下文

组件模块通常返回 `Class(function(self, inst) ... end)`；`inst:AddComponent("my_mod_counter")` 加载 `components/my_mod_counter.lua`。组件文件不放入 PrefabFiles。`AddComponentPostInit` 是构造后的扩展钩子，不负责给实体添加该组件。

当前调用顺序为 `ReplicateComponent(name) → cmp(inst) → inst.components[name] = loadedcmp → ComponentPostInit(loadedcmp, inst)`。构造器内使用 `self`；此时从 `inst.components[name]` 取自身会得到 nil。其他组件是否存在取决于宿主装配顺序，PostInit 也不保证所有依赖已添加。

| 对象 | 契约 |
|---|---|
| `self.inst` | 当前宿主 EntityScript；不是自动拥有全部玩法组件 |
| `inst.components.x` | 当前端实际添加的组件；先核对初始化路径 |
| `inst.replica.x` | 当前实体有效的 Replica 接口；主机和客机均可能使用，不是“仅主机” |
| `TheWorld` | 当前运行分片的世界，地表和洞穴各有一个；前端/worldgen 环境另查 |
| `GLOBAL` | 模组环境提供的全局引用；普通 require 模块不以“GLOBAL 始终存在”为前提 |

## 网络合同

普通权威玩法组件放服务端；有公共初始化需求的组件按同类原版放公共区，不能由“组件”二字决定运行端。

自定义 Replica 使用模组环境 `AddReplicableComponent("my_mod_counter")`，模块为 `components/my_mod_counter_replica.lua`。引擎通过实体复制流程构造 Replica；组件注册不等于自动同步任意 Lua 字段。网络值、classified 及其附着时机参照当前同类原版，主组件 setter 负责所有权威写入，Replica 提供读取接口和变化通知。

不存在可默认套用的通用 `SetReplicateData/ReadReplicate` 合同，也不要求在 modinfo 增加 `replicable_components`。Class 第三参只是属性 setter；是否写 netvar 由实际 setter 决定。dirty 只通知变化，绑定时先读取初值，再处理后续变化。

## 生命周期与保存

| 回调 | 责任 |
|---|---|
| `OnSave()` | 返回纯数据，可另返回 GUID 值列表 refs；不返回函数、任务或实体对象 |
| `OnLoad(data, newents)` | 允许旧档无字段；不依赖其他组件的固定加载顺序 |
| `LoadPostPass(newents, data)` | 解析保存的实体引用，容忍目标未恢复 |
| `LongUpdate(dt)` | 只在相应调用路径推进；dt 不自动等于现实离线时长 |
| `OnRemoveFromEntity()` | 单独 RemoveComponent 时撤销本组件贡献 |
| `OnRemoveEntity()` | 宿主移除时收尾；与前一出口共用幂等清理函数 |

回调由实际运行该组件及相应保存/更新流程的一端执行，不统一标为“所有端”。完整签名及 Prefab 回调区别见 [持久化契约](../../dst-persistence-migration/references/persistence-contract.md)。

保存玩法事实与重建依据；可推导的最大值、FX 和 modifier 可在加载后按同一公式恢复。冷却是否保存由玩法合同决定，不能一概当作可丢弃瞬时值。重复应用后不能累乘基础值，也不能清空其他系统的 modifier。

## 查证与验收

2026-10-17 对照本机安装包的 `entityscript.lua:AddComponent/RemoveComponent`、`entityreplica.lua:ReplicateComponent/ReplicateEntity`、`modutil.lua:AddReplicableComponent` 与 `class.lua`；快照见 [源码复核记录](../../dst-source-research/references/source-research.md#2026-10-17-知识内容复核)。

验证首次生成、构造依赖、真实客机读取、读档缺字段、单独移除组件、重复 Apply/Cleanup 与实体移除。源码确认不代表这些游戏路径已经跑过。

## 可复用组件的组织与接入

组件文件处理状态和业务规则，初始化/配置模块处理参数与 Hook；是否拆成两个文件取决于复用需求，不是每个组件的强制结构。使用稳定、唯一的模块/字段/事件/netvar 前缀，并通过显式参数传入依赖；从 debug.getinfo 路径推断前缀只适用于已知命名和 loader，不能当通用前提。

Init 可配置等级上限、攻速或行为开关，但不能任意推迟到实体复制完成后再创建网络字段。直接实体 netvar 与 Replica 构造按 [网络合同](../../dst-networking-rpc/references/network-contract.md) 建立。EntityScript 没有可直接套用的通用 AddNetworkVariable(name, type, default) API；旧教程的该写法属于未实现的项目助手，不能复制成官方用法。是否复制由客户端读取需求决定，不把“主客机组件”视为天然优于纯服务端组件。

| 复用能力 | 归属和需要保留的合同 |
|---|---|
| 攻速/装备辅助 | 组件保存数据，初始化器分别接 combat、SG 时间线与动画速度，避免只改一处 |
| Action/Trader 扩展 | 模组环境注册 Action/收集器/SG；客户端只预检，服务器验证文本对应行为、距离与目标 |
| 升级系统 | 可配置等级/上限与每级效果，保存进度，按范围选网络类型，幂等重建加成 |
| 休眠暂停任务 | OnEntitySleep/OnEntityWake 成对处理，移除时取消，唤醒不叠加周期任务 |
| 临时实体追踪 | 生成时登记、移除时注销；查询前校验，避免全表扫描与强引用泄漏 |
| 扩展标记与皮肤 | 先核对目标消费者与复制范围；自定义网络位不自动成为原生 HasTag，皮肤可只用初始化 Hook |

Action 接入见 [动作合同](../../dst-action-authoring/references/action-pipeline.md)，生命周期与资源清理沿本文前段。可复用性来自命名隔离、参数合同、正确运行端与可撤销贡献，而非复制某个项目的文件名。


## 创建组件：Class、OnSave 与 OnLoad

物理路径 `scripts/components/my_mod_counter.lua`；由 Prefab 在所需运行端 `inst:AddComponent("my_mod_counter")`。下面只演示纯数据保存，不包含网络读取协议。

```lua
local MyModCounter = Class(function(self, inst)
    self.inst = inst
    self.value = 0
end)

function MyModCounter:OnSave()
    return { value = self.value }
end

function MyModCounter:OnLoad(data)
    if data ~= nil and type(data.value) == "number" then
        self.value = data.value
    end
end

return MyModCounter
```

组件没有任务、监听或其他外部贡献时不必写空清理方法；需要时按上文 OnRemoveFromEntity/OnRemoveEntity 合同实现幂等清理。模块加载与各文件职责见 [Prefab 契约](../../dst-prefab-authoring/references/prefab-contract.md)。
