# `AnimState` 系统组件

> 适用版本：API 10+
> 最后更新：2026-07-12

当任务涉及动画播放、动画控制、动画状态管理时，使用此组件。

原生引擎对象：当前 scripts.zip 不含对应 Lua 实现。以 Entity:Add 对象的创建方式和同类原版 Prefab 调用点核对；下方接口不是一份可 require 的组件源码。

高频方法：

- `SetBank(name)`
- `SetBuild(buildname)`
- `PlayAnimation(animname, loop)`
- `PushAnimation(animname, loop)`
- `SetBankAndPlayAnimation(bankname, animname)`
- `SetScale(x, y, z)`
- `SetMultColour(r, g, b, a)`
- `SetAddColour(r, g, b, a)`
- `SetHue(hue)`
- `SetSaturation(saturation)`
- `SetBrightness(brightness)`
- `IsCurrentAnimation(animname)`
- `AnimDone()`
- `GetCurrentAnimationLength()`
- `Pause()`
- `Resume()`
- `Hide(layername)`
- `Show(layername)`
- `OverrideSymbol(oldsymbol, newbuild, newsymbol)`
- `ClearOverrideSymbol(symbol)`

常见搭配：

- `AnimState` + `Entity`（实体动画）
- `AnimState` + `StateGraph`（状态机动画）
- `AnimState` + `UIAnim`（UI动画）

常见陷阱：

- `SetBank()` 和 `SetBuild()` 需要在 `PlayAnimation()` 之前调用。
- 动画名由 bank/anim.bin 提供，build 提供符号图像；二者分别核对。
- `PushAnimation()` 会等待当前动画播放完再播放。

---

## 获取AnimState

```lua
local animstate = inst.AnimState
```

创建实体时：

```lua
inst.entity:AddAnimState()
local animstate = inst.AnimState
```

---

## 设置动画

### 设置Bank和Build

```lua
animstate:SetBank("character")
animstate:SetBuild("character")
```

### 播放动画

```lua
animstate:PlayAnimation("idle", true)
```

参数：animname（动画名），loop（是否循环，默认false）

### 推送动画

```lua
animstate:PushAnimation("attack", false)
```

等待当前动画播放完后再播放。

### 快捷设置并播放

```lua
animstate:SetBankAndPlayAnimation("character", "idle")
```

---

## 动画控制

### 暂停动画

```lua
animstate:Pause()
```

### 恢复动画

```lua
animstate:Resume()
```

### 设置播放速度

```lua
animstate:SetDeltaTimeMultiplier(2)
```

参数：速度倍率（1为正常速度）

### 设置动画时间

```lua
animstate:SetTime(0.5)
```

设置从第几秒开始播放。

### 设置动画帧数

```lua
animstate:SetFrame(10)
```

---

## 动画状态查询

### 当前动画是否为指定动画

```lua
if animstate:IsCurrentAnimation("idle") then
    -- 当前播放的是idle动画
end
```

### 动画是否播放完毕

```lua
if animstate:AnimDone() then
    -- 动画播放完毕
end
```

### 获取当前动画长度

```lua
local length = animstate:GetCurrentAnimationLength()
```

返回秒数。

### 获取当前动画帧数

```lua
local frame = animstate:GetCurrentAnimationFrame()
```

---

## 颜色和效果

### 设置叠乘颜色

```lua
animstate:SetMultColour(1, 0, 0, 1)
```

参数：r, g, b, a（0-1）

### 设置叠加颜色

```lua
animstate:SetAddColour(0, 0, 1, 0.5)
```

参数：r, g, b, a（0-1）

### 设置色度

```lua
animstate:SetHue(0.5)
```

参数：0-1之间的色度值

### 设置饱和度

```lua
animstate:SetSaturation(0.8)
```

参数：0-1之间的饱和度值

### 设置亮度

```lua
animstate:SetBrightness(1.5)
```

参数：0-2之间的亮度值（0为亏曝，2为过曝）

---

## 通道控制

### 隐藏通道

```lua
animstate:HideSymbol("arm_l")
```

### 显示通道

```lua
animstate:ShowSymbol("arm_l")
```

### 覆盖通道

```lua
animstate:OverrideSymbol("arm_l", "new_build", "new_arm_l")
```

### 清除覆盖通道

```lua
animstate:ClearOverrideSymbol("arm_l")
```

### 清除所有覆盖通道

```lua
animstate:ClearAllOverrideSymbols()
```

---

## 图层控制

### 隐藏图层

```lua
animstate:Hide("shadow")
```

### 显示图层

```lua
animstate:Show("shadow")
```

---

## 缩放

### 设置缩放

```lua
animstate:SetScale(1.5, 1.5, 1)
```

---

## 实战示例

### 示例1：创建带动画的实体

```lua
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    
    inst.AnimState:SetBank("my_entity")
    inst.AnimState:SetBuild("my_entity")
    inst.AnimState:PlayAnimation("idle", true)
    
    return inst
end
```

### 示例2：根据状态切换动画

```lua
function inst:SetState(state)
    if state == "attack" then
        inst.AnimState:PlayAnimation("attack", false)
        inst.AnimState:PushAnimation("idle", true)
    elseif state == "walk" then
        inst.AnimState:PlayAnimation("walk", true)
    else
        inst.AnimState:PlayAnimation("idle", true)
    end
end
```

---

## 注意事项

1. **Bank和Build**：必须先设置Bank和Build才能播放动画
2. **动画名称**：动画名称必须与build中的定义一致
3. **循环播放**：设置loop为true才能循环播放
4. **颜色叠加**：叠乘颜色会受原图颜色影响，叠加颜色几乎不受原图影响