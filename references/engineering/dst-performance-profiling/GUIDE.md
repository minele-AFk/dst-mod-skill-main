---
name: dst-performance-profiling
description: Profile and optimize Don't Starve Together mods. Use when diagnosing server tick lag, client frame drops, excessive FindEntities calls, OnUpdate or periodic-task load, Brain and stategraph churn, network traffic, entity leaks, UI update cost, allocations, or performance regressions after a mod change.
---

# DST 性能分析与优化

先用可重复场景和实际数据定位热点，再降低调用频率、搜索规模、分配和复制量。

## 工作流

1. 记录硬件、服务器类型、玩家数、世界天数、实体数量、模组配置和可重复的负载场景。
2. 区分服务器 tick、客户端渲染/UI、网络、世界生成和载入卡顿，不混用指标。
3. 用 profiler.lua、perfutil、带限流的计时日志或实体计数定位最贵函数与调用频率。
4. 优先检查 OnUpdate、DoPeriodicTask、FindEntities、Brain 条件、SG timeline、全局事件和重复 Widget 更新。
5. 从算法和频率优化：事件替代轮询、标签过滤、平方距离、分桶/缓存、Sleep、批处理和静态更新。
6. 检查每 tick 临时表、闭包、字符串拼接、网络 dirty 和 FX/子实体数量。
7. 用相同场景比较修改前后平均值、峰值和正确性，并保留退化检测。

## 源码锚点

- profiler.lua、perfutil.lua、stats.lua。
- entityscript.lua：组件更新、任务、事件、睡眠。
- brain.lua、behaviourtree.lua、stategraph.lua。
- simutil.lua 与 TheSim:FindEntities 调用点。
- widgets/widget.lua：UI 更新。

## 不变量

- 不要凭代码风格猜热点，先测量。
- 缓存必须有失效规则，不能用错误状态换速度。
- 降低频率时验证游戏时间、暂停和 LongUpdate 语义。
- 优化不能把服务器权威计算移到不可信客户端。

## 验证

- 同一复现场景有修改前后可比较数据。
- 热点降低且没有把成本转移到更频繁的网络或内存分配。
- 大量实体、长时间运行和玩家加入离开后性能保持稳定。

## 按需资源

- 需要检查顺序与指标解释时读取 [performance-checklist.md](references/performance-checklist.md)。

## 先减少无效工作，再决定架构

邻近触发先检查 playerprox 的 near/far 迟滞与合适模式，再决定是否自建周期扫描。动画淡入/声音过渡只在过渡期间更新，到目标即停止；静止效果不永久挂高频任务。

缓存需说明拥有者、键、有效期及失效事件；树重建、Widget 重建或实体移除后旧缓存不得继续指向已失效对象。降低查询频率前确认边界延迟是否能接受，不凭风格把每个查询都换成全局管理器。

测试建议测实体/任务/监听/网络消息随 N 增长的趋势，区分一次性初始化和稳定运行成本。没有前后同场景测量时只能报告静态风险，不能写“性能已提升”。

从 [世界与空间](../dst-mod-engineering/worldgen-spatial.md) 及 [Buff 与邻近效果](../dst-mod-engineering/combat-buffs-containers.md) 提炼；具体 playerprox 行为仍查目标源码。
