---
name: dst-events-tasks-lifecycle
description: Manage Don't Starve Together events, world-state watchers, scheduled tasks, updates, sleep and wake transitions, and cleanup. Use when writing ListenForEvent callbacks, DoTaskInTime or DoPeriodicTask logic, component updates, entity sleep behavior, delayed actions, or diagnosing leaked callbacks and removed-entity errors.
---

# DST 事件监听、定时任务与生命周期清理

为每个回调确定所有者、事件源、取消时机和睡眠语义，避免实体移除后继续执行。

## 工作流

1. 记录事件名、事件源、监听者、data 契约和谁负责解除监听；不要只凭字符串相同假设数据结构。
2. 使用同一函数引用配对 ListenForEvent 与 RemoveEventCallback；跨实体监听时明确 source。
3. 监听世界变量时配对 WatchWorldState 与 StopWatchingWorldState，并决定初始化时是否主动同步一次。
4. 一次性延迟使用 DoTaskInTime，稳定低频循环使用 DoPeriodicTask，组件级连续更新仅用于确有需要的状态。
5. 把任务句柄保存到明确字段；重启任务前先 Cancel，并在执行后清空句柄。
6. 决定实体睡眠时任务应暂停、继续、折算 LongUpdate 还是在唤醒时重建。
7. 在 OnRemoveEntity、OnRemoveFromEntity、Widget Kill 或 SG onexit 中执行对应清理。

## 源码锚点

- entityscript.lua：事件、世界状态、任务、睡眠和移除。
- scheduler.lua：调度与线程。
- components/ 与 prefabs/：OnEntitySleep、OnEntityWake、LongUpdate 范例。
- widgets/widget.lua：UI 更新和销毁生命周期。

## 不变量

- 回调先验证 inst、目标与组件仍然有效。
- 不要每帧扫描可用事件或低频任务解决的问题。
- 不要用匿名函数注册后再试图用另一个匿名函数解除。
- 服务器玩法任务与客户端表现任务分开建立。
- `PushEvent(event,data)` 先调用全部监听者，再按普通 SG 队列条件投递；`PushEventImmediate(event,data)` 同样先调用监听者，但立即调用 `sg:HandleEvent`，不再等待常规 SG 队列。二者都会继续推送给 Brain。即时事件用于必须立即打断/切换 SG 的权威状态，不能为了减少延迟而对高频表现事件全局替换。

## 生命周期归属

- 当前 `EntityScript:Remove` 会清理该实体登记的事件回调和 pending tasks；组件单独 `RemoveComponent` 只走其组件退出路径，不等于移除宿主。Buff/组件停止而宿主还在，或任务挂在玩家、世界、全局输入等更长寿命对象上时，仍要显式结束本机制持有的资源。
- 刷新、取消与重施加共用幂等清理；旧任务不能在结束时清掉新一轮句柄，延迟 FX 不能在效果取消后重新出现。清理缓存引用与撤销效果同步进行，外部删除后再次施加应能重建。
- 每项效果明确死亡、幽灵、重连、切分片和重启政策；由玩法决定清除、暂停或继续，不从某个案例推导统一政策。
- 状态贡献要按“进入一次、退出一次”的归属设计。当前 `SGbuzzard` 用 `ConfigureFlying` 同时提高飞行实体、添加 `notraptrigger`、关闭地面速度倍率，落地时反向恢复；这类 helper 必须幂等，并由正常结束、受击、冻结、死亡、取消和直接 `GoToState` 等离开路径检查。死亡或实体移除是状态机之外的兜底，不能只依赖某一个 `onexit`。

事件顺序已于 2026-10-23 核对安装版 `entityscript.lua:1290-1326`；此前一项于 2026-10-17 核对 `entityscript.lua:RemoveComponent/Remove`。生命周期设计检查项仍需按目标机制验证；相关单案例候选为 `RULE-LIFE-001`，不代表跨项目实机通过。

## 验证

- 移除实体或组件后不再触发回调。
- 睡眠、唤醒、保存重载和世界暂停不会重复创建任务。
- 周期逻辑的频率、初始延迟和长时间跳过行为符合设计。

## 按需资源

- 保存、任务所有权、提前移除及恢复顺序需要展开时读 [生命周期与恢复](../../engineering/dst-mod-engineering/lifecycle-save.md)。
