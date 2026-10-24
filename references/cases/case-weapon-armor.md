# 实战案例：武器和护甲系统

> 适用版本：API 10+
> 最后更新：2026-07-12

当任务涉及创建自定义武器、护甲、帽子时，参考此案例。

---

## 一、创建武器

### 基础武器

创建 `scripts/prefabs/wuqi.lua`：

```lua
local assets = {
    Asset("ANIM", "anim/wuqi.zip"),
    Asset("ANIM", "anim/swap_wuqi.zip"),
    Asset("ATLAS", "images/inventoryimages/wuqi.xml"),
    Asset("IMAGE", "images/inventoryimages/wuqi.tex"),
}

local function onequip(inst, owner)
    owner.AnimState:OverrideSymbol("swap_object", "swap_wuqi", "swap_wuqi")
    owner.AnimState:Show("ARM_carry")
    owner.AnimState:Hide("ARM_normal")
end

local function onunequip(inst, owner)
    owner.AnimState:Hide("ARM_carry")
    owner.AnimState:Show("ARM_normal")
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    
    MakeInventoryPhysics(inst)
    
    inst.AnimState:SetBank("wuqi")
    inst.AnimState:SetBuild("wuqi")
    inst.AnimState:PlayAnimation("idle")
    
    inst:AddTag("sharp")
    inst:AddTag("pointy")
    
    inst.entity:SetPristine()
    
    if not TheWorld.ismastersim then
        return inst
    end
    
    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(34)
    
    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(200)
    inst.components.finiteuses:SetUses(200)
    inst.components.finiteuses:SetOnFinished(inst.Remove)
    
    inst:AddComponent("inspectable")
    
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/wuqi.xml"
    
    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(onequip)
    inst.components.equippable:SetOnUnequip(onunequip)
    
    MakeHauntableLaunch(inst)
    
    return inst
end

return Prefab("wuqi", fn, assets)
```

### 特殊属性武器

```lua
local function onattack(inst, attacker, target)
    if target and target.components.health and not target.components.health:IsDead() then
        SpawnPrefab("lightning").Transform:SetPosition(target:GetPosition():Get())
        target.components.health:DoDelta(-30)
    end
    
    if attacker.components.sanity and attacker.components.sanity:GetPercent() < 1 then
        attacker.components.sanity:DoDelta(1)
    end
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddLight()
    inst.entity:AddNetwork()
    
    MakeInventoryPhysics(inst)
    
    inst.AnimState:SetBank("wuqi")
    inst.AnimState:SetBuild("wuqi")
    inst.AnimState:PlayAnimation("idle")
    inst.AnimState:SetBloomEffectHandle("shaders/anim.ksh")
    
    inst.Light:SetFalloff(0.7)
    inst.Light:SetIntensity(.5)
    inst.Light:SetRadius(4)
    inst.Light:SetColour(255/255, 255/255, 192/255)
    inst.Light:Enable(true)
    
    inst:AddTag("sharp")
    inst:AddTag("pointy")
    
    inst.entity:SetPristine()
    
    if not TheWorld.ismastersim then
        return inst
    end
    
    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(50)
    inst.components.weapon:SetOnAttack(onattack)
    
    inst:AddComponent("tool")
    inst.components.tool:SetAction(ACTIONS.CHOP, 15)
    inst.components.tool:SetAction(ACTIONS.MINE, 3)
    
    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(100)
    inst.components.finiteuses:SetUses(100)
    inst.components.finiteuses:SetConsumption(ACTIONS.CHOP, 1)
    inst.components.finiteuses:SetConsumption(ACTIONS.MINE, 2)
    inst.components.finiteuses:SetOnFinished(inst.Remove)
    
    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/wuqi.xml"
    inst.components.inventoryitem:SetOnDroppedFn(function() inst.Light:Enable(true) end)
    inst.components.inventoryitem:SetOnPutInInventoryFn(function() inst.Light:Enable(true) end)
    
    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(onequip)
    inst.components.equippable:SetOnUnequip(onunequip)
    inst.components.equippable.walkspeedmult = TUNING.CANE_SPEED_MULT
    
    MakeHauntableLaunch(inst)
    
    return inst
end
```

---

## 二、创建护甲

创建 `scripts/prefabs/yifu.lua`：

```lua
local assets = {
    Asset("ANIM", "anim/yifu.zip"),
    Asset("ATLAS", "images/inventoryimages/yifu.xml"),
    Asset("IMAGE", "images/inventoryimages/yifu.tex"),
}

local function OnBlocked(owner, data)
    owner.SoundEmitter:PlaySound("dontstarve/wilson/hit_armour")
end

local function onequip(inst, owner)
    owner.AnimState:OverrideSymbol("swap_body", "yifu", "swap_body")
    inst:ListenForEvent("blocked", OnBlocked, owner)
end

local function onunequip(inst, owner)
    owner.AnimState:ClearOverrideSymbol("swap_body")
    inst:RemoveEventCallback("blocked", OnBlocked, owner)
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    
    MakeInventoryPhysics(inst)
    
    inst.AnimState:SetBank("yifu")
    inst.AnimState:SetBuild("yifu")
    inst.AnimState:PlayAnimation("anim")
    
    inst:AddTag("wood")
    inst.foleysound = "dontstarve/movement/foley/logarmour"
    
    inst.entity:SetPristine()
    
    if not TheWorld.ismastersim then
        return inst
    end
    
    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/yifu.xml"
    
    inst:AddComponent("waterproofer")
    inst.components.waterproofer:SetEffectiveness(TUNING.WATERPROOFNESS_ABSOLUTE)
    
    inst:AddComponent("insulator")
    inst.components.insulator:SetInsulation(240)
    
    inst:AddComponent("fuel")
    inst.components.fuel.fuelvalue = TUNING.LARGE_FUEL
    
    MakeSmallBurnable(inst, TUNING.SMALL_BURNTIME)
    MakeSmallPropagator(inst)
    
    inst:AddComponent("armor")
    inst.components.armor:InitCondition(1500, 0.9)
    inst.components.armor:AddWeakness("beaver", TUNING.BEAVER_WOOD_DAMAGE)
    
    inst:AddComponent("equippable")
    inst.components.equippable.equipslot = EQUIPSLOTS.BODY
    inst.components.equippable:SetOnEquip(onequip)
    inst.components.equippable:SetOnUnequip(onunequip)
    
    MakeHauntableLaunch(inst)
    
    return inst
end

return Prefab("yifu", fn, assets)
```

---

## 三、创建帽子

创建 `scripts/prefabs/maozi.lua`：

```lua
local assets = {
    Asset("ANIM", "anim/maozi.zip"),
    Asset("IMAGE", "images/inventoryimages/maozi.tex"),
    Asset("ATLAS", "images/inventoryimages/maozi.xml"),
}

local function onequiphat(inst, owner)
    owner.AnimState:OverrideSymbol("swap_hat", "maozi", "swap_hat")
    owner.AnimState:Show("HAT")
    owner.AnimState:Show("HAT_HAIR")
    owner.AnimState:Hide("HAIR_NOHAT")
    owner.AnimState:Hide("HAIR")
    
    if owner:HasTag("player") then
        owner.AnimState:Hide("HEAD")
        owner.AnimState:Show("HEAD_HAT")
    end
    
    if inst.components.fueled then
        inst.components.fueled:StartConsuming()
    end
end

local function onunequiphat(inst, owner)
    owner.AnimState:Hide("HAT")
    owner.AnimState:Hide("HAT_HAIR")
    owner.AnimState:Show("HAIR_NOHAT")
    owner.AnimState:Show("HAIR")
    
    if owner:HasTag("player") then
        owner.AnimState:Show("HEAD")
        owner.AnimState:Hide("HEAD_HAT")
    end
    
    if inst.components.fueled then
        inst.components.fueled:StopConsuming()
    end
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    
    MakeInventoryPhysics(inst)
    
    inst.AnimState:SetBank("maozi")
    inst.AnimState:SetBuild("maozi")
    inst.AnimState:PlayAnimation("anim")
    
    inst:AddTag("hat")
    inst:AddTag("hide")
    
    inst.entity:SetPristine()
    
    if not TheWorld.ismastersim then
        return inst
    end
    
    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/maozi.xml"
    
    inst:AddComponent("equippable")
    inst.components.equippable.equipslot = EQUIPSLOTS.HEAD
    inst.components.equippable:SetOnEquip(onequiphat)
    inst.components.equippable:SetOnUnequip(onunequiphat)
    inst.components.equippable.dapperness = TUNING.DAPPERNESS_LARGE
    
    inst:AddComponent("tradable")
    
    MakeHauntableLaunchAndPerish(inst)
    
    return inst
end

return Prefab("common/inventory/maozi", fn, assets)
```

---

## 四、modmain.lua 配置

```lua
PrefabFiles = {
    "yifu",
    "wuqi",
    "maozi",
}

STRINGS.NAMES.YIFU = "护甲"
STRINGS.RECIPE_DESC.YIFU = "大佬做护甲不？"
STRINGS.CHARACTERS.GENERIC.DESCRIBE.YIFU = "这衣服真暖和."

STRINGS.NAMES.MAOZI = "帽子"
STRINGS.RECIPE_DESC.MAOZI = "制作一顶漂亮的帽子"
STRINGS.CHARACTERS.GENERIC.DESCRIBE.MAOZI = "真好看呀"

STRINGS.NAMES.WUQI = "武器"
STRINGS.RECIPE_DESC.WUQI = "大佬来做把武器吧"
STRINGS.CHARACTERS.GENERIC.DESCRIBE.WUQI = "打人老疼了"

AddRecipe("yifu",
    {Ingredient("fish", 2), Ingredient("berries", 3)},
    RECIPETABS.WAR, TECH.SCIENCE_ONE,
    nil, nil, nil, nil, nil,
    "images/inventoryimages/yifu.xml", "yifu.tex")

AddRecipe("maozi",
    {Ingredient("fish", 2), Ingredient("berries", 3)},
    RECIPETABS.DRESS, TECH.SCIENCE_TWO,
    nil, nil, nil, nil, nil,
    "images/inventoryimages/maozi.xml", "maozi.tex")

AddRecipe("wuqi",
    {Ingredient("fish", 2), Ingredient("berries", 3)},
    RECIPETABS.WAR, TECH.SCIENCE_TWO,
    nil, nil, nil, nil, nil,
    "images/inventoryimages/wuqi.xml", "wuqi.tex")
```

---

## 五、武器特殊属性汇总

| 属性 | 组件 | 示例 |
|------|------|------|
| 攻击力 | `weapon` | `SetDamage(34)` |
| 攻击距离 | `weapon` | `SetRange(8, 10)` |
| 攻击特效 | `weapon` | `SetOnAttack(onattack)` |
| 耐久度 | `finiteuses` | `SetMaxUses(200)` |
| 工具功能 | `tool` | `SetAction(ACTIONS.CHOP, 15)` |
| 加速 | `equippable` | `walkspeedmult = TUNING.CANE_SPEED_MULT` |
| 瞬移 | `blinkstaff` | `AddComponent("blinkstaff")` |
| 发光 | `Light` | `SetRadius(4)` |
| 冰杖效果 | `freezable` | `AddColdness(1)` |

---

## 六、高级武器特效

### 6.1 雷电武器

```lua
local function onattack_lightning(inst, attacker, target)
    if target and target.components.health and not target.components.health:IsDead() then
        local pos = target:GetPosition()
        SpawnPrefab("lightning").Transform:SetPosition(pos.x, pos.y, pos.z)
        target.components.health:DoDelta(-30)
    end

    if attacker.components.sanity and attacker.components.sanity:GetPercent() < 1 and not target:HasTag("wall") then
        attacker.components.sanity:DoDelta(1)
    end
end

local function fn_lightning_sword()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddLight()
    inst.entity:AddNetwork()

    MakeInventoryPhysics(inst)

    inst.AnimState:SetBank("lightning_sword")
    inst.AnimState:SetBuild("lightning_sword")
    inst.AnimState:PlayAnimation("idle")
    inst.AnimState:SetBloomEffectHandle("shaders/anim.ksh")

    inst.Light:SetFalloff(0.7)
    inst.Light:SetIntensity(.5)
    inst.Light:SetRadius(4)
    inst.Light:SetColour(255/255, 255/255, 192/255)
    inst.Light:Enable(true)

    inst:AddTag("sharp")
    inst:AddTag("pointy")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(50)
    inst.components.weapon:SetOnAttack(onattack_lightning)

    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(100)
    inst.components.finiteuses:SetUses(100)
    inst.components.finiteuses:SetOnFinished(inst.Remove)

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/lightning_sword.xml"
    inst.components.inventoryitem:SetOnDroppedFn(function() inst.Light:Enable(true) end)
    inst.components.inventoryitem:SetOnPutInInventoryFn(function() inst.Light:Enable(true) end)

    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(onequip)
    inst.components.equippable:SetOnUnequip(onunequip)

    MakeHauntableLaunch(inst)

    return inst
end
```

### 6.2 冰杖武器

```lua
local function onattack_ice(inst, attacker, target)
    if IsDLCEnabled(CAPY_DLC) then
        inst.SoundEmitter:PlaySound("dontstarve_DLC002/common/obsidian_wetsizzles")
    end

    if not target:IsValid() then
        return
    end

    if target.components.sleeper and target.components.sleeper:IsAsleep() then
        target.components.sleeper:WakeUp()
    end

    if target.components.burnable then
        if target.components.burnable:IsBurning() then
            target.components.burnable:Extinguish()
        elseif target.components.burnable:IsSmoldering() then
            target.components.burnable:SmotherSmolder()
        end
    end

    if target.sg ~= nil and not target.sg:HasStateTag("frozen") then
        target:PushEvent("attacked", { attacker = attacker, damage = 0 })
    end

    if target.components.freezable then
        target.components.freezable:AddColdness(1)
        target.components.freezable:SpawnShatterFX()
    end
end

local function fn_ice_staff()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    MakeInventoryPhysics(inst)

    inst.AnimState:SetBank("icestaff")
    inst.AnimState:SetBuild("icestaff")
    inst.AnimState:PlayAnimation("idle")

    inst:AddTag("icestaff")
    inst:AddTag("extinguisher")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(0)
    inst.components.weapon:SetProjectile("ice_projectile")
    inst.components.weapon:SetOnAttack(onattack_ice)

    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(20)
    inst.components.finiteuses:SetUses(20)
    inst.components.finiteuses:SetOnFinished(inst.Remove)

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/icestaff.xml"

    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(onequip)
    inst.components.equippable:SetOnUnequip(onunequip)

    MakeHauntableLaunch(inst)

    return inst
end
```

### 6.3 瞬移杖

瞬移系统的完整实现请参考传送系统案例：[case-teleport-system.md](case-teleport-system.md)

### 6.4 风与航行装备的版本边界

旧段落依赖单机海难 CAPY_DLC/GetWorld/GetPlayer 和不存在的 worldwind:SetOverrideAngle，不能用于当前 DST。船上增益应查当前 boatphysics、mast、boatrotator 及装备拥有者，明确风、动力、旋转与客户端表现分别由谁控制。源组件只管理本分片风，不用虚构角度覆盖 API。

按设计为装备建立私有来源，卸装/移除/船毁时清理；不全局把整个世界风向写成持有者朝向。具体接入查 [海洋专题](../gameplay/dst-ocean-boats-fishing/GUIDE.md)。本案例不承诺已实现顺风装备。

### 6.5 多用工具武器

```lua
local function fn_multi_tool()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    MakeInventoryPhysics(inst)

    inst.AnimState:SetBank("multi_tool")
    inst.AnimState:SetBuild("multi_tool")
    inst.AnimState:PlayAnimation("idle")

    inst:AddTag("sharp")
    inst:AddTag("pointy")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(25)

    inst:AddComponent("tool")
    inst.components.tool:SetAction(ACTIONS.CHOP, 15)
    inst.components.tool:SetAction(ACTIONS.MINE, 3)
    inst.components.tool:SetAction(ACTIONS.HAMMER, 15)
    inst.components.tool:SetAction(ACTIONS.DIG)
    if IsDLCEnabled(CAPY_DLC) then
        inst.components.tool:SetAction(ACTIONS.HACK, 15)
    end

    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(200)
    inst.components.finiteuses:SetUses(200)
    inst.components.finiteuses:SetConsumption(ACTIONS.CHOP, 1)
    inst.components.finiteuses:SetConsumption(ACTIONS.MINE, 2)
    inst.components.finiteuses:SetConsumption(ACTIONS.HAMMER, 3)
    inst.components.finiteuses:SetConsumption(ACTIONS.DIG, 3)
    if inst.components.finiteuses.current < 0 then
        inst.components.finiteuses.current = 0
    end
    inst.components.finiteuses:SetOnFinished(inst.Remove)

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/multi_tool.xml"

    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(onequip)
    inst.components.equippable:SetOnUnequip(onunequip)
    inst.components.equippable.walkspeedmult = TUNING.CANE_SPEED_MULT
    inst.components.equippable.dapperness = TUNING.CRAZINESS_MED / 4

    MakeHauntableLaunch(inst)

    return inst
end
```

## 七、武器特殊属性汇总

| 属性 | 组件 | 示例 |
|------|------|------|
| 攻击力 | `weapon` | `SetDamage(34)` |
| 攻击距离 | `weapon` | `SetRange(8, 10)` |
| 攻击特效 | `weapon` | `SetOnAttack(onattack)` |
| 耐久度 | `finiteuses` | `SetMaxUses(200)` |
| 工具功能 | `tool` | `SetAction(ACTIONS.CHOP, 15)` |
| 加速 | `equippable` | `walkspeedmult = TUNING.CANE_SPEED_MULT` |
| 瞬移 | `blinkstaff` | `AddComponent("blinkstaff")` |
| 发光 | `Light` | `SetRadius(4)` |
| 冰杖效果 | `freezable` | `AddColdness(1)` |
| 雷电效果 | 自定义 | `SpawnPrefab("lightning")` |
| 海难顺风 | 自定义 | `worldwind:SetOverrideAngle()` |
| 精神回复 | `equippable` | `dapperness = TUNING.CRAZINESS_MED` |

## 八、注意事项

1. 武器动画需要两个：地上放置动画和手持动画
2. 护甲需要监听 `blocked` 事件播放音效
3. 帽子需要正确处理头发和头部的显示/隐藏
4. 配方的贴图路径需要正确配置
5. 冰杖效果需要检查 `CAPY_DLC` 是否启用
6. 瞬移杖需要使用 `blinkstaff` 组件
7. 海难专属功能需要检查 `CAPY_DLC` 是否启用
8. 多用工具需要为不同动作设置不同的耐久消耗