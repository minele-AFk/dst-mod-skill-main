# `health`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改生命值、死亡流程、无敌状态、回血或最大生命值调优时，使用此文件。

官方源码：

- `scripts/components/health.lua`

相关官方预制件示例：

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/glommer.lua`

高频方法：

- `GetPercent()`
- `SetPercent(percent, overtime, cause)`
- `DoDelta(amount, overtime, cause, ignore_invincible, afflicter, ignore_absorb)`
- `SetCurrentHealth(amount)`
- `SetMaxHealth(amount)`
- `SetPenalty(penalty)`
- `DeltaPenalty(delta)`
- `Kill()`
- `ForceKill()`
- `SetInvincible(val)`
常见组件搭配：

- `health` + `combat`
- `health` + `lootdropper`
- 玩家端 `health` + `hunger` + `sanity`

常见陷阱：

- `DoDelta(...)` 和 `SetPercent(...)` 不能互换使用。
- `Kill()` 遵循更正常的死亡流程；`ForceKill()` 是强制覆盖。
- 生命值变更属于服务端权威逻辑。

---

## 伤害承受计算公式

基于源码 `health.lua:613-649`，`DoDelta` 的伤害计算流程：

### 核心公式

```
实际伤害 = 原始伤害 × 吸收减免 × 外部吸收减免 + 固定减免
```

### 完整计算流程

```lua
-- 1. 非致命伤害检查（饥饿/冷热低于阈值时不造成致命伤害）
if old_percent <= nonlethal_pct and 
   ((cause == "cold" or cause == "hot") and nonlethal_temperature) or
   (cause == "hunger" and nonlethal_hunger) then
    return 0  -- 不造成伤害
end

-- 2. 伤害重定向检查
if self.redirect ~= nil and self.redirect(...) then
    return 0  -- 伤害被重定向
end

-- 3. 无敌状态检查
if not ignore_invincible and (IsInvincible() or is_teleporting) then
    return 0  -- 无敌
end

-- 4. 吸收减免计算（只对伤害生效）
if amount < 0 and not ignore_absorb then
    -- 玩家吸收 + 基础吸收
    local absorb_total = (playerabsorb ~= 0 and afflicter:HasTag("player") and playerabsorb or 0) + absorb
    
    -- 百分比吸收减免
    amount = amount * math.clamp(1 - absorb_total, 0, 1)
    amount = amount * math.max(1 - externalabsorbmodifiers:Get(), 0)
    
    -- 固定减免（只对玩家伤害生效）
    if afflicter ~= nil then
        amount = math.min(0, amount + externalreductionmodifiers:Get())
    end
end

-- 5. 自定义修改器
if self.deltamodifierfn ~= nil then
    amount = self.deltamodifierfn(...)
end

-- 6. 单次伤害上限
if maxdamagetakenperhit ~= nil and amount < maxdamagetakenperhit then
    amount = maxdamagetakenperhit
end

-- 7. 应用伤害
self:SetVal(currenthealth + amount, cause, afflicter)
```

### 关键属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `absorb` | number | 基础吸收百分比（已废弃，使用 externalabsorbmodifiers） |
| `playerabsorb` | number | 玩家伤害吸收百分比（已废弃） |
| `externalabsorbmodifiers` | SourceModifierList | 外部吸收减免（百分比），默认加法 |
| `externalreductionmodifiers` | SourceModifierList | 外部固定减免，默认加法 |
| `deltamodifierfn` | function | 自定义伤害修改函数 |
| `maxdamagetakenperhit` | number | 单次最大承受伤害 |

---

## 火焰伤害计算

基于源码 `health.lua:190-239`：

```lua
function Health:GetFireDamageScale()
    return fire_damage_scale 
        * externalfiredamagemultipliers:Get() 
        * (burnable:GetControlledBurn() and burnable:GetControlledBurn().damage or 1)
end

function Health:DoFireDamage(amount, doer, instant)
    local mult = self:GetFireDamageScale()
    
    -- 火焰伤害上限（每秒）
    if firedamageinlastsecond + amount > TUNING.MAX_FIRE_DAMAGE_PER_SECOND then
        amount = TUNING.MAX_FIRE_DAMAGE_PER_SECOND - firedamageinlastsecond
    end
    
    -- 应用伤害
    self:DoDelta(-amount * mult, false, "fire", nil, doer)
end
```

---

## 生命恢复系统

### 基础恢复

```lua
-- 开启恢复
inst.components.health:StartRegen(2, 2)  -- 每2秒恢复2点

-- 停止恢复
inst.components.health:StopRegen()
```

### 多来源恢复（推荐）

```lua
-- 添加恢复来源
inst.components.health:AddRegenSource(inst, 1, 1, "skill_regen")

-- 移除恢复来源
inst.components.health:RemoveRegenSource(inst, "skill_regen")
```

---

## 实战示例

### 百分比减伤

```lua
-- 添加50%减伤
inst.components.health.externalabsorbmodifiers:SetModifier("my_skill", 0.5)

-- 移除减伤
inst.components.health.externalabsorbmodifiers:RemoveModifier("my_skill")
```

### 固定减伤

```lua
-- 添加5点固定减伤
inst.components.health.externalreductionmodifiers:SetModifier("my_skill", 5)
```

### 自定义伤害修改

```lua
-- 反弹50%伤害
inst.components.health.deltamodifierfn = function(inst, amount, ...)
    if amount < 0 and inst.components.combat.lastattacker then
        inst.components.combat.lastattacker.components.health:DoDelta(amount * -0.5)
    end
    return amount
end
```

后续阅读：

- [stategraph-contract.md](../../gameplay/dst-stategraph-authoring/references/stategraph-contract.md)
- [player-network-patterns.md](../../patterns/network/player-network-patterns.md)
