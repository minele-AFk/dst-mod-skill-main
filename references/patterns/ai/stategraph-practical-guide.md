# 状态机实战指南：CommonStates、攻击与时间线

按需查阅 CommonStates 签名、完整生物状态图和高级片段。对象与预测合同统一见 [StateGraph 合同](../../gameplay/dst-stategraph-authoring/references/stategraph-contract.md)。本轮按当前安装包核对，示例未实机运行。

---

## 一、状态机基础概念

### 1.1 StateGraph 结构

```lua
local states = { State{ name = "idle", tags = { "idle" } } }
local events = {}
local actionhandlers = {}
return StateGraph("my_mod_creature", states, events, "idle", actionhandlers)
```

### 1.2 State 结构

每个状态包含以下核心部分：

| 属性 | 作用 | 示例 |
|------|------|------|
| `name` | 状态名称 | `"idle"`, `"attack"` |
| `tags` | 状态标签 | `{"idle", "canrotate"}` |
| `onenter` | 进入状态时执行 | 播放动画、停止移动 |
| `onupdate` | 每帧更新 | 检查条件、执行逻辑 |
| `onexit` | 离开状态时执行 | 清理资源 |
| `ontimeout` | 超时回调 | 状态自动切换 |
| `events` | 事件监听 | 动画完成、伤害事件 |
| `timeline` | 时间线 | 按时间触发动作 |

### 1.3 核心函数

```lua
inst.sg:GoToState(state_name, data)       -- 切换到指定状态
inst.sg:HasStateTag(tag)                  -- 检查当前状态是否有指定标签
inst.sg:HasAnyStateTag(tag1, tag2)       -- 检查是否有任一标签
inst.sg:SetTimeout(time)                  -- 设置状态超时
inst.sg:AddStateTag(tag)                 -- 添加状态标签
inst.sg:RemoveStateTag(tag)              -- 移除状态标签
```

---

## 二、CommonStates 常用状态生成器

官方提供了大量预定义的状态生成函数，位于 `commonstates.lua`：

### 2.1 基础状态

```lua
-- 添加空闲状态
CommonStates.AddIdle(states, funny_idle_state, anim_override, timeline)

-- 添加简单状态（播放动画后返回指定状态）
CommonStates.AddSimpleState(states, name, anim, tags, finishstate, timeline, fns)

-- 添加简单动作状态（带时间线触发）
CommonStates.AddSimpleActionState(states, name, anim, time, tags, finishstate, timeline, fns)
```

### 2.2 移动状态

```lua
-- 添加跑步状态（run_start, run, run_stop）
CommonStates.AddRunStates(states, timelines, anims, softstop, delaystart, fns)

-- 添加行走状态（walk_start, walk, walk_stop）
CommonStates.AddWalkStates(states, timelines, anims, softstop, delaystart, fns)

-- 简化版跑步状态
CommonStates.AddSimpleRunStates(states, anim, timelines)

-- 简化版行走状态
CommonStates.AddSimpleWalkStates(states, anim, timelines)
```

### 2.3 战斗状态：AddCombatStates 与 attacktimeline

```lua
-- 添加战斗状态（hit, attack, death）
CommonStates.AddCombatStates(states, timelines, anims, fns, data)

-- 仅添加受击状态
CommonStates.AddHitState(states, timeline, anim)

-- 添加触电状态
CommonStates.AddElectrocuteStates(states, timelines, anims, fns)
```

### 2.4 其他常用状态

```lua
-- 添加睡眠状态（sleep, sleeping, wake）
CommonStates.AddSleepStates(states, timelines, fns)

-- 添加冰冻状态（frozen, thaw）
CommonStates.AddFrozenStates(states, onoverridesymbols, onclearsymbols)

-- 添加跳跃状态（用于两栖生物）
CommonStates.AddHopStates(states, wait_for_pre, anims, timelines, land_sound, landed_in_falling_state, data, fns)
```

---

## 三、CommonHandlers 常用事件处理器

### 3.1 核心事件

```lua
-- 攻击事件处理
CommonHandlers.OnAttack()  -- 监听 "doattack" 事件

-- 受伤事件处理
CommonHandlers.OnAttacked(hitreact_cooldown, max_hitreacts, skip_cooldown_fn)

-- 死亡事件处理
CommonHandlers.OnDeath()  -- 监听 "death" 事件

-- 冰冻事件处理
CommonHandlers.OnFreeze()  -- 监听 "freeze" 事件

-- 触电事件处理
CommonHandlers.OnElectrocute()  -- 监听 "electrocute" 事件

-- 睡眠事件处理
CommonHandlers.OnSleep()  -- 监听 "gotosleep" 事件

-- 移动事件处理
CommonHandlers.OnLocomote(can_run, can_walk)
```

### 3.2 事件处理器示例

```lua
events = {
    CommonHandlers.OnAttack(),           -- 攻击时切换到 attack 状态
    CommonHandlers.OnAttacked(),         -- 受伤时切换到 hit 状态
    CommonHandlers.OnDeath(),            -- 死亡时切换到 death 状态
    CommonHandlers.OnFreeze(),           -- 冰冻时切换到 frozen 状态
    CommonHandlers.OnLocomote(true, true), -- 移动状态管理
}
```

---

## 四、完整状态机示例

### 4.1 简单生物状态机

保存为 scripts/stategraphs/SGmy_mod_creature.lua，由宿主 SetStateGraph("SGmy_mod_creature") 加载。宿主须先提供 locomotor、combat、health、lootdropper、物理和以下真实动画：idle_loop、atk、hit、death、run/walk 系列、action、eat；这些自有资源未包含在示例中。GOHOME/EAT 的目标还须满足原版 Action 业务要求。

```lua
require("stategraphs/commonstates")

local actionhandlers = {
    ActionHandler(ACTIONS.GOHOME, "action"),
    ActionHandler(ACTIONS.EAT, "eat"),
}

local events = {
    CommonHandlers.OnAttack(),
    CommonHandlers.OnAttacked(),
    CommonHandlers.OnDeath(),
    CommonHandlers.OnLocomote(true, true),
}

local states = {
    State{
        name = "idle",
        tags = { "idle", "canrotate" },
        onenter = function(inst)
            inst.components.locomotor:StopMoving()
            inst.AnimState:PlayAnimation("idle_loop", true)
        end,
        events = {
            EventHandler("animover", function(inst)
                inst.sg:GoToState("idle")
            end),
        },
    },
    
    State{
        name = "attack",
        tags = { "attack", "busy" },
        onenter = function(inst, target)
            inst.components.locomotor:StopMoving()
            inst.AnimState:PlayAnimation("atk")
            inst.components.combat:StartAttack()
            inst.sg.statemem.target = target or inst.components.combat.target
        end,
        timeline = {
            TimeEvent(12 * FRAMES, function(inst)
                local target = inst.sg.statemem.target
                if target ~= nil and target:IsValid() then
                    inst.components.combat:DoAttack(target)
                end
            end),
        },
        events = {
            EventHandler("animover", function(inst)
                inst.sg:GoToState("idle")
            end),
        },
    },
    
    State{
        name = "hit",
        tags = { "hit", "busy" },
        onenter = function(inst)
            inst.components.locomotor:StopMoving()
            inst.AnimState:PlayAnimation("hit")
        end,
        events = {
            EventHandler("animover", function(inst)
                inst.sg:GoToState("idle")
            end),
        },
    },
    
    State{
        name = "death",
        tags = { "dead" },
        onenter = function(inst)
            inst.components.locomotor:StopMoving()
            inst.AnimState:PlayAnimation("death")
            RemovePhysicsColliders(inst)
            inst:DropDeathLoot()
        end,
    },
}

-- 添加移动状态
CommonStates.AddRunStates(states)
CommonStates.AddWalkStates(states)

-- 两个映射状态都必须存在；默认时间线在指定时间执行 BufferedAction。
CommonStates.AddSimpleActionState(states, "action", "action", 10 * FRAMES)
CommonStates.AddSimpleActionState(states, "eat", "eat", 10 * FRAMES)
return StateGraph("my_mod_creature", states, events, "idle", actionhandlers)
```

### 4.2 使用 CommonStates 的简化版本

与 4.1 同样需要宿主组件和匹配的动画，special 动画及项目事件消费者另行实现。AddCombatStates 不提供默认伤害帧，所以下面显式给 attacktimeline；AddSimpleActionState 若传自定义 timeline，也会替换默认执行时间线。

```lua
require("stategraphs/commonstates")

local events = {
    CommonHandlers.OnAttack(),
    CommonHandlers.OnAttacked(),
    CommonHandlers.OnDeath(),
    CommonHandlers.OnLocomote(true, true),
}

local states = {}

-- 使用 CommonStates 添加基础状态
CommonStates.AddIdle(states)
CommonStates.AddRunStates(states)
CommonStates.AddWalkStates(states)
CommonStates.AddCombatStates(states, {
    attacktimeline = {
        TimeEvent(12 * FRAMES, function(inst)
            local target = inst.sg.statemem.target
            if target ~= nil and target:IsValid() then
                inst.components.combat:DoAttack(target)
            end
        end),
    },
})

-- 添加自定义状态
table.insert(states, State{
    name = "special_ability",
    tags = { "busy", "special" },
    onenter = function(inst)
        inst.components.locomotor:StopMoving()
        inst.AnimState:PlayAnimation("special")
    end,
    timeline = {
        TimeEvent(20 * FRAMES, function(inst)
            -- 释放技能效果
            inst:PushEvent("special_ability_trigger")
        end),
    },
    events = {
        EventHandler("animover", function(inst)
            inst.sg:GoToState("idle")
        end),
    },
})

return StateGraph("my_mod_creature", states, events, "idle")
```

---

## 五、时间线（Timeline）详解

时间线是状态机中按时间顺序执行动作的机制：

### 5.1 基本用法

```lua
timeline = {
    TimeEvent(10 * FRAMES, function(inst)
        -- 第10帧执行
        -- 在这里播放项目已注册、已验证的声音事件。
    end),
    TimeEvent(20 * FRAMES, function(inst)
        -- 第20帧执行
        local target = inst.sg.statemem.target
        if target ~= nil and target:IsValid() then
            inst.components.combat:DoAttack(target)
        end
    end),
    TimeEvent(30 * FRAMES, function(inst)
        -- 第30帧执行
        inst.sg:GoToState("idle")
    end),
}
```

### 5.2 时间线与状态组合

```lua
State{
    name = "multi_attack",
    tags = { "attack", "busy" },
    onenter = function(inst)
        inst.components.locomotor:StopMoving()
        inst.AnimState:PlayAnimation("multi_atk")
    end,
    timeline = {
        TimeEvent(10 * FRAMES, function(inst)
            inst.components.combat:DoAttack()
        end),
        TimeEvent(25 * FRAMES, function(inst)
            inst.components.combat:DoAttack()
        end),
        TimeEvent(40 * FRAMES, function(inst)
            inst.components.combat:DoAttack()
        end),
    },
    events = {
        EventHandler("animover", function(inst)
            inst.sg:GoToState("idle")
        end),
    },
}
```

---

## 六、状态机最佳实践

### 6.1 状态标签的使用

状态标签用于快速查询状态属性：

```lua
-- 在状态中定义标签
State{
    name = "attack",
    tags = { "attack", "busy", "nointerrupt" },
    onenter = function(inst)
        -- 在此添加本项目需要的进入逻辑。
    end,
}

-- 在其他地方查询
if inst.sg:HasStateTag("busy") then
    -- 正在执行忙碌动作
end

if inst.sg:HasAnyStateTag("attack", "special") then
    -- 正在攻击或释放技能
end
```

### 6.2 状态数据传递

使用 `statemem` 保存当前状态的数据；它会在 GoToState 时清空。跨状态使用 GoToState(nextstate, data) 显式传参，或管理 sg.mem 的生命周期：

```lua
-- 在 onenter 中存储数据
State{
    name = "attack",
    onenter = function(inst, target)
        inst.sg.statemem.target = target
        inst.sg.statemem.damage = 20
    end,
    timeline = {
        TimeEvent(15 * FRAMES, function(inst)
            -- 使用 statemem 中的数据
            inst.components.combat:DoAttack(inst.sg.statemem.target)
        end),
    },
}
```

### 6.3 状态中断处理

通过事件和标签控制状态中断：

```lua
State{
    name = "casting",
    tags = { "busy", "nointerrupt" },  -- 由具体 handler 检查，不是引擎绝对锁
    onenter = function(inst)
        inst.AnimState:PlayAnimation("cast")
    end,
    events = {
        EventHandler("attacked", function(inst, data)
            -- 本例选择消费受击事件；死亡等其他事件仍走各自合同。
            return true
        end),
    },
}
```

### 6.4 动画完成检测

```lua
State{
    name = "use_item",
    onenter = function(inst)
        inst.AnimState:PlayAnimation("use_item")
    end,
    events = {
        EventHandler("animover", function(inst)
            -- 确保动画真正完成
            if inst.AnimState:AnimDone() then
                inst.sg:GoToState("idle")
            end
        end),
    },
}
```

### 6.5 状态超时机制

```lua
State{
    name = "searching",
    onenter = function(inst)
        inst.AnimState:PlayAnimation("search")
        inst.sg:SetTimeout(3)  -- 3秒超时
    end,
    ontimeout = function(inst)
        -- 超时后切换状态
        inst.sg:GoToState("idle")
    end,
}
```

---

## 七、调试技巧

### 7.1 打印状态信息

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
-- 在状态的 onenter 中添加调试信息
onenter = function(inst)
    print("Entering state:", inst.sg.currentstate.name)
    ...
end
```

### 7.2 检查状态机状态

```lua
-- 检查当前状态
print("Current state:", inst.sg.currentstate.name)

-- 检查状态标签
print("Has attack tag:", inst.sg:HasStateTag("attack"))

-- 检查是否有特定状态
print("Has hit state:", inst.sg:HasState("hit"))
```

---

## 八、高级技巧

### 8.1 共享状态工厂

SG 没有自动继承合同。直接 require 某个 SG 再 deepcopy 其 states 仍可能共享函数闭包和引用，也会混入该图的组件/预测假设。复用时优先 CommonStates；自有共享模块可返回创建新 State 表的工厂，每次构造返回新对象，检查重名并显式组装 events/actionhandlers。

### 8.2 动态状态切换

此片段要求 health 组件以及 flee/attack 目的状态存在；动态条件不能保证这些依赖。

```lua
-- 根据条件动态切换状态
State{
    name = "decision",
    onenter = function(inst)
        if inst.components.health:GetPercent() < 0.5 then
            inst.sg:GoToState("flee")
        else
            inst.sg:GoToState("attack")
        end
    end,
}
```

### 8.3 状态回调函数

```lua
-- 使用回调函数处理状态逻辑
State{
    name = "complex_action",
    onenter = function(inst, params)
        inst.AnimState:PlayAnimation("complex")
        
        -- 存储回调函数
        inst.sg.statemem.oncomplete = params ~= nil and params.oncomplete or nil
    end,
    events = {
        EventHandler("animover", function(inst)
            if not inst.AnimState:AnimDone() then return end
            local oncomplete = inst.sg.statemem.oncomplete
            inst.sg.statemem.oncomplete = nil
            inst.sg:GoToState("idle")
            if oncomplete ~= nil then oncomplete(inst) end
        end),
    },
}

-- 使用
inst.sg:GoToState("complex_action", {
    oncomplete = function(inst)
        print("Action completed!")
    end,
})
```

---

## 九、参考资源

- 官方源码：`scripts/stategraphs/commonstates.lua`
- 玩家状态机：`scripts/stategraphs/SGwilson.lua`
- 蜘蛛状态机：`scripts/stategraphs/SGspider.lua`
- 龙蝇状态机：`scripts/stategraphs/SGdragonfly.lua`
本轮源码依据：stategraph.lua、commonstates.lua、entityscript.lua。DropDeathLoot 与 OnPreLoad 在当前 EntityScript 中确实存在；不要因旧教程其他错误误删这些有效接口。
