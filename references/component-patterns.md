# 高频组件模式

当任务主要涉及常见官方组件而非整个子系统时使用此文件。

如果任务还依赖于 prefab 标签或动作/查询路由，请阅读 `references/patterns/prefab/tag-patterns.md`。
如果任务还依赖于光照、FX prefabs 或声音播放，请阅读 `references/patterns/asset/effects-patterns.md`。

本页面是路由和预测层。方法列表和每个组件的陷阱在 `references/components/` 下。

## 各组件详情页面

### 生存类 (survival)
- [components/survival/health.md](components/survival/health.md)
- [components/survival/hunger.md](components/survival/hunger.md)
- [components/survival/sanity.md](components/survival/sanity.md)

### 战斗类 (combat)
- [components/combat/combat.md](components/combat/combat.md)
- [components/combat/weapon.md](components/combat/weapon.md)
- [components/combat/armor.md](components/combat/armor.md)
- [components/combat/equippable.md](components/combat/equippable.md)

### 物品类 (items)
- [components/items/inventoryitem.md](components/items/inventoryitem.md)
- [components/items/inspectable.md](components/items/inspectable.md)
- [components/items/stackable.md](components/items/stackable.md)
- [components/items/finiteuses.md](components/items/finiteuses.md)
- [components/items/edible.md](components/items/edible.md)
- [components/items/cookable.md](components/items/cookable.md)
- [components/items/fuel.md](components/items/fuel.md)
- [components/items/tool.md](components/items/tool.md)

### 存储类 (storage)
- [components/storage/inventory.md](components/storage/inventory.md)
- [components/storage/container.md](components/storage/container.md)

### 行为类 (behavior)
- [components/behavior/talker.md](components/behavior/talker.md)

### 世界类 (world)
- [components/world/pickable.md](components/world/pickable.md)
- [components/world/workable.md](components/world/workable.md)
- [components/world/deployable.md](components/world/deployable.md)

### 工具类 (utility)
- [components/utility/timer.md](components/utility/timer.md)

## 组件分类索引

### 生存类 (survival)
- [components/survival/health.md](components/survival/health.md)
- [components/survival/hunger.md](components/survival/hunger.md)
- [components/survival/sanity.md](components/survival/sanity.md)
- [components/survival/sleeper.md](components/survival/sleeper.md)
- [components/survival/temperature.md](components/survival/temperature.md)
- [components/survival/moisture.md](components/survival/moisture.md)

### 战斗类 (combat)
- [components/combat/combat.md](components/combat/combat.md)
- [components/combat/weapon.md](components/combat/weapon.md)
- [components/combat/equippable.md](components/combat/equippable.md)
- [components/combat/armor.md](components/combat/armor.md)
- [components/combat/damagetyperesist.md](components/combat/damagetyperesist.md)

### 物品类 (items)
- [components/items/inspectable.md](components/items/inspectable.md)
- [components/items/inventoryitem.md](components/items/inventoryitem.md)
- [components/items/stackable.md](components/items/stackable.md)
- [components/items/finiteuses.md](components/items/finiteuses.md)
- [components/items/edible.md](components/items/edible.md)
- [components/items/cookable.md](components/items/cookable.md)
- [components/items/fuel.md](components/items/fuel.md)
- [components/items/tool.md](components/items/tool.md)
- [components/items/perishable.md](components/items/perishable.md)

### 存储类 (storage)
- [components/storage/inventory.md](components/storage/inventory.md)
- [components/storage/container.md](components/storage/container.md)

### 世界类 (world)
- [components/world/pickable.md](components/world/pickable.md)
- [components/world/workable.md](components/world/workable.md)
- [components/world/deployable.md](components/world/deployable.md)

### 行为类 (behavior)
- [components/behavior/talker.md](components/behavior/talker.md)

### AI类 (ai)
- [components/ai/follower.md](components/ai/follower.md)

### 工具类 (utility)
- [components/utility/timer.md](components/utility/timer.md)
- [components/utility/locomotor.md](components/utility/locomotor.md)

### 系统类 (system)
- [components/system/blinkstaff.md](components/system/blinkstaff.md)
- [components/system/recallmark.md](components/system/recallmark.md)
- [components/system/worldmigrator.md](components/system/worldmigrator.md)

## 何时值得阅读本页面

当用户要求以下内容时，先阅读本页面：

- 生命值增益、伤害、无敌、最大生命值、死亡流程
- 饥饿值消耗、饥饿、食物类消费行为
- 理智值增益或损失、疯狂、光环免疫、惩罚
- 战斗目标选择、攻击范围、攻击时机、伤害逻辑
- 可穿戴行为、装备和卸下回调、槽位限制
- 护甲耐久度或吸收
- 武器伤害、投射物行为、攻击回调
- 某物是否应该可拾取、可堆叠、可食用、可烹饪、可燃烧或有限使用
- 行为应该属于物品侧、背包侧还是世界目标侧
- 箱子、背包、冰箱或自定义背包容器逻辑

## 快速组件映射

- 物品基础
  - `inspectable`
  - `inventoryitem`
  - `stackable`
  - `finiteuses`
- 存储和持有
  - `inventory`
  - `container`
- 物品行为
  - `edible`
  - `cookable`
  - `fuel`
  - `tool`
- 世界交互
  - `pickable`
  - `workable`
  - `timer`
  - `talker`
- 生存
  - `health`
  - `hunger`
  - `sanity`
- 战斗
  - `combat`
  - `weapon`
  - `armor`
  - `equippable`

规则：

- 这些捆绑是常见模式，不是强制清单
- 从最小的组件集开始，匹配预期行为
- 仅当 prefab 真正需要该能力时才添加组件
- 如果请求包含否定约束，如"无限耐久"或"不可检查"，移除您原本会预期的默认组件

## 出现时机和通常位置

在打开详情页面之前，使用此作为第一个路由通道：

- `inspectable`
  - 几乎每个面向玩家的对象或物品
  - 它的缺失往往比存在更有信息量
- `inventoryitem`
  - 当事物可以进入背包槽位或作为松散物品存在时
- `stackable`
  - 当多个副本应在一个槽位中合并时
- `finiteuses`
  - 当物品有使用次数耐久度而不是燃料或护甲状态时
- `inventory`
  - 通常在玩家、追随者或特殊持有者上
- `container`
  - 在背包、箱子、冰箱、包裹、便携存储或可打开结构上
- `edible`
  - 在可以直接食用的东西上
- `cookable`
  - 在烹饪时会转换成另一个 prefab 的东西上
- `fuel`
  - 在被消耗的燃料物品上，而不是被燃料驱动的目标上
- `tool`
  - 在执行动作的物品上
- `pickable`
  - 在世界采集节点上，不是松散物品
- `workable`
  - 在被加工的目标上
- `timer`
  - 当延迟阶段或冷却时间应该干净地保存或加载时
- `talker`
  - 在玩家和许多类生物 prefabs 上很常见
  - 缺失 `talker` 可能是一个有意的设计信号

## 常见组件组合

对于大多数面向玩家的 prefabs，假设 `inspectable`，除非 prefab 有意不可检查。
将每行视为候选捆绑，当请求明确排除某个能力时可以减少。

- 松散背包材料
  - `inspectable` + `inventoryitem`
- 可堆叠材料
  - `inspectable` + `inventoryitem` + `stackable`
- 可食用物品
  - `inspectable` + `inventoryitem` + `edible`
- 也可以烹饪的原料
  - `inspectable` + `inventoryitem` + `edible` + `cookable`
- 燃料物品
  - `inspectable` + `inventoryitem` + 通常 `stackable` + `fuel`
- 工具物品
  - `inspectable` + `inventoryitem` + `finiteuses` + `tool` + 通常 `equippable`
- 生物战斗单位
  - `health` + `combat`
- 玩家生存调整
  - `health` + `hunger` + `sanity`
- 武器物品
  - `inspectable` + `inventoryitem` + `finiteuses` + `weapon` + `equippable`
- 无限耐久武器物品
  - `inspectable` + `inventoryitem` + `weapon` + `equippable`
  - 省略 `finiteuses`
- 可穿戴护甲
  - `equippable` + `armor`
- 可穿戴容器
  - `inspectable` + `inventoryitem` + `equippable` + `container`
- 无限耐久工具物品
  - `inspectable` + `inventoryitem` + `tool` + 通常 `equippable`
  - 省略 `finiteuses`
- 世界采集植物
  - `pickable` + `inspectable` + 通常 `workable`
- 可锤击或可挖掘结构
  - `inspectable` + `workable` + 通常 `container` 或 `lootdropper`
- 存储物品或结构
  - `container` + 通常 `inspectable`

## 意图索引

当用户用普通语言描述功能而不是按组件名称描述时使用此索引。
在这里应用减法推理：如果请求排除某个能力，移除通常提供该能力的组件。

- "我想添加一个武器物品"
  - 从 `inspectable` + `inventoryitem` + `finiteuses` + `weapon` + `equippable` 开始
  - 如果是玩家手持，然后检查装备视觉效果和 `AnimState`
- "我想添加一个无限耐久武器"
  - 从 `inspectable` + `inventoryitem` + `weapon` + `equippable` 开始
  - 不要添加 `finiteuses`
  - 根据官方反例如 `hambat` 验证
- "我想添加护甲或服装"
  - 从 `inspectable` + `inventoryitem` + `equippable` 开始
  - 如果应该吸收伤害，添加 `armor`
- "我想添加一个背包"
  - 从 `inspectable` + `inventoryitem` + `equippable` + `container` 开始
- "我想添加一个箱子或存储结构"
  - 从 `inspectable` + `container` 开始
  - 如果可以被锤击或拆除，添加 `workable`
- "我想添加一个基础材料物品"
  - 从 `inspectable` + `inventoryitem` 开始
  - 如果应该在背包中合并，添加 `stackable`
  - 如果可以作为燃料燃烧，添加 `fuel`
- "我想添加一个食物物品"
  - 从 `inspectable` + `inventoryitem` + `edible` 开始
  - 如果应该堆叠，添加 `stackable`
  - 如果烹饪时应该转换，添加 `cookable`
- "我想添加一个可烹饪原料"
  - 从 `inspectable` + `inventoryitem` + 通常 `edible` + `cookable` 开始
- "我想添加一个工具物品"
  - 从 `inspectable` + `inventoryitem` + `finiteuses` + `tool` 开始
  - 如果是手持装备，添加 `equippable`
- "我想添加一个无限耐久工具"
  - 从 `inspectable` + `inventoryitem` + `tool` 开始
  - 如果是手持装备，添加 `equippable`
  - 不要添加 `finiteuses`
  - 根据官方反例如 `lucy` 验证
- "我想添加一个可采摘的世界植物或资源"
  - 从 `pickable` + `inspectable` 开始
  - 如果也可以被挖起或破坏，添加 `workable`
- "我想添加一个可锤击或可挖掘结构"
  - 从 `inspectable` + `workable` 开始
  - 如果存储物品，添加 `container`
- "我想添加具有定时状态变化的东西"
  - 从 `timer` 开始
  - 然后将其与它计时的游戏玩法组件配对
- "我想添加一个有意不使用 `talker` 的生物"
  - 首先验证最接近的官方生物 prefab，因为许多类生物 prefabs 确实包含 `talker`
  - 将缺失 `talker` 视为有意的设计选择
- "我想添加一个有意不使用 `inspectable` 的 prefab"
  - 首先验证最接近的官方 prefab，因为大多数面向玩家的 prefabs 确实包含 `inspectable`
  - 将缺失 `inspectable` 视为有意的交互选择

## 实用阅读顺序

1. 使用本页面预测可能的组件捆绑。
2. 打开 `references/components/` 下匹配的各组件页面。
3. 仅当任务跨越多个相邻组件时，使用捆绑摘要页面。
4. 阅读 `scripts/components/` 下的官方组件文件本身。
5. 阅读以相同方式使用该组件的最接近官方 prefab。
6. 如果组件影响动画、动作或网络，也检查匹配的窄参考页面。

## 自定义组件开发模式

当需要创建新的游戏机制或扩展现有功能时，可以创建自定义组件。

### 组件结构

```lua
local MyComponent = Class(function(self, inst)
    self.inst = inst

    -- 初始化属性
    self.value = 0
    self.max = 100
    self.enabled = false

    -- 初始化任务和事件监听
    self.update_task = nil
    self.inst:ListenForEvent("death", OnDeath)
end)

-- 方法定义
function MyComponent:Enable()
    self.enabled = true
    self.update_task = self.inst:DoPeriodicTask(1, self.OnUpdate, 0, self)
end

function MyComponent:Disable()
    self.enabled = false
    if self.update_task then
        self.update_task:Cancel()
        self.update_task = nil
    end
end

function MyComponent:OnUpdate()
    -- 周期性更新逻辑
    if self.enabled then
        self:DoDelta(1)
    end
end

function MyComponent:DoDelta(val)
    self.value = math.clamp(self.value + val, 0, self.max)
    -- 触发网络同步（如果需要）
    self:SyncValue()
end

function MyComponent:SyncValue()
    -- 通过 replica 同步到客户端
    if self.inst.replica.mycomponent then
        self.inst.replica.mycomponent:SetValue(self.value)
    end
end

-- 持久化
function MyComponent:OnSave()
    return {
        value = self.value,
        enabled = self.enabled
    }
end

function MyComponent:OnLoad(data)
    if data then
        self.value = data.value or 0
        self.enabled = data.enabled or false
        if self.enabled then
            self:Enable()
        end
    end
end

return MyComponent
```

### 组件元表同步（网络变量）

使用元表回调实现自动同步：

```lua
local function OnValueChanged(self, val)
    -- 当 value 属性改变时自动同步到客户端
    if self.inst.replica.mycomponent then
        self.inst.replica.mycomponent:SetValue(val)
    end
end

local MyComponent = Class(function(self, inst)
    self.inst = inst
    self.value = 0
end, nil, {
    value = OnValueChanged  -- 元表回调
})
```

### Replica 实现

创建客户端副本组件：

```lua
local MyComponentReplica = Class(function(self, inst)
    self.inst = inst

    -- 定义网络变量
    self._value = net_byte(inst.GUID, "mycomponent._value")
    self._enabled = net_bool(inst.GUID, "mycomponent._enabled")
end)

-- 客户端只读方法
function MyComponentReplica:GetValue()
    return self._value:value()
end

function MyComponentReplica:IsEnabled()
    return self._enabled:value()
end

-- 服务端设置方法
function MyComponentReplica:SetValue(val)
    self._value:set(val)
end

function MyComponentReplica:SetEnabled(val)
    self._enabled:set(val)
end

return MyComponentReplica
```

### 在 Prefab 中注册组件

```lua
local function CommonInit(inst)
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    inst.entity:SetPristine()
end

local function MasterInit(inst)
    -- 服务端添加组件
    inst:AddComponent("mycomponent")
    inst.components.mycomponent:Enable()
end

local function ClientInit(inst)
    -- 客户端添加 replica
    inst.replica.mycomponent = MyComponentReplica(inst)
end

local prefab = Prefab("myitem", function()
    local inst = CreateEntity()
    CommonInit(inst)

    if not TheWorld.ismastersim then
        -- 客户端初始化
        ClientInit(inst)
        return inst
    end

    MasterInit(inst)
    return inst
end)

return prefab
```

### 注册可复制组件

在 `modmain.lua` 中注册自定义组件：

```lua
AddReplicableComponent("mycomponent")
```

### 组件使用示例

```lua
-- 获取组件
local comp = inst.components.mycomponent

-- 调用方法
comp:DoDelta(10)
comp:Enable()

-- 客户端读取状态
if inst.replica.mycomponent then
    local value = inst.replica.mycomponent:GetValue()
end
```

### 组件设计最佳实践

1. **单一职责**：每个组件只负责一个功能
2. **服务端权威**：状态修改应在服务端进行
3. **网络同步最小化**：只同步必要的数据
4. **持久化支持**：实现 `OnSave/OnLoad` 方法
5. **事件驱动**：使用事件系统解耦组件间通信
6. **清理资源**：在组件禁用或实体死亡时清理任务和事件

---

## 经验法则

- 使用本页面决定什么可能属于 prefab。
- 使用 `references/components/` 下的各组件文件检查方法和常见陷阱。
- 当同时涉及多个相邻组件时，使用捆绑摘要页面。
- 然后根据最接近的官方 prefab 验证所有内容。
