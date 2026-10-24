---
name: dst-persistence-migration
description: Implement durable Don't Starve Together save and load behavior. Use when writing Component OnSave, OnLoad, LoadPostPass or LongUpdate methods, Prefab OnSave, OnLoad, OnLoadPostPass or OnLongUpdate callbacks, GetPersistData, SetPersistData, versioned data, entity references, save upgrades, retrofit logic, or fixing state lost after rollback, unload, or world migration.
---

# DST 存档、加载与迁移

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

只保存恢复玩法状态所需的稳定数据，并让旧版本、缺字段和实体重建顺序都可安全处理。

## 工作流

1. 列出必须跨重启保存的字段、可从当前世界推导的字段、临时缓存和外部实体引用。默认值放在构造函数中；`OnSave` 返回空表或 `nil` 时，对应组件的 `OnLoad` 不会被调用。
2. 为数据添加显式 schema 版本；Component:OnSave 的第一个返回值只放可序列化数据，必要时第二个返回值提供实体 refs。Prefab 的 inst.OnSave(inst, data) 写入传入的 data 表，并可返回 refs。
3. OnLoad 接受 nil、缺字段、旧枚举和非法范围，先迁移再应用默认值。
4. 对每个实体引用，在保存数据中保留稳定 GUID 映射并通过 OnSave 的 refs 让引擎收集对象；Component 在 LoadPostPass(newents, data) 解析，Prefab 则把签名为 (inst, newents, data) 的函数赋给 inst.OnLoadPostPass。目标缺失时降级，不持有旧 EntityScript。
5. Component 使用 LongUpdate(dt)，Prefab 把签名为 (inst, dt) 的函数赋给 inst.OnLongUpdate；按离线时间推进腐败、计时或生长时限制负值、极大值并遵守暂停规则。
6. 改变世界生成或世界组件时区分新世界配置、旧存档 Retrofit 与 Component 或 Prefab 在 OnLoad 中执行的一次性 schema 迁移。不要假设存在可供模组调用的统一存档升级钩子。
7. 谨慎使用 `add_component_if_missing`。它会触发 `require("components/<name>")`；存档引用了模组自定义组件而加载时该模组不可用，可能使读档报错。原版组件相对安全，但仍须处理组件缺失和版本差异。
8. 在保存、载入、回滚、关服重启、换分片、删除关联实体和关闭模组读档场景验证。

## 源码锚点

- entityscript.lua：GetSaveRecord、GetPersistData、SetPersistData、LoadPostPass 和 LongUpdate。
- components/ 中的 OnSave、OnLoad、LoadPostPass、LongUpdate，以及 prefabs/ 中的 inst.OnSave、inst.OnLoad、inst.OnLoadPostPass、inst.OnLongUpdate 范例。
- savefileupgrades.lua：内置存档格式升级实现，不是模组公开钩子；worldsettings_overrides.lua、map/retrofit_savedata.lua：世界设置与 Retrofit。

## 不变在

- 不要保存函数、userdata、任务句柄、组件对象或 EntityScript。
- 不要假设 OnLoad 时其他实体和世界组件已全部可用。
- 不要因为字段缺失就删除整个旧存档状态。
- 迁移必须幂等；多次加载同一版本不会重复发奖励或重复生成实体。
- `OnSave` 返回空数据等于没有恢复入口；不能把“构造时的默认值”当作读档恢复。
- `add_component_if_missing` 只补回存档已经标记的组件，不能让旧档凭空获得从未保存的新组件。

## 验证

- 新存档和至少一个模拟旧 schema 都能恢复。
- 关联实体存在、缺失和被替换三种情况均安全。
- 回滚后不会因外部副作用或重复迁移产生额外状态。
- 关闭相关模组或缺少自定义组件时，存档失败路径有明确日志且不会误称已兼容。

## 按需资源

- 需要数据边界、引用恢复和迁移顺序时读取 [persistence-contract.md](references/persistence-contract.md)。
- 需要完整保存/加载/PostPass/LongUpdate 顺序和补组件风险时读取 [persistence-contract.md](references/persistence-contract.md) 的“完整生命周期顺序”。
- 需要世界 KV（键值对存档）及其作用域（全局/世界/生物）存取模式时查阅 `references/mod-notes/` 下 [mod-shanhaisc.md](../../mod-notes/mod-shanhaisc.md)（山海秘藏）与 [mod-difu.md](../../mod-notes/mod-difu.md)（地府）原始笔记。
