# 角色能力：海上游泳（amphibiouscreature 方案）

让角色能直接在海里游泳：走到岸边自动跳下去、游向对岸时自动跳上岸，不坐船也不溺水。
与「踏水/虚空行走」的碰撞层方案不同，本方案走**官方水陆两栖组件 `amphibiouscreature`**。

## 原理一句话

复用官方 `amphibiouscreature` 组件来管理「进海/上岸」状态（进海加 `swimming` 标签、触发水陆切换回调），
但用 `ShouldTransition = false` **禁用 locomotor 在水陆交界的自动跳跃过渡**，改成自建跳跃状态 + 清碰撞层主动跳入/跳出海洋。
（进海/上岸的 `swimming` 状态仍由组件 `OnUpdate` 自动维护。）

## 官方组件要点（components/amphibiouscreature.lua）

- `OnUpdate` 每帧检测当前位置 `IsPassableAtPoint`（可通行=陆地），与当前 `in_water` 不一致时自动调 `OnEnterOcean` / `OnExitOcean`。
- `OnEnterOcean`：加官方 `swimming` 标签、切 ocean bank、回调 `enterwaterfn`。
- `OnExitOcean`：删 `swimming` 标签、切 land bank、回调 `exitwaterfn`。
- `ShouldTransition(x, z)`：由 `locomotor` 的平台跳跃逻辑调用（`components/locomotor.lua`），判定"走到水陆交界是否自动 hop 过渡"。返回 `false` 即禁用该自动过渡，避免与自建跳跃冲突。（注意：进海/上岸的 `swimming` 状态由 `OnUpdate` 维护，不经过此函数。）

## 最小实现（核心三步）

```lua
-- 服务端挂官方水陆两栖组件
inst:AddComponent("amphibiouscreature")
inst.components.amphibiouscreature:SetEnterWaterFn(OnEnterWater)
inst.components.amphibiouscreature:SetExitWaterFn(OnExitWater)
inst.components.amphibiouscreature:SetBanks("wilson", "wilson")  -- 水陆共用一套 bank

-- 关掉官方被动切换（避免与自建跳跃状态冲突）
inst.components.amphibiouscreature.ShouldTransition = function(self, x, z)
    return false
end

-- 关溺水
if inst.components.drownable then
    inst.components.drownable.enabled = false
end
```

## 进海/上岸表现回调

```lua
local function OnEnterWater(inst)
    inst:AddTag("swimming")                 -- 供状态机判断用
    inst.AnimState:PlayAnimation("idle_ocean", true)  -- 海上 idle 动画
    inst.DynamicShadow:Enable(false)
    -- 可在此生成水浪/水花特效子实体
end

local function OnExitWater(inst)
    inst:RemoveTag("swimming")
    inst.DynamicShadow:Enable(true)
    -- 移除水浪特效
end
```

## 跳跃下海/上岸（跳过水陆边界阻挡）

```lua
-- 跳跃状态：起跳前清掉水和船的边界碰撞，才能越过海陆交界
AddStategraphState("wilson", State{
    name = "swim_hop",
    tags = { "busy", "jumping", "nopredict" },
    onenter = function(inst)
        inst.components.locomotor:Stop()
        inst.AnimState:PlayAnimation("jump_pre", false)
        inst.Physics:ClearCollidesWith(COLLISION.LAND_OCEAN_LIMITS)
        inst.Physics:ClearCollidesWith(COLLISION.BOAT_LIMITS)
    end,
    onexit = function(inst)
        inst.Physics:CollidesWith(COLLISION.LAND_OCEAN_LIMITS)
        inst.Physics:CollidesWith(COLLISION.BOAT_LIMITS)
    end,
    -- ...落地回到 idle，动画结束可 PerformBufferedAction 结算
})
```

## 自动探测水陆边界（触发跳跃）

在客户端做"当前位置 + 前方 1 码是否跨水陆边界"检测，跨了就 Push 一个跳跃动作（走缓冲动作/RPC 链路），实现"走到海边自动跳下去、上岸自动跳上来"：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
-- 每帧 OnUpdate（客户端，非专服）
local cur = inst:GetPosition()
local ahead = cur + 朝向偏移   -- 前方 1 码
if 在陆地(cur) and 在水上(ahead) then
    -- PushAction(下海跳跃动作, 目标点)
elseif 在水上(cur) and 在陆地(ahead) then
    -- PushAction(上岸跳跃动作, 目标点)
end
```

游泳期间的 idle/run 用 `*_ocean` 后缀动画（覆写 wilson/wilson_client 的 idle、run 状态按 `swimming` 标签分支），并生成水花。

## 各环节说明

| 环节 | 作用 |
| --- | --- |
| `amphibiouscreature` 组件 | 官方水陆状态管理：进海/上岸加删 `swimming` 标签、切 bank、触发回调 |
| `ShouldTransition = false` | 禁用 locomotor 在水陆交界的自动 hop 过渡，避免与自建跳跃状态双重跳跃 |
| `drownable.enabled = false` | 关溺水，海里不判定淹死 |
| 跳跃状态清碰撞层 | 跳过 `LAND_OCEAN_LIMITS` / `BOAT_LIMITS` 的海陆交界阻挡 |
| `*_ocean` 动画 + 水花特效 | 海上移动的表现层 |
| 客户端边界探测 + 跳跃动作 | 自动下海/上岸的输入链路（可做开关按键） |

## 常见坑

- **必须服务端挂组件**：`amphibiouscreature` 和物理相关操作只在 `ismastersim` 生效。
- **别忘设 `ShouldTransition = false`**：否则 `locomotor` 会在水陆交界自动触发 hop 过渡，和你自建的跳跃状态打架，出现重复跳跃。
- **幽灵死亡/复活要处理**：角色死亡（ghost）或复活时若在海里，需手动 `OnExitOcean` / `OnEnterOcean` 恢复状态，否则复活后卡在水陆状态不一致。
- **飞行/其它移动能力冲突**：若有飞行组件，进海回调里要判断飞行中不触发下水。
- **服务端/客户端一致**：自动探测通常在客户端做，但跳跃结算必须走服务端权威的动作链路；客户端与服务器 SG 都要加对应状态。

官方源码：`components/amphibiouscreature.lua`（OnEnterOcean / OnExitOcean / ShouldTransition / SetEnterWaterFn）、`components/drownable.lua`（enabled / IsOverWater）、`stategraphs/SGwilson.lua`（jumpin 等跳跃状态参考）。

---

## 相关枢纽

- [character-walkonwater.md](character-walkonwater.md) - 同主题的另一条路线：切换物理碰撞层实现踏水/虚空行走（不依赖 `amphibiouscreature`）。
