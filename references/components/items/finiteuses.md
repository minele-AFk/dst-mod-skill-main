# `finiteuses`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改物品使用次数、耐久消耗或用完后的行为时，使用此文件。

官方源码：

- `scripts/components/finiteuses.lua`

相关官方预制件示例：

- `scripts/prefabs/spear.lua`
- `scripts/prefabs/pickaxe.lua`

高频方法：

- `SetMaxUses(val)`
- `SetUses(val)`
- `GetUses()`
- `GetPercent()`
- `SetPercent(amount)`
- `Use(num)`
- `Repair(repairvalue)`
- `SetOnFinished(fn)`
- `SetConsumption(action, uses)`
- `SetModifyUseConsumption(fn)`
常见组件搭配：

- `finiteuses` + `weapon`
- `finiteuses` + `tool`
- `finiteuses` + `inventoryitem`

常见陷阱：

- 使用次数为0时物品会被移除（除非设置了 `keeponfinished`）。
- 不同动作可以设置不同的消耗次数。
- 装备类物品的耐久消耗在 `equippable` 组件中处理，不是 `finiteuses`。

---

## 耐久消耗机制

基于源码 `finiteuses.lua:10-125`：

### 核心属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `total` | number | 100 | 最大使用次数 |
| `current` | number | 100 | 当前使用次数 |
| `consumption` | table | {} | 各动作的消耗配置 |
| `ignorecombatdurabilityloss` | boolean | false | 是否忽略战斗耐久损耗 |
| `modifyuseconsumption` | function | nil | 自定义消耗计算函数 |

### 消耗流程

```lua
function FiniteUses:SetUses(val)
    local was_positive = self.current > 0
    self.current = val
    self.inst:PushEvent("percentusedchange", {percent = self:GetPercent()})
    
    if self.current <= 0 then
        self.current = 0
        if was_positive then
            -- 用完了，添加标签
            self.inst:AddTag("usesdepleted")
            -- 调用用完回调
            if self.onfinished ~= nil then
                self.onfinished(self.inst)
            end
        end
    elseif not was_positive then
        -- 从0恢复，移除标签
        self.inst:RemoveTag("usesdepleted")
    end
end

function FiniteUses:Use(num)
    self:SetUses(self.current - (num or 1))
end

function FiniteUses:OnUsedAsItem(action, doer, target)
    local uses = self.consumption[action]
    if uses ~= nil then
        -- 效率用户加成
        if doer ~= nil and doer:IsValid() and doer.components.efficientuser ~= nil then
            uses = uses * (doer.components.efficientuser:GetMultiplier(action) or 1)
        end
        
        -- 自定义消耗修改
        if self.modifyuseconsumption then
            uses = self.modifyuseconsumption(uses, action, doer, target, self.inst)
        end
        
        self:Use(uses)
    end
end
```

---

## 实战示例

### 设置使用次数

```lua
local fu = inst.components.finiteuses

-- 设置最大使用次数
fu:SetMaxUses(50)

-- 设置当前使用次数
fu:SetUses(30)

-- 获取当前使用次数
local current = fu:GetUses()
```

### 设置动作消耗

```lua
local fu = inst.components.finiteuses

-- 攻击消耗1次
fu:SetConsumption(ACTIONS.ATTACK, 1)

-- 砍树消耗2次
fu:SetConsumption(ACTIONS.CHOP, 2)

-- 挖矿消耗3次
fu:SetConsumption(ACTIONS.MINE, 3)
```

### 自定义消耗计算

```lua
local fu = inst.components.finiteuses

fu:SetModifyUseConsumption(function(uses, action, doer, target, inst)
    -- 根据目标类型调整消耗
    if target and target:HasTag("giant") then
        return uses * 2  -- 打大型怪物消耗翻倍
    end
    return uses
end)
```

### 修复耐久

```lua
-- 修复20点耐久
inst.components.finiteuses:Repair(20)

-- 设置回满耐久
inst.components.finiteuses:SetPercent(1)
```

### 用完后保留物品

```lua
-- 默认用完后移除物品
inst.components.finiteuses:SetOnFinished(function(inst)
    inst:Remove()
end)

-- 用完后保留但不可用（需要设置keeponfinished）
-- 在prefab中设置：inst.components.finiteuses.keeponfinished = true
```

后续阅读：

- [weapon.md](../combat/weapon.md)
- [tool.md](tool.md)
