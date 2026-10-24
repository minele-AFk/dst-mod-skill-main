# `tool`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改工人端动作效果（如砍伐、采矿、锤击、挖掘或其他工具动作支持）时，使用此文件。

官方源码：

- `scripts/components/tool.lua`

相关官方预制件示例：

- `scripts/prefabs/axe.lua`
- `scripts/prefabs/lucy.lua`

高频方法：

- `EnableToughWork(tough)`
- `CanDoToughWork()`
- `GetEffectiveness(action)`
- `SetAction(action, effectiveness)`
- `CanDoAction(action)`
常见组件搭配：

- `tool` + `inventoryitem`
- `tool` + `finiteuses`
- `tool` + `equippable`

常见陷阱：

- `tool` 属于动作物品。
- 目标端工作逻辑在 `workable` 中。
- 如果请求说无限耐久，省略 `finiteuses`。

---

## 工具分类系统

基于源码 `tool.lua:11-51`：

### 核心机制

```lua
local Tool = Class(function(self, inst)
    self.inst = inst
    self.actions = {}  -- 动作→效率映射表
    
    inst:ListenForEvent("percentusedchange", PercentChanged)
    inst:AddTag("tool")
end)

function Tool:SetAction(action, effectiveness)
    assert(TOOLACTIONS[action.id], "invalid tool action")
    self.actions[action] = effectiveness or 1
    self.inst:AddTag(action.id.."_tool")  -- 添加工具标签
end

function Tool:GetEffectiveness(action)
    return self.actions[action] or 0
end

function Tool:CanDoAction(action)
    return self.actions[action] ~= nil
end
```

### 效率计算

工具的 `effectiveness`（效率）会影响工作速度和消耗：

- **效率 > 1**：工作更快，消耗更少
- **效率 = 1**：正常工作速度
- **效率 < 1**：工作更慢，消耗更多

效率在 `workable` 组件中被应用到工作进度计算。

### 常见工具动作

| 动作 | 标签 | 用途 |
|------|------|------|
| `ACTIONS.CHOP` | `chop_tool` | 砍树 |
| `ACTIONS.MINE` | `mine_tool` | 挖矿 |
| `ACTIONS.DIG` | `dig_tool` | 挖掘 |
| `ACTIONS.HAMMER` | `hammer_tool` | 锤击 |
| `ACTIONS.HARVEST` | `harvest_tool` | 收割 |
| `ACTIONS.TILL` | `till_tool` | 耕地 |

---

## 实战示例

### 创建多功能工具

```lua
local tool = inst.components.tool

-- 设置为斧头（效率1）
tool:SetAction(ACTIONS.CHOP, 1)

-- 设置为镐（效率1.5，更快）
tool:SetAction(ACTIONS.MINE, 1.5)

-- 设置为锤子（效率0.8，更慢）
tool:SetAction(ACTIONS.HAMMER, 0.8)

-- 设置为铲子（效率1）
tool:SetAction(ACTIONS.DIG, 1)
```

### 检查工具能力

```lua
local tool = inst.components.tool

-- 检查是否能砍树
if tool:CanDoAction(ACTIONS.CHOP) then
    print("可以砍树")
end

-- 获取砍树效率
local effectiveness = tool:GetEffectiveness(ACTIONS.CHOP)
print("砍树效率:", effectiveness)
```

### 设置强力工作模式

```lua
-- 启用强力工作（可以处理更强硬的目标）
inst.components.tool:EnableToughWork(true)

-- 检查是否启用
if inst.components.tool:CanDoToughWork() then
    print("可以处理强力目标")
end
```

后续阅读：

- [workable.md](../world/workable.md)
- [action-pipeline.md](../../core/dst-action-authoring/references/action-pipeline.md)
