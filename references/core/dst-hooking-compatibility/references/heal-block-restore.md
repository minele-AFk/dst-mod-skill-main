# 治疗封锁（禁疗）的实现与反制

讲解「让目标无法回血」的一种常见做法（直接遮蔽组件实例方法），为什么它会一直残留、只能在重进后消失，以及如何从另一个 mod 无侵入地反制并永久恢复。

## 适用场景

- 做一个会「封锁目标治疗」的能力（攻击带禁疗、Buff 禁疗等）。
- 排查某个生效后一直存在、重进才消失的效果为什么清不掉。
- 在自己的 mod 里防御别人用「实例方法覆盖」改掉了 `health.DoDelta` 导致回血永久失效。

核心前提（Lua 元表机制）：组件方法定义在**类表**上，实例通过元表 `__index` 回落；给**实例**赋一个同名字段会遮蔽类方法，而类方法本身始终还在。

## 一、实现：遮蔽 health 实例的 DoDelta

按原版 `components/health.lua`，`Health:DoDelta` 是类方法（所有 `health` 实例共用）。禁疗常在每次「攻击命中他人」时，对目标做一次实例级覆盖：

```lua
local function onhitother(inst, data)
    local target = data.target
    if target.components.health and not target.components.health.dodalta_hooked
        and inst.open_nohealth then
        target.components.health.dodalta_hooked = true   -- 防重复覆盖的标记
        local oldDoDelta = target.components.health.DoDelta
        target.components.health.DoDelta = function(self, amount, overtime, cause, ...)
            if amount and amount > 0 and inst.open_nohealth then
                return                                  -- 正数（治疗）直接吞掉
            end
            return oldDoDelta(self, amount, overtime, cause, ...)
        end
    end
end
```

要点：
- 覆盖写的是**目标实体的实例字段** `target.components.health.DoDelta`，不影响其他实体的类方法。
- 用闭包捕获施法者，每次调用现读 `inst.open_nohealth`，所以开关状态是动态生效的。
- `dodalta_hooked` 只用于「只挂一次」，不是生命周期管理。

## 二、为什么「一直存在，只能重进消失」

- 该覆盖**只安装、从不回收**：没有定时器、没有 debuff 组件、没有 `onremove` 监听、没有还原逻辑。
- 它永久驻留在目标实体的 `health` 实例上，直到该实体实例销毁。
- 重进（世界/服务端重启后实体重建）会从类表重新生成一份全新 `DoDelta`，残留的实例覆盖自然消失——这正是「退出重进才恢复」的原因。
- 若施法者一直保持 `open_nohealth == true`，任何被打过的目标从此彻底无法恢复生命。

## 三、反制：把实例字段置 nil，回落类方法

原版 `Health:DoDelta` 还完整地保留在类表上，只是被目标的实例字段遮蔽。另一个 mod 只需把这个实例字段置 `nil`，下一次 `:DoDelta()` 就会自动回落类方法，立即恢复原版回血：

```lua
local function restore_healing(ent)
    local h = ent.components and ent.components.health
    if h == nil or h.DoDelta == nil then return end
    -- 只处理"实例自己定义了 DoDelta"的实体（遮蔽了类方法）
    local class_do_delta = getmetatable(h).__index.DoDelta
    if h.DoDelta ~= class_do_delta then
        h.DoDelta = nil   -- 回落类上的原版方法
    end
end
```

关键：**不要把 `dodalta_hooked` 标记改回 false/删掉**。保留它，对方「只挂一次」的判断仍然命中，就不会对同一目标重新覆盖，实现一次性根治。

## 四、全局自动清理

要覆盖任意被污染的目标时，利用服务端全局实体表 `Ents`（GUID→实体）做低频周期扫描：

```lua
local function scan()
    if not TheWorld or not TheWorld.ismastersim then return end
    for guid, ent in pairs(Ents) do
        if ent and ent.components and ent.components.health then
            restore_healing(ent)
        end
    end
end
-- 世界就绪后挂周期任务，例如 TheWorld:DoPeriodicTask(1, scan)
```

注意 `pairs(Ents)` 全扫有开销，只用于确有需要且低频执行的场景；对已知目标可用精确的还原调用，不必全扫。

## 五种反制思路对比

| 方式 | 做法 | 特点 |
| --- | --- | --- |
| 实例还原（推荐） | `ent.components.health.DoDelta = nil` | 治本，一次永久恢复该目标；可配合扫描 |
| 屏蔽开关 | 让施法者的 `open_nohealth = false` | 反映效果、即时生效；开关一开又复发，属治标 |
| 类级包装 | 不动 `DoDelta`，从治疗入口（如 `healthdelta`/`SetVal` 前置）拦截 | 成本高，需覆盖所有治疗来源 |
| 事件监听移除 | 在目标移除/施法结束事件里还原 | 需要可靠的清理时点，覆盖不到未监听路径 |
| 直接改类方法 | 全局包装 `Health:DoDelta` | 影响所有实体，除非确需全局否则避免 |

## 通用启示（兼容性要点）

- 方法补丁有「**遮蔽实例字段**」与「**改类方法**」两种，二者的影响范围、持久性和反制难度差异很大。
- 实例字段遮蔽：范围最小、易反制（置 nil 即回落），但会被误读成「mod 专用 bug」。
- 类方法覆盖：影响所有实体，反制必须重建类方法或包装入口，冲突风险更高。
- 装 `dodalta_hooked` 之类的守卫时，只标记「已处理」，不要把守卫当清理依据；真正的清理要显式还原，否则只是暂缓重复覆盖。

官方源码：`components/health.lua`（`Health:DoDelta` 类方法、`SetVal`/`healthdelta` 事件）；`mainfunctions.lua`（`Ents` 全局实体表）。