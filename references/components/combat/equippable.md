# `equippable`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改装备/卸下钩子、装备槽位、移动速度、精神恢复或装备限制时，使用此文件。

官方源码：

- `scripts/components/equippable.lua`

相关官方预制件示例：

- `scripts/prefabs/backpack.lua`
- `scripts/prefabs/armor_grass.lua`

高频方法：

- `SetOnEquip(fn)`
- `SetOnUnequip(fn)`
- `SetOnPocket(fn)`
- `Equip(owner, from_ground)`
- `Unequip(owner)`
- `GetWalkSpeedMult()`
- `SetPreventUnequipping(shouldprevent)`
- `ShouldPreventUnequipping()`
- `GetDapperness(owner, ignore_wetness)`
- `IsRestricted(target)`
常见组件搭配：

- `equippable` + `inventoryitem`
- `equippable` + `weapon`
- `equippable` + `armor`
- `equippable` + `container`

常见陷阱：

- 装备视觉效果通常还需要 `owner.AnimState:OverrideSymbol(...)`。
- `equippable` 本身不会创建护甲或武器行为。
- 装备限制应该在存档/读档和角色切换的边界情况下测试。

---

## 装备槽位系统

基于源码 `equippable.lua:25-53`：

### 核心属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `isequipped` | boolean | false | 是否已装备 |
| `equipslot` | EQUIPSLOTS | HANDS | 装备槽位 |
| `walkspeedmult` | number | nil | 移动速度倍率 |
| `dapperness` | number | 0 | 精神恢复值 |
| `dapperfn` | function | nil | 自定义精神恢复函数 |
| `insulated` | boolean | false | 是否绝缘（防电击） |
| `restrictedtag` | string | nil | 装备限制标签 |
| `preventunequipping` | boolean | false | 是否阻止卸下 |
| `equippedmoisture` | number | 0 | 装备携带的湿度 |
| `maxequippedmoisture` | number | 0 | 最大携带湿度 |

### 装备槽位常量

```lua
EQUIPSLOTS = {
    HANDS = 1,      -- 双手（武器、工具）
    HEAD = 2,       -- 头部（帽子、头盔）
    BODY = 3,       -- 身体（护甲、衣服）
    FEET = 4,       -- 脚部（鞋子）
    BACK = 5,       -- 背部（背包）
    NECK = 6,       -- 颈部（项链）
    BODYTEMP = 7,   -- 体温槽（暖石等）
    EYES = 8,       -- 眼部（眼镜）
}
```

---

## 移动速度系统

基于源码 `equippable.lua:126-144`：

```lua
function Equippable:GetWalkSpeedMult()
    local speed = self.walkspeedmult or 1.0
    
    local owner = self.inst.components.inventoryitem and self.inst.components.inventoryitem.owner
    
    if owner and self.isequipped then
        -- 活力buff加成（最低速度提升25%）
        if speed < 1 and owner:HasTag("vigorbuff") then
            speed = math.min(1, speed + 0.25)
        end
        
        -- 自定义速度修改函数
        local speedmodifierfn = owner.inventory_EquippableWalkSpeedMultModifier
        if speedmodifierfn ~= nil then
            speed = speedmodifierfn(owner, speed, self.inst)
        end
    end
    
    return speed
end
```

**速度倍率计算：**

- `walkspeedmult = 1.0`：正常速度
- `walkspeedmult = 1.25`：+25% 移动速度
- `walkspeedmult = 0.75`：-25% 移动速度

---

## 精神恢复系统

基于源码 `equippable.lua:196-200`：

```lua
function Equippable:GetDapperness(owner, ignore_wetness)
    local dapperness = self.dapperness
    
    -- 对鱼人翻转精神效果
    if self.flipdapperonmerms and owner and owner:HasTag("merm") then
        dapperness = -dapperness
    end
    
    -- 自定义精神恢复函数
    if self.dapperfn ~= nil then
        dapperness = self.dapperfn(self.inst, owner)
    end
    
    -- 潮湿惩罚
    if not ignore_wetness and owner and owner.components.moisture and owner.components.moisture:GetMoisture() > 0 then
        local wet_penalty = 0.5 + (1 - owner.components.moisture:GetMoisture() / 100) * 0.5
        dapperness = dapperness * wet_penalty
    end
    
    return dapperness
end
```

**精神恢复值说明：**

- `dapperness > 0`：增加精神恢复（如花帽）
- `dapperness = 0`：无效果
- `dapperness < 0`：减少精神恢复（如暗影装备）

角色若只对“暗影物品的负面精神效果”有抗性，应先调用 `equippable:GetDapperness(owner, ignore_wetness)` 取得包含自定义函数和潮湿规则的最终值，再判断 `shadow_item` 且 `dapperness < 0`。当前 Wanda 和 Maxwell 都只在结果为负时缩放；正收益保持原值。旧写法若只按 `shadow_item` 标签缩放，会把正精神收益也错误改变。`ignore_wetness` 应传角色真实使用的能力，不硬编码真假。

---

## 装备限制系统

```lua
function Equippable:IsRestricted(target)
    if not target:HasAnyTag("player", "possessedbody") then
        return false  -- 限制只对玩家生效
    end
    
    -- 绑定物品检查
    local linkeditem = self.inst.components.linkeditem
    if linkeditem and linkeditem:IsEquippableRestrictedToOwner() then
        local owneruserid = linkeditem:GetOwnerUserID()
        if owneruserid and owneruserid ~= target.userid then
            return true  -- 不是物品主人，无法装备
        end
    end
    
    -- 标签限制检查
    return self.restrictedtag ~= nil
        and self.restrictedtag:len() > 0
        and not target:HasTag(self.restrictedtag)
end
```

---

## 实战示例

### 设置装备属性

```lua
local equip = inst.components.equippable

-- 设置装备槽位
equip.equipslot = EQUIPSLOTS.HEAD

-- 设置移动速度加成（+25%）
equip.walkspeedmult = 1.25

-- 设置精神恢复（+5/分钟）
equip.dapperness = TUNING.DAPPERNESS_LARGE

-- 设置绝缘（防电击）
equip.insulated = true

-- 设置装备限制（只有特定角色可以装备）
equip.restrictedtag = "mycharacter"
```

### 装备/卸下回调

```lua
local equip = inst.components.equippable

-- 装备时回调
equip:SetOnEquip(function(inst, owner)
    -- 装备时的效果
    owner.components.sanity:SetMax(owner.components.sanity.max + 20)
    
    -- 视觉效果
    owner.AnimState:OverrideSymbol("swap_body", "my_item", "swap_body")
end)

-- 卸下时回调
equip:SetOnUnequip(function(inst, owner)
    -- 卸下时恢复
    owner.components.sanity:SetMax(owner.components.sanity.max - 20)
    
    -- 恢复视觉
    owner.AnimState:ClearOverrideSymbol("swap_body")
end)
```

### 阻止卸下

```lua
-- 阻止卸下（如任务物品）
inst.components.equippable:SetPreventUnequipping(true)

-- 允许卸下
inst.components.equippable:SetPreventUnequipping(false)
```

### 自定义精神恢复

```lua
local equip = inst.components.equippable

equip.dapperfn = function(inst, owner)
    -- 根据条件返回不同的精神恢复值
    if owner:HasTag("wet") then
        return 0.5  -- 潮湿时效果减半
    end
    return 1
end
```

后续阅读：

- [weapon.md](weapon.md)
- [armor.md](armor.md)
