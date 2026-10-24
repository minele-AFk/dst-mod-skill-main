# `inspectable`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改检查文本、状态字符串、名称覆盖行为或有意移除普通检查时，使用此文件。

官方源码：

- `scripts/components/inspectable.lua`

相关官方预制件示例：

- `scripts/prefabs/treasurechest.lua`
- `scripts/prefabs/rope.lua`

高频方法：

- `SetDescription(desc)`
- `SetNameOverride(nameoverride)`
- `GetStatus(viewer)`
- `GetDescription(viewer)`
常见组件搭配：

- 几乎任何面向玩家的预制件
- `inspectable` + 运行时 `STRINGS`

常见陷阱：

- 许多检查 bug 实际上是错误的预制件名称或错误的 `STRINGS` 键。
- `inspectable` 非常常见，其缺失通常是有意的选择。
- 特殊检查文本通常需要 [runtime-i18n-patterns.md](../../patterns/runtime-i18n-patterns.md)。

后续阅读：

- [runtime-i18n-patterns.md](../../patterns/runtime-i18n-patterns.md)
- [tag-patterns.md](../../patterns/prefab/tag-patterns.md)