# 持久化常见陷阱

当保存或加载逻辑技术上运行正常，但在重新加载、迁移或时间跳跃后恢复的状态不正确时，请参考此文件。

## 常见失败模式

- 状态在重新加载后重置
  - `OnSave(...)` 从未写入它或 `OnLoad(...)` 从未恢复它
- 链接的实体在重新加载后为 nil
  - 应该在 `LoadPostPass(...)` 中解析
- 离线时间已过但作物、计时器或腐烂状态没有推进
  - `LongUpdate(dt)` 缺失或不完整
- 子辅助实体重生为空
  - 可能需要 `GetSaveRecord()` 或 `GetPersistData()`
- 旧存档崩溃或丢失新行为
  - 先区分“旧档没有新组件”和“存档已有组件数据但读档时组件缺失”；前者需要 Prefab 装配或显式迁移，后者才可能涉及 `add_component_if_missing`
- 关闭模组后读档直接报错
  - `add_component_if_missing` 会 `require("components/<name>")`；自定义组件缺失时可能无法进入存档，不能把该标记当作卸载兼容层
- 组件默认值只在构造时正确，读档后变成 nil
  - 组件的 `OnSave` 可能返回空表或 nil，导致对应 `OnLoad` 根本不执行；默认值必须在构造阶段建立
- 本地设置在运行之间不断重置
  - 任务可能使用了实体保存钩子而不是 `TheSim` 持久字符串
- 世界特定数据在不同存档之间泄漏
  - 在需要世界或实体保存生命周期的地方使用了普通持久字符串

## 实用规则

- 不要直接在保存数据中存储活动实体对象
- 如果其他保存的实体可能尚未存在，不要在 `OnLoad(...)` 中重新连接它们
- 不要将 `LongUpdate(...)` 用于普通的即时恢复逻辑
- 当一个规范字段足够时，不要保存大量冗余状态
- 不要把 `OnLoad` 当作一定执行的生命周期钩子；先确认该组件确实产出了可恢复数据
- 不要用 `add_component_if_missing` 掩盖“旧档没有新组件”的迁移问题

## 快速排查

- 生命周期顺序不清楚
  - 阅读 `references/core/dst-persistence-migration/references/persistence-contract.md`
  - 重点核对 `GetPersistData → SetPersistData → LoadPostPass → LongUpdate` 的完整顺序
  - 需要跨存档本地配置或缓存
- 阅读 `references/patterns/persistence/persistent-string-patterns.md`
- 格式错误的序列化数据可能是真正的问题
  - 阅读 `references/patterns/network/protected-call-patterns.md`
- 需要最小化实现模式
  - 阅读 `references/core/dst-persistence-migration/references/persistence-contract.md`
- 症状导向调试
  - 同时阅读 `references/patterns/diagnostic-patterns.md`
