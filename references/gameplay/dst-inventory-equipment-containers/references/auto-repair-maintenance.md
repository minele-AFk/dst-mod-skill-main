# 耐久维护：周期性自动修复容器内耐用耗材

场景：想要一件装备/储物**自动维修**其内容物——放在里面的武器、护甲、耐久工具会按固定间隔恢复耐久，间隔与修复量可随档位变化（如喂绿宝石提升维修效率）。

这是一个独立的**能力系统**：它只负责"修什么、多久修一次、修多少、修到多少封顶"，与"怎么获得这个能力"（如投喂升级）解耦。可单独做成被动属性，也可被投喂升级的 `fn` 回调触发。

## 一、核心：周期任务遍历容器逐件补耐久

用一个周期任务（如每秒），对容器内每个**耐用耗材**（`fueled` / `armor` / `finiteuses`）按间隔累计补一小口耐久：

```lua
inst._repair_task = inst._repair_task or inst:DoPeriodicTask(1, function()
    local dt = math.clamp(17 - inst.greennum * 2, 1, 15)  -- 喂越多间隔越短
    local repairnum = 1 / dt * 0.01                        -- 每次补 n% 耐久
    local max = inst._max_percent or 1                     -- 修复上限封顶

    local function ForEachItemfn(target)
        if target.components.fueled then
            local percent = target.components.fueled:GetPercent()
            target.components.fueled:SetPercent(math.min(math.max(max, percent), percent + repairnum))
        end
        if target.components.armor then
            local percent = target.components.armor:GetPercent()
            target.components.armor:SetPercent(math.min(math.max(max, percent), percent + repairnum))
        end
        if target.components.finiteuses then
            local percent = target.components.finiteuses:GetPercent()
            target.components.finiteuses:SetPercent(math.min(math.max(max, percent), percent + repairnum))
        end
    end
    inst.components.container:ForEachItem(ForEachItemfn)
end)
```

## 二、关键参数

- **维修间隔 `dt`**：`clamp(17 - greennum*2, 1, 15)`，最低 1 秒、最高 15 秒；`greennum` 是"维修档位"（喂绿宝石提升）。
- **每次维修量**：`1/dt * 0.01`，即"每 dt 秒补 1% 耐久"，间隔越短补得越频繁。
- **修复上限封顶 `_max_percent`**：`SetPercent(min(max(max, percent), percent + repairnum))`，保证不会一次修过头，也限制能修到的上限。

## 三、作用于哪些对象

- 通过 `container:ForEachItem` 遍历**容器内**的物品；若采用双容器扩容，需分别对主、子容器都做 `ForEachItem`。
- 可维修的对象：带 `fueled`（可加油燃料）、`armor`（护甲）、`finiteuses`（有限使用次数）组件的物品——覆盖了大部分会损耗的装备/工具。
- 只补未损坏的缺少部分（`GetPercent` < 100%），不会凭空增加不满耐久。

## 四、与"投喂升级系统"的关系

耐久维护是**被触发的能力系统**之一。投喂系统回调里只开启/提高档位，维护逻辑在本系统：

```lua
-- 投喂"绿宝石"→ 提升维修档位（greennum+1），维修逻辑由本系统周期任务执行
receiver:AddItemTrigger("GREENGEM", function(inst, item, nownum)
    inst.greennum = nownum            -- 档位驱动 dt
end, 8)
```

`紫宝石` 提升的"修复上限 `_max_percent`"同样属于本系统（维修封顶），由投喂回调累加。

## 五、要点与陷阱

- **遍历范围要全**：双容器时主、子都要 `ForEachItem`，否则漏修。
- **只补不增**：每次只把耐久往上抬一个小口，用 `min(max, percent + repairnum)` 防超补。
- **上限封顶**：`_max_percent` 决定能修到的天花板，避免无限叠档后装备各种超耐久。
- **周期任务随睡眠挂起**：`entitysleep/entitywake` 应管理 `_repair_task`，睡眠时不空转。

## 官方源码

- `components/fueled.lua`：`GetPercent` / `SetPercent`。
- `components/armor.lua`：`GetPercent` / `SetPercent`。
- `components/finiteuses.lua`：`GetPercent` / `SetPercent`。
- `components/container.lua`：`ForEachItem`。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。