# 农田压力、浇水与收获 Hook（原版机制 + Mod 实战）

**适用**：仅农田 `farm_plant` / `farming_manager` / `farmplantstress`（种子作物、养分、照料）。

**不适用**：挖出再种的**移植作物**（浆果丛等 `pickable`）——术语与免施肥见 [transplant-pickable.md](transplant-pickable.md)。

**适用技能树玩法**：给自定义角色做农耕流技能（浇水满值、作物免疫季节/家庭压力、收获额外产出）时，直接复用原版组件并 hook 对应回调，不要重写整套农田逻辑。

> 以下源码均基于 `D:\mods\scripts`（脚本包），调用链与 mod 实战写法均已核对。

## 一、农田压力系统（farmplantstress）

### 1.1 数据模型

组件 [components/farmplantstress.lua](file:///d:/mods/scripts/components/farmplantstress.lua) 在每个农田作物（`farm_plant`）上维护三类表：

| 成员 | 含义 | 关键消费点 |
| --- | --- | --- |
| `self.stressors[name]` | 该压力源当前**是否受压**（bool） | `MakeCheckpoint()` 累加线程 |
| `self.stressors_testfns[name]` | 压力源**测试函数** `test(inst, currentstress, apply)` | `GetStressDescription()`（心情提示）+ `GetDebugString()` |
| `self.stressor_fns[name]` | 受压状态**变化回调** | `SetStressed()` 状态翻转时 | 
| `self.stress_points` | 累积压力点数 | `CalcFinalStressState()` 定级 |

### 1.2 压力源与判定（prefabs/farm_plants.lua）

原版一个作物注册了 7 类压力源：

```lua
AddStressCategory("nutrients",   NutrientsStressTest)   -- 土壤养分不足
AddStressCategory("moisture",    MoistureStressTest)    -- 水分低于 plant_def.moisture.min_percent
AddStressCategory("killjoys",    KillJoyStressTest)     -- 附近敌意植物超标
AddStressCategory("family",      FamilyStressTest)      -- 附近同家族作物 < family_min_count
AddStressCategory("overcrowding",OvercrowdingStressTest)-- 同格作物超上限
AddStressCategory("season",      SeasonStressTest)      -- 当前季节不在 plant_def.good_seasons
AddStressCategory("happiness",   HappinessStressTest)   -- 交互（恶作剧/冰雹）扣心情
```

各测试函数要点：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
SeasonStressTest:  return not inst.plant_def.good_seasons[TheWorld.state.season]
FamilyStressTest:  num_plants = #FindEntities(x,y,z, plant_def.family_check_dist,
                                             {plant_def.plant_type_tag})
                   return num_plants < plant_def.family_min_count   -- 没伙伴就受压
OvercrowdingStressTest: 同格 farm_plant 数量 > TUNING.FARM_PANT_OVERCROWDING_MAX_PLANTS
```

### 1.3 压力点数如何累加（关键调用链）

压力点**不是**持续累加，而是每个生长阶段切换时打一次"检查点"：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
-- prefabs/farm_plants.lua :: MakeStressCheckpoint(inst, is_final_stage)
SetStressed("family",   FamilyStressTest(inst, nil, true))     -- ① 硬编码调用局部测试函数
SetStressed("season",   SeasonStressTest(inst, nil, true))
...
farmplantstress:MakeCheckpoint()                                -- ② 把 true 的数量加进 stress_points

-- components/farmplantstress.lua :: MakeCheckpoint()
for name, stressed in pairs(self.stressors) do
    if stressed then stress = stress + 1 end
end
self.stress_points = self.stress_points + stress
```

最终按 `stress_points` 定级：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
stress <= 1  → FARM_PLANT_STRESS.NONE
stress <= 6  → LOW      -- "低压力"，几乎不影响
stress <= 11 → MODERATE -- "中压力"
else         → HIGH     -- "高压力"，产出大幅下降
```

### 1.4 常见坑：改 `stressors_testfns` 不等于真正免压

`stressors_testfns`（压力源测试表）在 **原版只被"心情提示"和"调试串"消费**，**不参与 `MakeCheckpoint` 的压点累加**。累加路径 `MakeStressCheckpoint` 是**硬编码调用局部函数** `FamilyStressTest`/`SeasonStressTest` 后再 `SetStressed` 的。

所以下面这种只覆盖 `stressors_testfns` 的写法，**仅能骗过 UI 心情显示，不会真正免掉影响长势的压力点**：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
AddComponentPostInit("farmplantstress", function(self)
    local old = self.MakeCheckpoint
    self.MakeCheckpoint = function(s, ...)
        if s.inst.components.某技能 and s.inst.components.某技能.level >= 3 then
            s.stressors_testfns['family'] = function() return false end
        end
        old(s, ...)
    end
end)
```

**要真正免疫压力点**，应直接覆盖 `SetStressed` 的入参（或整个 `MakeCheckpoint`），在累加前把对应压力源强制设为 `false`：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
AddComponentPostInit("farmplantstress", function(self)
    local old = self.SetStressed
    self.SetStressed = function(s, name, stressed, doer)
        if (name == "family" or name == "season") and s.inst.components.某技能
            and s.inst.components.某技能.level >= X then
            stressed = false           -- 直接吞掉季节/家庭压力
        end
        return old(s, name, stressed, doer)
    end
end)
```

> 不建议靠 `MakeCheckpoint` 事后 `-N` 压点：它已被 "允许 1 次失误"（NONE 阈值≤1）等容错逻辑覆盖，语义不清。

---

## 二、浇水："一次浇满"的实现

### 2.1 原版浇水动作

浇水走 `ACTIONS.POUR_WATER_GROUNDTILE.fn`；真正给土壤加水的是组件 `wateryprotection`：

```lua
-- components/wateryprotection.lua :: SpreadProtectionAtPoint()
if self.addwetness and TheWorld.components.farming_manager then
    TheWorld.components.farming_manager:AddSoilMoistureAtPoint(x, y, z, self.addwetness)
end
```

即：**每次浇水给土壤增加的水量 = `wateryprotection.addwetness`**。

### 2.2 Mod 一次浇满的正确姿势

不自己重写土壤类型判断，而是**借用水壶的 wateryprotection 组件**，把 `addwetness` 临时改成土壤最大含水量再 `SpreadProtection`：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
local oldpour = GLOBAL.ACTIONS.POUR_WATER_GROUNDTILE.fn
GLOBAL.ACTIONS.POUR_WATER_GROUNDTILE.fn = function(act)
    -- 命中条件：特定角色 + 已解锁技能(等级>=1)
    if act.invobject and act.invobject:IsValid() and act.doer:HasTag("你角色tag")
        and act.doer.某技能 and act.doer.某技能:value() >= 1 then
        local watering = SpawnPrefab("wateringcan")
        if watering then
            watering.components.wateryprotection.addwetness = TUNING.SOIL_MAX_MOISTURE_VALUE -- 满值
            if act.target and act.target:IsValid() then
                watering.components.wateryprotection:SpreadProtection(act.target)
            else
                watering.components.wateryprotection:SpreadProtectionAtPoint(act:GetActionPoint():Get())
            end
            watering:Remove()  -- 用完立即销毁临时壶
        end
    end
    return oldpour(act)  -- 再走原版浇水
end
```

要点/坑：

- `TUNING.SOIL_MAX_MOISTURE_VALUE` 是土壤允许的最大含水量，设成它即"一次满水"。
- 用完 `watering:Remove()`，避免生成残留实体。
- 若在 `oldpour` 之外提前 `return`，记得补原始 `wateringcan` 的"水不够/伪装失败"分支（`finiteuses` 为 0 要 `return false, "OUT_OF_WATER"`）。

---

## 三、收获额外产出（hook lootdropper）

### 3.1 给"自己种的"作物打标

播种时原版会推 `on_planted` 事件，携带播种者：

```lua
-- components/farmplantable.lua :: Plant()
plant:PushEvent("on_planted", { doer = planter, seed = self.inst, in_soil = true })
```

`doer` 是播种者，**与种子类型无关**——未知/随机种子走同一路径也会触发。技能/角色只需在此判断播种者：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
AddComponentPostInit("growable", function(self)
    if self.inst:HasTag("farm_plant") then self.inst:AddComponent("我自己的plant组件") end
    self.inst:ListenForEvent("on_planted", function(inst, data)
        if data.doer:HasTag("你角色tag") and data.doer.某技能:value() >= 2 then
            inst:AddTag("你角色种的作物")          -- 打上归属标记
            inst.components.我自己的plant组件.level = data.doer.某技能:value()
        end
    end)
end)
```

### 3.2 收成时追加产出

拦截 `lootdropper:GenerateLoot`，用作物的 `plant_def.seed` / `plant_def.product`（原版自动填充的产物名）做追加：

```lua
AddComponentPostInit("lootdropper", function(self)
    local old = self.GenerateLoot
    self.GenerateLoot = function(s, ...)
        local loots = old(s, ...)
        if s.inst:HasTag("你角色种的作物")
            and s.inst.components.pickable and s.inst.components.pickable:CanBePicked()
            and not s.inst.is_oversized then
            if s.inst.plant_def and s.inst.plant_def.seed then
                table.insert(loots, s.inst.plant_def.seed)   -- +1 种子
                -- 更高等级再插 N 次实现"硕果/丰收"叠加
            end
            if s.inst.plant_def and s.inst.plant_def.product then
                table.insert(loots, s.inst.plant_def.product) -- +1 果实
            end
        end
        return loots
    end
end)
```

陷阱：

- 巨型作物（`is_oversized`）不走 `GenerateLoot` 追加这段，需另 hook `SpawnLootPrefab`，并把母株 `level` 传给掉落物，让加成继续继承。
- 掉落物若带 `_seeds` 后缀，要按 `plant_def.seed` 追加而不是拼字符串，避免改作物名后失效。
- 判定用"播种者 + 等级"，不要用"种子类型"，否则未知/随机种子种出的作物拿不到加成（或误加）。

---

## 四、对话联动农田（hook INTERACT_WITH）

### 4.1 想做的效果

"一次对话作物，圈内所有作物一起被照料：减压力 + 加快成长"。**它不是单独的光环技能**，而是包在角色对作物发起的原版 `INTERACT_WITH`（照料/对话作物）动作之上。

### 4.2 原版基准（actions.lua）

```lua
ACTIONS.INTERACT_WITH.fn = function(act)
    if act.target ~= nil and act.target.components.farmplanttendable ~= nil then
        if act.target.components.farmplanttendable:TendTo(act.doer) then
            act.doer.components.talker:Say(GetString(act.doer, "ANNOUNCE_TALK_TO_PLANTS"))
            return true
        end
    end
end
```

原版只对 `act.target` 一个作物 `TendTo`，并让角色说一句"跟植物说话"。

### 4.3 扩展写法

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
-- 加快成长:把当前生长阶段剩余时间缩短 20%
local function ReduceGrowthTime(inst)
    if inst.components.growable and inst.components.growable:IsGrowing() then
        local remaining_time = inst.components.growable.targettime - GetTime()
        if remaining_time > 0 then
            inst.components.growable:ExtendGrowTime(-(remaining_time * 0.2)) -- 负数=缩短
        end
    end
end

local CALC_CANT_TAGS = { "FX", "NOCLICK", "DECOR", "INLIMBO" }
local PLANTTAG = { "tendable_farmplant" }
local oldinteract = GLOBAL.ACTIONS.INTERACT_WITH.fn
GLOBAL.ACTIONS.INTERACT_WITH.fn = function(act)
    -- 触发条件:你的角色 tag + 目标存在 + 不哑巴 + 精英/技能等级门槛
    if act.doer:HasTag("你角色tag") and act.target and (not act.doer:HasTag("mime"))
        and act.doer.某精英阶段 and act.doer.某精英阶段:value() >= 2 then
        local x, y, z = act.doer.Transform:GetWorldPosition()
        -- 半径 5 扫描所有可照料作物
        local ents = TheSim:FindEntities(x, y, z, 5, PLANTTAG, CALC_CANT_TAGS)
        for i, v in ipairs(ents) do
            if v.components.farmplanttendable and v ~= act.target then
                if v.components.farmplanttendable:TendTo(act.doer) then
                    v.components.farmplantstress.stress_points = math.max(0, v.components.farmplantstress.stress_points - 1)
                    ReduceGrowthTime(v)
                end
            end
        end
        act.target.components.farmplantstress.stress_points = math.max(0, act.target.components.farmplantstress.stress_points - 1)
        ReduceGrowthTime(act.target)
    end
    return oldinteract(act) -- 再走原版:对目标 TendTo + 说话
end
```

### 4.4 要点与坑

- **"大范围"以动作触发为准**：必须先对某个可照料作物发起 `INTERACT_WITH`，才会连带半径内的其他作物。若想真正"自动定时扫田"，需另加 `DoPeriodicTask`；单靠这个 hook 是"一次对话、圈内联动"。
- **范围联动食材**：用玩家位置 `TheSim:FindEntities(x,y,z,5, {"tendable_farmplant"}, CANT_TAGS)`，`tendable_farmplant` 是"可照料农田作物"标签；不含巨型/未照料状态会自动排掉。
- **直接减压力**：这里直接 `stress_points = math.max(0, ...-1)`，是操作**真累加器**，真实有效（与"改 `stressors_testfns` 只骗 UI"的坑不同）。
- **成长加速**：`growable:ExtendGrowTime(-delta)` 传负数即缩短当前阶段；`delta = 剩余时间 × 0.2` 意为每次削减约 20% 当前进度，别传固定秒数，否则对长阶段压得太狠。
- **避免重复**：联动循环里用 `v ~= act.target` 排除正在对话的目标，目标单独处理一次，否则 `oldinteract` 会再 `TendTo` 一遍造成重复。
