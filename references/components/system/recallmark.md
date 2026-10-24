# recallmark（召回标记组件）

## 概述

`recallmark` 组件用于记录玩家的位置，以便后续召回传送。常见于传送法杖、传送门等需要返回特定位置的功能。

---

## 一、属性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `recall_x` | number | nil | 标记位置X坐标 |
| `recall_y` | number | nil | 标记位置Y坐标 |
| `recall_z` | number | nil | 标记位置Z坐标 |
| `recall_worldid` | number | nil | 标记所在世界ID（用于跨碎片传送） |

---

## 二、方法

### 2.1 MarkPosition(x, y, z, worldid)

标记一个位置供后续召回。

**参数：**
- `x` (number) - X坐标
- `y` (number) - Y坐标
- `z` (number) - Z坐标
- `worldid` (number, 可选) - 世界ID

**示例：**
```lua
function RecallStaff:CastSpell(pt)
    local caster = self.inst.components.inventoryitem:GetGrandOwner()
    if caster and caster.components.recallmark then
        local x, y, z = caster.Transform:GetWorldPosition()
        caster.components.recallmark:MarkPosition(x, y, z, TheShard:GetShardId())
    end
end
```

### 2.2 GetMarkedPosition()

获取已标记的位置。

**返回值：**
- (table) - 包含 `x`, `y`, `z`, `worldid` 的位置表

**示例：**
```lua
function ReturnStaff:CastSpell()
    local caster = self.inst.components.inventoryitem:GetGrandOwner()
    if caster and caster.components.recallmark then
        local pos = caster.components.recallmark:GetMarkedPosition()
        if pos then
            caster.Physics:Teleport(pos.x, pos.y, pos.z)
        end
    end
end
```

### 2.3 IsMarked()

检查是否有标记位置。

**返回值：**
- (boolean) - 是否有标记

**示例：**
```lua
function CheckRecall(inst)
    if inst.components.recallmark and inst.components.recallmark:IsMarked() then
        return true
    end
    return false
end
```

### 2.4 IsMarkedForSameShard()

检查标记是否在当前碎片。

**返回值：**
- (boolean) - 标记是否在当前碎片

**示例：**
```lua
function CanRecall(inst)
    if inst.components.recallmark and inst.components.recallmark:IsMarked() then
        if inst.components.recallmark:IsMarkedForSameShard() then
            return true, "same_shard"
        else
            return true, "cross_shard"
        end
    end
    return false
end
```

### 2.5 Copy(rhs)

复制另一个实体的标记位置。

**参数：**
- `rhs` (Entity) - 源实体

**示例：**
```lua
function TransferMark(from_inst, to_inst)
    if from_inst.components.recallmark and to_inst.components.recallmark then
        to_inst.components.recallmark:Copy(from_inst.components.recallmark)
    end
end
```

---

## 三、使用示例

### 3.1 在玩家实体上添加召回标记

```lua
AddPrefabPostInit("player", function(inst)
    if not TheWorld.ismastersim then
        return
    end
    inst:AddComponent("recallmark")
end)
```

### 3.2 创建召回法杖

```lua
local assets = {
    Asset("ANIM", "anim/swap_recallstaff.zip"),
}

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    MakeInventoryPhysics(inst)

    inst.AnimState:SetBank("recallstaff")
    inst.AnimState:SetBuild("swap_recallstaff")
    inst.AnimState:PlayAnimation("idle")

    inst:AddTag("recallstaff")
    inst:AddTag("nopunch")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/recallstaff.xml"

    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(function(inst, owner)
        owner.AnimState:OverrideSymbol("swap_object", "swap_recallstaff", "swap_recallstaff")
        owner.AnimState:Show("ARM_carry")
        owner.AnimState:Hide("ARM_normal")
    end)
    inst.components.equippable:SetOnUnequip(function(inst, owner)
        owner.AnimState:Hide("ARM_carry")
        owner.AnimState:Show("ARM_normal")
    end)

    inst:AddComponent("spellcaster")
    inst.components.spellcaster:SetSpellFn(function(inst, target, pos)
        local caster = inst.components.inventoryitem:GetGrandOwner()
        if caster and caster.components.recallmark then
            if caster.components.recallmark:IsMarked() then
                local marked_pos = caster.components.recallmark:GetMarkedPosition()
                if caster.components.recallmark:IsMarkedForSameShard() then
                    caster.Physics:Teleport(marked_pos.x, marked_pos.y, marked_pos.z)
                else
                    if caster.components.worldmigrator then
                        caster.components.worldmigrator:Activate(marked_pos.worldid)
                    end
                end
            else
                local x, y, z = caster.Transform:GetWorldPosition()
                caster.components.recallmark:MarkPosition(x, y, z, TheShard:GetShardId())
            end
        end
    end)
    inst.components.spellcaster.canuseontargets = false
    inst.components.spellcaster.canusefrominventory = true

    inst:AddComponent("inspectable")

    return inst
end

return Prefab("recallstaff", fn, assets)
```

---

## 四、跨碎片召回

当标记位置在不同碎片时，需要配合 `worldmigrator` 组件使用：

```lua
function CrossShardRecall(caster)
    if caster.components.recallmark and caster.components.recallmark:IsMarked() then
        local pos = caster.components.recallmark:GetMarkedPosition()
        
        if caster.components.recallmark:IsMarkedForSameShard() then
            caster.Physics:Teleport(pos.x, pos.y, pos.z)
        else
            if Shard_IsWorldAvailable(pos.worldid) then
                caster.components.worldmigrator:SetDestinationWorld(pos.worldid, false)
                caster.components.worldmigrator:Activate(caster)
            end
        end
    end
end
```

---

## 五、注意事项

1. **网络同步**：标记位置需要通过网络同步到客户端
2. **碎片感知**：使用 `IsMarkedForSameShard()` 判断是否需要跨碎片传送
3. **世界ID**：正确使用 `TheShard:GetShardId()` 获取当前碎片ID
4. **存档保存**：标记位置需要在存档时保存，加载时恢复
5. **位置验证**：召回前应该验证目标位置是否有效
