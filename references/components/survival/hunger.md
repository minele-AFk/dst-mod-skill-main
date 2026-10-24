# `hunger`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改饥饿值、消耗速率、暂停或恢复流程或饿死行为时，使用此文件。

官方源码：

- `scripts/components/hunger.lua`

相关官方预制件示例：

- `scripts/prefabs/player_common.lua`

高频方法：

- `SetMax(amount)`
- `SetRate(rate)`
- `Pause()`
- `Resume()`
- `IsStarving()`
- `GetPercent()`
- `SetPercent(p, overtime)`
- `SetCurrent(current, overtime)`
- `DoDelta(delta, overtime, ignore_invincible)`
- `LongUpdate(dt)`
常见组件搭配：

- 玩家 `hunger` + `health`
- 玩家 `hunger` + `sanity`

常见陷阱：

- `SetRate(...)` 改变的是持续消耗速率，不是当前饥饿值。
- 饿死伤害来自饥饿更新路径，不是单次写入。
- 存档或读档行为通常需要注意 `LongUpdate(...)`。

---

## 饥饿消耗机制

基于源码 `hunger.lua:24-90`：

### 核心属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `max` | number | 100 | 最大饥饿值 |
| `current` | number | 100 | 当前饥饿值 |
| `hungerrate` | number | 1 | 饥饿消耗速率 |
| `hurtrate` | number | 1 | 饿死伤害速率 |
| `burning` | boolean | true | 是否正在消耗饥饿 |
| `burnrate` | number | 1 | 消耗倍率（已废弃） |
| `burnratemodifiers` | SourceModifierList | - | 消耗倍率（推荐） |
| `overridestarvefn` | function | nil | 自定义饿死行为 |

### 消耗流程

```lua
-- 每1秒调用一次
local UPDATE_PERIOD = 1

local function OnTaskTick(inst, self)
    self:DoDec(UPDATE_PERIOD)
end

function Hunger:DoDec(dt, ignore_damage)
    if self:IsPaused() then
        return
    end
    
    -- 饥饿消耗
    local burn_rate = self.hungerrate * self.burnratemodifiers:Get()
    self:DoDelta(-burn_rate * dt)
    
    -- 饿死伤害
    if not ignore_damage and self.current <= 0 then
        local hurt_rate = self.hurtrate * self.burnratemodifiers:Get()
        if self.inst.components.health then
            self.inst.components.health:DoDelta(-hurt_rate * dt, false, "hunger")
        end
    end
end
```

---

## 状态转换

```lua
-- 暂停消耗
function Hunger:Pause()
    self.burning = false
    if self.updatetask ~= nil then
        self.updatetask:Cancel()
        self.updatetask = nil
    end
end

-- 恢复消耗
function Hunger:Resume()
    self.burning = true
    if self.updatetask == nil then
        self.updatetask = self.inst:DoPeriodicTask(UPDATE_PERIOD, OnTaskTick, nil, self)
    end
end
```

---

## 实战示例

### 修改消耗速率

```lua
-- 增加50%饥饿消耗
inst.components.hunger.burnratemodifiers:SetModifier("my_skill", 1.5)

-- 减少50%饥饿消耗
inst.components.hunger.burnratemodifiers:SetModifier("my_skill", 0.5)

-- 移除倍率
inst.components.hunger.burnratemodifiers:RemoveModifier("my_skill")
```

### 暂停/恢复饥饿

```lua
-- 暂停饥饿消耗（如无敌状态）
inst.components.hunger:Pause()

-- 恢复饥饿消耗
inst.components.hunger:Resume()
```

### 自定义饿死行为

```lua
inst.components.hunger:SetOverrideStarveFn(function(inst)
    -- 自定义饿死逻辑
    inst.components.health:DoDelta(-2)  -- 每秒扣2血
end)
```

### 饥饿增减

```lua
-- 增加50点饥饿
inst.components.hunger:DoDelta(50)

-- 减少20点饥饿
inst.components.hunger:DoDelta(-20)

-- 设置为50%饥饿
inst.components.hunger:SetPercent(0.5)
```

后续阅读：

- [health.md](health.md)
- [persistence-contract.md](../../core/dst-persistence-migration/references/persistence-contract.md)
