# sleeper：睡意、入睡测试与 SG

源码复核：2026-10-18，components/sleeper.lua。此组件的睡眠与实体离开模拟范围的 EntitySleep 是不同机制。

## 方法

| 接口 | 合同 |
|---|---|
| IsAsleep() / IsHibernating() / IsInDeepSleep() | 分别查询对应状态/条件，不从字段名猜深睡状态 |
| SetSleepTest(fn) / SetWakeTest(fn, time) | 配置测试，签名与调用频率读实际消费者 |
| SetResistance(resist) / SetExtraResist(resist) | 睡眠抵抗的不同入口 |
| AddSleepiness(sleepiness, sleeptime) | 累加睡意并与 resistance 比较，不是固定 0–1 百分比 |
| GoToSleep(sleeptime) / WakeUp() | 发起状态变化；目标 SG 仍需相应状态支持 |
| GetTimeAwake() / GetTimeAsleep() | 持续时间查询 |

当前 AddSleepiness 比较 > resistance 与 == resistance 有不同调度；不能把 0.2 一律解释成“增加 20% 睡意，持续 5 秒”。IsInDeepSleep 按 asleep 与 sleepiness 条件算，不是文档旧字段 isindeepsleep。

## 事件与状态机

组件实际推 gotosleep 与 onwakeup；不是旧表虚构的 sleepstart/sleepstop/wakeup。事件生产与 SG 消费都要追踪，不能凭方法返回就声称已经播放睡眠动画。

睡眠不自动等于不会受攻击。受击唤醒、深睡、冬眠及角色 grogginess 是不同路径；要实现免疫先定义针对哪类睡眠，再查该实体实际组件/SG。

## 生命周期

睡眠测试、WearOff、实体 Sleep/Wake 和移除有各自任务/更新政策；不在原函数后无条件恢复旧状态。自定义测试可检查依赖组件，但不得假设每个 sleeper 都是有玩家三维的角色。

保存与长更新沿组件实现核对，不冻结成“冬眠绝不会自然醒”的通用规则。

## 验证

检查抵抗阈值上下及相等、强制入睡、受击、睡眠测试变化、实体休眠/唤醒、读档和 SG 中断。当前只是源码合同检查。

[Brain](../../gameplay/dst-brain-authoring/GUIDE.md) · [SG](../../gameplay/dst-stategraph-authoring/GUIDE.md) · [生存](../../gameplay/dst-status-buffs-survival/GUIDE.md)
