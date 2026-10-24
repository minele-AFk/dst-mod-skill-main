---
name: dst-brain-authoring
description: Create and modify Don't Starve Together brains and behaviour trees. Use when writing Brain files, Behaviour nodes, priorities, tasks, selectors, decorators, conditions, postitions, movement, combat targeting, panic, flee, social, nest, sleep, and wake logic.
---

# DST Brain 与 Behaviour Tree 编写

让 Brain 负责意图选择和优先级调度，SG 负责动作执行，Component 负责持久状态。

## 工作流

1. 从同类原版 Brain 理解优先级；局部需求先评估 AddBrainPostInit 的窄修改，整份复制会形成需要跟随原版维护的分叉。
2. 使用当前 Behaviour Tree 的 PriorityNode/SelectorNode 等真实节点，区分周期重评、开始条件与持续条件。
3. 条件节点先验证目标存在、距离合法、冷却就绪；不满足时短路返回 false，不抛出异常。
4. 用已核实 Behaviour 及 FindWalkableOffset 等同类原版路径选择位置，检查地形、平台、距离与目标有效性，不猜 Postion 节点。
5. 行动节点调用 SG 状态、Component 方法或 SpawnPrefab；避免在 Behaviour 里直接操作位置或伤害。
6. 为 panic、flee、sleep、nest 和 social 意图保留原版优先级结构；新增意图插入对应分组。
7. 测试饥饿、受伤、夜间、战斗和玩家接近时的意图切换。
8. 复用 `BrainCommon` 便捷节点时按当前签名传参。当前 `RunAwayFromQueenTorch(inst)` 接收实体，已有调用传 `self.inst`；把 Brain 对象 `self` 传进去会让逃跑行为围绕错误的宿主运行。

## 源码锚点

- brain.lua、behaviourtree.lua：Brain 和 Behaviour 执行引擎。
- behaviours/：原版行为节点实现。
- prefabs/ 中同类生物的 SetBrain 调用。
- stategraphs/：SG 接口与状态名。

## 不变量

- Behaviour 不保存持久数据；数据留在 Component。
- 不要在条件节点执行副作用。
- 权威 Brain 在宿主服务端初始化；其内部可使用已确认的服务端组件，不为每次读取机械叠加运行端判断。
- 移动目标失效时 Brain 必须能重新选择或停止。

## 验证

- 实体在不同情境下表现出预期的意图切换。
- 目标丢失或距离过远时不会卡死或崩溃。
- 检查服务端 Brain 的决策及客户端看到的复制结果，不要求客机运行同一份权威 AI。

## 按需资源

- 需要 Brain 最小接入、意图优先级组合、运行机制、节点/装饰器及 Behaviour 参数时读取 [brain-node-behaviour-quickref.md](references/brain-node-behaviour-quickref.md)。
- 需要多个完整场景、调试和自定义行为示例时读取 [brain-practical-guide.md](../../patterns/ai/brain-practical-guide.md)。

## 条件、动作与树重建

IfNode 在进入时检查条件，WhileNode 在子行为运行时持续检查；Sequence/Selector 的 RUNNING 子节点保留执行状态，不能描述成“所有 Visit 都无记忆重启”。条件不产生扣费或生成实体等副作用。

DoAction 发起并观察 BufferedAction；目标生物 SG 必须有 ActionHandler 与实际 PerformBufferedAction 路径。行为选中了目标不证明动作已经执行。

Brain:_Start_Internal 在 OnStart 建树后调用 Mod PostInit；Stop/Restart 或休眠唤醒可重建树。补丁对当前根/目标节点做幂等，不能用永久实例标记跳过新树，也不假定 children[3] 永远是原目标。暂停干预使用相同私有 reason 成对 StopBrain/RestartBrain。

本轮核对 brain.lua:206-225、behaviourtree.lua:319-375,768-788；来源 [角色与 AI](../../engineering/dst-mod-engineering/characters-brains-stategraphs.md)。测试启动、重启、休眠唤醒、目标删除与动作失败，并确保测试实体醒着。
