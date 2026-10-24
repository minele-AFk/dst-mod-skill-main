# 投喂升级系统：喂指定物品触发升级（触发机制）

场景：想要一个可长期成长的装备/储物——玩家**手持指定物品对着它右键使用**，物品被消耗并触发一次升级回调；同一种可喂次数有限，喂满该类型后不再接受。典型：随身储物盒喂宝石来解锁/叠加各项能力。

> **本页只管"升级触发机制"**：能喂吗 → 触发回调 → 消耗 → 满级停。它本质是一条"**手持物品作用于目标**"的自定义 `USEITEM` 动作链路（见本子技能 action-pipeline）。投喂回调 `fn` 只是与"能力系统"之间的**接缝**；喂出来的具体能力不归本系统，由各自的能力系统实现并链接到文末。

## 一、通用组件：receiver（喂料接收器）

一个独立组件负责"注册可喂类型 → 判断能否喂 → 触发回调 → 消耗物品 → 计数/持久化/满级拦截"。

```lua
local item_receiver = Class(function(self, inst)
    inst:AddTag("item_receiver")               -- 也作为自定义动作的命中标签
    self.inst = inst
    self.receiverd_prefab = {}                 -- prefab -> {maxnum, per_require_num}
    self.receiverd_num = {}                    -- prefab -> 已喂次数
    self.receiverd_fn = {}                     -- prefab -> 升级回调(inst, item, nownum, prefab, doer)
end)

-- 注册一种可喂物；fn 每次投喂触发；maxnum 为该类型上限（-1 表示无限）
function item_receiver:AddItemTrigger(prefab, fn, maxnum, per_require_num)
    self.receiverd_fn[prefab] = fn
    self.receiverd_prefab[prefab] = { maxnum = maxnum, per_require_num = per_require_num }
    self.receiverd_num[prefab] = 0
end

-- 客户端判断可否喂（用于动作显隐）
function item_receiver:CanReceiveItem_client(item)
    if self.receiverd_prefab[item.prefab] then
        return self.canreceivedfn and self.canreceivedfn(self.inst, item) or true
    end
end

-- 服务器最终校验
function item_receiver:CanReceiveItem(item)
    local cfg = self.receiverd_prefab[item.prefab]
    if cfg and (self.receiverd_num[item.prefab] < cfg.maxnum or cfg.maxnum == -1)
        and (not cfg.per_require_num
            or item.components.stackable and item.components.stackable:StackSize() >= cfg.per_require_num) then
        return true
    end
end

function item_receiver:ReceiveItem(item, doer)
    if self:CanReceiveItem(item) then
        self.receiverd_num[item.prefab] = (self.receiverd_num[item.prefab] or 0) + 1
        if self.receiverd_fn[item.prefab] then
            self.receiverd_fn[item.prefab](self.inst, item, self.receiverd_num[item.prefab], item.prefab, doer)
        end
        if self.receiverd_num[item.prefab] >= self.receiverd_prefab[item.prefab].maxnum then
            self.inst:PushEvent("full_receiverd", item.prefab)   -- 满级事件
        end
        if doer then doer:PushEvent("repair") end                 -- 反馈音效事件
        self:ConsumeReceiveItem(item)                              -- 消耗投喂物
        return true
    end
end

-- 消耗：单件删除，或按 per_require_num 从堆叠取
function item_receiver:ConsumeReceiveItem(item)
    local per_require_num = self.receiverd_prefab[item.prefab].per_require_num
    if item.components.stackable then
        if per_require_num then item.components.stackable:Get(per_require_num):Remove()
        else item.components.stackable:Get():Remove() end
    else
        item:Remove()
    end
end
```

## 二、自定义交互动作接线（右键物品 → 目标）

投喂不是"放进口袋/容器"，而是**手持物品对着目标使用**。用典型的 `USEITEM + inventoryitem` 动作：

```lua
AddComponentAction("USEITEM", "inventoryitem", function(inst, doer, target, actions, right)
    if right and doer:HasTag("player") and target:HasTag("item_receiver") then
        local recv = target.components.item_receiver
        if recv:CanReceiveItem_client(inst) then
            actions:PushAction(ACTIONS.CUSTOM_GIVE_ITEM, 99)   -- 优先级高，覆盖默认"放入"
        end
    end
end)
```

自定义动作本身（`AddAction`）的 `fn` 做服务器端执行：

```lua
AddAction("CUSTOM_GIVE_ITEM", "投喂", function(act)
    local recv = act.target and act.target.components.item_receiver
    return recv and recv:ReceiveItem(act.invobject, act.doer) or false
end)
```

**双层校验**：客户端 `CanReceiveItem_client` 只决定是否显示动作；真正执行前服务器 `CanReceiveItem` 再次校验，防作弊/防到上限后继续喂。

> 这是通用"手持物品作用于目标并触发"的动作模式，可复用到喂料、投食、充能、附着等任何"拿 A 打 B"的交互。

## 三、能力通过回调解锁（升级只负责触发）

升级系统**不拥有任何能力**。喂一次物品，它只做三件事：计数 → 调用注册回调 `fn` → 消耗物品并（可选）点亮满级拦截。**回调里干嘛是能力系统的事**：

```lua
-- 例：喂蓝宝石 → 投喂只触发回调，保鲜由"容器保鲜能力"实现
inst.components.receiver:AddItemTrigger("BLUEGEM", function(inst, item, nownum)
    inst.components.preserver:SetPerishRateMultiplier(1 - 0.5 * nownum)  -- 能力侧实现，此处仅举例
end, 2)
```

`fn(inst, item, nownum, prefab, doer)` 即升级系统与能力系统的**接缝**：`nownum` 是当前档位，能力据此决定数值曲线。可喂物 → 回调 = 一个"解锁/叠加入口"，不同能力落到各自系统：

| 可喂物 | 交给的能力系统 | 详见 |
|--------|----------------|------|
| 蓝宝石 → 反鲜/保鲜 | 容器保鲜（内容物不腐败） | dst-inventory-equipment-containers / 容器存储 |
| 橙宝石 → 无限堆叠 | 容器堆叠上限 | dst-inventory-equipment-containers / 容器存储 |
| 绿宝石 → 自动维修 | 耐久维护（周期性修复耐用耗材） | dst-inventory-equipment-containers / 物品行为 |
| 紫宝石 → 提升维修上限 | 耐久维护封顶 | dst-inventory-equipment-containers / 物品行为 |
| 火把 → 携带照明 | 携带被动（夜间/洞内光源） | dst-status-buffs-survival / 携带被动 |

> 接入建议：本系统只负责"能不能喂、触发什么、满级停"；能力数值与实现一律放对应能力系统文档，升级系统不越界。

## 四、满级拦截与持久化

- 满级：某类型达到 `maxnum` 推 `full_receiverd` 事件 → 绑 `full<prefab>` 标签 → `canreceivedfn = function(inst, item) return not inst:HasTag("full"..item.prefab) end`，此后该类型不再接受，也不会再显示"投喂"动作。
- 持久化：`OnSave` 存 `receiverd_num`；`OnLoad` 恢复计数，并**重放**回调（`for i=1,num do fn(inst,nil,i,prefab) end`）让已喂效果随存档重建，且重新补推满级事件。

## 五、要点与陷阱

- **优先放"投喂"动作**：`USEITEM` 动作优先级给到 99，否则会默认触发"放入容器/使用"而抢不到投喂。
- **服务器权威**：计数、消耗、满级判定只发生在服务器；客户端仅决定可喂与否。
- **喂满要能停**：`canreceivedfn` + `full_receiverd` 是"可变上限"的关键，没有它会无限触发。
- **触发状态落盘**：已喂次数（档位）要在 `OnSave` 带走，`OnLoad` 重放回调，让能力系统据此重建效果。
- **多来源叠加**：同类可喂物多次叠加时，`nownum` 即当前档位，回调以此驱动能力曲线——但要不要叠、怎么叠由能力系统决定。

## 能力系统文档链接

以下"能力"由各自的系统实现，投喂只是它们的解锁入口：

- 容器保鲜（内容不腐败）/ 无限堆叠：`dst-inventory-equipment-containers` → `portable-chef-container.md`、`dual-container-expansion.md`。
- 耐久维护（自动维修 + 维修上限封顶）：`dst-inventory-equipment-containers` → `auto-repair-maintenance.md`。
- 携带被动（暖石恒温 / 喂火把照明）：`dst-status-buffs-survival` → `carried-passive-buffs.md`。

## 官方源码

- `scripts/main/functions.lua`：`AddComponentAction`、`AddAction`、`actions`。
- `components/stackable.lua`：`Get(n)`、`StackSize`、`Remove`（消耗投喂物）。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。