# 进食三维修改

目标：角色吃食物时，生命/饥饿/理智的增减可被修改（如减半），并能控制只改正向增益或只改负面减益。

## 官方基础：absorption 系数

官方 `Eater:Eat` 计算三维（`components/eater.lua`）：

```lua
health_delta = food.components.edible:GetHealth(self.inst) * base_mult * self.healthabsorption
hunger_delta = food.components.edible:GetHunger(self.inst) * base_mult * self.hungerabsorption
sanity_delta = food.components.edible:GetSanity(self.inst) * base_mult * self.sanityabsorption
```

- `GetHealth/GetHunger/GetSanity` 可正可负（负面食物扣血/扣理智）。
- `absorption` 是乘数，**不分正负**。设 `0.5` 时正向增益与负面减益同时减半。
- 应用实例：本体设 `eater.healthabsorption = hungerabsorption = sanityabsorption = 0.5`，后阶段把系数还原成 `1` 解除。

## 只改单向：符号过滤的 DoDelta hook

absorption 不能单向，改用「进食标记 + DoDelta 符号判断」。

**① 进食标记**（包 `Eater:Eat`）：

```lua
function Eater:Eat(food, feeder, ...)
    self.inst.noa_eating = true
    local r = oldEat(self, food, feeder, ...)
    self.inst.noa_eating = false
    return r
end
```

**② 吸收系数还原为 1**，避免和新 hook 双重减半。

**③ 给三点组件 DoDelta 挂符号过滤的包壳**（省略号透传原参）：

```lua
local function halve(comp, key, mode, factor)
    local old = comp[key]
    comp[key] = function(self, amount, overtime, ...)
        if self.inst.noa_eating then
            local hit = (mode == "positive" and amount > 0)
                     or (mode == "negative" and amount < 0)
                     or mode == "both"
            if hit then amount = amount * (factor or 0.5) end
        end
        return old(self, amount, overtime, ...)
    end
end

halve(inst.components.health, "DoDelta", "both")   -- 双向减半
halve(inst.components.sanity, "DoDelta", "positive") -- 只减正向
```

模式：`positive`（减半回血/回理智/回饥饿）、`negative`（减半扣减）、`both`。

## 注意

- 别忘了进食标记，否则战斗伤害/治疗也会被减半。
- absorption 没还原会和新 hook 叠加成 `0.25`。
- 按具体食物过滤：加 `and not food:HasTag("xxx")`。

官方参考：`components/eater.lua`、`edible.lua`、`health.lua`/`sanity.lua`/`hunger.lua`。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。