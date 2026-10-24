# 便携厨具容器：一格装下整个厨房

场景：想做一个**可携带的多功能容器**（类似"丰饶角"背囊），在一个物品里集成多个功能分区，例如：

- 大格**保鲜储物**（食物不腐坏、无限堆叠）
- **一键批量烹饪**（按便携烹饪锅配方出菜）
- **一键调味**
- **晾晒 / 烤制 / 调味料研磨**（瞬时加工）
- **三维存储与自动补给**（把食物转成饥饿/理智/血量积累值，开启后自动补三维）
- **特效料理槽**（吃料理不消耗食物，改为扣别的东西触发 buff）

核心思想：**一个 `container` 承载全部功能，按槽位区间划分分区**；每个分区有专属过滤规则、专属加工逻辑。

## 1. 总览：容器分区与区号常量

先规划好每个分区的槽位范围，并把**各分区的起始槽**存进 `TUNING`，供后续按区读写：

```lua
-- 布局示例：28 格，划分为 8 个区
-- slotpos[i] = 第 i 区的最后一个槽位号，slotpos[i-1]+1 ~ slotpos[i] 即第 i 区
slotpos[1] = 16  -- ① A：4x4 保鲜储物格
slotpos[2] = 18  -- ② A：烹饪食材槽（2 格，配合①合计 4 格食材）
slotpos[3] = 20  -- ③ 调味槽（2 格）
slotpos[4] = 21  -- ④ 消耗槽（1 格，转三维积累）
slotpos[5] = 22  -- ⑤ 晾晒槽（1 格）
slotpos[6] = 23  -- ⑥ 烤制槽（1 格）
slotpos[7] = 24  -- ⑦ 研磨槽（1 格）
slotpos[8] = 28  -- ⑧ 特效料理槽（4 格）
TUNING.MYCHEF_SLOT_POS = slotpos
```

> 用 `slotpos[i]` 而非硬编码槽号的好处：布局调整只改这一处，其余加工逻辑全部跟着切换。

## 2. 槽位过滤（itemtestfn 按分区放行/拦截）

容器开启 `usespecificslotsforitems = true` 后，项能否放入某槽由 `itemtestfn` 决定。按 `slot` 归属哪一区返回 true/false：

```lua
-- containers.lua 的 widgetsetup 配置中
function params.my_horn.itemtestfn(container, item, slot)
    if not item or item == container.inst then return end
    local slotpos = TUNING.MYCHEF_SLOT_POS
    if slot <= slotpos[1] then          -- 储物区：基本放行
        return true
    elseif slot <= slotpos[2] then      -- 烹饪食材：cooking.IsCookingIngredient
        return cooking.IsCookingIngredient(item.prefab)
            and not container.inst:HasTag("burnt")
    elseif slot <= slotpos[3] then      -- 调味槽：放香料/未调味料理
        return (slot == slotpos[3] and item:HasTag("spice"))
            or (slot ~= slotpos[3] and item:HasTag("preparedfood") and not item:HasTag("spicedfood"))
    elseif slot <= slotpos[4] then      -- 消耗槽：可食用
        for k, v in pairs(FOODTYPE) do
            if item:HasTag("edible_" .. v) then return true end
        end
    elseif slot <= slotpos[5] then      -- 晾晒槽：可晾晒
        return item:HasTag("dryable")
    elseif slot <= slotpos[6] then      -- 烤制槽：可烧烤
        return item:HasTag("cookable")
    elseif slot <= slotpos[7] then      -- 研磨槽：放调味料原料
        return true
    elseif slot <= slotpos[8] then      -- 特效料理槽：放预制料理
        return item:HasTag("preparedfood")
    end
end
```

## 3. 保鲜 + 无限堆叠（储物区的"反鲜"）

- `preserver:SetPerishRateMultiplier(-1)`：容器内物品腐败倍率为负 → **永不腐坏**。
- `container:EnableInfiniteStackSize(true)`：允许无限堆叠（配合储物区）。

```lua
inst:AddComponent("preserver")
inst.components.preserver:SetPerishRateMultiplier(-1)
inst.components.container:EnableInfiniteStackSize(true)
```

## 4. 自定义容器界面 + 动作按钮（按钮即功能入口）

- 在 `containers.lua` 的 widgetsetup 里给该容器配 `animbank/animbuild` 和 `noa_postinit`。
- `noa_postinit` 中动态创建若干 `ImageButton`（烹饪/调味/消耗/开关），每个按钮点击通过 **MOD_RPC** 发给服务器执行对应函数。
- 关闭时按钮跟随容器关闭（返回 `olditemtestfn` 之外，还需处理按钮的回收）。

要点：**UI 只用 RPC 发指令鉴权，真正的逻辑在服务端组件里**，客户端不做有效性判断。

## 5. 一键批量烹饪（cooking.CalculateRecipe）

在组件里做菜按钮对应的函数：

```lua
function MyChef:DoCook(inst, doer)
    local container = inst.components.container
    local ingredients = {}
    local start = TUNING.MYCHEF_SLOT_POS[1] or 16
    for i = start + 1, start + 4 do      -- 读 4 格食材（含各区)
        local v = container.slots[i]
        if not v then return end
        table.insert(ingredients, v)
    end
    -- 批量倍数 = 所有食材堆叠数的最小值
    local finalnum
    for k, v in pairs(ingredients) do
        if v.components.stackable then
            finalnum = math.min(v.components.stackable:StackSize(), finalnum or v.components.stackable:StackSize())
        else
            finalnum = 1
        end
    end
    local product = cooking.CalculateRecipe("portablecookpot", ingredient_prefabs)
    local recipe = cooking.GetRecipe("portablecookpot", product)
    local stacksize = (recipe and recipe.stacksize or 1) * finalnum
    -- 批量产出 + 继承食材平均新鲜度 + 批量扣料
    for i = 1, stacksize do
        local loot = SpawnPrefab(product)
        loot.components.perishable:SetPercent(avg_spoilage)
        container:GiveItem(loot, nil, inst:GetPosition())
    end
    for k, v in pairs(ingredients) do v.components.stackable:Get(finalnum):Remove() end
end
```

关键点：
- `cooking.CalculateRecipe(cooker, prefabs)` / `cooking.GetRecipe(cooker, product)` 按配方表解析成品（官方 `cooking.lua`）。
- **新鲜度继承**：遍历食材 `perishable:GetPercent()` 取平均值，成品 `SetPercent(avg) + StartPerishing()`，避免凭空产出一批全新料理。
- **批量倍数取最小值**，保证不会出现某些食材不够分的情况。

## 6. 每秒瞬时加工槽（晾晒 / 烤制 / 研磨）

在组件的 `OnSecondTick()`（`inst:DoPeriodicTask(1, ...)`）里轮询特定槽，把"需要时间"的世界行为变成瞬时：

```lua
function MyChef:OnSecondTick()
    -- 晾晒槽：dryable → 瞬间产物
    local a = container:GetItemInSlot(TUNING.MYCHEF_SLOT_POS[5])
    if a then
        local p = SpawnPrefab(a.components.dryable:GetProduct())
        container:GiveItem(p, nil, self.inst:GetPosition())
        a:Remove()
    end
    -- 烤制槽：cookable → 瞬间烤熟
    local b = container:GetItemInSlot(TUNING.MYCHEF_SLOT_POS[6])
    if b and b.components.cookable then
        local c = b.components.cookable:Cook(self.inst, self.inst)
        container:GiveItem(c, nil, self.inst:GetPosition()); b:Remove()
        self.inst.SoundEmitter:PlaySound("dontstarve/wilson/cook")
    end
end
```

要点：统一节奏（如每秒轮询一次）来自动处理这几类"放进去等结果"的加工，省去各槽各自计时。

## 7. 三维存储与自动补给

- **存储**：消耗槽按钮把格内食物移除，并把 `edible.healthvalue/hungervalue/sanityvalue` 累加到 `store_health/store_hunger/store_sanity`。
- **补给**：开关开启后，每秒把这些积累值补到主人三维，补的量不超过缺口，只扣实际补到的部分。
- **理智按"有效上限"判断**：判断是否缺理智用 `sanity:GetPercentWithPenalty()` 而非 `GetPercent()`，这样带有"黑血/红心惩罚"的角色也会被正确补满（官方 `components/sanity.lua`）。

```lua
local function refillHealth(self, Health)
    local maxdelta = Health.maxhealth - Health.currenthealth
    local delta = math.min(self.store_health, maxdelta)
    Health:DoDelta(delta)
    self.store_health = math.max(0, self.store_health - delta)
end
```

- **持久化**：`OnSave/OnLoad` 保存积累值与开关；用 `named` 组件把积累值写进物品名（如 `丰饶角 饥饿X/理智X/血量X`），玩家悬浮即可看到存量。

## 8. 特效料理槽：吃而食物不消失

hook `Eater:Eat`（官方 `components/eater.lua`）：当被吃的食物位于特效料理槽时，**不执行真实食用、不消耗食物**，而是只触发 `OnEaten` 效果并改为付出替代代价（如 -100 饥饿）后返回 true：

```lua
local oldEat = Eater.Eat
function Eater:Eat(food, feeder, ...)
    feeder = feeder or self.inst
    if food and self:PrefersToEat(food) then
        local owner = food.components.inventoryitem and food.components.inventoryitem.owner
        if owner and owner:HasTag("my_chef") then
            for i = 1, 4 do   -- 检查特效料理槽
                local slotfood = owner.components.container:GetItemInSlot(TUNING.MYCHEF_SLOT_POS[7] + i)
                if slotfood == food then
                    food.components.edible:OnEaten(self.inst)
                    self.inst.components.hunger:DoDelta(-100)
                    return true  -- 吃掉但没真删食物
                end
            end
        end
    end
    return oldEat(self, food, feeder, ...)
end
```

要点：先判断食物归属与所在槽，命中才走"不消耗"分支；否则回落到原 `Eater:Eat`，避免影响其他食物。

## 优点与取舍

- **分区清晰**：一个容器通过槽位区间拆分多种功能，布局用 TUNING 常量集中管理。
- **瞬时加工**：把原版的"等时间"表现成"放进去就出结果"，体验爽快，实现简单（统一轮询）。
- **批量做菜**：配合 `cooking.CalculateRecipe` 和新鲜度继承，能让玩家囤一批食材一次出整组料理。
- 注意：每个功能槽的过滤、加工、持久化都是独立点，文档中各节均可单独复用，不必强行套用整套容器逻辑。

## 官方源码

- `cooking.lua`：`CalculateRecipe`、`GetRecipe`、`IsCookingIngredient`。
- `components/container.lua`、`components/container_replica.lua`、`scripts/containers.lua`：widgetsetup、槽位、过滤与 `EnableInfiniteStackSize`。
- `components/preserver.lua`：`SetPerishRateMultiplier`（保鲜）。
- `components/perishable.lua`：`SetPercent`、`StartPerishing`、`GetPercent`。
- `components/dryable.lua` / `components/cookable.lua`：`GetProduct` / `Cook`。
- `components/eater.lua`：`Eat`、`PrefersToEat`。
- `components/sanity.lua`：`GetPercentWithPenalty`（有效上限判断）。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。