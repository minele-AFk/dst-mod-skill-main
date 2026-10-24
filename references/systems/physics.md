# `Physics` 系统组件

> 适用版本：API 10+
> 最后更新：2026-07-12

当任务涉及物理系统、碰撞检测、速度控制、传送时，使用此组件。

原生引擎对象：当前 scripts.zip 不含对应 Lua 实现。以 Entity:Add 对象的创建方式和同类原版 Prefab 调用点核对；下方接口不是一份可 require 的组件源码。

高频方法：

- `SetSphere(r)`
- `SetCapsule(rad, height)`
- `SetCylinder(radius, height)`
- `SetTriangleMesh(mesh)`
- `CollidesWith(collision_type)`
- `SetCollides(bool)`
- `SetActive(bool)`
- `IsActive()`
- `SetVel(vx, vy, vz)`
- `GetVelocity()`
- `Teleport(x, y, z)`
- `SetMass(mass)`
- `GetMass()`
- `SetFriction(friction)`
- `SetDamping(damping)`
- `SetRestitution(restitution)`
- `SetCollisionCallback(fn)`

常见搭配：

- `Physics` + `Entity`（物理实体）
- `Physics` + `Locomotor`（移动系统）
- `Physics` + `Combat`（战斗系统）

常见陷阱：

- 物理碰撞需要正确设置碰撞体积。
- 传送需要在服务端执行。

---

## 获取Physics

```lua
local physics = inst.Physics
```

创建实体时：

```lua
inst.entity:AddPhysics()
local physics = inst.Physics
```

---

## 设置碰撞体积

### 设置球体

```lua
physics:SetSphere(1)
```

参数：半径

### 设置胶囊体

```lua
physics:SetCapsule(0.5, 1)
```

参数：半径，高度

### 设置圆柱体

```lua
physics:SetCylinder(1, 2)
```

参数：半径，高度

### 设置三角形网格

```lua
physics:SetTriangleMesh(PLAYER_COLLISION_MESH)
```

---

## 碰撞控制

### 添加碰撞类型

```lua
physics:CollidesWith(COLLISION.WORLD)
physics:CollidesWith(COLLISION.CHARACTERS)
physics:CollidesWith(COLLISION.GIANTS)
```

### 清除碰撞类型

```lua
physics:ClearCollidesWith(COLLISION.WORLD)
```

### 清除所有碰撞

```lua
physics:ClearCollisionMask()
```

### 设置碰撞开关

```lua
physics:SetCollides(true)
```

### 设置碰撞回调

```lua
physics:SetCollisionCallback(function(inst, other)
    print("碰撞了:", other)
end)
```

---

## 物理状态

### 启用物理

```lua
physics:SetActive(true)
```

### 禁用物理

```lua
physics:SetActive(false)
```

### 检查物理是否活跃

```lua
if physics:IsActive() then
    -- 物理系统活跃
end
```

---

## 速度控制

### 设置速度

```lua
physics:SetVel(2, 0, 2)
```

参数：vx, vy, vz

### 获取速度

```lua
local vx, vy, vz = physics:GetVelocity()
```

### 设置电机速度覆盖

```lua
physics:SetMotorVelOverride(3, 0, 3)
```

### 清除电机速度覆盖

```lua
physics:ClearMotorVelOverride()
```

---

## 传送

### 物理传送

```lua
physics:Teleport(10, 0, 10)
```

参数：x, y, z

---

## 物理属性

### 设置质量

```lua
physics:SetMass(100)
```

### 获取质量

```lua
local mass = physics:GetMass()
```

### 设置摩擦

```lua
physics:SetFriction(0.5)
```

### 设置阻尼

```lua
physics:SetDamping(0.1)
```

### 设置弹性

```lua
physics:SetRestitution(0.5)
```

---

## 实战示例

### 示例1：创建有物理碰撞的实体

```lua
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddPhysics()
    inst.entity:AddNetwork()
    
    inst.Physics:SetSphere(1)
    inst.Physics:CollidesWith(COLLISION.WORLD)
    inst.Physics:CollidesWith(COLLISION.CHARACTERS)
    inst.Physics:SetActive(true)
    
    return inst
end
```

### 示例2：设置实体速度

```lua
function inst:Launch(direction, speed)
    local vx = direction.x * speed
    local vz = direction.z * speed
    inst.Physics:SetVel(vx, 0, vz)
end

inst:Launch(Vector3(1, 0, 0), 5)
```

---

## 注意事项

1. **碰撞体积**：必须设置碰撞体积才能产生碰撞
2. **服务端权威**：物理状态和传送应该在服务端执行
3. **性能影响**：复杂的碰撞体积会影响性能