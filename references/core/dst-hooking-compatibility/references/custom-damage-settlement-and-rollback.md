# 自定义伤害结算、穿透与致死回滚

这份专题承接[自定义伤害与致死保护的通用分层](custom-damage-death-layers.md)。总览负责选择入口和核对覆盖范围；这里展开两条“多数常规防御会失效”的完整路径，以及对应的防御实现边界。

适用前提：用户已经确认玩法需要穿透常规减伤、削减上限、锁血或拦截强制死亡。这里是机制与兼容性模板，不是默认的战斗设计，也不承诺对任意第三方实现绝对生效。

## 攻击端

攻击端优先保留一次合法攻击应有的副作用。能复用原版受击链时，用瞬态标记只放行指定层；只有目标入口被明确锁死且玩法确实需要时，才增加并行受击链或自定义落值。

### 完整穿透模板

> 2026-10-23 兼容性更正：安装版 `759671` 中，公开 `Combat:GetAttacked` 只转发到 `GetAttacked_Internal`；普通 `DoAttack`、范围攻击和投射物命中直接调用内部入口。只包装公开入口无法覆盖普通攻击。

原版 `Combat:GetAttacked/GetAttacked_Internal` 从受击入口到血量落值会依次经过多道检查和数值变换。只在 `DoDelta` 上放行，会留下护甲、闪避、抗性、承伤倍率和位面阶段；只清掉位面参数，又可能失去对应的攻击表现。

| 阶段 | 常见入口 | 穿透动作 | 必须保留的语义 |
| --- | --- | --- | --- |
| 目标与重定向 | `redirectdamagefn`、`ShouldRecoil` | 按玩法决定是否允许目标仍拒绝本次能力 | 无效目标、骑乘重定向和明确拒绝不能误判为命中 |
| 闪避 | `attackdodger:CanDodge` | 本次标记期间返回假 | 冷却和闪避动画仍保持原状态 |
| 护甲 | `inventory:ApplyDamage` | 标记期间返回原普通伤害和原 `spdamage` | 不扣护甲耐久，不重复发抵抗表现 |
| 骑乘 | `saddler:ApplyDamage` | 标记期间返回原普通伤害和原 `spdamage` | 坐骑仍然有效，不能被误判为已吸收 |
| 类型抗性 | `damagetyperesist:GetResist` | 将小于 `1` 的系数钳到 `1`，保留大于 `1` 的增伤 | 其他 tag 的增伤与减伤仍按乘法叠加 |
| 条件承伤倍率 | `combat:ApplyConditionExternalDamageTakenMultiplier` | 标记期间跳过额外减伤 | 只跳过明确属于本次攻击的条件层 |
| 外部承伤倍率 | `combat.externaldamagetakenmultipliers` | 可保留增伤、跳过减伤，或整体回到 `1` | 选择“只去减伤”时必须保存原始倍率 |
| 目标无敌 | `health:IsInvincible`、`DoDelta` 参数 | 本次能力可传 `ignore_invincible = true` | 是否只对非玩家生效由玩法决定 |
| 位面实体 | `planarentity:AbsorbDamage` | 原样返回传入普通伤害与特殊伤害 | 避免触发错误的“非位面抵抗”表现 |
| 位面防御 | `SpDamageUtil.ApplySpDefense` | 原样返回特殊伤害表 | 清空表要写成 `nil`，不要留下空表 |
| 吸收与固定减免 | `health:DoDelta` | 传 `ignore_absorb = true` | 不改变治疗和零值刷新路径 |
| 单次限伤 | `health.maxdamagetakenperhit` | 只在本次调用期间设置 `_ignore_maxdamagetakenperhit` | 保存旧值，异常和嵌套调用都能恢复 |
| 共同落值 | `health:SetVal` | 需要绕过 `minhealth` 或统一落值钩子时才替换 | 自行补齐上限、死亡事件、击杀统计和副作用 |

“大部分情况下生效”来自覆盖调用实际经过的常见层，不等于无条件的真实伤害。未 hook 的自定义入口、直接字段写入、后加载的实例方法覆盖和独立落值仍可能拦住本次攻击。

### 瞬态标志与实例包装

每次能力调用前建立只属于本次攻击的实体标志，退出时恢复原状态。完整实现要保存函数、实体实例、实体标志和限伤标志的旧值，并用保护调用确保报错也执行恢复。

```lua
-- 仅展示恢复结构；各包装函数和减伤规则由宿主实现。
local function run_attack_with_cleanup(attacker, target, damage, weapon, spdamage)
    local old_attacker = attacker.my_attack_bypass
    local old_target = target.my_attack_bypass_target
    attacker.my_attack_bypass = true
    target.my_attack_bypass_target = true

    local ok, result = pcall(
        target.components.combat.GetAttacked,
        target.components.combat,
        attacker,
        damage,
        weapon,
        nil,
        spdamage
    )

    attacker.my_attack_bypass = old_attacker
    target.my_attack_bypass_target = old_target
    if not ok then
        error(result, 0)
    end
    return result
end
```

若目标侧采用懒包装，第一次遇到实体时保存原方法并替换实例方法，之后只用开关分流。重复安装要检查自己的包装标记，包装函数未命中开关时原样调用旧方法并转发全部参数和多返回值。

```lua
local function wrap_once(target, field, marker, wrapper)
    local component = target.components.combat
    if component == nil or rawget(component, marker) then
        return false
    end
    rawset(component, marker, component[field])
    component[field] = wrapper
    return true
end
```

这是安装顺序示意，调用者仍要提供正确的 `self`、参数和多返回值。若另一个 mod 在之后覆盖同一方法，本次包装会失效；若本次包装覆盖了它，它保存的“原方法”可能已经包含本次逻辑，双方都应支持嵌套链和明确的禁用字段。

目标侧开关应在实际受击入口置位，并在正常返回和报错路径都关闭。包装公开入口时要额外覆盖内部入口；不要只在最终事件处理里关闭，因为目标死亡、重定向或中途报错都可能提前结束。

### 类型抗性与增伤

如果目标是“移除减伤、保留增伤”，类型抗性要分别处理小于、大于和等于 `1` 的系数。把所有结果都强制写成 `1` 会丢掉其他 mod 的弱点增伤；只拦某些减伤则要在标记中携带具体能力类型，不能用一个永久布尔覆盖普通攻击。

```lua
local function bypass_reduction_only(mult)
    if type(mult) == "number" and mult < 1 then
        return 1
    end
    return mult
end
```

多个来源的倍率可能已经乘成最终系数。先确认 `GetResist` 的返回值仍代表总系数，再决定钳制位置；不能只检查某一个来源 tag。

### 位面双开关

位面免疫可以用两个被击方开关覆盖两条常见入口：

1. `SpDamageUtil.ApplySpDefense` 对目标返回 `nil`，表示当前特殊伤害表没有穿透量。
2. 目标 `Combat:GetAttacked` 在进入后续处理前把 `spdamage` 清为 `nil`。

```lua
local SpDamageUtil = require("components/spdamageutil")
local old_apply_sp_defense = SpDamageUtil.ApplySpDefense

SpDamageUtil.ApplySpDefense = function(ent, tbl, ...)
    if ent ~= nil and ent.my_planar_immune then
        return nil
    end
    return old_apply_sp_defense(ent, tbl, ...)
end
```

目标入口使用实例包装时，仍要保存原 `GetAttacked` 并在未开启免疫时透传。两种开关都必须支持多来源语义；若多个系统都能设置免疫，关闭其中一个不能直接清掉共享布尔。重连和读档后要按权威状态重建，而不是保存一个无法清理的临时标记。

这两个入口能覆盖原版受击链汇入的 `spdamage`，不能证明所有第三方自定义伤害都被拦截。绕过两个 Combat 受击入口、直接修改特殊伤害表、调用自定义落值或写血量的能力仍要按实际路径另测。另一个常见错误是把 `ApplySpDefense` 的“返回 `nil`”写成空表：当前结算会继续读取空表，语义和多返回值都不稳。

### 自定义受击链与落值

若目标原版入口被锁死，可以按调用方合同增加并行方法，但必须自行补齐：

- 目标有效、阵营、友伤和 PvP 检查。
- `lastattacker`、受击时间、攻击类型和事件。
- 攻击者的 `killed`、掉落归属和 `onhitother`。
- 普通伤害与特殊伤害的分别处理。
- 血量上限、黑血惩罚、生存线和死亡事件。
- 重定向、目标移除、异常恢复和重复命中。

直接复制当前 `GetAttacked_Internal` 的固定行数，会在游戏更新后漏掉新阶段。更稳妥的是复用原版可调用方法，只在明确位置用条件短路；必须复制时记录复核版本，并把每个保留/删除的阶段写成验收项。

自定义落值若绕过 `DoDelta`，还要自己决定是否调用 `SetVal`、是否发送 `healthdelta` 和 `ondelta`、是否处理 `minhealth` 以及返回值代表什么。只写 `currenthealth` 会跳过 Replica setter 的同步，HUD、repairable、死亡判定和网络状态可能不一致。

## 防御端

防御端先判断攻击落在哪一层。每种保护只覆盖自己的共同入口；把所有保护都堆在同一方法上，通常只能拦住一部分攻击。

### 血上限、黑血与当前血量

当前 `Health:SetMaxHealth(amount)` 会同时写入 `maxhealth` 和 `currenthealth`，再刷新 HUD。攻击方若直接写 `maxhealth`，不会自动经过该方法，也不会同步当前血量和界面。

有效上限还要考虑 `penalty`：`GetMaxWithPenalty()` 使用 `maxhealth - maxhealth * penalty`，当前黑血惩罚有 `0.75` 的上限。因此只守 `maxhealth` 不覆盖 `SetPenalty/DeltaPenalty` 提升惩罚的路径；只守 penalty 也不覆盖直接削减上限。

默认只有 `save_maxhealth` 为真时，`OnSave` 才保存 `maxhealth`。重连、读档和跨会话的“永久削减”必须保存恢复依据；不要在加载时先满血再等待后续修正。

### 落值、锁血与击杀入口

| 入口 | 经过的层 | 常见防御是否有效 | 关键边界 |
| --- | --- | --- | --- |
| `SetVal` | 上限、`minhealth`、死亡事件 | `SetMinHealth` 可钳制 | 自定义落值不调用它时无效 |
| `DoDelta` | 无敌、吸收、修改器、限伤，再调 `SetVal` | 包装或修改器可拦截 | `ignore_*` 参数可跳过对应层 |
| `Kill` | `DoDelta`，临时跳过单次限伤 | 无敌和 `DoDelta` 包装仍可能拦截 | 吸收没有被跳过 |
| `ForceKill` | `DoDelta`，临时跳过限伤、无敌和吸收 | 自定义 `DoDelta` 包装仍可能拦截 | 不是直接写字段 |
| 直接写 `currenthealth` | 不经过方法 | 只有字段守卫或外部回滚能处理 | 还会漏掉 setter、事件和 HUD |
| 手动推死亡事件 | 血量可能仍为正 | 字段守卫不足 | 还要处理事件和后续死亡副作用 |

`SetMinHealth(1)` 只保护经过当前 `SetVal` 的落值。自定义落值读取了 `minhealth` 却没有回钳，仍然会死；攻击直接写字段也绕过它。`SetInvincible` 只对未传 `ignore_invincible` 的 `DoDelta` 生效。

保命资源和额外生命应在致死落值前判断旧血量为正且新值非正。消耗、恢复、传送和特效要有确定的提交顺序，失败时不能重复扣资源；资源不足、召唤物失效、重连和正常死亡都要分别验收。

### 字段守卫与 setter

`health.maxhealth` 和 `health.currenthealth` 是 Class 属性 setter。普通赋值会同步 Replica、repairable 和百分比状态；直接 `rawset` 虽然能拦住字段，却会破坏这些副作用。实例守卫应复制旧元表、保留其他元方法，并把最终写入交还给旧 `__newindex`。

```lua
local function install_health_guard(health, resting_max, lethal_floor)
    local old_meta = getmetatable(health)
    if old_meta == nil or old_meta.__newindex == nil then
        return false
    end

    local old_newindex = old_meta.__newindex
    local function guarded_newindex(self, key, value)
        if key == "maxhealth" and type(value) == "number"
            and self._my_resting_max ~= nil
            and value < self._my_resting_max then
            value = self._my_resting_max
        elseif key == "currenthealth" and type(value) == "number"
            and self._my_lethal_floor ~= nil
            and value <= 0 then
            value = self._my_lethal_floor
        end
        return old_newindex(self, key, value)
    end

    local new_meta = {}
    for key, value in pairs(old_meta) do
        new_meta[key] = value
    end
    new_meta.__newindex = guarded_newindex
    if not pcall(setmetatable, health, new_meta) then
        return false
    end

    health._my_resting_max = resting_max
    health._my_lethal_floor = lethal_floor or 1
    return true
end
```

复制模板前还要增加项目自己的幂等标记，保存多个守卫的嵌套关系，并定义谁有权抬高 `_my_resting_max`、谁可以关闭 `_my_lethal_floor`。这里没有直接给出完整安装函数，因为安装时机、多个来源和撤销策略必须与宿主项目一起确定。

守卫会把该实例所有致命字段写入钳回生存线，通常等于全域锁血。它也可能拦掉正常死亡、其他 mod 的复活流程和调试命令。需要精确保护时，应在攻击开始时开启、在结算结束后关闭，并用来源信息决定是否允许死亡。

### 死亡事件盾与最终副作用

字段守卫能阻止 `IsDead()` 变真，却不能撤销已经发出的 `death` 和 `entity_death`。当前 `SetVal` 的顺序是：发两个死亡事件，处理器返回后，才添加 `NOCLICK`、设置 `persists = false`、创建侵蚀任务。只在 `death` 回调里立即清理，会被后续官方步骤再次覆盖。

更稳妥的防御是在致死值进入 `SetVal` 前把血量恢复到安全线。若必须用事件盾，应在下一任务帧检查最终状态并清理；同时核对玩家进度、幽灵/尸体转换、实体移除、掉落、任务和自定义监听是否已经发生。已经完成的这些副作用不能都当作可逆。

死亡事件盾应携带攻击来源，只拦截规则明确允许获救的能力。只看“当前血量大于零”会把正常死亡和外部复活流程一起改写。

### 位面免疫与攻击端的互补

防御端的两个位面开关只覆盖对应入口。攻击端若要在一次能力中穿透它们，需要让目标在本次调用中暂时不命中免疫分支，并在结束、报错和重定向返回后恢复。不要把“位面免疫”写成“任何位面伤害都无法进入”：第三方自定义入口、直接落值和绕过 `GetAttacked` 的路径需要单独处理。

### 防御端验收

- 普通伤害、`Kill`、`ForceKill`、自定义落值、直接字段写入和手动死亡事件分别测试。
- 护甲、骑乘、类型抗性、条件/外部承伤倍率、位面实体和位面防御分别开关。
- 检查 `maxhealth`、`penalty`、`currenthealth`、HUD、Replica 和 `IsDead()` 是否一致。
- 检查死亡事件次数、击杀归属、幽灵/尸体转换、侵蚀、掉落、存档和复活。
- 测试重复安装、嵌套包装、后加载覆盖、目标失效、中途报错和主客机同步。

## 两端组合检查

| 攻击路径 | 主要穿透 | 常见遗漏 | 防御端补位 |
| --- | --- | --- | --- |
| 原版 `GetAttacked` + 瞬态标记 | 已 hook 的常见减伤层 | 未覆盖的自定义入口、字段写入 | 共同落值、字段和事件保护 |
| 并行受击链 | 未复用的原版阶段 | 合法性、事件、仇恨和击杀归属 | 同名入口拒绝、自定义落值保护 |
| 自定义落值 | `DoDelta` 的修改器、限伤、无敌和吸收 | 上限、生存线、事件、返回值和 HUD | 共同落值检查、字段和事件保护 |
| 直接写 `currenthealth` | 全部方法层保护 | 事件、setter、HUD 和统一后置逻辑 | 字段守卫、来源匹配、外部回滚 |
| 手动推死亡事件 | 基于血量为零的常规死亡判定 | 重复事件、幽灵/尸体和侵蚀 | 更早的事件盾和最终副作用清理 |

这些结论来自静态源码与文档审计。游戏内伤害、主客机、真实客户端、重连读档和第三方组合仍需在授权环境中验证。

源码锚点：

- `class.lua:28-45,83-114`：属性 setter 与 `__newindex`。
- `components/health.lua:154-186,503-648`：保存上限、落值、无敌、吸收、限伤、强制击杀和死亡副作用。
- `components/combat.lua:568-713,1227-1268`：受击入口、减伤阶段、事件、击杀归属和条件倍率。
- `components/spdamageutil.lua:95-115`：位面防御结算与 `nil` 语义。
- `components/inventory.lua:408`、`components/saddler.lua:61`、`components/damagetyperesist.lua:32`、`components/planarentity.lua:7`、`components/attackdodger.lua:30`：常见减伤入口。
