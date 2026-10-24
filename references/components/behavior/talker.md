# `talker`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改对话气泡、闲聊、NPC 或 Boss 台词或有意省略普通对话时，使用此文件。

官方源码：

- `scripts/components/talker.lua`

相关官方预制件示例：

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/daywalker.lua`

高频方法：

- `MakeChatter()`
- `Chatter(strtbl, strid, time, forcetext, echotochatpriority)`
- `Say(script, time, noanim, force, nobroadcast, colour, text_filter_context, original_author_netid, onfinishedlinesfn, sgparam)`
- `ShutUp()`
- `IgnoreAll(source)`
- `StopIgnoringAll(source)`
常见组件搭配：

- `talker` + `inspectable`
- `talker` + strings
- `talker` + 网络感知的玩家或生物展示

常见陷阱：

- 对话展示还取决于调用者上下文和字符串键，不仅仅是 `talker.lua`。
- 许多类生物预制件已经包含 `talker`；缺失它通常是有意的选择。
- 聊天回声、本地气泡显示和强制文本是不同的关注点。

后续阅读：

- [runtime-i18n-patterns.md](../../patterns/runtime-i18n-patterns.md)
- [player-patterns.md](../../patterns/player-patterns.md)