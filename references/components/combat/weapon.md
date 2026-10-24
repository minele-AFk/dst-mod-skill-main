# `weapon`

> 源码复核：2026-10-23，本机安装包 `scripts.zip`（游戏版本 `759671`）；不等同于线上最新版本。
> 常用声明已对照源码；机制与数值仍需按目标版本和运行端确认。

当任务涉及修改武器端伤害、投射物行为、电击命中或攻击回调时，使用此文件。

官方源码：

- `scripts/components/weapon.lua`

相关官方预制件示例：

- `scripts/prefabs/spear.lua`
- `scripts/prefabs/slingshot.lua`

高频方法：

- `SetDamage(dmg)`
- `SetRange(attack, hit)`
- `SetProjectile(projectile)`
- `SetProjectileOffset(offset)`
- `SetOnAttack(fn)`
- `SetOnProjectileLaunch(fn)`
- `SetOnProjectileLaunched(fn)`
- `SetElectric(damage_mult, wet_damage_mult)`
- `GetDamage(attacker, target)`
- `EnableToughFight(tough)` / `CanDoToughFight()`

常见组件搭配：

- `weapon` + `equippable`
- `weapon` + `inventoryitem`
- `weapon` + `combat`
- `weapon` + 可选 `finiteuses`

常见陷阱：

- 最终攻击流程仍会经过攻击者的 `combat` 组件。
- 投射物武器通常需要匹配的预制件、状态机和动画行为。
- 武器范围是叠加到攻击者基础范围的修正值，不是两处都设置相同绝对值；核对 `combat:GetAttackRange()` / `GetHitRange()` 和玩家动作距离。
- `EnableToughFight` 只把 `tough` 设为非 false 的布尔值；`Combat:ShouldRecoil` 会拒绝 tough 目标，除非攻击者有 `toughfighter` 标签或此武器返回 `CanDoToughFight()==true`。
- `OnAttack` 对 finiteuses 扣耐久；已弹跳的 projectile（`IsBounced()`）不扣该次耐久。偏转回调本身不提供反伤。

---

## 武器伤害计算

本机 `scripts/components/weapon.lua` 的 `Weapon:GetDamage` 流程节录（上下文还需引入 `SpDamageUtil`）：

```lua
function Weapon:GetDamage(attacker, target)
    local dmg = FunctionOrValue(self.damage, self.inst, attacker, target)
    local spdmg = SpDamageUtil.CollectSpDamage(self.inst)
    
    -- 伤害类型加成
    if self.inst.components.damagetypebonus ~= nil then
        local damagetypemult = self.inst.components.damagetypebonus:GetBonus(target)
        dmg = dmg * damagetypemult
        spdmg = SpDamageUtil.ApplyMult(spdmg, damagetypemult)
    end
    
    return dmg, spdmg
end
```

### 关键属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `damage` | number/function | 10 | 基础伤害（可传函数动态计算） |
| `attackrange` | number | nil | 攻击范围加成（叠加到combat） |
| `hitrange` | number | nil | 命中范围加成 |
| `projectile` | string | nil | 投射物预制件名 |
| `stimuli` | string | nil | 刺激类型（如"electric"） |
| `electric_damage_mult` | number | nil | 电击伤害倍率 |
| `electric_wet_damage_mult` | number | nil | 潮湿时电击伤害倍率 |
| `tough` | boolean/nil | nil | `CanDoToughFight()` 仅在值为 true 时通过；用 `EnableToughFight` 设置 |

---

## 投射物系统

`Weapon:LaunchProjectile(attacker, target)` 在服务端依序运行：

1. 有 projectile 配置时调用发射前回调。
2. 尝试 SpawnPrefab；成功后先定位到攻击者附近，简单投射物可用 projectile_offset 调整位置。
3. 简单 projectile 走 Throw，并处理可选 projectiledelay；complexprojectile 走 Launch。具体运动、命中与伤害由各投射物合同决定。
4. 调用发射后回调，即使生成失败，传入的 proj 也可能为 nil。

这不是可直接替换官方函数的简化实现。定制时保留原函数的位置、可见性延迟和回调顺序，缺少分支会改变生成位置或行为。

---

## 实战示例

### 自定义伤害计算

```lua
-- 基于目标血量的伤害
local weapon = inst.components.weapon
weapon:SetDamage(function(inst, attacker, target)
    if target and target.components.health then
        local health_percent = target.components.health:GetPercent()
        return 10 + (1 - health_percent) * 20  -- 目标血量越低伤害越高
    end
    return 10
end)
```

### 攻击特效回调

SetOnAttack 的示例回调收到物品、攻击者与目标，目标允许失效。这里只补表现/设计明确的额外行为；不再直接 health:DoDelta 重复完整武器攻击，也不假定 attack_fx 已存在。包装旧 onattack 时保留它的实际调用和参数。

### 电击武器

```lua
weapon:SetElectric(2, 3)  -- 设置基础倍率 2 与湿度附加系数 3，不是“潮湿总倍率 3”
```

电击流程的条件分支还会检查目标与刺激类型。本机 `combat:CalcDamage` 在适用分支使用 `基础倍率 + 湿度附加系数 * target:GetWetMultiplier()`，因此不能把第二个参数直接当作潮湿时的最终倍率。

后续阅读：

- [combat.md](combat.md)
- [animstate-patterns.md](../../patterns/asset/animstate-patterns.md)
