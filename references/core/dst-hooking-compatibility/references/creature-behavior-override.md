# 拦截生物对玩家的特定行为（实例方法覆盖）

场景：让某个已有生物不再对玩家做某个动作（如啜食者不扑头、不抓取、不偷夺等），但不想改动它整体的逻辑。

## 原理

这类"能不能做某动作"的判定，往往是生物 prefab 上的一个**实例方法**（例如啜食者的 `HatTest`）。做法是把原方法保存到实例字段，再原位包装一层：先查我们的条件，命中就短路返回 `false`，否则调用原方法。用 `AddPrefabPostInit` 只在主机端执行。

```lua
local function fakeTest(inst, target, ...)
    if target and target.components.inventory
        and target.components.inventory:EquipHasTag("mytag") then
        return false                     -- 命中条件：直接拒绝该动作
    end
    if inst.noa_oldTest then
        return inst.noa_oldTest(inst, target, ...)
    end
end

AddPrefabPostInit("slurper", function(inst)
    if not TheWorld.ismastersim then
        return inst
    end
    inst.noa_oldTest = inst.HatTest      -- 保存原方法
    inst.HatTest = fakeTest              -- 实例级覆盖
end)
```

## 要点

- **只在主机端覆盖**：`AddPrefabPostInit` 里先判 `if not TheWorld.ismastersim then return inst end`。
- **装备判定**：主机用 `components.inventory:EquipHasTag(tag)`；客户端侧可用 `replica.inventory:EquipHasTag(tag)`。
- **必须回退原方法**：存 `noa_oldTest` 并在未命中时调用 `inst.noa_oldTest(inst, target, ...)`，不破坏原有判定。
- **只影响该实例**：覆盖的是这一个生物实体实例的字段，不影响其他同类生物。

## 案例：啜食者不扑头

官方 Slurper 通过 `HatTest`（即 `CanHatTarget`）决定能否扑上目标头部（`prefabs/slurper.lua` L82）：它默认只判断"头顶是否已有个啜食者"（`hat == nil or hat.prefab ~= inst.prefab`），也就是说玩家戴着普通帽子照样会被扑。

做法：给玩家的某件头饰打一个专属标签，再包装啜食者的 `HatTest`，检测到该标签就返回 `false`，啜食者便放弃这个目标。

```lua
local function fakeHatTest(inst, target, ...)
    if target and target.replica.inventory
        and target.replica.inventory:EquipHasTag("mychar_ringhat") then
        return false
    end
    if inst.noa_oldHatTest then
        return inst.noa_oldHatTest(inst, target, ...)
    end
end

AddPrefabPostInit("slurper", function(inst)
    if not TheWorld.ismastersim then
        return inst
    end
    inst.noa_oldHatTest = inst.HatTest
    inst.HatTest = fakeHatTest
end)
```

## 官方源码

- `prefabs/slurper.lua`：`CanHatTarget`（L82-97）、`HatTest = CanHatTarget`（L352）。
- `components/inventory.lua`：`EquipHasTag`（玩家端判定是否装备了某标签物品）。