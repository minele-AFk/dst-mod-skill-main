# `armor`

> 适用版本：API 10+
> 方法签名复核：2026-10-23，本机安装快照（游戏版本 `759671`）；不代表游戏行为验收。

当任务涉及修改防护量、耐久条件、破损流程或护甲修复时，使用此文件。

官方源码：

- `scripts/components/armor.lua`

相关官方预制件示例：

- `scripts/prefabs/armor_grass.lua`

高频方法：

- `InitCondition(amount, absorb_percent)`
- `InitIndestructible(absorb_percent)`
- `SetAbsorption(absorb_percent)`
- `SetCondition(amount)`
- `SetPercent(amount)`
- `GetPercent()`
- `TakeDamage(damage_amount)`
- `Repair(amount)`
- `SetOnFinished(fn)`
- `SetKeepOnFinished(keep)`
- `AddWeakness(tag, bonus_damage)`
- `RemoveWeakness(tag)`
常见组件搭配：

- `armor` + `equippable`
- `armor` + `inventoryitem`

常见陷阱：

- `armor` 是防护和耐久逻辑，不是装备槽位所有权。
- 破损行为通常还需要物品和装备回调。
- 不可破坏的护甲与普通高耐久护甲不同。
- `SetKeepOnFinished(false)` 会显式关闭保留；省略或传非 false 会保留。耐久归零后仍可能调用 finished 回调，但实体是否移除由该字段决定。

---

## 护甲减免计算

基于源码 `armor.lua:126-164`，护甲在 `inventory:ApplyDamage` 中被调用：

### 核心流程

```lua
function Armor:GetAbsorption(attacker, weapon)
    -- 检查是否能抵抗该攻击类型
    return self:CanResist(attacker, weapon) and self.absorb_percent or nil
end

function Armor:CanResist(attacker, weapon)
    if self.tags == nil then
        return true  -- 无标签限制，可抵抗所有攻击
    elseif attacker ~= nil then
        -- 检查攻击者或武器是否有匹配的标签
        for i, v in ipairs(self.tags) do
            if attacker:HasTag(v) or (weapon ~= nil and weapon:HasTag(v)) then
                return true
            end
        end
    end
    return false  -- 无法抵抗，护甲不生效
end

function Armor:GetBonusDamage(attacker, weapon)
    -- 获取弱点加成伤害
    if self.weakness == nil or attacker == nil then
        return 0
    end
    local damage = 0
    for k, v in pairs(self.weakness) do
        if (attacker:HasTag(k) or (weapon ~= nil and weapon:HasTag(k))) and v > damage then
            damage = v
        end
    end
    return damage
end

function Armor:TakeDamage(damage_amount)
    -- 耐久消耗（受倍率影响）
    damage_amount = damage_amount * self.conditionlossmultipliers:Get()
    self:SetCondition(self.condition - damage_amount)
    self.inst:PushEvent("armordamaged", damage_amount)
end
```

多个弱点标签同时命中时，`GetBonusDamage` 返回最高值，不求和。弱点是“额外伤害”，不能与 `absorb_percent` 的减伤当成同一层。

### 关键属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `condition` | number | 100 | 当前耐久 |
| `maxcondition` | number | 100 | 最大耐久 |
| `absorb_percent` | number | - | 伤害吸收百分比（0-1） |
| `tags` | table | nil | 可抵抗的攻击类型标签列表 |
| `weakness` | table | nil | 弱点表，key=标签, value=额外伤害 |
| `indestructible` | boolean | false | 是否不可破坏 |
| `conditionlossmultipliers` | SourceModifierList | - | 耐久消耗倍率 |

---

## 实战示例

### 创建普通护甲

```lua
local armor = inst.components.armor
armor:InitCondition(100, 0.6)  -- 100耐久，吸收60%伤害
```

### 创建不可破坏护甲

```lua
local armor = inst.components.armor
armor:InitIndestructible(0.8)  -- 不可破坏，吸收80%伤害
```

### 设置护甲弱点

```lua
local armor = inst.components.armor

-- 对"fire"标签的攻击者/武器额外受到10点伤害
armor:AddWeakness("fire", 10)

-- 移除弱点
armor:RemoveWeakness("fire")
```

### 设置护甲抗性标签

```lua
local armor = inst.components.armor

-- 只抵抗"beaver"和"player"类型的攻击
armor:SetTags({ "beaver", "player" })

-- 此时护甲对其他类型攻击不生效
```

### 耐久消耗倍率

```lua
-- 减少50%耐久消耗
inst.components.armor.conditionlossmultipliers:SetModifier("my_skill", 0.5)

-- 移除倍率
inst.components.armor.conditionlossmultipliers:RemoveModifier("my_skill")
```

后续阅读：

- [equippable.md](equippable.md)
- [inventoryitem.md](../items/inventoryitem.md)
