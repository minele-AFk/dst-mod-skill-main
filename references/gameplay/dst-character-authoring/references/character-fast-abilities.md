# 角色被动能力：快速进食 与 快速制作

给自定义角色添加「吃得快」「造得快」两类被动能力。两者走**完全不同的原理**：
- 快速进食 = 自定义状态机（SG）状态 + 动作目标重定向（提速动画并提前触发进食）。
- 快速制作 = 复用官方内建 `fastbuilder` 标签（建造/制作时长减半）。

## 一、快速制作（fastbuilder 标签）— 最简单

**一行即可**：直接给玩家加官方内建标签。

```lua
-- 角色能力、buff 挂载时
inst:AddTag("fastbuilder")
```

官方在 `stategraphs/SGwilson.lua` 的建造/制作状态里判断该标签：

```lua
-- 建造
inst.sg:GoToState("construct", inst:HasTag("fastbuilder") and .5 or 1)
-- 制作/其它
inst.sg:SetTimeout(inst:HasTag("fastbuilder") and .5 or 1)
```

带 `fastbuilder` 时建造/制作时长减半。这也是原版温妮的机制（`prefabs/winona.lua` 里同样 `AddTag("fastbuilder")`）。
**如果想取消该能力：`inst:RemoveTag("fastbuilder")`。**

## 二、快速进食（自定义 SG 状态 + 动作重定向）

需要两步：加能力标记 + 重定向进食动作到自定义快速状态。

### 1) 加能力标记

```lua
inst.noa_fast_eat = true
```

### 2) 重定向 EAT 动作到自定义状态

包装 `wilson`（及客户端 `wilson_client`）状态机的 `actionhandlers[ACTIONS.EAT].deststate`：

```lua
local actionlist = {
    [ACTIONS.EAT] = function(inst, act, oldresult)
        if act.doer and act.doer.noa_fast_eat then
            return "noa_eat"      -- 有标记时走自定义快速状态
        end
        -- 否则返回 nil，回落到旧状态
    end,
}

AddStategraphPostInit("wilson", function(self)
    for k, v in pairs(actionlist) do
        local oldhandlers = self.actionhandlers[k].deststate
        self.actionhandlers[k].deststate = function(inst, action)
            local oldresult = oldhandlers(inst, action)
            local newresult = v(inst, action, oldresult)
            if newresult then return newresult end
            return oldresult
        end
    end
end)
```

要点：`deststate` 包装后先调旧逻辑拿 `oldresult`，自定义逻辑返回新状态则覆盖，否则回退。**也要对客户端 SG（`wilson_client`）做同样处理，否则本地预测不一致。**

### 3) 自定义快速进食状态

在玩家 SG 里注册状态（可直接 `AddStategraphState`）：

```lua
local eat_mult = 3   -- 提速倍率

AddStategraphState("wilson", "noa_eat", {
    name = "noa_eat",
    tags = { "nopredict", "busy", "keep_pocket_rummage" },

    onenter = function(inst, foodinfo)
        inst.components.locomotor:Stop()
        -- 播放快速进食动画，并 3 倍速
        inst.AnimState:PlayAnimation("quick_eat_pre")
        inst.AnimState:PushAnimation("quick_eat", false)
        inst.AnimState:SetDeltaTimeMultiplier(eat_mult)
        inst.components.hunger:Pause()
    end,

    timeline = {
        -- 提前触发实际进食（12帧 / 3 = 4帧）
        TimeEvent(12 / eat_mult * FRAMES, function(inst)
            if inst.components.eater ~= nil then
                inst.components.eater:Eat(inst:GetBufferedAction().invobject)
            else
                inst:PerformBufferedAction()
            end
        end),
    },
})
```

关键点：
- `SetDeltaTimeMultiplier(eat_mult)` 让动画按倍率加速播放。
- `TimeEvent(12 / eat_mult * FRAMES)` 把真正 `Eat` 的时刻按同样的倍率提前，动画和进食同时变快。
- 记得对称处理 `timeline` 里的实际进食调用路径（有没有 feeder / 是否是 buffered action）。

## 常见坑

- **只改服务端 SG 忘了客户端**：快速进食等动作预测需要同时在 `wilson_client` 处理，否则本地会有延迟/回跳。
- **`deststate` 包装错误返回值**：自定义逻辑返回 `nil` 时必须回落到 `oldresult`，否则其它动作行为被破坏。
- **`fastbuilder` 影响面**：它是通用标签，所有用到它的建造/制作状态都会提速；如需只对特定动作生效，用自定义 SG 状态方案而非标签。

官方源码：`stategraphs/SGwilson.lua`（fastbuilder 提速点）、`prefabs/winona.lua`（温妮加 fastbuilder）、`prefabs/player_common.lua`。

---

## 相关枢纽

- [character-fast-work.md](character-fast-work.md) - 同主题的第三条路线：覆写 `dolongaction` 统一加速采集/制造/交互，含双倍采集与一键收获。
- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。