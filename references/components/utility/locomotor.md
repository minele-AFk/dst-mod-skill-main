# `locomotor`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及移动系统、速度控制、寻路、跳跃时，使用此文件。

官方源码：

- `scripts/components/locomotor.lua`

相关官方预制件示例：

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/beefalo.lua`

高频方法：

- `WalkForward(direct)`
- `RunForward(direct)`
- `WalkInDirection(direction, should_run)`
- `RunInDirection(direction, throttle)`
- `GoToPoint(pt, bufferedaction, run, overridedest)`
- `GoToEntity(target, bufferedaction, run)`
- `PushAction(bufferedaction, run, try_instant)`
- `StopMoving()`
- `SetExternalSpeedMultiplier(source, key, m)`
- `RemoveExternalSpeedMultiplier(source, key)`
- `GetWalkSpeed()`
- `GetRunSpeed()`
常见组件搭配：

- `locomotor` + `combat`
- `locomotor` + `follower`
- `locomotor` + `rideable`

常见陷阱：

- `GoToPoint()` 和 `GoToEntity()` 可能不会立即开始移动。
- 速度倍率需要成对使用 `SetExternalSpeedMultiplier()` 和 `RemoveExternalSpeedMultiplier()`。
- 客户端预测移动需要特殊处理。

---

## 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `walkspeed` | number | 步行速度 |
| `runspeed` | number | 跑步速度 |
| `slowmultiplier` | number | 慢速倍率 |
| `fastmultiplier` | number | 快速倍率 |
| `externalspeedmultiplier` | number | 外部速度倍率 |

---

## 移动控制

### 基础移动

```lua
inst.components.locomotor:WalkForward(inst:GetForwardVector())
inst.components.locomotor:RunForward(inst:GetForwardVector())
```

### 方向移动

```lua
local dir = Vector3(1, 0, 0)
inst.components.locomotor:WalkInDirection(dir)
inst.components.locomotor:RunInDirection(dir, 1)
```

### 目标移动

```lua
local target_pos = Vector3(10, 0, 10)
inst.components.locomotor:GoToPoint(target_pos, nil, true)

local target_entity = FindEntity(inst, 10, function(ent)
    return ent:HasTag("player")
end)
if target_entity then
    inst.components.locomotor:GoToEntity(target_entity, nil, true)
end
```

---

## 速度控制

### 设置速度倍率

```lua
inst.components.locomotor:SetExternalSpeedMultiplier(inst, "slow_effect", 0.5)
```

移除速度倍率：

```lua
inst.components.locomotor:RemoveExternalSpeedMultiplier(inst, "slow_effect")
```

### 临时地面速度倍率

```lua
inst.components.locomotor:PushTempGroundSpeedMultiplier(0.8)
```

### 设置步行/跑步速度

```lua
inst.components.locomotor.walkspeed = 5
inst.components.locomotor.runspeed = 8
```

---

## 路径控制

### 停止移动

```lua
inst.components.locomotor:StopMoving()
```

### 取消路径

```lua
inst.components.locomotor:ResetPath()
```

### 设置到达回调

```lua
inst.components.locomotor:SetReachDestinationCallback(function(inst)
    print("到达目的地")
end)
```

---

## 特殊移动

### 跳跃

```lua
inst.components.locomotor:StartHopping(x, z, target_platform)
```

### 平台跳跃

```lua
inst.components.locomotor:SetAllowPlatformHopping(true)
```

### 地面速度倍率

```lua
inst.components.locomotor:EnableGroundSpeedMultiplier(true)
inst.components.locomotor:SetFasterOnGroundTile("grass", true)
```

---

## 实战示例

### 示例1：创建可移动的生物

```lua
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddPhysics()
    inst.entity:AddNetwork()
    
    inst.Physics:SetSphere(1)
    inst.Physics:CollidesWith(COLLISION.WORLD)
    
    inst:AddComponent("locomotor")
    inst.components.locomotor.walkspeed = 3
    inst.components.locomotor.runspeed = 6
    
    return inst
end
```

### 示例2：添加减速效果

```lua
inst.components.locomotor:SetExternalSpeedMultiplier(inst, "freeze", 0.3)
inst:DoTaskInTime(5, function()
    inst.components.locomotor:RemoveExternalSpeedMultiplier(inst, "freeze")
end)
```

### 示例3：向玩家移动

```lua
local player = FindClosestPlayerToInst(inst, 20)
if player then
    inst.components.locomotor:GoToEntity(player, nil, false)
end
```

---

## 注意事项

1. **服务端权威**：移动控制应该在服务端执行
2. **预测移动**：客户端需要处理预测移动以避免延迟感
3. **碰撞检测**：需要设置物理碰撞才能正常移动
4. **速度叠加**：多个外部速度倍率会相乘叠加