# 角色被动能力：踏水 / 跨洞穴虚空行走

让角色能直接走在**水面上**、跨过**洞穴虚空（无底洞）**，无需坐船也不会溺水。
常见于各类特色角色/飞行/踏水类 mod。

## 原理一句话

不靠地图/水面标签判定，而是**直接切换物理碰撞层**：
- 普通实体碰撞掩码是 `COLLISION.WORLD`（世界边界，包含水面、虚空四周的阻挡墙），所以在水边被挡住。
- 把角色改成只碰撞 **`COLLISION.GROUND`**（地面层），就能跨过水面/虚空屏障，同时仍在实地上正常站立。

官方对照：飞行实体跨屏障正是用 `TheWorld:CanFlyingCrossBarriers() and COLLISION.GROUND or COLLISION.WORLD`（见 `standardcomponents.lua` 多处）。

## 最小实现（核心两行）

```lua
inst.Physics:ClearCollidesWith(COLLISION.WORLD)  -- 不再撞水面/虚空屏障
inst.Physics:CollidesWith(COLLISION.GROUND)      -- 仍和地面碰撞，防止掉穿
```

## 完整模板（含配套处理）

```lua
local function spawnsplash(inst)  -- 视觉水花（可选）
    local theta = (inst.Transform:GetRotation() - 180) * DEGREES
    local offset = Vector3(0, 0, 0) -- 可自行算朝向偏移
    local fx = SpawnPrefab("weregoose_splash")
    local newpt = offset + Vector3(inst.Transform:GetWorldPosition())
    fx.Transform:SetPosition(newpt:Get())
end

-- 状态开关：开=可踏水，关=恢复正常
local function collidesDirty(inst, get)
    if get then
        inst.Physics:ClearCollidesWith(COLLISION.WORLD)
        inst.Physics:CollidesWith(COLLISION.GROUND)
    else
        inst.Physics:CollidesWith(COLLISION.WORLD)
    end
end

local function OnCollide(inst, other)
    -- 走回陆地/悬崖边缘碰触 TheWorld 时，重新断言可踏水状态，防止被卡住
    if other == TheWorld then
        collidesDirty(inst, true)
    end
end

local function ApplyWalkOnWater(inst)
    -- 1. 切碰撞层（关平台跳避免和船登台冲突）
    inst.components.locomotor:SetAllowPlatformHopping(false)
    -- 2. 禁用溺水（站在水面上不按溺水判定）
    if inst.components.drownable then
        inst.components.drownable.enabled = false
        inst.components.drownable.ShouldDrown = function() return false end
    end
    -- 3. 设置碰撞回调兜底
    if inst.Physics then
        collidesDirty(inst, true)
        inst.Physics:SetCollisionCallback(OnCollide)
    end
    -- 4. 视觉水花（可选）
    inst:DoPeriodicTask(0.2, function()
        if inst.components.drownable ~= nil and inst.components.drownable:IsOverWater()
            and inst:HasTag("moving") then
            SpawnPrefab("weregoose_splash").entity:SetParent(inst.entity)
        end
    end)
end

AddPrefabPostInit("noa", function(inst)
    if not TheWorld.ismastersim then return end
    ApplyWalkOnWater(inst)
end)
```

## 各环节说明

| 环节 | 作用 |
| --- | --- |
| `ClearCollidesWith(WORLD)` + `CollidesWith(GROUND)` | 核心：允许跨水面/虚空屏障，仍踩地面 |
| `SetCollisionCallback(OnCollide)` | 回到陆地碰 `TheWorld` 时重新套用可踏水状态，避免卡地形 |
| `drownable.enabled = false` + `ShouldDrown=false` | 关溺水。官方 `ShouldDrown` 默认就是 `IsOverWater()` |
| `SetAllowPlatformHopping(false)` | 避免与船的登台/平台跳跃逻辑打架 |
| 水花周期任务 | 纯视觉表现，额外加分项 |

## 进阶：彻底无视障碍的真・飞行/虚影模式

如果还想**穿墙 + 踏水 + 跨虚空**（连生物、障碍全忽略），用更彻底的碰撞清空：

```lua
local function collidesDirty2(inst, get)
    if get then
        inst.Physics:ClearCollisionMask()
        inst.Physics:CollidesWith(COLLISION.GROUND)  -- 只保留地面，其余全部忽略
    else
        inst.Physics:CollidesWith(COLLISION.OBSTACLES)
        inst.Physics:CollidesWith(COLLISION.WORLD)
        inst.Physics:CollidesWith(COLLISION.SMALLOBSTACLES)
        inst.Physics:CollidesWith(COLLISION.CHARACTERS)
        inst.Physics:CollidesWith(COLLISION.GIANTS)
        inst.Physics:CollidesWith(COLLISION.GROUND)
    end
end
```

需要切换开关（例如某个技能/按键触发）时，监听对应事件来 `true/false` 反复切换即可。

## 常见坑

- **必须主机端执行**：碰撞层是权威物理，`Physics` 操作只在 `ismastersim` 生效；记得像模板里那样 `if not TheWorld.ismastersim then return end`。
- **不要用 `ClearCollridesWith(GROUND)`**：那样角色会掉穿地面。
- **切换要对称**：关闭能力时要把碰撞层恢复（`CollidesWith(WORLD)` 或完整 `cur` 分支），否则能力残留。
- **碰撞回调开销**：`SetCollisionCallback` 会频繁被调用，回调里逻辑要轻量，别做 heavy 计算。
- **与船/平台的交互**：可踏水后角色可能和 Boat 交互异常，用 `SetAllowPlatformHopping(false)` 规避。

官方源码：`components/drownable.lua`（IsOverWater / ShouldDrown）、`standardcomponents.lua`（COLLISION.WORLD/GROUND 掩码用法）。

---

## 相关枢纽

- [character-swim-ocean.md](character-swim-ocean.md) - 同主题的另一条路线：复用官方 `amphibiouscreature` 组件实现海上游泳（含跳跃下海/上岸）。
- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。