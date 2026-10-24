# `fuel`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改被消耗的燃料物品，而不是被燃料驱动的目标时，使用此文件。

官方源码：

- `scripts/components/fuel.lua`

相关官方预制件示例：

- `scripts/prefabs/rope.lua`
- `scripts/prefabs/cattoy_mouse.lua`

高频方法：

- `SetOnTakenFn(fn)`
- `Taken(target)`
常见组件搭配：

- `fuel` + `inventoryitem`
- `fuel` + `stackable`

常见陷阱：

- `fuel` 是被消耗的物品。
- 如果任务是关于机器或火源上的燃料等级，检查目标的 `fueled` 组件。

后续阅读：

- [world-system-patterns.md](../../patterns/world-system-patterns.md)
- [inventoryitem.md](inventoryitem.md)