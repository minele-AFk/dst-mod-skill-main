# VFX粒子特效实战指南

基于饥荒联机版官方源码和示例代码的粒子特效实现指南。

---

## 一、VFXEffect系统基础

### 1.1 核心概念

VFXEffect是饥荒联机版的粒子系统，包含以下核心组件：

| 组件 | 说明 |
|------|------|
| Emitter（发射器） | 管理粒子的产生和生命周期 |
| Texture（纹理） | 粒子显示的图像 |
| Shader（着色器） | 控制粒子渲染方式 |
| Envelope（包络） | 控制粒子在生命周期内的属性变化 |
| BlendMode（混合模式） | 控制粒子颜色混合方式 |

### 1.2 创建流程

```lua
-- 1. 创建实体
local inst = CreateEntity()
inst.entity:AddTransform()
inst.entity:AddNetwork()
inst:AddTag("FX")
inst.entity:SetPristine()
inst.persists = false
if TheNet:IsDedicated() then
    return inst -- 结构片段置于 Prefab fn 内，专服不创建本地粒子。
end

-- 2. 添加VFXEffect组件
local effect = inst.entity:AddVFXEffect()
effect:InitEmitters(1)  -- 初始化1个发射器

-- 3. 设置渲染资源
effect:SetRenderResources(0, TEXTURE, SHADER)

-- 4. 设置包络（颜色、缩放）
effect:SetColourEnvelope(0, COLOUR_ENVELOPE_NAME)
effect:SetScaleEnvelope(0, SCALE_ENVELOPE_NAME)

-- 5. 设置混合模式和其他属性
effect:SetBlendMode(0, BLENDMODE.Additive)
effect:EnableBloomPass(0, true)

-- 6. 添加发射器更新函数
EmitterManager:AddEmitter(inst, nil, emit_fn)
```

---

## 二、包络系统

### 2.1 颜色包络

控制粒子在生命周期内的颜色变化：

```lua
local COLOUR_ENVELOPE_NAME = "my_colour_envelope"

local function InitColourEnvelope()
    local envs = {}
    local t = 0
    local step = 0.15
    
    while t + step + 0.01 < 1 do
        -- 时间点t的颜色（RGBA，0-1）
        table.insert(envs, { t, { 1, 1, 0.6, 1 } })      -- 黄色不透明
        t = t + step
        table.insert(envs, { t, { 1, 1, 0.6, 0 } })      -- 黄色透明
        t = t + 0.01
    end
    
    -- 生命周期结束时的颜色
    table.insert(envs, { 1, { 1, 1, 0.6, 0 } })
    
    EnvelopeManager:AddColourEnvelope(COLOUR_ENVELOPE_NAME, envs)
end
```

### 2.2 缩放包络

控制粒子在生命周期内的大小变化：

```lua
local SCALE_ENVELOPE_NAME = "my_scale_envelope"

local function InitScaleEnvelope()
    local sparkle_max_scale = 0.4
    
    EnvelopeManager:AddVector2Envelope(
        SCALE_ENVELOPE_NAME,
        {
            { 0, { sparkle_max_scale, sparkle_max_scale } },      -- 开始时大小
            { 1, { sparkle_max_scale * 0.5, sparkle_max_scale * 0.5 } },  -- 结束时大小
        }
    )
end
```

### 2.3 包络使用注意事项

- 包络只需要初始化一次（使用 `InitEnvelope = nil` 防止重复初始化）
- 包络名称必须唯一
- 时间点必须从0到1

---

## 三、球面发射器算法

### 3.1 核心原理

基于球坐标系生成三维空间中的随机方向：

```lua
-- 球坐标系转笛卡尔坐标系
local phi = PI2 * math.random()            -- 方位角 [0, 2π]
local theta = math.acos(UnitRand())        -- 极角 [0, π]
local nor = Vector3(
    math.sin(theta) * math.cos(phi),       -- x
    math.sin(theta) * math.sin(phi),       -- y
    math.cos(theta)                        -- z
)
```

### 3.2 完整实现

```lua
local function CreateExplodeEmitter(minDis, maxDis, dis, isEntad)
    local minDistSq = minDis and minDis * minDis or 0
    local maxDisSq = maxDis * maxDis
    
    return function(cur, newIsEntad)
        if newIsEntad ~= nil then
            isEntad = newIsEntad
        end
        
        if not cur then
            -- 初始化新粒子位置
            local phi = PI2 * math.random()
            local theta = math.acos(UnitRand())
            local nor = Vector3(math.sin(theta)*math.cos(phi), math.sin(theta)*math.sin(phi), math.cos(theta))
            return nor * (isEntad and maxDis or minDis or dis)
        else
            -- 更新现有粒子位置
            if (not isEntad and cur:LengthSq() >= maxDisSq) or 
               (isEntad and cur:LengthSq() <= minDistSq + EPSILON) then
                return nil  -- 粒子到达边界，销毁
            else
                local nor = Vector3(cur:Get()):Normalize()
                local off = nor * dis
                local newPos = cur + (isEntad and -off or off)
                return newPos
            end
        end
    end
end
```

### 3.3 参数说明

| 参数 | 说明 |
|------|------|
| `minDis` | 最小距离（球心附近） |
| `maxDis` | 最大距离（球面） |
| `dis` | 每次移动的步长 |
| `isEntad` | `true`=向内收缩，`false`=向外扩散 |

### 3.4 使用示例

```lua
-- 向外扩散效果（从球心向球面）
local sphere_emitter = CreateExplodeEmitter(2, 4, 0.05)

-- 向内收缩效果（从球面向球心）
local sphere_emitter = CreateExplodeEmitter(2, 4, 0.05, true)
```

---

## 四、粒子发射函数

### 4.1 核心结构

```lua
local MAX_LIFETIME = 1.75
local posList = {}  -- 维护所有活跃粒子的位置

local function emit_sparkle_fn(effect, sphere_emitter)
    -- 1. 更新现有粒子
    local newPosList = {}
    for _, p in ipairs(posList) do
        local newPos = sphere_emitter(p)
        if newPos then
            table.insert(newPosList, newPos)
        end
    end
    
    -- 2. 生成新粒子
    for i = 1, 1 do
        local newPos = sphere_emitter()
        table.insert(newPosList, newPos)
    end
    
    posList = newPosList
    
    -- 3. 发射粒子
    for _, p in ipairs(posList) do
        local nor = Vector3(p:Get()):Normalize()
        local vx, vy, vz = -0.1 * nor.x, -0.1 * nor.y, -0.1 * nor.z
        local lifetime = MAX_LIFETIME * (0.7 + UnitRand() * 0.3)
        local angle = math.random() * 360
        local uv_offset = math.random(0, 3) * 0.25
        local ang_vel = (UnitRand() - 1) * 5
        
        effect:AddRotatingParticleUV(
            0,              -- emitter index
            lifetime,       -- 生命周期
            p.x, p.y, p.z,  -- 位置
            vx, vy, vz,     -- 速度
            angle, ang_vel, -- 角度和角速度
            uv_offset, 0    -- UV偏移
        )
    end
end
```

### 4.2 常用粒子添加方法

| 方法 | 说明 |
|------|------|
| `AddParticleUV` | 添加普通粒子（带UV偏移） |
| `AddRotatingParticleUV` | 添加旋转粒子（带UV偏移） |
| `AddParticle` | 添加普通粒子（无UV偏移） |
| `AddRotatingParticle` | 添加旋转粒子（无UV偏移） |

---

## 五、渲染设置

### 5.1 着色器选择

| 着色器 | 效果 | 适用场景 |
|--------|------|----------|
| `vfx_particle.ksh` | 颜色较淡 | 普通粒子 |
| `vfx_particle_add.ksh` | 加法混合，更亮 | 火焰、魔法、发光效果 |
| `vfx_particle_reveal.ksh` | 高亮方块 | 特殊效果 |

### 5.2 混合模式

| 模式 | 效果 | 注意事项 |
|------|------|----------|
| `BLENDMODE.AlphaBlended` | 标准透明 | 透明区域可能显示黑色 |
| `BLENDMODE.Premultiplied` | 预乘透明 | 透明区域可能显示黑色 |
| `BLENDMODE.Additive` | 加法混合 | 适合发光效果，不会显示黑色 |

### 5.3 完整渲染设置示例

```lua
local effect = inst.entity:AddVFXEffect()
effect:InitEmitters(1)

-- 设置渲染资源
effect:SetRenderResources(0, "fx/sparkle.tex", "shaders/vfx_particle_add.ksh")

-- 设置UV帧大小（从纹理中选择粒子图像）
effect:SetUVFrameSize(0, 0.25, 1)

-- 设置最大粒子数和生命周期
effect:SetMaxNumParticles(0, 4800)
effect:SetMaxLifetime(0, 1.75)

-- 设置包络
effect:SetColourEnvelope(0, COLOUR_ENVELOPE_NAME)
effect:SetScaleEnvelope(0, SCALE_ENVELOPE_NAME)

-- 设置混合模式
effect:SetBlendMode(0, BLENDMODE.Additive)

-- 启用光晕
effect:EnableBloomPass(0, true)

-- 设置渲染顺序
effect:SetSortOrder(0, 0)
effect:SetSortOffset(0, 2)
```

---

## 六、完整实战示例

### 6.1 创建扩散/收缩粒子特效

```lua
local SPARKLE_TEXTURE = "fx/sparkle.tex"
local ADD_SHADER = "shaders/vfx_particle_add.ksh"

local COLOUR_ENVELOPE_NAME = "my_colour_envelope"
local SCALE_ENVELOPE_NAME = "my_scale_envelope"

local assets = {
    Asset("IMAGE", SPARKLE_TEXTURE),
    Asset("SHADER", ADD_SHADER),
}

local function CreateExplodeEmitter(minDis, maxDis, dis, isEntad)
    local minDistSq = minDis and minDis * minDis or 0
    local maxDisSq = maxDis * maxDis
    
    return function(cur, newIsEntad)
        if newIsEntad ~= nil then
            isEntad = newIsEntad
        end
        
        if not cur then
            local phi = PI2 * math.random()
            local theta = math.acos(UnitRand())
            local nor = Vector3(math.sin(theta)*math.cos(phi), math.sin(theta)*math.sin(phi), math.cos(theta))
            return nor * (isEntad and maxDis or minDis or dis)
        else
            if (not isEntad and cur:LengthSq() >= maxDisSq) or 
               (isEntad and cur:LengthSq() <= minDistSq + EPSILON) then
                return nil
            else
                local nor = Vector3(cur:Get()):Normalize()
                local off = nor * dis
                local newPos = cur + (isEntad and -off or off)
                return newPos
            end
        end
    end
end

local function InitEnvelope()
    local envs = {}
    local t = 0
    local step = 0.15
    while t + step + 0.01 < 1 do
        table.insert(envs, { t, { 1, 1, 0.6, 1 } })
        t = t + step
        table.insert(envs, { t, { 1, 1, 0.6, 0 } })
        t = t + 0.01
    end
    table.insert(envs, { 1, { 1, 1, 0.6, 0 } })
    
    EnvelopeManager:AddColourEnvelope(COLOUR_ENVELOPE_NAME, envs)
    
    local max_scale = 0.4
    EnvelopeManager:AddVector2Envelope(SCALE_ENVELOPE_NAME, {
        { 0, { max_scale, max_scale } },
        { 1, { max_scale * 0.5, max_scale * 0.5 } },
    })
    
    InitEnvelope = nil
end

local MAX_LIFETIME = 1.75
local posList = {}

local function emit_sparkle_fn(effect, sphere_emitter)
    local newPosList = {}
    for _, p in ipairs(posList) do
        local newPos = sphere_emitter(p)
        if newPos then
            table.insert(newPosList, newPos)
        end
    end
    
    for i = 1, 1 do
        local newPos = sphere_emitter()
        table.insert(newPosList, newPos)
    end
    
    posList = newPosList
    
    for _, p in ipairs(posList) do
        local nor = Vector3(p:Get()):Normalize()
        local vx, vy, vz = -0.1 * nor.x, -0.1 * nor.y, -0.1 * nor.z
        local lifetime = MAX_LIFETIME * (0.7 + UnitRand() * 0.3)
        local angle = math.random() * 360
        local uv_offset = math.random(0, 3) * 0.25
        local ang_vel = (UnitRand() - 1) * 5
        
        effect:AddRotatingParticleUV(0, lifetime, p.x, p.y, p.z, vx, vy, vz, angle, ang_vel, uv_offset, 0)
    end
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddNetwork()
    inst:AddTag("FX")
    inst.entity:SetPristine()
    inst.persists = false
    
    if TheNet:IsDedicated() then
        return inst
    elseif InitEnvelope ~= nil then
        InitEnvelope()
    end
    
    local effect = inst.entity:AddVFXEffect()
    effect:InitEmitters(1)
    
    effect:SetRenderResources(0, resolvefilepath(SPARKLE_TEXTURE), resolvefilepath(ADD_SHADER))
    effect:SetUVFrameSize(0, 0.25, 1)
    effect:SetMaxNumParticles(0, 4800)
    effect:SetMaxLifetime(0, 1.75)
    effect:SetColourEnvelope(0, COLOUR_ENVELOPE_NAME)
    effect:SetScaleEnvelope(0, SCALE_ENVELOPE_NAME)
    effect:SetBlendMode(0, BLENDMODE.Additive)
    effect:EnableBloomPass(0, true)
    effect:SetSortOrder(0, 0)
    effect:SetSortOffset(0, 2)
    
    -- 向外扩散效果
    local sphere_emitter = CreateExplodeEmitter(2, 4, 0.05)
    
    EmitterManager:AddEmitter(inst, nil, function()
        emit_sparkle_fn(effect, sphere_emitter)
    end)
    
    return inst
end

return Prefab("my_sphere_fx", fn, assets)
```

### 6.2 使用方式

```lua
-- 创建特效
local fx = SpawnPrefab("my_sphere_fx")
fx.Transform:SetPosition(x, y, z)

-- 延迟移除
fx:DoTaskInTime(5, function(inst)
    inst:Remove()
end)
```

---

## 七、常见问题

### 7.1 粒子看不见

- 检查UV帧大小是否正确（`SetUVFrameSize`）
- 检查包络是否正确初始化
- 检查渲染顺序是否在其他物体后面

### 7.2 粒子显示为黑色方块

- 按实际纹理、预乘 alpha 与 shader 家族核对 blend；Additive 不是修复所有黑块的通用开关。
- 确保纹理、UV、颜色包络和透明约定一致。

### 7.3 性能问题

- 限制最大粒子数（`SetMaxNumParticles`）
- 减少每帧发射的粒子数量
- 使用较低分辨率的纹理

### 7.4 服务器崩溃

- 确保在专用服务器上跳过粒子创建（`TheNet:IsDedicated()`）
- 包络名称必须唯一

---

## 八、参考源码

| 文件 | 内容 |
|------|------|
| `scripts/vfx.lua` | VFXEffect系统核心实现 |
| `scripts/envelopemanager.lua` | 包络管理器 |
| `scripts/entityvfxeffect.lua` | 实体VFX组件 |
| `scripts/prefabs/fireflies.lua` | 萤火虫粒子特效 |
| `scripts/prefabs/lightning.lua` | 闪电粒子特效 |

## 本例的使用边界

发射数量、半径、纹理、最大粒子数和寿命是示例设计，不是原版通用预算；完整例仍依赖实际资源、Envelope/EmitterManager 和当前原生调用合同。创建失败先检查 fx 非 nil；资源与客户端真实画面另验收，不以 Lua 解析代替。
