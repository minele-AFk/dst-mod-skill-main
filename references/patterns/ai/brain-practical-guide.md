# AI 大脑实战指南

基于 DST 官方源码的完整 AI 大脑开发教程。

---

## 一、大脑基础概念

### 1.1 Brain 结构

```lua
local CustomBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
    
    -- 定义行为树节点
    self.root = PriorityNode({
        -- 行为节点列表（按优先级排列）
    }, .25)
end)

return CustomBrain
```

### 1.2 行为节点类型

DST 使用行为树（Behavior Tree）作为 AI 决策系统：

| 节点类型 | 作用 | 示例 |
|---------|------|------|
| `PriorityNode` | 优先级节点，从高到低执行 | 根节点 |
| `SequenceNode` | 顺序节点，按顺序执行 | 先检查条件再执行动作 |
| `ParallelNode` | 并行节点，同时执行多个子节点 | 同时移动和播放动画 |
| `LoopNode` | 循环节点，重复执行 | 循环执行动作 |
| `IfNode` | 条件节点，满足条件执行 | 简单条件判断 |
| `WhileNode` | 循环条件节点 | 条件满足时持续执行 |
| `ActionNode` | 动作节点，执行单个动作 | 执行特定行为 |
| `DoAction` | 执行 BufferedAction | 执行拾取、攻击等动作 |
| `ChattyNode` | 带对话的节点 | 执行动作时说话 |

### 1.3 节点状态

每个行为节点有三种状态：

| 状态 | 含义 |
|------|------|
| `READY` | 准备执行 |
| `RUNNING` | 正在执行 |
| `SUCCESS` | 执行成功 |
| `FAILED` | 执行失败 |

---

## 二、常用行为节点详解

### 2.1 PriorityNode（优先级节点）

```lua
PriorityNode({
    -- 优先级从高到低
    Node1,  -- 最高优先级
    Node2,
    Node3,  -- 最低优先级
}, .25)  -- 更新频率（秒）
```

### 2.2 IfNode（条件节点）

```lua
IfNode(
    function() return inst.components.health:GetPercent() < 0.5 end,  -- 条件
    "LowHealth",                                                      -- 名称
    RunAway(inst)                                                     -- 满足时执行的节点
)
```

### 2.3 WhileNode（循环条件节点）

```lua
WhileNode(
    function() return inst.components.health:IsDead() end,  -- 循环条件
    "Dead",                                                 -- 名称
    Wait(inst)                                              -- 循环执行的节点
)
```

### 2.4 ActionNode（动作节点）

```lua
ActionNode(function(inst)
    -- 执行具体动作
    inst:PushEvent("custom_action")
end, "CustomAction")
```

### 2.5 DoAction（执行 BufferedAction）

```lua
DoAction(inst, getactionfn, name, run, timeout)
```

---

## 三、官方行为库详解

位于 `scripts/behaviours/` 目录下，包含大量预定义行为：

### 3.1 移动行为

```lua
-- 追逐并攻击目标
ChaseAndAttack(inst, max_chase_time, give_up_dist, max_attacks, findnewtargetfn, walk, distance_from_ocean_target)

-- 追逐并撞击
ChaseAndRam(inst, max_chase_time, give_up_dist, ram_dist, ram_speed, findnewtargetfn)

-- 追逐并攻击但避开特定对象
ChaseAndAttackAndAvoid(inst, max_chase_time, give_up_dist, max_attacks, avoid_tags, avoid_dist, findnewtargetfn)

-- 跟随目标
Follow(inst, targetfn, min_dist, max_dist, follow_dist, keepface)

-- 徘徊
Wander(inst, homelocation, max_dist, times, getdirectionFn, setdirectionFn, checkpointFn, data)

-- 逃跑
RunAway(inst, tags, dist, getaway)

-- 跑到指定距离
RunToDist(inst, target, dist, run)

-- 被吸引
StandAndAttack(inst, range, fn, fn2)
```

### 3.2 防御行为

```lua
-- 使用盾牌
UseShield(inst, shieldprefab, min_health_pct, max_health_pct)

-- 避开电击围栏
AvoidElectricFence(inst)

-- 避开光线
AvoidLight(inst, light_threshold, range)
```

### 3.3 其他行为

```lua
-- 恐慌逃跑
Panic(inst)

-- 恐慌并避开
PanicAndAvoid(inst, avoid_tags, avoid_dist)

-- 面朝实体
FaceEntity(inst, targetfn, keepfacingfn)

-- 站立不动
StandStill(inst, keepfn, timeout)

-- 查找最近目标
FindClosest(inst, tags, dist, musttags, canttags, oneoftags)

-- 聊天节点
ChattyNode(inst, chatterstring, childnode)
```

---

## 四、ChaseAndAttack 详解

这是最常用的战斗行为节点：

### 4.1 参数说明

```lua
ChaseAndAttack(inst, max_chase_time, give_up_dist, max_attacks, findnewtargetfn, walk, distance_from_ocean_target)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `inst` | entity | 实体 |
| `max_chase_time` | number | 最大追逐时间（秒） |
| `give_up_dist` | number | 放弃追逐距离 |
| `max_attacks` | number | 最大攻击次数 |
| `findnewtargetfn` | function | 寻找新目标的函数 |
| `walk` | bool | 是否走路而非跑步 |
| `distance_from_ocean_target` | number/function | 与海洋目标保持的距离 |

### 4.2 核心逻辑

```lua
-- 源码核心流程（chaseandattack.lua）
function ChaseAndAttack:Visit()
    if self.status == READY then
        -- 验证目标，寻找新目标
        combat:ValidateTarget()
        if combat.target == nil and self.findnewtargetfn then
            combat:SetTarget(self.findnewtargetfn(self.inst))
        end
        
        if combat.target ~= nil then
            self.status = RUNNING  -- 开始追逐
        else
            self.status = FAILED   -- 没有目标
        end
    end
    
    if self.status == RUNNING then
        -- 检查目标是否有效
        -- 计算距离，决定是否攻击或继续追逐
        -- 检查是否达到最大攻击次数或超时
        
        if combat:TryAttack() then
            -- 尝试攻击
        end
    end
end
```

---

## 五、Wander 详解

### 5.1 参数说明

```lua
Wander(inst, homelocation, max_dist, times, getdirectionFn, setdirectionFn, checkpointFn, data)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `inst` | entity | 实体 |
| `homelocation` | point/function | 家园位置或获取位置的函数 |
| `max_dist` | number/function | 最大游荡距离 |
| `times` | table | 时间配置（minwalktime, randwalktime, minwaittime, randwaittime） |
| `getdirectionFn` | function | 获取方向的函数 |
| `setdirectionFn` | function | 设置方向的函数 |
| `checkpointFn` | function | 检查点函数 |
| `data` | table | 额外配置（wander_dist, ignore_walls, should_run 等） |

### 5.2 核心逻辑

```lua
-- 源码核心流程（wander.lua）
function Wander:Visit()
    if self.status == READY then
        inst.components.locomotor:StopMoving()
        self:Wait(self.times.minwaittime + math.random() * self.times.randwaittime)
        self.status = RUNNING
    elseif self.status == RUNNING then
        if self:IsFarFromHome() then
            -- 远离家园，返回家园
            self.inst.components.locomotor:GoToPoint(self:GetHomePos())
        else
            -- 随机选择方向游荡
            self:PickNewDirection()
        end
    end
end
```

---

## 六、完整大脑示例

### 6.1 简单战斗生物大脑

```lua
require("behaviours/chaseandattack")
require("behaviours/wander")
require("behaviours/standstill")
require("braincommon")

local MIN_FOLLOW_DIST = 2
local MAX_FOLLOW_DIST = 5
local TARGET_FOLLOW_DIST = 3

local CustomBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
end)

local function GetLeader(inst)
    return inst.components.follower ~= nil and inst.components.follower:GetLeader() or nil
end

local function ShouldFollowLeader(inst)
    local leader = GetLeader(inst)
    return leader ~= nil and not leader:HasTag("playerghost") and leader:IsValid()
end

local function GetWanderPoint(inst)
    return inst.components.follower:GetLeader():GetPosition()
end

function CustomBrain:OnStart()
    local root = PriorityNode({
        -- 最高优先级：死亡状态
        WhileNode(function() return self.inst.components.health:IsDead() end, "Dead",
            StandStill(self.inst)),
        
        -- 恐慌状态
        BrainCommon.PanicTrigger(self.inst),
        
        -- 跟随玩家（如果有跟随者组件）
        WhileNode(function() return ShouldFollowLeader(self.inst) end, "FollowLeader",
            Follow(self.inst, GetLeader, MIN_FOLLOW_DIST, TARGET_FOLLOW_DIST, MAX_FOLLOW_DIST)),
        
        -- 追逐并攻击
        ChaseAndAttack(self.inst, 10, 8),
        
        -- 游荡
        Wander(self.inst, GetWanderPoint, 20),
    }, .25)
    
    self.bt = BT(self.inst, root)
end

return CustomBrain
```

### 6.2 更复杂的大脑示例

```lua
require("behaviours/chaseandattack")
require("behaviours/wander")
require("behaviours/panic")
require("behaviours/follow")
require("behaviours/runaway")
require("behaviours/standstill")

local SEE_FOOD_DIST = 10
local SEE_PLAYER_DIST = 15
local MAX_CHASE_TIME = 10
local MAX_CHASE_DIST = 20

local FOOD_TAGS = { "edible" }
local FOOD_CANT_TAGS = { "INLIMBO", "NOCLICK", "DECOR", "planted" }

local function EatFoodAction(inst)
    local target = FindEntity(inst, SEE_FOOD_DIST, nil, FOOD_TAGS, FOOD_CANT_TAGS)
    if target then
        return BufferedAction(inst, target, ACTIONS.EAT)
    end
end

local function ShouldRunAway(inst)
    return inst.components.health:GetPercent() < 0.3
end

local function RunAwayFromPlayer(inst)
    local player = FindPlayer(inst, SEE_PLAYER_DIST)
    return player
end

local ComplexBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
end)

function ComplexBrain:OnStart()
    local root = PriorityNode({
        -- 死亡
        WhileNode(function() return self.inst.components.health:IsDead() end, "Dead",
            StandStill(self.inst)),
        
        -- 低血量逃跑
        WhileNode(function() return ShouldRunAway(self.inst) end, "RunAway",
            RunAway(self.inst, { "player" }, SEE_PLAYER_DIST)),
        
        -- 恐慌
        Panic(self.inst),
        
        -- 吃东西
        DoAction(self.inst, EatFoodAction, "EatFood"),
        
        -- 追逐攻击
        ChaseAndAttack(self.inst, MAX_CHASE_TIME, MAX_CHASE_DIST),
        
        -- 游荡
        Wander(self.inst, function() return self.inst:GetPosition() end, 20),
    }, .25)
    
    self.bt = BT(self.inst, root)
end

return ComplexBrain
```

---

## 七、BufferedAction 详解

### 7.1 创建 BufferedAction

```lua
BufferedAction(inst, target, action, tool, pos, options)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `inst` | entity | 执行者 |
| `target` | entity | 目标实体 |
| `action` | ACTION | 动作类型（ACTIONS.EAT, ACTIONS.ATTACK 等） |
| `tool` | entity | 使用的工具 |
| `pos` | point | 目标位置 |
| `options` | table | 额外选项 |

### 7.2 常用动作类型

| 动作 | 说明 |
|------|------|
| `ACTIONS.ATTACK` | 攻击 |
| `ACTIONS.EAT` | 吃 |
| `ACTIONS.PICKUP` | 拾取 |
| `ACTIONS.PICK` | 采集 |
| `ACTIONS.CHOP` | 砍树 |
| `ACTIONS.MINE` | 挖矿 |
| `ACTIONS.DIG` | 挖掘 |
| `ACTIONS.TILL` | 耕地 |
| `ACTIONS.GOHOME` | 回家 |
| `ACTIONS.GIVE` | 给予 |
| `ACTIONS.DROP` | 丢弃 |
| `ACTIONS.PLACE` | 放置 |
| `ACTIONS.BUILD` | 建造 |

### 7.3 BufferedAction 方法

```lua
local ba = BufferedAction(inst, target, ACTIONS.EAT)

-- 添加成功回调
ba:AddSuccessAction(function()
    print("Action succeeded!")
end)

-- 添加失败回调
ba:AddFailAction(function()
    print("Action failed!")
end)

-- 设置选项
ba.options.wholestack = true  -- 堆叠操作
```

---

## 八、BrainCommon 常用工具函数

位于 `scripts/brains/braincommon.lua`：

### 8.1 恐慌触发器

```lua
-- 火焰/暗影生物恐慌
BrainCommon.PanicTrigger(inst)

-- 电击围栏恐慌
BrainCommon.ElectricFencePanicTrigger(inst)

-- 受惊时恐慌
BrainCommon.PanicWhenScared(inst, loseloyaltychance, chatty)

-- 吐根糖浆效果恐慌
BrainCommon.IpecacsyrupPanicTrigger(inst)
```

### 8.2 协助领袖

```lua
-- 协助领袖执行动作（采矿、砍树、挖掘、耕地）
BrainCommon.NodeAssistLeaderDoAction(self, parameters)

-- 协助领袖拾取物品
BrainCommon.NodeAssistLeaderPickUps(self, parameters)
```

### 8.3 盐舔石相关

```lua
-- 是否应该寻找盐舔石
BrainCommon.ShouldSeekSalt(inst)

-- 锚定到盐舔石
BrainCommon.AnchorToSaltlick(inst)
```

---

## 九、行为树调试

### 9.1 打印行为树状态

```lua
-- 在大脑中添加调试
function CustomBrain:OnStart()
    local root = PriorityNode({...}, .25)
    self.bt = BT(self.inst, root)
    self.bt:Start()
    
    -- 打印行为树状态
    self.inst:DoPeriodicTask(1, function()
        print("Brain status:", self.bt.status)
        print("Current node:", tostring(self.bt.currentnode))
    end)
end
```

### 9.2 使用 DBString

```lua
-- 许多行为节点实现了 DBString 方法
print("Wander state:", wander_node:DBString())
```

---

## 十、高级技巧

### 10.1 自定义行为节点

```lua
local MyCustomNode = Class(BehaviourNode, function(self, inst, param)
    BehaviourNode._ctor(self, "MyCustomNode")
    self.inst = inst
    self.param = param
end)

function MyCustomNode:Visit()
    if self.status == READY then
        -- 检查条件
        if self.inst.components.health:GetPercent() < self.param.threshold then
            self.status = RUNNING
        else
            self.status = FAILED
        end
    end
    
    if self.status == RUNNING then
        -- 执行动作
        self.inst.components.combat:SetTarget(nil)
        self.inst.components.locomotor:Stop()
        
        -- 完成
        self.status = SUCCESS
    end
end

function MyCustomNode:OnStop()
    -- 清理
end
```

### 10.2 动态行为树

```lua
function CustomBrain:OnStart()
    local function UpdateRoot()
        local nodes = {
            WhileNode(function() return self.inst.components.health:IsDead() end, "Dead",
                StandStill(self.inst)),
        }
        
        -- 根据条件动态添加节点
        if self.inst.components.follower then
            table.insert(nodes, Follow(self.inst, GetLeader, 2, 3, 5))
        end
        
        table.insert(nodes, ChaseAndAttack(self.inst, 10, 8))
        table.insert(nodes, Wander(self.inst, nil, 20))
        
        return PriorityNode(nodes, .25)
    end
    
    self.bt = BT(self.inst, UpdateRoot())
end
```

### 10.3 条件装饰器

```lua
-- 使用 ConditionNode 包装条件
local function HasEnoughHealth(inst)
    return inst.components.health:GetPercent() > 0.5
end

PriorityNode({
    ConditionNode(HasEnoughHealth, "HealthCheck",
        ChaseAndAttack(self.inst, 10, 8)),  -- 只有健康时才攻击
    Wander(self.inst, nil, 20),
}, .25)
```

---

## 十一、参考资源

- 官方行为库：`scripts/behaviours/`
- 大脑通用函数：`scripts/brains/braincommon.lua`
- 蜘蛛大脑：`scripts/brains/spiderbrain.lua`
- 猪人部落大脑：`scripts/brains/pigbrain.lua`
- 牛群大脑：`scripts/brains/beefalobrain.lua`