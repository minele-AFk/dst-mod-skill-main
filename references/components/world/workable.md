# `workable`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改锤击、采矿、砍伐、挖掘或其他目标端工作进度和完成回调时，使用此文件。

官方源码：

- `scripts/components/workable.lua`

相关官方预制件示例：

- `scripts/prefabs/treasurechest.lua`
- `scripts/prefabs/berrybush.lua`

高频方法：

- `SetRequiresToughWork(tough)`
- `SetWorkAction(act)`
- `GetWorkAction()`
- `SetWorkable(able)`
- `SetWorkLeft(work)`
- `GetWorkLeft()`
- `CanBeWorked()`
- `SetMaxWork(work)`
- `WorkedBy(worker, numworks)`
- `SetOnWorkCallback(fn)`
- `SetOnFinishCallback(fn)`
常见组件搭配：

- `workable` + `lootdropper`
- `workable` + `pickable`
- `workable` + `tool`

常见陷阱：

- `workable` 是目标端的；动作物品通常需要 `tool`。
- 许多破坏流程还需要战利品、燃烧或结构清理。
- 如果加载后完成行为看起来错误，也要检查存档或读档回调。

后续阅读：

- [tool.md](../items/tool.md)
- [world-system-patterns.md](../../patterns/world-system-patterns.md)