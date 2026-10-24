# 伪进食：让「正常不能吃的东西」变得可吃

需求目标：角色能吃原本没有 `edible`、或无法走进食管线的物品（如噩梦燃料 `nightmarefuel`、地狱燃料 `horrorfuel`、启迪碎片 `purebrilliance`、警报脉冲等）。
原理：**完全绕过 `edible`/`eater` 的进食管线**，用「自定义动作 + 运行时挂自定义组件 + 手动结算属性」实现一套伪进食流程。

> 注意：这是与「给标准食物加 `edible`」完全不同的做法。若物品能走正常食用，优先按 `references/components/items/edible.md` 配置 `edible`；此模式用于真正常规吃不了的物品。

## 三步实现

### 1) 可吃物品清单（数据驱动，决定哪些 prefab 可吃 + 数值）

对每个目标 prefab 运行时挂一个自定义组件，并配置吃后的生命/饥饿/理智数值：

```lua
local caneatlist = {
    nightmarefuel        = { health = 10,  sanity = -10, hunger = 30 },
    horrorfuel           = { health = 40,  sanity = -30, hunger = 60 },
    archive_security_pulse = { health = 25, hunger = 25 },
    moonstorm_spark      = { hunger = 20 },
    purebrilliance       = { health = 50, sanity = 70, hunger = 30 },
}
for prefab, dat in pairs(caneatlist) do
    AddPrefabPostInit(prefab, function(inst)
        if not TheWorld.ismastersim then return inst end
        local e = inst:AddComponent("noa_ediable")   -- 自定义组件
        e.healthvalue, e.hungervalue, e.sanityvalue = dat.health, dat.hunger, dat.sanity
    end)
end
```

### 2) 自定义组件：`BeEated` 手动结算

```lua
local noa_ediable = Class(function(self, inst)
    self.inst = inst
end)

function noa_ediable:BeEated(doer)
    -- 手动套三维（绕过 edible 的数值管道）
    if self.healthvalue ~= 0 then doer.components.health:DoDelta(self.healthvalue) end
    if self.hungervalue ~= 0 then doer.components.hunger:DoDelta(self.hungervalue) end
    if self.sanityvalue ~= 0 then doer.components.sanity:DoDelta(self.sanityvalue) end
    -- 可附加角色能量/台词等
    -- if doer.components.my_energy then doer.components.my_energy:Add(self.inst.prefab) end
    -- 消费物品：不同损耗形式各自处理
    if self.inst.components.finiteuses then
        self.inst.components.finiteuses:Use(1)
    elseif self.inst.components.stackable then
        self.inst.components.stackable:Get(1):Remove()
    else
        self.inst:Remove()
    end
    return true
end
return noa_ediable
```

### 3) 自定义 Action（NOA_EAT）

注册一个动作，`fn` 检测目标有 `noa_ediable` 组件就去调 `BeEated`，并 `state = 'eat'` 复用进食动画：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
{
    id = 'NOA_EAT',
    str = "NOA_EAT",
    fn = function(act)
        local obj = act.target or act.invobject
        if obj.components.noa_ediable then
            return obj.components.noa_ediable:BeEated(act.doer)
        end
    end,
    state = 'eat',
    actiondata = { priority = 99 },  -- 高优先级优先于普通 EAT
}
```

## 关键点

- **入口是自定义 Action**：不进 `eater:Eat`，所以不存在 `CanEat`/`TestFood`/`edible` 判定，天然能吃任何东西。
- **必须主机端**挂组件和结算（`noa_energybody_init` 里 `return inst if not ismastersim`）。
- **消费逻辑三档**：有限次数（`finiteuses:Use`）/ 可堆叠（`stackable:Get(1):Remove`）/ 整体 `Remove`，按物品实际组件选择。
- **扩展成本低**：数据驱动，想加一种可食物品只需在清单加一行，无需改动作或组件。
- **复用进食动画**：Action 的 `state='eat'` 让角色使用标准进食表现，行为自然。

## 常见坑

- 只加组件不注册 Action，则没有交互入口，仍然吃不了。
- 没有 `finiteuses`/`stackable` 的物品且忘记 `Remove` 会残留、无法真正吃掉。
- 数值用 `DoDelta` 时注意吸收系数/上限；若希望吃出溢出效果需自行判满。
- `is_mastersim` 之外的端不要执行结算，避免双端重复扣物品。

官方参考：`components/edible.lua`、`components/eater.lua`（吃食判定链，见 `references/components/items/edible.md`）。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。