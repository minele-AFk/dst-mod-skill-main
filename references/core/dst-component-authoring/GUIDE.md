---
name: dst-component-authoring
description: Design and implement Don't Starve Together Components. Use when defining __init, inst:AddComponent, component fields, methods, ReplicateComponent, OnSave/OnLoad/LongUpdate, common helpers, and Replica interfaces.
---

# DST 组件编写

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

把可序列化状态、玩法逻辑和网络契约集中在 Component 内部，让 Prefab、SG、Brain 和其他系统只通过稳定接口访问。

## 工作流

1. 确定组件职责、宿主实体类型、哪些字段需要同步、是否需要 Replica。
2. 模块返回 Class(function(self, inst) ... end)，由 inst:AddComponent("my_mod_name") 添加；AddComponentPostInit 只扩展已创建实例。
3. 构造器先初始化 self.inst 与状态；此时 inst.components.my_mod_name 尚未指向自身，不能依赖未装配的其他组件。
4. 按实际用途选择服务端权威组件或公共组件；需要客户端接口时单独设计 Replica。
5. 自定义 Replica 用 AddReplicableComponent 注册，提供 components/my_mod_name_replica.lua；不用 modinfo 的虚构注册字段。
6. 明确每个网络值的创建、权威 setter、Replica 读取与 dirty 事件；绑定时读取初值。普通字段赋值和 Class 属性代理本身不自动联网。
7. 按玩法合同实现 OnSave、OnLoad、LoadPostPass；需要时间追赶时再核对 LongUpdate 调用者。
8. 外部通过具体组件的已核实方法交互；存在性使用 inst.components.name ~= nil，不猜通用 Get/Set 或 HasComponent 接口。

## 源码锚点

- components/name.lua 与 components/name_replica.lua：分别核对主组件与 Replica 接口。
- entityscript.lua、entityreplica.lua：AddComponent、RemoveComponent、Replica 构造与持久化调用者。
- modutil.lua：AddReplicableComponent、AddComponentPostInit。
- 运行端由宿主初始化决定；权威玩法通常在服务端，客户端读取所需 Replica 或网络状态。
- 其他组件：常见组件的字段名（owner、inst、owner.components、enable、disabled 等）。

## 不变量

- 客户端不访问仅服务端存在的主组件；具有公共初始化需求的组件不能机械移到服务端。
- Replica 可读接口、netvar 编码与初始化必须双方一致；不要把 Lua 字段同名当作同步机制。
- 主机分支并不保证依赖组件已存在；依赖按装配顺序或显式初始化接口连接。
- 存档、任务与 modifier 分别拥有清理和恢复责任，不能依赖组件删除自动撤销所有业务副作用。

## 验证

- 实体生成、移除、睡眠、保存和回滚后组件状态一致。
- 玩家服务器端组件和玩家客户端组件之间的 Replica 同步一致。
- 涉及迁移时在目标分片重建数据与引用，不把本分片任务或 GUID 直接交给另一分片使用。

## 按需资源

- 字段命名与生命周期契约读取 [component-contract.md](references/component-contract.md)。
- 需要常用组件（workable/tool/weapon/sanity/temperature/stackable/spawner/timer/stewer/trader/teleporter/trap 等）的字段与方法速查时读取 [component-api-quickref.md](references/component-api-quickref.md)。
- 需要再生/生长类玩法（区域资源再生 / 批量 prefab 工厂 / 生长推进 / 三阶段草药 / 刷新与再植）时查阅 `references/mod-notes/` 下 [mod-fengyun.md](../../mod-notes/mod-fengyun.md)（丰耘秘境）与 [mod-daogui.md](../../mod-notes/mod-daogui.md)（道诡异仙）原始笔记。
