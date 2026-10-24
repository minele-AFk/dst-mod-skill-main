# `Light` 系统组件

> 适用版本：API 10+
> 最后更新：2026-07-12

当任务涉及光照系统、发光效果、光源控制时，使用此组件。

原生引擎对象：当前 scripts.zip 不含对应 Lua 实现。以 Entity:Add 对象的创建方式和同类原版 Prefab 调用点核对；下方接口不是一份可 require 的组件源码。

高频方法：

- `Enable(enabled)`
- `IsEnabled()`
- `SetColour(r, g, b)`
- `GetColour()`
- `SetRadius(radius)`
- `GetRadius()`
- `SetIntensity(intensity)`
- `GetIntensity()`
- `SetFalloff(falloff)`
- `GetFalloff()`
- `EnableClientModulation(enabled)`

常见搭配：

- `Light` + `Entity`（发光实体）
- `Light` + `AnimState`（发光动画）
- `Light` + `Player`（玩家光源）

常见陷阱：

- 渲染、网络可见状态和玩法对光的查询分别核对，不以专服无画面推导 Light 没有业务影响。
- 光源半径过大可能影响性能。

---

## 获取Light

```lua
local light = inst.Light
```

创建实体时：

```lua
inst.entity:AddLight()
local light = inst.Light
```

---

## 基础控制

### 启用光源

```lua
light:Enable(true)
```

### 禁用光源

```lua
light:Enable(false)
```

### 检查光源是否启用

```lua
if light:IsEnabled() then
    -- 光源已启用
end
```

---

## 设置颜色

### 设置颜色

```lua
light:SetColour(1, 0, 0)
```

参数：r, g, b（0-1）

### 获取颜色

```lua
local r, g, b = light:GetColour()
```

---

## 设置半径

### 设置半径

```lua
light:SetRadius(3)
```

### 获取半径

```lua
local radius = light:GetRadius()
```

### 获取计算后的半径

```lua
local calc_radius = light:GetCalculatedRadius()
```

---

## 设置强度

### 设置强度

```lua
light:SetIntensity(0.5)
```

参数：0-1之间的强度值

### 获取强度

```lua
local intensity = light:GetIntensity()
```

---

## 设置衰减

### 设置衰减

```lua
light:SetFalloff(0.9)
```

参数：0-1之间的衰减值，越大衰减越快

### 获取衰减

```lua
local falloff = light:GetFalloff()
```

---

## 客户端调制

### 启用客户端调制

```lua
light:EnableClientModulation(true)
```

---

## 实战示例

### 示例1：创建发光实体

```lua
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddLight()
    inst.entity:AddNetwork()
    
    inst.Light:SetColour(1, 0.8, 0)
    inst.Light:SetRadius(2)
    inst.Light:SetIntensity(0.5)
    inst.Light:SetFalloff(0.9)
    inst.Light:Enable(true)
    
    return inst
end
```

### 示例2：动态光源

```lua
function inst:SetLightIntensity(intensity)
    inst.Light:SetIntensity(intensity)
    inst.Light:Enable(intensity > 0)
end

inst:SetLightIntensity(0.3)
```

---

## 注意事项

1. **客户端效果**：光照效果只在客户端可见
2. **性能影响**：光源半径过大或数量过多会影响性能
3. **颜色设置**：颜色值范围是0-1，不是0-255