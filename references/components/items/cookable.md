# `cookable`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改生食到熟食的预制件转换或添加烹饪时间回调时，使用此文件。

官方源码：

- `scripts/components/cookable.lua`

相关官方预制件示例：

- `scripts/prefabs/veggies.lua`

高频方法：

- `SetOnCookedFn(fn)`
- `Cook(cooker, chef)`
常见组件搭配：

- `cookable` + `inventoryitem`
- `cookable` + `edible`

常见陷阱：

- `cookable` 是转换逻辑，本身不包含营养值。
- 烹饪输出的预制件仍需要自己完整的设置。

后续阅读：

- [edible.md](edible.md)
- [prefab-contract.md](../../core/dst-prefab-authoring/references/prefab-contract.md)