# `timer`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改冷却时间、延迟状态变化或必须在存档和读档中存活的计时器时，使用此文件。

官方源码：

- `scripts/components/timer.lua`

相关官方预制件示例：

- `scripts/prefabs/farm_plow.lua`
- `scripts/prefabs/daywalker.lua`

高频方法：

- `TimerExists(name)`
- `StartTimer(name, time, paused, initialtime_override)`
- `StopTimer(name)`
- `IsPaused(name)`
- `PauseTimer(name)`
- `ResumeTimer(name)`
- `GetTimeLeft(name)`
- `SetTimeLeft(name, time)`
- `GetTimeElapsed(name)`
- `LongUpdate(dt)`
常见组件搭配：

- `timer` + 事件监听器
- `timer` + 存档或读档生命周期

常见陷阱：

- `timer` 存储定时状态；它本身不执行游戏玩法行为。
- 预制件仍需要监听计时器完成事件。
- 如果世界在未加载时前进，检查 `LongUpdate(...)`。

后续阅读：

- [persistence-contract.md](../../core/dst-persistence-migration/references/persistence-contract.md)
- [diagnostic-patterns.md](../../patterns/diagnostic-patterns.md)