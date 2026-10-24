# Brain 节点与 Behaviour 行为速查

> 本页统一维护 Brain 入门、优先级组合、运行机制、节点与 Behaviour 参数；完整场景例子见实战指南。
> 出处已对照本地权威源码 `D:\mods\scripts`（brain.lua / behaviourtree.lua / behaviours/）。以源码为准而非此处行号。

## 1. 运行机制（brain.lua + behaviourtree.lua）

- `Brain = Class(...)`：`OnStart()` 建树、`OnUpdate()` 驱动 `self.bt:Update()`、`OnStop()` 清理。实体通过 `inst:StartBrain()` / `inst:StopBrain(reason)` / `inst:RestartBrain(reason)` 控制。
- `BrainWrangler`（= `BrainManager` 全局调度器）：按 tick 唤醒（`Sleep(inst, t)` 精确到 tick 的 `tickwaiters`），无 sleep 时间的树直接 Hibernate（低负载优化）。`Brain:ForceUpdate()` → `bt:ForceUpdate()` + `BrainManager:Wake(self)`——事件驱动的即时重估。
- `BT = Class(inst, root)`：`Update()` = `root:Visit()`（只访问 RUNNING 分支）+ `SaveStatus()`（lastresult 记录）+ `Step()`（非 RUNNING 重置子树）。`GetSleepTime()` 取树内最小 sleep 值。
- `BehaviourNode`：四态 `SUCCESS/FAILED/READY/RUNNING`；`self:Sleep(t)` 设置下次唤醒时间；子节点由 `_ctor(self, name, children)` 挂 parent 指针。
- 节点每 tick 重估：`PriorityNode` 按 `period`（默认 1 秒，实战多用 `.25/.5`）节流评估，`noscatter` 关闭随机首评偏移；RUNNING 子节点仍保留自身状态，Sequence/Selector 等可继续进行中的分支；具体重评/重置由各 Visit/Reset/Step 实现，不能把整棵树称作无记忆。

## 2. 节点与装饰器全集（behaviourtree.lua）

| 节点 | 行为 |
|---|---|
| `ConditionNode(fn, name)` | 纯条件，仅 SUCCESS/FAILED |
| `MultiConditionNode(start, continue)` | 双阶段条件（start 通过后每帧只查 continue） |
| `ConditionWaitNode(fn)` | 条件为真才 SUCCESS，否则 RUNNING |
| `ActionNode(action)` | 执行函数立即 SUCCESS |
| `WaitNode(time)` | 等待时间（可函数） |
| `SequenceNode(children)` | 顺序执行，遇 FAILED/RUNNING 停（= 逻辑与） |
| `SelectorNode(children)` | 依次尝试，遇 SUCCESS/RUNNING 停（= 逻辑或） |
| `NotDecorator` / `FailIfRunningDecorator` / `FailIfSuccessDecorator` | 单子装饰器：取反 / 失败化 |
| `LoopNode(children, maxreps)` | 循环序列 |
| `RandomNode(children)` | 随机起点尝试 |
| `PriorityNode(children, period, noscatter)` | **优先级调度器（顶层根）** |
| `ParallelNode(children)` | 并行，全部成功才成功 |
| `ParallelNodeAny(children)` | 并行，任一成功即成功 |
| `EventNode(inst, event, child, priority)` | 事件触发门控（事件 → ForceUpdate） |
| `LatchNode(inst, latchduration, child)` | 冷却闩：两次进入间隔 latchduration |
| `WhileNode(cond, name, node)` | = ParallelNode{ConditionNode, node}：**每帧检查条件，条件为假立即中断子节点**（防逃逸守卫） |
| `IfNode(cond, name, node)` | = SequenceNode{ConditionNode, node}：**条件只在开始时查一次** |
| `IfThenDoWhileNode(ifcond, whilecond, name, node)` | = ParallelNode{MultiConditionNode, node}：开始查 if，之后每帧查 while |

> WhileNode 适合运行中需要持续保持的外部条件，IfNode 适合通过后继续执行。ChaseAndAttack 本身也有目标校验；是否再包持续守卫由额外终止条件决定，不机械要求所有追击加 WhileNode。

## 3. 常用 Behaviour（behaviours/* ）参数速查

> 全部 `Class(BehaviourNode, ...)`。Visit 生命周期：READY 时做启动逻辑（找目标/定状态）→ 置 RUNNING → RUNNING 时每 tick 重估并 `self:Sleep(t)` 节流 → 成功/失败置状态返回。节点的 status、目标、计时等字段可跨 Visit 保留，重置/退出时清理；不要将 RUNNING 误解为每帧重新初始化。

- **ChaseAndAttack(inst, max_chase_time, give_up_dist, max_attacks, findnewtargetfn, walk, distance_from_ocean_target)**：核心战斗。READY 时 `combat:ValidateTarget()`；RUNNING 时：目标无效→FAILED、目标死亡→SUCCESS、`combat:TryAttack()` 尝试攻击、`locomotor:GoToPoint` 靠近、超时/超距 `combat:GiveUp()`。监听 `onattackother/onmissother` 重置追随时钟并计数 max_attacks。OnStop 必须 RemoveEventCallback。
- **ChaseAndAttackAndAvoid(inst, findavoidanceobjectfn, avoid_dist, ...)**：追击时若避让物在目标方向 45° 内，把目标点横向偏移 avoid_dist。
- **ChaseAndRam(inst, max_chase_time, give_up_dist, max_charge_dist, max_attacks)**：锁 ram_angle 直线冲撞，跑过头 ForceAttack；加 `ChaseAndRam` tag 用于动画。
- **StandAndAttack(inst, findnewtargetfn, timeout)**：站桩攻击（炮塔/眼球），Stop + FacePoint + TryAttack。
- **AttackWall(inst)**：面前 30° 扇形内找 wall 攻击。
- **Wander(inst, homelocation, max_dist, times, getdirectionFn, setdirectionFn, checkpointFn, data)**：homelocation 可为函数；walk/wait 交替；`FindWalkableOffset` 找可行走偏移（水陆两版）；`data.wander_dist` 默认 12、`should_run` 可跑。
- **Follow(inst, target, min_dist, target_dist, max_dist, canrun, alwayseval, inlimbo_invalid)**：三距环。过近 BACKOFF（`RunInDirection(angle+180)` 反向跑）、过远/异船 APPROACH（`GoToPoint(target_pos, nil, canrun)`），进入 target_dist 内 SUCCESS。**异平台判定**：`allow_platform_hopping` 时双方 `GetCurrentPlatform()` 不等视为 APPROACH。每 tick `self:Sleep(.25)`。
- **Approach(inst, target, dist, canrun)**：简化版 Follow（只接近）。
- **RunAway(inst, hunterparams, see_dist, safe_dist, fn, runhome, fix_overhang, walk_instead, safe_point_fn)**：hunterparams 支持 `{tags=,notags=,oneoftags=,fn=,getfn=,seeequipped=}`；反方向 + FindWalkableOffset 避墙 + 折返角记忆 1 秒；safe_dist 内 SUCCESS；runhome 时 homeseeker:GoHome。
- **RunToDist(inst, hunterparams, safe_dist, fn, ...)**：跑到与目标恰好 safe_dist 处。`dist_sq` 接近 safe_dist 且 abs 差 <0.75 判 SUCCESS；水生生物自动切 FindSwimmableOffset。
- **Leash(inst, homelocation, max_dist, inner_return_dist, running)**：越界→返回；**LeashAndAvoid** 返回途中绕避让物。
- **FaceEntity(inst, getfn, keepfn, timeout, customalert)**：面向目标；空闲时自动切 `alert` 状态。空闲压力全无时自用 `customalert`。
- **DoAction(inst, getactionfn, name, run, timeout)**：getactionfn 返回 BufferedAction → `locomotor:PushAction`；成功/失败回调置 pendingstatus；超时 FAILED。**这是让实体执行任意 ACTIONS 的通用桥梁**。
- **FindClosest / FindLight / FindFlower / FindFarmPlant**：找目标+靠近（CHECK_INTERVAL 5 秒重找）。
- **Panic / PanicAndAvoid**：随机方向跑（0.25-0.5 秒换向）。
- **ControlMinions(inst)**：minionspawner 组件驱动小兵自动 PICKUP/HARVEST。
- **UseShield(inst, ...)**：受击累计超阈值→PushEvent("entershield")；Onexit 推 "exitshield"。
- **ChattyNode(inst, ...)**：装饰器，子节点 RUNNING 期间随机 chatter。
- **MinPeriod(inst, minperiod, immediate, child)**：装饰器，距上次成功不足 minperiod 直接 FAILED（节流）。

## 4. BrainCommon 共享组件（brains/braincommon.lua）

| 组件 | 说明 |
|---|---|
| `PanicTrigger(inst)` | = WhileNode(ShouldTriggerPanic, "PanicTrigger", Panic(inst))，起火/月灼/闹鬼触发 |
| `PanicWhenScared(inst, loseloyaltychance, chatty)` | epicscare 事件驱动恐慌，可附加忠诚度丢失并行节点 + ChattyNode |
| `NodeAssistLeaderDoAction(self, parameters)` | 跟随领袖做事（MINE/CHOP/DIG/TILL 各有 Starter/KeepGoing/FindNew 默认值） |
| `NodeAssistLeaderPickUps(self, parameters)` | 帮领袖捡东西/上交（PickUpAction/GiveAction/DropAction 三级） |
| `PossessChassisNode(inst, update_rate)` | 找可附身机甲→Leash 靠近→PushEventImmediate("possess_chassis") |
| `AnchorToSaltlick(inst)` / `ShouldSeekSalt` | 盐舔块锚定游荡 |
| `RunAwayFromQueenTorch(inst)` | 找最近 Queen Torch 并跑出 10 格、到 15 格外停止；当前参数是实体，不是 Brain 的 `self` |

**共享模式技巧**：包装节点 OnStop 挂清理回调（移除事件监听）的标准写法：

```lua
local old = node.OnStop
node.OnStop = function(self, ...)
    -- 清理本补丁的资源。
    if old ~= nil then
        return old(self, ...)
    end
end
```

## 5. 自定义 Behaviour + Brain 完整骨架（原样风格）

自定义 behaviour 继承 `BehaviourNode`。核心：READY 时做启动逻辑（找目标/定状态）→ 置 RUNNING → RUNNING 时每 tick 重估并 `self:Sleep(t)` 节流 → 成功/失败置状态返回。保留正在运行所需的目标和计时，在 Reset/OnStop 中释放；持久化玩法事实仍交给组件。以下只展示节点组合思路，SEE_DIST 等设计常量和 require 需由项目补齐，不是可直接运行成品。

```lua
-- 自定义 behaviour 节点（继承 BehaviourNode）
MyPeck = Class(BehaviourNode, function(self, inst)
    BehaviourNode._ctor(self, "MyPeck")
    self.inst = inst
    self.target = nil
    self.timer = 0
end)

function MyPeck:Visit()
    if self.status == READY then
        self.target = FindEntity(self.inst, SEE_DIST, nil, { "peckable" }, { "FX", "INLIMBO" })
        if self.target ~= nil then
            self.status = RUNNING
            self.timer = GetTime() + 2
        else
            self.status = FAILED
        end
    end
    if self.status == RUNNING then
        if not self.target:IsValid() or GetTime() > self.timer then
            self.status = SUCCESS
            self.inst.components.locomotor:Stop()
        elseif self.inst:IsNear(self.target, 2) then
            self.inst.components.locomotor:Stop()
            self.inst.components.combat:DoAttack(self.target)  -- 或 PushEvent 驱动 SG
            self.status = SUCCESS
        else
            self.inst.components.locomotor:GoToPoint(self.target:GetPosition(), nil, true)
            self:Sleep(.25)
        end
    end
end

-- Brain 本体：参数区 → 条件函数区（闭包风格）→ 自定 behaviour → OnStart 组 PriorityNode
local MyMobBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
end)

function MyMobBrain:OnStart()
    local root = PriorityNode(
    {
        BrainCommon.PanicTrigger(self.inst),                          -- 1 恐慌
        WhileNode(function() return ShouldAttack(self.inst) end, "HasTarget",
            ChaseAndAttack(self.inst, MAX_CHASE_TIME, SEE_DIST * 2)), -- 2 追击
        DoAction(self.inst, GoHomeAction, "GoHome", true),            -- 3 回巢
        MyPeck(self.inst),                                            -- 4 自定义行为
        Leash(self.inst, GetHomePos, LEASH_DIST, 4, true),            -- 5 拴绳
        FaceEntity(self.inst, function() return self.inst.components.combat.target end,
            function(inst, t) return t ~= nil and t:IsValid() and inst:IsNear(t, SEE_DIST) end), -- 6 面向
        Wander(self.inst, GetHomePos, WANDER_DIST),                   -- 7 游荡兜底
    }, .25)
    self.bt = BT(self.inst, root)
end

function MyMobBrain:OnStop() end  -- 清理（如事件监听）

return MyMobBrain
```

要点：参数常量放顶部；条件函数全部闭包式；`DoAction(inst, getactionfn, name, run, timeout)` 用 `BufferedAction` 返回任意 ACTIONS 的通用桥梁；OnStop 对称撤销事件监听。

## 6. 特殊 Brain 变体

- **wilsonbrain.lua（约 21 行）**：全游戏最小 brain——`WhileNode(按住主键, ChaseAndAttack(inst, 5))` + 兜底 `ChaseAndAttack(inst, 5, nil, 1)`（第 4 参 max_attacks=1）。玩家平时由 playercontroller 驱动，brain 只在按住左键时追击。
- **hostedbrain.lua**：编队进攻 AI——`PARASITES` 全局表记录同族单位，`CanAttackTarget` 限制同一目标最多 2 只同时攻击；Leash 到编队位；DoAction 清预留目标。
- **beecommon.lua / wobycommon.lua / wx78_shadowdrone_braincommon.lua**：返回纯函数表（共享目标、GoHomeAction），供多个 brain `require` 复用——"共享函数模块"模式。

## 7. 选入口、组合优先级与最小接入

Brain 选择意图，Behaviour 执行可持续决策，Component 保存玩法事实与冷却，SG 执行动画与原子动作。新生物需要不同决策结构时创建 scripts/brains/<name>.lua；只是调整原版优先级/目标时先考虑 AddBrainPostInit，并沿对应 Prefab 的 require 与 SetBrain 找真实对象。

```lua
require "behaviours/wander"

local MyBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
end)

function MyBrain:OnStart()
    local root = PriorityNode({
        Wander(self.inst, function() return self.inst:GetPosition() end, 4),
    }, .25)
    self.bt = BT(self.inst, root)
end

return MyBrain
```

上例是单独的 Brain 模块；Prefab 在权威装配路径 require("brains/mybrain") 后 SetBrain，并安装匹配 SetStateGraph。没有给 self.bt 分配真实 BT，文件存在也不能驱动决策。完整场景与多种示例见 [实战指南](../../../patterns/ai/brain-practical-guide.md)。

| 意图 | 常用节点 |
|---|---|
| 优先级选择/顺序完成 | PriorityNode / SequenceNode |
| 开始条件/持续条件 | IfNode / WhileNode |
| 动作/战斗 | DoAction、ActionNode / ChaseAndAttack、StandAndAttack |
| 主人和领地 | Follow、Leash |
| 紧急/待机 | RunAway、Panic / Wander、StandStill |

常见意图从死亡/禁用、恐慌/逃跑、战斗/技能、主人/领地、工作/社交到待机，但应按同类生物原版与玩法调整。限制搜索半径与标签、缓存稳定 home、设置合理评估周期并让节点 Sleep，不在高频条件中不断造闭包、大表或全图扫描。

现有 Brain 可用 AddBrainPostInit("pigguardbrain", function(brain) ... end) 的结构扩展，但省略部分需替换为真实逻辑，且应对每次 OnStart 重建后的当前树处理。自定义 Behaviour 实现 Visit、Reset、Stop/OnStop 对应实际基类出口，正确维护 READY/RUNNING/SUCCESS/FAILED，并在中断时解除任务和监听。

先读同类 Prefab、Brain、braincommon 和 SG。目标选择错误先看 Brain；选择正确但动画/命中/睡眠执行错误看 SG 与 commonstates；附近目标查询见 [实体搜索](../../../patterns/runtime/entity-query-patterns.md)。
