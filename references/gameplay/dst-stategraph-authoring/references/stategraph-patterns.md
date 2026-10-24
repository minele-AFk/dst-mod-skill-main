# StateGraph 设计模式与事件转发

基础构造、事件消费、标签和预测字段统一见 [状态合同](stategraph-contract.md)；可组合示例见 [实战指南](../../../patterns/ai/stategraph-practical-guide.md)。本页保留具体复用取舍与原版调查线索，不把某个 SG 的结构推广为全体规则。

## 1. 共享状态与工厂

常见组织是 states、events、actionhandlers 三表，再返回 StateGraph；事件驱动物件可不需要 ActionHandler。模块名、内部名和实例不同，默认状态必须真实存在。复用优先检查 commonstates 的工厂是否符合本实体动画/组件，再决定手写；不存在“所有 SG 必须用同一个 SGCommon 工厂”的前提。

| 需求 | 当前 commonstates.lua 入口 |
|---|---|
| 单动画回到下一状态 | AddSimpleState(states, name, anim, tags, finishstate, timeline, fns) |
| 动画中执行缓冲动作 | AddSimpleActionState(states, name, anim, time, tags, finishstate, timeline, fns) |
| 移动 | AddRunStates/AddWalkStates、AddSimpleRunStates/AddSimpleWalkStates |
| 战斗 | AddCombatStates、AddHitState、AddDeathState |
| 睡眠/冻结 | AddSleepStates/AddSleepExStates、AddFrozenStates |
| 事件 | CommonHandlers.OnAttack/OnAttacked/OnDeath/OnLocomote/OnSleep/OnFreeze/OnFossilize |
| 睡眠标记协调后的动画结束 | CommonHandlers.OnNoSleepAnimOver(nextstate) |

当前源码没有 AddHitReactionStates、AddWeaponSwing、OnDoAttack、OnGotoSleep 这几种旧页写法；不要按相似名字造调用。`AddSimpleActionState` 传 timeline 会替换默认缓冲动作执行；`AddCombatStates` 要自己提供 attacktimeline，详见合同与实战。

## 2. 动作桥接与循环阶段

Brain 的 DoAction 或项目逻辑给出 BufferedAction，再由 locomotor/实体动作路径进入 SG。ActionHandler 的目的状态函数可按 prechop/chopping 等标签选择起手与循环；返回 nil 表示当前不选该状态。不要用定时器直接跳状态来绕开动作资格和成功/失败链。

循环动作还涉及 playercontroller 的按键续用、缓冲动作有效性、物品/目标变化和客户端预览，不是简单每十帧无条件 PushBufferedAction。只改执行帧时保留原有开始、续用、退出合同。

## 3. 标签是查询协议

idle/moving/running/attack/hit/busy/sleep/doing 描述行为；canrotate、nointerrupt、nosleep、nofreeze、nomorph、noelectrocute 以及预测标签依赖实际消费者。新增或动态 AddStateTag/RemoveStateTag 前查 handler 如何解释该标签，退出撤销本状态贡献。

`busy + nointerrupt` 不阻止所有转移；状态内事件先处理、未消费再到全局事件，是否允许受击/睡眠/冻结须分别核对，不能凭标签名称推导。

## 4. 跨状态节流与回调

节流时间戳可放 sg.mem，当前执行对象放 statemem；前者要避免永久残留，后者不能跨状态取值。原版 SGwilson 的 monkeycursehit handler 使用 mem 时间戳控制转移频率，是调查高频事件的具体线索，不意味着所有事件都应该固定节流一秒。

StateGraph 定义共享，不能把实体特有时间戳存入定义表。完成回调先从 statemem 取出并清空，明确先切状态还是先回调，避免回调重入后清理新状态资源。

## 5. 活动物件与高级交互线索

SGyotb_stage 的 trader_arrives、contestenabled、onflourishend 等事件驱动阶段切换，可用于调查活动物件的外部流程；它仍包含动画与状态退出，不能称为无动画的纯事件机。onexit 推送外部事件时检查是否引起嵌套转移。

以下为需要按目标源码再追的设计方向，未在本轮逐个证明具体生物与参数：

- 连段：帧事件组织多段命中，若使用项目/原版 DoComboArcAttack，先查其所属对象、范围、目标过滤和伤害归属，不当通用 EntityScript API。
- 位移与碰撞：逐帧 MotorVelOverride 与掩码改变均需中断恢复；玩家临时穿越其他角色复用同类 SGwilson 状态，不能随意替换碰撞助手。
- 变形/筑巢：替换 Prefab 前迁移需要保留的数据、位置与引用；SpawnPrefab 失败不提前删除原实体。清理原实体附属任务/物理并核对存档。
- 动态可打断性：在指定帧修改标签，并沿全局 attacked/death handler 验证实际退出与清理。

2026-10-21 对照当前安装包 stategraph.lua、commonstates.lua、SGwilson.lua 和 SGyotb_stage.lua 的上述入口。历史精读线索不等于本轮逐例复现；未进行动画、AI 或主客机实测。
