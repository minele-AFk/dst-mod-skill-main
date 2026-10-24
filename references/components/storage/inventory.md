# `inventory`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改活跃物品流程、装备访问、隐藏背包或所有者端物品查找和消耗时，使用此文件。

官方源码：

- `scripts/components/inventory.lua`

相关官方预制件示例：

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/molehill.lua`

高频方法：

- `GetActiveItem()`
- `GetEquippedItem(eslot)`
- `FindItem(fn)`
- `FindItems(fn)`
- `GiveItem(inst, slot, src_pos)`
- `DropItem(item, wholestack, randomdir, pos, keepoverstacked)`
- `Equip(item, old_to_active, no_animation, force_ui_anim)`
- `Unequip(equipslot, slip, force)`
- `HasItemWithTag(tag, amount)`
- `GetItemByName(item, amount, checkallcontainers)`
- `ConsumeByName(item, amount)`
- `Open()`
- `Close(keepactiveitem)`
常见组件搭配：

- `inventory` + `inventoryitem`
- `inventory` + `equippable`
- 玩家 `inventory` + `container`

常见陷阱：

- `inventory` 是所有者端的持有逻辑，不是槽位部件的存储 UI。
- 许多交互会同时涉及 `inventory` 和 `inventoryitem`。
- 如果任务是箱子或背包 UI 行为，也需要检查 `container` 组件。

后续阅读：

- [inventoryitem.md](../items/inventoryitem.md)
- [container.md](container.md)