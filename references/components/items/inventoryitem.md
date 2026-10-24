# `inventoryitem`

> 适用版本：API 10+
> 方法签名复核：2026-10-23，本机安装快照（游戏版本 `759671`）；不代表游戏行为验收。

当任务涉及修改拾取、丢弃、所有者转换、背包槽位存在或图标覆盖行为时，使用此文件。

官方源码：

- `scripts/components/inventoryitem.lua`

相关官方预制件示例：

- `scripts/prefabs/rope.lua`
- `scripts/prefabs/spear.lua`

高频方法：

- `SetOwner(owner)`
- `SetOnDroppedFn(fn)`
- `SetOnActiveItemFn(fn)`
- `SetOnPickupFn(fn)`
- `SetOnPutInInventoryFn(fn)`
- `OnPutInInventory(owner)`
- `OnDropped(randomdir, speedmult)`
- `OnPickup(pickupguy, src_pos)`
- `IsHeld()`
- `IsHeldBy(guy)`
- `RemoveFromOwner(wholestack, keepoverstacked)`
- `ChangeImageName(newname)`
- `EnableTemperature(enable)`
- `GetTemperature()` / `GetTemperaturePercent()`
- `SetTemperature(temp)` / `AddTemperature(delta)`
- `SetTemperatureModifier(name, value)` / `RemoveTemperatureModifier(name)`
- `inventoryitem_DeactivateBeforeLaunch`
常见组件搭配：

- `inventoryitem` + `inspectable`
- `inventoryitem` + `stackable`
- `inventoryitem` + `equippable`
- `inventoryitem` + `edible`, `fuel`, `finiteuses`, 或 `weapon`

常见陷阱：

- `inventoryitem` 属于物品实体，不是所有者的整个背包系统。
- 持有和丢弃行为通常需要所有者端的 `inventory` 和物品端的 `inventoryitem`。
- 如果物品无法进入容器，也要检查容器端的过滤器。

## 物品温度

`inventoryitemtemperature` 是扩展组件，应由 `inventoryitem:EnableTemperature(true)` 添加并连接 Replica；不要在不支持此包装路径的物品上把它当成独立温度模拟器。服务器温度、上下限、绝缘、潮湿惩罚和 modifier 由扩展组件维护，客户端查询走 Replica。详细合同见 [inventoryitemtemperature.md](../system/inventoryitemtemperature.md)。

发射物品前调用公共辅助函数 `DeactivateInventoryItemBeforeLaunch(inst)`。它优先调用 `inst.components.mine:Deactivate()`，否则调用实体的 `inst.inventoryitem_DeactivateBeforeLaunch()`；任一处理过时返回 true，未找到入口时返回 nil。这个函数只负责让当前物品退出原有激活/物理形态，不自动保存内容、归还物品或重建实体；具体效果仍由 Prefab 和调用者完成。

后续阅读：

- [inventory.md](../storage/inventory.md)
- [container.md](../storage/container.md)
- [useabletargeteditem.md](useabletargeteditem.md)
