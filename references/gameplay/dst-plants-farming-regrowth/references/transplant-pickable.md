# 移植作物（`pickable`）：术语与免施肥

> 分类：`gameplay/dst-plants-farming-regrowth`  
> 组件详情：[`pickable.md`](../../../components/world/pickable.md)  
> **不要**与农田 `farm_plant` 混为一谈；农田见 [farm-stress-and-hooks.md](farm-stress-and-hooks.md)

## 术语（用户口径）

| 说法 | 实际系统 | 典型对象 |
|------|----------|----------|
| **移植作物** | `pickable` + `workable(DIG)` + `OnTransplant` | 浆果丛、草、树枝、多肉仙人掌等 `dug_*` 再种下 |
| **农作物 / 农田作物** | `farm_plant` + `farming_manager` + `farmplantstress` | 种子种在耕好的土上，养分/压力/照料 |

用户说 **「移植作物视为野生 / 免施肥 / 不需要施肥」** → 默认按 **`pickable` 移植链路** 实现。  
除非点名 **农作物、farm_plant、农田养分**，否则不要做成 `farming_manager` 免养分。

## 原版移植链路（为何要施肥）

```text
挖掉 → dug_berrybush 等物品
种下 → pickable:OnTransplant()
         → transplanted = true
         → ontransplantfn(inst)     -- 浆果丛：MakeBarren() + 播 dead
     → 贫瘠，CanBeFertilized() == true，必须施肥才活

以后 cycles_left 耗尽 → MakeBarren() → 又要施肥
```

锚点：

- `components/pickable.lua`：`OnTransplant`、`MakeBarren`、`CanBeFertilized`、`Fertilize`、`cycles_left`
- `prefabs/berrybush.lua`：`ontransplantfn` → `MakeBarren`

野生未挖的植物：`transplanted == false`，种下时**不**走这条 barren。

## 需求分档

| 档 | 含义 | 做法概要 |
|----|------|----------|
| 1 视为野生 | 种下不必先施肥，之后与野生一样（采满 cycle 仍可能贫瘠） | 移植后恢复 `cycles_left`，洗掉 barren 动画 |
| 2 永远免施肥 | 移植后永不因贫瘠要肥 | 移植后恢复健康 **且** `MakeBarren` 对移植植物 no-op 或立刻 `RestoreHealthy` |

## 选项 2：移植后永远不用施肥（`modmain.lua`）

只影响 `pickable.transplanted` 的实例；野生未挖不受影响。

```lua
-- 移植作物永远免施肥（选项 2）——放在 modmain.lua，勿改 D:\mods\scripts

local function IsManaged(pickable)
    return pickable.transplanted
        -- 可再收窄：and pickable.inst.prefab:find("berrybush")
end

local function RestoreHealthy(pickable)
    local inst = pickable.inst
    if inst == nil or not inst:IsValid() then
        return
    end
    -- 有 max_cycles：打满；nil cycles_left = 原版「无限采」语义
    if pickable.max_cycles ~= nil then
        pickable.cycles_left = math.max(pickable.max_cycles, 1)
    else
        pickable.cycles_left = nil
    end
    if pickable.makefullfn ~= nil then
        pickable.makefullfn(inst)
    elseif pickable.Regen ~= nil then
        pickable:Regen()
    end
end

AddComponentPostInit("pickable", function(self)
    local old_OnTransplant = self.OnTransplant
    if old_OnTransplant ~= nil then
        self.OnTransplant = function(pickable, ...)
            local result = old_OnTransplant(pickable, ...)
            -- 官方末尾会调 ontransplantfn（浆果丛 MakeBarren）；种完立刻拉回
            if IsManaged(pickable) then
                RestoreHealthy(pickable)
            end
            return result
        end
    end

    -- 更狠：移植植物根本不进贫瘠（避免 dead 闪一下）
    local old_MakeBarren = self.MakeBarren
    self.MakeBarren = function(pickable, ...)
        if IsManaged(pickable) then
            return
        end
        return old_MakeBarren(pickable, ...)
    end

    local old_CanBeFertilized = self.CanBeFertilized
    self.CanBeFertilized = function(pickable)
        if IsManaged(pickable) then
            return false
        end
        return old_CanBeFertilized ~= nil and old_CanBeFertilized(pickable) or false
    end
end)
```

说明：

- 若 `ontransplantfn` 仍先播 `dead`，种下后靠 `RestoreHealthy` / `makefullfn` 洗回 idle。
- 枯萎 `witherable` 是另一套；夏季枯萎也要免的话需再包 `witherable`。

## 边界

- 范围默认所有 `transplanted` 的 `pickable`；要只浆果丛用 prefab/tag 过滤。
- 客机：`pickable` 权威在主机，`AddComponentPostInit` 即可。
- 农田免养分见 [farm-stress-and-hooks.md](farm-stress-and-hooks.md)，与本文无关。
