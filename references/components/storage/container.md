# `container`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改槽位数、部件设置、打开或关闭流程、接受过滤器或存储端物品移除时，使用此文件。

官方源码：

- `scripts/components/container.lua`

相关官方预制件示例：

- `scripts/prefabs/backpack.lua`
- `scripts/prefabs/treasurechest.lua`

高频方法：

- `WidgetSetup(prefab, data)`
- `GetWidget()`
- `SetNumSlots(numslots)`
- `CanTakeItemInSlot(item, slot)`
- `GiveItem(item, slot, src_pos, drop_on_fail)`
- `RemoveItemBySlot(slot, keepoverstacked)`
- `RemoveAllItems()`
- `GetItemInSlot(slot)`
- `GetAllItems()`
- `Open(doer)`
- `Close(doer)`
- `IsOpen()`
- `CanOpen()`
- `FindItem(fn)`
- `HasItemWithTag(tag, amount)`
- `DestroyContents(onpredestroyitemcallbackfn)`
常见组件搭配：

- `container` + `inventoryitem`
- `container` + `equippable`
- `container` + `workable`

常见陷阱：

- 部件布局数据必须与实际槽位行为匹配。
- 许多打开或关闭的 bug 是副本或 UI 预期的 bug，而不仅仅是服务端容器逻辑。
- 物品接受问题通常来自 `CanTakeItemInSlot(...)` 或部件不匹配。

后续阅读：

- [Widget 编写入口](../../world-ui-assets/dst-ui-widget-authoring/GUIDE.md)
- [player-network-patterns.md](../../patterns/network/player-network-patterns.md)