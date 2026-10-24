# `stackable`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改堆叠大小、部分消耗、拆分行为或堆叠感知物品逻辑时，使用此文件。

官方源码：

- `scripts/components/stackable.lua`

相关官方预制件示例：

- `scripts/prefabs/rope.lua`
- `scripts/prefabs/crumbs.lua`

高频方法：

- `IsStack()`
- `StackSize()`
- `IsFull()`
- `SetStackSize(sz)`
- `Get(num)`
- `RoomLeft()`
- `Put(item, source_pos)`
- `SetOnDeStack(fn)`
常见组件搭配：

- `stackable` + `inventoryitem`
- `stackable` + `edible`
- `stackable` + `fuel`

常见陷阱：

- 堆叠逻辑必须处理部分移除，不仅仅是整物品转换。
- 可食用和燃料行为可能需要堆叠感知回调。
- 堆叠溢出或空间不足的 bug 通常是物品端的问题，不是背包 UI 的问题。

后续阅读：

- [inventoryitem.md](inventoryitem.md)
- [edible.md](edible.md)