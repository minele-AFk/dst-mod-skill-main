# Prefab 加载与构造契约

## 固定顺序

1. CreateEntity。
2. 添加 Transform、AnimState、Physics、Network 等原生子系统。
3. 设置客户端必须立即知道的动画、标签和 Prefab 直接创建的 netvar。
4. 调用 SetPristine。
5. 非主机立即返回。
6. 主机添加普通 Component、Brain、SG、保存和权威事件；已注册的可复制 Component 会先构造 Replica。
7. 返回 Prefab。

## 判断放置位置

| 内容 | SetPristine 前 | 主机分支 |
| --- | --- | --- |
| Network、Prefab 直接创建的 netvar | 是 | 否 |
| 可复制 Component 的 Replica netvar | 由 ReplicateComponent 创建 | AddComponent 可触发 |
| 客户端动画初值 | 是 | 否 |
| 客户端动作所需标签 | 是 | 否 |
| 权威玩法 Component | 否 | 是 |
| Brain 与服务器 SG | 否 | 是 |
| 掉落、伤害、计时 | 否 | 是 |
| OnSave、OnLoad | 否 | 是 |

`Make*Physics`、`MakeInventoryFloatable`、`Make*Pristine` 等标准助手用于在构造阶段建立物理、漂浮和 pristine 状态，应放在 `SetPristine` 之前。`Make*Burnable`、`Make*Propagator`、`MakeHauntable*`、冰冻等依赖主机权威逻辑的助手放在主机分支；不要只按函数名猜顺序。

标准助手的参数、返回值和适用对象以 `standardcomponents.lua` 的实际定义为准。不同助手可能创建组件、监听事件或修改物理状态，调用前先核对同类原版 Prefab，避免把库存物理套给建筑或角色。

## 原生子系统

Entity:AddAnimState、AddPhysics、AddLight、AddFollower、AddVFXEffect 等可能没有 Lua 定义。用同类 Prefab 调用点确认顺序与参数。不要把 Inventory 物理套给建筑或角色。

## 生命周期

检查以下路径是否需要处理：

- OnEntitySleep 与 OnEntityWake
- inst.OnSave、inst.OnLoad、inst.OnLoadPostPass、inst.OnLongUpdate
- OnRemoveEntity
- 进入和离开库存
- 装备和卸下
- 燃烧、冻结、工作和死亡
- 子实体、任务、事件与循环声音清理

## 模板适用边界与依赖

上面的顺序面向普通网络实体；本地 FX、classified 和纯服务端控制实体需要自己的构造策略。表中“普通 Component”指权威玩法组件，有公共需求的组件不适用这一行。SetPristine 不会自动同步任意 Lua 字段，也不会把所有渲染调用变成网络协议。

PrefabFiles 列文件模块，Prefab(name, fn, assets, deps) 的 name 是注册名；一模块可返回多个 Prefab，文件名不必等于所有注册名。assets 是资源，deps 是依赖 Prefab 名，二者不能混用。顶层 Assets 与 Prefab 私有 assets 按使用者配置，不必重复塞入全部资源。

依据 [实体与组件参考](../../../engineering/dst-mod-engineering/entities-components.md)；组件实际装配顺序另见 [组件契约](../../dst-component-authoring/references/component-contract.md)。


## PrefabFiles 文件模块、注册名与职责

`PrefabFiles = { "my_mod_item" }` 位于 modmain，实际文件为 **`scripts/prefabs/my_mod_item.lua`**，不是 Mod 根下 `prefabs/`。当前 mods.lua 将 Mod 的 scripts 加入模块搜索路径，再调用 `LoadPrefabFile("prefabs/" .. prefab_path, ...)`；这里的模块路径不能直接当物理根路径。

文件必须返回一个或多个 `Prefab(...)` 对象；也可返回 `MakePlacer(...)` 生成的 placer。PrefabFiles 不带 `.lua`，注册名以 `Prefab(name, ...)` 为准；依赖列表是依赖声明，**不是 SpawnPrefab 白名单**，不会使未注册名字凭空可生成。

| 内容 | 文件/入口 | 责任 |
|---|---|---|
| 注册、顶层 Assets、Hook | `modmain.lua` / modimport | 启动与粘合，见 [入口模式](../../../patterns/startup/modmain-patterns.md) |
| 世界实体/背包物品 | `scripts/prefabs/<module>.lua` | 构造与最终挂载组件、Brain、SG |
| 可复用有状态业务 | `scripts/components/<name>.lua` | Class 模块，AddComponent 加载，不进 PrefabFiles |
| 客户端读取伙伴 | `scripts/components/<name>_replica.lua` | modmain 用 AddReplicableComponent 注册，设计网络字段 |
| AI 决策 | `scripts/brains/<name>.lua` | require 返回脑类，Prefab SetBrain 接入 |
| 动画/动作计时 | `scripts/stategraphs/SG<name>.lua` | SetStateGraph 接入，见 [SG 合同](../../../gameplay/dst-stategraph-authoring/references/stategraph-contract.md) |

小幅扩展官方组件可用 AddComponentPostInit；自有可复用业务可建新组件。组件模块样例、构造时机与清理见 [组件契约](../../dst-component-authoring/references/component-contract.md)。客户端读取需求按 Replica/netvar 设计，不在客户端直接读服务器组件。

## 类型组合与模板选择

以下是装配方向，不是仅添加这些组件就完成玩法；先添加组件，再设置属性，并核对它们之间的依赖。

| 类型 | 常用组合与必须补齐的行为 | 保留位置 |
|---|---|---|
| 物品/材料 | inspectable、inventoryitem；按需 stackable、fuel、燃烧/漂浮助手 | [物品模板](../assets/item-template.lua) |
| 武器/护甲 | weapon 或 armor + equippable；装备/卸下表现成对，耐久与损坏路径 | [物品与装备专题](../../../gameplay/dst-inventory-equipment-containers/GUIDE.md) |
| 建筑/容器 | 物理、container 配置、开关回调；workable 工作与完成回调；placer/配方另接 | [建筑模板](../assets/building-template.lua)、[容器契约](../../../components/storage/container.md) |
| 生物 | 按行为选择 health、combat、lootdropper、locomotor；真实 Brain、SG 与动画 | [Brain 专题](../../../gameplay/dst-brain-authoring/GUIDE.md)、[SG 专题](../../../gameplay/dst-stategraph-authoring/GUIDE.md) |
| FX/声音代理/本地助手 | 生命周期、运行端和可见范围；不机械套普通网络实体骨架 | [效果模式](../../../patterns/asset/effects-patterns.md) |

普通骨架见 [Prefab 模板](../assets/prefab-template.lua)，Make* 的签名/适用对象见 [标准助手](../../../patterns/prefab/standard-helper-patterns.md)，动画配置见 [AnimState 模式](../../../patterns/asset/animstate-patterns.md)，皮肤另见 [皮肤模式](../../../patterns/skin/skin-patterns.md)。这些模板需要自己的资源和业务实现，不代表可独立运行的完整 Mod。

## 变体工厂与性能边界

共享多数设置、只改参数/build/标签/回调时，可用 commonfn + 小包装器或配置表 → factory → `return unpack(results)`；原版 staff.lua 可作同类参考。不要把业务差异很大的变体塞进巨大配置表，分文件更清楚时保持分离。具体设计例见 [Prefab 编写模式](prefab-authoring-patterns.md)。

缓存组件引用前确认其生命周期，不跨 RemoveComponent 继续使用旧对象。事件与定时任务按触发频率和测量结果选择，DoPeriodicTask 不自动更省开销；任务、监听和子实体要有清理出口。查询采用有效标签过滤，但标签有真实消费者，不能给普通实体随意加 player/character 冒充角色。见 [标签模式](../../../patterns/prefab/tag-patterns.md) 与 [实体查询](../../../patterns/runtime/entity-query-patterns.md)。

跨端数值使用有效的 netvar/Replica/classified 协议，不能用虚构的 AddChildEntity 片段替代 classified 生成与附着；生命周期见 [网络契约](../../dst-networking-rpc/references/network-contract.md)。

本节 2026-10-21 对照当前安装包 mods.lua、entityscript.lua、entityreplica.lua 与既有模板；未执行物品、容器、生物或远端客户端实机验收。
