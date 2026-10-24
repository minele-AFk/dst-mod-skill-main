# worldmigrator（世界迁移器组件）

## 概述

`worldmigrator` 组件用于跨碎片传送，常见于传送门、虫洞、世界传送器等需要在不同碎片之间移动玩家或实体的功能。

---

## 一、属性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `id` | string | nil | 传送门唯一标识 |
| `auto` | boolean | false | 是否自动迁移 |
| `enabled` | boolean | true | 是否启用 |
| `linkedWorld` | number | nil | 链接的目标世界ID |
| `receivedPortal` | boolean | false | 是否已接收传送请求 |

---

## 二、方法

### 2.1 SetDestinationWorld(world, permanent)

设置目标世界。

**参数：**
- `world` (number) - 目标世界ID
- `permanent` (boolean) - 是否永久链接

**示例：**
```lua
function SetDestination(inst, worldid)
    if inst.components.worldmigrator then
        inst.components.worldmigrator:SetDestinationWorld(worldid, false)
    end
end
```

### 2.2 Activate(doer)

激活传送。

**参数：**
- `doer` (Entity) - 触发传送的实体（通常是玩家）

**示例：**
```lua
function UseTeleport(inst, doer)
    if inst.components.worldmigrator and inst.components.worldmigrator:IsActive() then
        inst.components.worldmigrator:Activate(doer)
    end
end
```

### 2.3 IsLinked()

检查是否已链接到目标世界。

**返回值：**
- (boolean) - 是否已链接

**示例：**
```lua
function CheckLink(inst)
    if inst.components.worldmigrator and inst.components.worldmigrator:IsLinked() then
        return true
    end
    return false
end
```

### 2.4 IsActive()

检查传送门是否激活。

**返回值：**
- (boolean) - 是否激活

**示例：**
```lua
function CanUse(inst)
    return inst.components.worldmigrator and inst.components.worldmigrator:IsActive()
end
```

### 2.5 IsBound()

检查传送门是否已绑定。

**返回值：**
- (boolean) - 是否已绑定

**示例：**
```lua
function CheckBound(inst)
    return inst.components.worldmigrator and inst.components.worldmigrator:IsBound()
end
```

### 2.6 IsFull()

检查目标世界是否已满。

**返回值：**
- (boolean) - 是否已满

**示例：**
```lua
function CanMigrate(inst, doer)
    if inst.components.worldmigrator:IsFull() then
        doer.components.talker:Say("目标世界已满！")
        return false
    end
    return true
end
```

### 2.7 IsAvailableForLinking()

检查是否可用于链接。

**返回值：**
- (boolean) - 是否可链接

**示例：**
```lua
function FindLinkablePortal(portals)
    for _, portal in ipairs(portals) do
        if portal.components.worldmigrator:IsAvailableForLinking() then
            return portal
        end
    end
    return nil
end
```

---

## 三、使用示例

### 3.1 创建虫洞传送门

```lua
local assets = {
    Asset("ANIM", "anim/wormhole.zip"),
}

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    inst.AnimState:SetBank("wormhole")
    inst.AnimState:SetBuild("wormhole")
    inst.AnimState:PlayAnimation("idle")

    inst:AddTag("wormhole")
    inst:AddTag("structure")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("worldmigrator")
    inst.components.worldmigrator.id = "wormhole_" .. tostring(math.random())
    inst.components.worldmigrator.auto = false

    inst:AddComponent("inspectable")

    inst:AddComponent("workable")
    inst.components.workable:SetWorkAction(ACTIONS.HAMMER)
    inst.components.workable:SetWorkLeft(3)
    inst.components.workable:SetOnWorkCallback(function(inst, worker, workleft)
        inst.AnimState:PlayAnimation("hit")
        inst.AnimState:PushAnimation("idle")
    end)
    inst.components.workable:SetOnFinishCallback(function(inst, worker)
        inst:Remove()
    end)

    return inst
end

return Prefab("wormhole", fn, assets)
```

### 3.2 跨碎片传送玩家

```lua
function CrossShardTeleport(player, target_worldid)
    if not player.components.worldmigrator then
        player:AddComponent("worldmigrator")
    end

    if Shard_IsWorldAvailable(target_worldid) then
        player.components.worldmigrator:SetDestinationWorld(target_worldid, false)
        player.components.worldmigrator:Activate(player)
        return true
    else
        return false
    end
end
```

---

## 四、虫洞配对

虫洞通常需要成对出现，互相链接：

```lua
function LinkWormholes(portal1, portal2)
    if portal1.components.worldmigrator and portal2.components.worldmigrator then
        portal1.components.worldmigrator:SetDestinationWorld(portal2:GetWorldID(), true)
        portal2.components.worldmigrator:SetDestinationWorld(portal1:GetWorldID(), true)
    end
end
```

---

## 五、与其他组件配合

### 5.1 与 recallmark 配合实现跨碎片召回

```lua
function RecallToMark(caster)
    if caster.components.recallmark and caster.components.recallmark:IsMarked() then
        local pos = caster.components.recallmark:GetMarkedPosition()
        
        if caster.components.recallmark:IsMarkedForSameShard() then
            caster.Physics:Teleport(pos.x, pos.y, pos.z)
        else
            CrossShardTeleport(caster, pos.worldid)
        end
    end
end
```

### 5.2 与 blinkstaff 配合实现远距离瞬移

```lua
function LongDistanceBlink(inst, target_pos)
    local caster = inst.components.inventoryitem:GetGrandOwner()
    
    local dist = caster:GetDistanceSqToPoint(target_pos)
    if dist < 100 then
        inst.components.blinkstaff:Blink(target_pos, caster)
    else
        if caster.components.recallmark then
            local x, y, z = caster.Transform:GetWorldPosition()
            caster.components.recallmark:MarkPosition(x, y, z, TheShard:GetShardId())
        end
        inst.components.blinkstaff:Blink(target_pos, caster)
    end
end
```

---

## 六、注意事项

1. **世界ID**：使用 `TheShard:GetShardId()` 获取当前碎片ID
2. **可用性检查**：使用 `Shard_IsWorldAvailable()` 检查目标世界是否可用
3. **世界已满**：使用 `IsFull()` 检查目标世界是否已满
4. **网络同步**：跨碎片传送需要正确的网络同步
5. **传送安全**：确保传送目标位置是安全的（没有障碍物）
6. **实体限制**：不是所有实体都能跨碎片传送，玩家通常可以
