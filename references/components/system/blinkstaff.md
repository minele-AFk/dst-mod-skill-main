# blinkstaff（瞬移杖组件）

## 概述

`blinkstaff` 组件用于实现瞬移效果，常见于瞬移杖等物品。该组件提供了完整的瞬移功能，包括特效、音效和回调机制。

---

## 一、属性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `onblinkfn` | function | nil | 瞬移完成后的回调函数 |
| `blinktask` | Task | nil | 瞬移任务对象 |
| `frontfx` | string | nil | 瞬移前特效prefab名称 |
| `backfx` | string | nil | 瞬移后特效prefab名称 |
| `presound` | string | nil | 瞬移前音效名称 |
| `postsound` | string | nil | 瞬移后音效名称 |

---

## 二、方法

### 2.1 SpawnEffect(inst)

生成瞬移特效。

**参数：**
- `inst` (Entity) - 实体对象

**示例：**
```lua
function BlinkStaff:Blink(pt, caster)
    self:SpawnEffect(self.inst)
    -- 执行瞬移逻辑
end
```

### 2.2 ResetSoundFX()

重置音效设置。

**示例：**
```lua
function BlinkStaff:OnEquip()
    self:ResetSoundFX()
    self:SetSoundFX("dontstarve/common/staff/blink", "dontstarve/common/staff/blinkback")
end
```

### 2.3 SetFX(front, back)

设置瞬移前后的特效。

**参数：**
- `front` (string) - 瞬移前特效prefab名称
- `back` (string) - 瞬移后特效prefab名称

**示例：**
```lua
self.inst.components.blinkstaff:SetFX("blink_front", "blink_back")
```

### 2.4 SetSoundFX(presound, postsound)

设置瞬移前后的音效。

**参数：**
- `presound` (string) - 瞬移前音效名称
- `postsound` (string) - 瞬移后音效名称

**示例：**
```lua
self.inst.components.blinkstaff:SetSoundFX(
    "dontstarve/common/staff/blink",
    "dontstarve/common/staff/blinkback"
)
```

### 2.5 Blink(pt, caster)

执行瞬移操作。

**参数：**
- `pt` (Vector3) - 目标位置坐标
- `caster` (Entity) - 施法者实体

**返回值：**
- (boolean) - 是否成功瞬移

**示例：**
```lua
function TeleportWand:CastSpell(pt)
    if self.inst.components.blinkstaff then
        return self.inst.components.blinkstaff:Blink(pt, self.inst.owner)
    end
    return false
end
```

---

## 三、使用示例

### 3.1 创建瞬移杖

```lua
local assets = {
    Asset("ANIM", "anim/swap_blinkstaff.zip"),
}

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    MakeInventoryPhysics(inst)

    inst.AnimState:SetBank("blinkstaff")
    inst.AnimState:SetBuild("swap_blinkstaff")
    inst.AnimState:PlayAnimation("idle")

    inst:AddTag("blinkstaff")
    inst:AddTag("nopunch")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/blinkstaff.xml"

    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(function(inst, owner)
        owner.AnimState:OverrideSymbol("swap_object", "swap_blinkstaff", "swap_blinkstaff")
        owner.AnimState:Show("ARM_carry")
        owner.AnimState:Hide("ARM_normal")
    end)
    inst.components.equippable:SetOnUnequip(function(inst, owner)
        owner.AnimState:Hide("ARM_carry")
        owner.AnimState:Show("ARM_normal")
    end)

    inst:AddComponent("blinkstaff")
    inst.components.blinkstaff:SetFX("blink_front", "blink_back")
    inst.components.blinkstaff:SetSoundFX(
        "dontstarve/common/staff/blink",
        "dontstarve/common/staff/blinkback"
    )

    inst:AddComponent("inspectable")

    return inst
end

return Prefab("blinkstaff", fn, assets)
```

### 3.2 使用瞬移功能

```lua
local function OnCastSpell(inst, target, pos)
    local caster = inst.components.inventoryitem:GetGrandOwner()
    if caster and inst.components.blinkstaff then
        inst.components.blinkstaff:Blink(pos, caster)
    end
end

inst:AddComponent("spellcaster")
inst.components.spellcaster:SetSpellFn(OnCastSpell)
inst.components.spellcaster.canuseontargets = false
inst.components.spellcaster.canusefrominventory = true
```

---

## 四、注意事项

1. **网络同步**：瞬移操作需要在服务端执行，客户端会自动同步位置
2. **特效管理**：需要确保特效prefab已正确定义和注册
3. **音效加载**：音效名称需要与游戏音效系统中的名称一致
4. **回调时机**：`onblinkfn` 在 `Blink` 验证成功、隐藏/隐藏阴影/无敌状态已设置、延迟任务创建后立即调用；真正传送到目标点由约 0.25 秒后的任务执行。需要“落地后”逻辑时使用项目自己的状态回调或 SG `onstopblinking`，不能把这个回调名当作完成通知。
5. **冷却处理**：建议配合 `cooldown` 组件使用，防止瞬移过于频繁
6. **位置验证**：`Blink` 已检查 `IsTeleportingPermittedFromPointToPoint`、目标点可通行和 `IsGroundTargetBlocked`；瞬移许可还包含 WagPunk 竞技场屏障与虚拟房间集合跨区规则。地图可见性使用 `IsVisibleRespectingVRSFromPointToPoint`，传送连接点另有 `IsTeleportLinkingPermittedFromPoint`；三者的结果不能互相替代。自定义传送不要只查可通行地皮。
7. **无 SG 的施法者**：当前 `Blink` 会在延迟期间隐藏施法者、关闭动态阴影并把生命设为无敌；没有 SG 时，任务结束后负责恢复。自定义替换或取消 `blinktask` 时必须自己保证这些状态被恢复。
8. **`DoGemShine` 不是落地通知**：延迟任务恢复施法者后，会先检查物品是否有 `DoGemShine` 并调用它，然后才再次检查目标点并执行 `Physics:Teleport`。目标延迟期间失效或最终检查失败时，`DoGemShine` 仍可能已经执行。它适合表现扩展，例如宝石发光；需要确认“确实传送成功”时，应另设成功回调或在受控业务路径中判断，不能只凭这个回调推断位移已经发生。
