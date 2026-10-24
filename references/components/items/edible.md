# `edible`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改食物的饥饿值、生命值、理智值、食用副作用或基于特殊食用者的覆盖时，使用此文件。

官方源码：

- `scripts/components/edible.lua`

相关官方预制件示例：

- `scripts/prefabs/veggies.lua`
- `scripts/prefabs/crumbs.lua`

高频方法：

- `GetSanity(eater)`
- `GetHunger(eater)`
- `GetHealth(eater)`
- `SetOnEatenFn(fn)`
- `SetHandleRemoveFn(fn)`
- `SetOverrideStackMultiplierFn(fn)`
- `SetGetHealthFn(fn)`
- `SetGetSanityFn(fn)`
- `OnEaten(eater)`
- `GetStackMultiplier()`
常见组件搭配：

- `edible` + `inventoryitem`
- `edible` + `stackable`
- `edible` + `cookable`

常见陷阱：

- `edible` 表示可食用行为，不是烹饪转换。
- 可堆叠食物可能需要覆盖堆叠消耗行为。
- 最终结果仍取决于食用者端的系统。

后续阅读：

- [cookable.md](cookable.md)
- [stackable.md](stackable.md)