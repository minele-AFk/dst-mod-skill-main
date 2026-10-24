# 自定义伤害与致死保护的通用分层

> 2026-10-23 兼容性更正：安装版 `759671` 的普通 `DoAttack`、范围攻击和投射物命中直接进入 `Combat:GetAttacked_Internal`，公开 `GetAttacked` 只转发。只包装公开 `GetAttacked` 不能拦截普通攻击。选择入口时同时检查内部入口和受击事件；下文对 `GetAttacked` 的描述保留作历史结构说明。

复杂战斗系统可能同时存在原版受击链、自定义受击链、自定义血量落值和死亡事件保护。攻击效果能否生效，取决于它实际经过哪条入口，以及目标是否在对应层拒绝、限制、吸收或回滚结果。

本文按**攻击端**和**防御端**整理通用机制，并收录常见的自定义入口和保护组合。示例中的 `GetCustomAttacked`、`DoCustomDelta` 和 `SetCustomVal` 是说明用占位名称，不是 DST 原生 API。官方源码重点是 `components/combat.lua`、`components/health.lua` 及常见减伤组件。

## 攻击端

攻击端的目标是让能力按设计命中，同时保留目标合法性、受击事件、仇恨和击杀归属。不能仅凭“直接扣血成功”认定一次攻击链路完整。

### 先确定实际入口

先画清一次攻击从触发到死亡的路径：

1. 攻击入口：公开 `combat:GetAttacked`、普通攻击实际使用的 `GetAttacked_Internal`，还是自定义受击方法。
2. 减伤阶段：护甲、骑乘、类型抗性、外部承伤倍率、位面实体和位面防御。
3. 血量落值：原版 `DoDelta → SetVal`，还是自定义落值方法。
4. 死亡结果：血量是否到零，`entity_death` 和 `death` 是否触发，以及后续的侵蚀、幽灵转换和复活。

不同入口绕过的层不同。攻击端应明确要穿过的防御层，以及必须保留的原版副作用。

### 原版受击链加瞬态标记

需要保留原版受击事件、仇恨和击杀归属时，优先复用公开 `GetAttacked`；若本次要求与普通 `DoAttack` 使用完全相同的内部路径，先核对当前版本的 `GetAttacked_Internal` 契约。两种调用都配合只在本次调用期间有效的标记放行指定减伤层。

```lua
-- 宿主把实际调用和标志恢复封装在同一函数；嵌套调用也能各自恢复。
local function call_with_attack_flags(attacker, target, damage, weapon, spdamage)
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

这是调用方式的示意，宿主侧还必须实现护甲、抗性、位面和血量等对应钩子。只设置标记不会自动穿透任何层。保存并恢复旧标记，可以避免影响后续普通攻击。若宿主允许并发或重入调用，必须给每个实体保存各自的旧值；共享一个临时字段再统一清空，会让外层调用的标志提前消失。若嵌套调用有独立的默认值语义，先判断字段是否存在并恢复缺失状态，而不是一律写回 `nil`。

一种常见实现是在受击入口按武器或攻击者设置实体标记，并在目标组件检查该标记：

- `Combat:GetAttacked`：根据来源设置本次真伤标记，调用原版受击，结束后清除。
- `inventory:ApplyDamage`：标记期间原样返回普通伤害与位面伤害，跳过护甲。
- `saddler:ApplyDamage`：标记期间跳过骑乘吸收。
- `damagetyperesist:GetResist`：把小于 `1` 的减伤系数提升到 `1`，同时保留大于 `1` 的增伤。
- `planarentity:AbsorbDamage`：标记期间原样返回，避免普通伤害被位面实体压缩。
- `SpDamageUtil.ApplySpDefense`：标记期间原样返回，避免位面伤害被位面防御抵消。
- `health:IsInvincible`：标记期间返回假；`DoDelta` 同时传 `ignore_invincible = true` 与 `ignore_absorb = true`。
- `health:DoDelta`：临时设置 `_ignore_maxdamagetakenperhit = true`，保存旧值并在调用后恢复。
- `attackdodger:CanDodge`：标记期间返回假，防止闪避使攻击不命中。

这类攻击仍会进入 `GetAttacked` 的后续流程，因此能保留 `attacked`、`onhitother`、`killed` 等事件。实际生效范围严格等于已经 hook 的层；目标新增的自定义减伤、独立受击方法或直接字段写入仍可能拦住攻击。

如果标记存在实体字段上，`DoDelta` 在消费标记时立即清除，后续伤害层可能看不到它；若只在受击入口首尾清理，嵌套受击可能提前关闭外层标记。应按真实调用顺序确定标记由谁创建、由谁消费、何时恢复，并测试嵌套受击与报错恢复。

### 自定义受击链

若原版入口已被目标或兼容 mod 锁死，可以增加一条并行受击方法。该路径能绕过未复用的原版阶段，但必须自行决定是否保留：

| 语义 | 保留后的结果 | 删掉后的常见结果 |
| --- | --- | --- |
| 合法目标与阵营检查 | 仍遵守敌对、友伤和 PvP 规则 | 可能误伤盟友或无效目标 |
| 受击事件和仇恨 | 目标会反击并触发受击特效 | 伤害生效但 AI 可能不反应 |
| `killed` 与击杀归属 | 击杀者、掉落和统计正常 | 目标死亡但无法可靠归功 |
| 护甲和类型抗性 | 防御能力按设计生效 | 大部分普通减伤被绕过 |
| 位面结算 | 位面攻击与防御正常 | 特殊伤害可能丢失或重复 |
| 单次限伤和无敌 | 高强度防御仍可拒绝攻击 | 可能直接清空大量血量 |

常见自定义攻击链会复制原版 `GetAttacked` 的结构，然后有选择地删除入口检查：

1. 先检查目标是否已死亡；有效目标才继续。
2. 更新 `lastattacker`、`lastwasattackedtime` 和攻击类型。
3. 根据设计跳过护甲、类型抗性、位面实体或目标无敌。
4. 调用自定义血量落值方法，而不是原版 `DoDelta`。
5. 用自定义落值返回的实际变化量生成 `damageresolved`。
6. 血量到零时补发攻击者的 `killed` 和自定义击杀回调。
7. 最后发送 `attacked`、攻击者的 `onhitother` 以及目标被拦截时的 `blocked`。

该路径可以保留仇恨和击杀归属，同时绕开没有复制的减伤。它也可能没有调用原版 `DoDelta`，所以目标在原版血量方法中设置的锁血、限伤、无敌和受击后短时无敌都不会自动生效。设计时必须逐项确认，而不是假定“复制了 GetAttacked 就复制了完整战斗规则”。

若自定义受击入口本身仍按“武器或攻击者标记”分流，还会覆盖两类情况：

- 未携带标记的普通攻击仍可走原版入口。
- 所有携带标记的能力统一走自定义入口，便于形成一致的穿透规则。
- 有明确开关时，可以按武器、角色来源或技能类型选择两条入口。
- 使用自定义入口后，目标的同名声明确认通常优先于原版入口；但仍可能被攻击者、武器或目标入口条件拒绝。

这些条件决定“大部分攻击能生效”的实际边界。攻击端应分别测试标记来源、无标记路径和目标的拒绝条件，而不是只测一条成功样例。

推荐复用原版已有阶段，只在明确需要穿透的位置短路。若整段复制原版实现，应记录复核的源码版本；游戏更新后重新对照，避免新加入的官方结算层被遗漏。

### 自定义血量落值

自定义落值方法可以绕过原版 `DoDelta` 中的吸收、单次限伤、无敌和修改器。一个完整的自定义落值方法通常直接执行以下步骤：

1. 记录旧血量。
2. 按最大生命值和黑血惩罚取得本次上限。
3. 读取 `minhealth`，对过低值做钳制。
4. 发送自定义的 `pre_health_setval` 或同等前置事件。
5. 写入 `currenthealth`。
6. 新值到零时发送 `entity_death`、`death` 和击杀统计。
7. 视设计添加 `NOCLICK`、关闭持久化并安排侵蚀。

自定义落值方法还可能额外发送 `healthdelta` 并调用 `ondelta`。设计时要写清：

- 伤害、治疗和零值刷新是否共用同一入口。
- 是否应用最大生命值与黑血惩罚，是否读取 `minhealth`。
- 是否返回实际变化量，调用方是否把返回值取反作为结算伤害。
- 是否触发 `healthdelta`、`ondelta`、`minhealth`、`entity_death` 和 `death`。
- 死亡事件是否按“旧血量为正、新血量非正”判定。

只复制原版 `SetVal` 的钳制和事件，却删掉 `DoDelta` 的修改器、限伤和无敌，就得到了一条“按正常范围落值，但大多数防御方法无法干预”的路径。它比直接字段写入更完整，也比原版方法穿透更多。

### 直接改字段与死亡事件

直接写 `currenthealth` 或手动推 `death` 可以绕开方法层保护，但也会漏掉或重复：

- HUD 刷新和 `healthdelta`。
- `IsDead()`、`death` 和 `entity_death` 的一致判定。
- 击杀归属、玩家统计和死亡副作用。
- 目标实体已被移除、已进入幽灵状态或处于其他死亡流程的情况。

这种路径适合明确要求突破常规结算的极少数能力。它仍可能被字段守卫、同名自定义方法覆盖或更早的死亡事件拦截，因此不能承诺对任意 mod 绝对生效。

### 攻击端验收

- 分别测试原版受击和自定义受击，确认事件、仇恨与击杀归属。
- 分别测试无甲、有甲、类型抗性、位面实体、位面防御、闪避和玩家无敌。
- 分别测试普通伤害、超过单次限伤、`ForceKill`、自定义落值致死和直接字段致死。
- 检查血量、HUD、`IsDead()`、死亡事件次数、幽灵转换和复活机会。
- 模拟攻击被拒绝、中途报错、目标失效和重复安装，确认临时标记会恢复。

## 防御端

防御端的目标是按设计限制或拒绝伤害，同时让正常死亡、复活和其他 mod 的能力保持可预测。先确认攻击落在哪一层，再选择同层保护。

### 从实际入口反向定位

根据攻击代码定位保护点：

| 攻击经过的位置 | 应检查的防御 |
| --- | --- |
| 原版 `GetAttacked` | 入口标签、目标合法性、护甲、抗性、位面和承伤倍率 |
| 自定义受击方法 | 是否复用原版阶段，是否有独立的拒绝与清理逻辑 |
| 原版 `DoDelta` | 无敌、吸收、修改器、单次限伤和 `minhealth` |
| 自定义落值方法 | 是否读取生存线、是否限制伤害、是否触发事件 |
| 直接写 `currenthealth` | 方法层保护全部失效，只能考虑字段守卫或外部回滚 |
| 手动推 `death` | 血量保护不足，还需要死亡事件盾 |

只看到 `SetInvincible`、`SetMinHealth`、限伤或护甲配置，不能直接认定它覆盖所有攻击入口。

### 入口拒绝

在受击方法开头检查目标标签、攻击者来源或攻击类型。这种方式适合明确拒绝某个类别，并应返回与调用方约定一致的结果，避免调用方把拒绝误判为命中。

来源标记必须成对清理。若使用世界事件或实体标签传递状态，还要覆盖目标失效、中途报错、重连和读档。

### 伤害结算与单次限伤

原版减伤链依次涉及护甲、骑乘、类型抗性、外部承伤倍率、位面实体和位面防御，最后才进入血量方法。只包装最后一层，会漏掉前面的拒绝和减伤。

`SetMaxDamageTakenPerHit` 在 `DoDelta` 中限制单次伤害。官方 `ForceKill` 会临时跳过该限制，自定义落值也可能完全不读取它。因此它只能保护已知路径。

另一个容易误判的点是 Lua 的真值规则：数字 `0` 为真。配置菜单里的“关闭”若返回 `0`，直接写 `if option then` 仍会启用逻辑；必须显式比较 `option ~= 0`、`option > 0` 或按布尔值判断。配置为数值时，应同时测试 `0`、正数和缺失值。

某些防御会同时叠加多道限制：

- 受击入口按标签或来源直接拒绝。
- `SetMaxDamageTakenPerHit` 限制经过 `DoDelta` 的单次伤害。
- 自定义 `DoDelta` 再次按剩余血量或固定数值限制伤害。
- 受击后短暂开启自定无敌，吞掉下一段时间内的 `DoDelta` 伤害。
- `SetVal` 在致命落值时消耗资源或召唤物，把血量恢复为满值。
- 死亡事件盾检查旧血量，取消来自存活目标的强制 `death` 和 `entity_death`。

这些层并非都能拦住所有路径。单次限伤和短时无敌通常只覆盖 `DoDelta`；自定义攻击链、直接落值和直接字段写入可能越过。防御设计必须为每条实际攻击入口分别补齐，不能假定某个强保护会自动覆盖其他入口。

常见防御组合的覆盖关系如下：

| 防御层 | 主要覆盖 | 常见漏口 |
| --- | --- | --- |
| 受击入口拒绝 | 原版和自定义受击方法本身 | 另一条入口、直接血量调用、手动死亡事件 |
| `SetMaxDamageTakenPerHit` | 经过 `DoDelta` 的单次伤害 | `ForceKill`、自定义落值、直接字段写入 |
| 自定义 `DoDelta` 的短时无敌 | 后续经过同一实例方法的伤害 | 自定义攻击链或直接落值 |
| 致命 `SetVal` 时消耗资源保命 | 经过该 `SetVal` 的致命落值 | 自定义落值、直接字段写入、未触发共同入口 |
| 死亡事件盾 | 已发出但对应目标仍存活的死亡事件 | 官方死亡事件之后仍会执行的标签、持久化和侵蚀步骤 |

覆盖关系必须按实际入口核对。攻击端也可能在受击入口保存并强制清除 `ignore_invincible`、`ignore_absorb` 和 `_ignore_maxdamagetakenperhit`，从而让限伤、吸收或无敌在本次伤害中失效；但“临时清除”和“永久覆盖方法”是不同的兼容性代价。

### 生存线与无敌

`SetMinHealth` 通过原版 `SetVal` 限制血量下限；自定义落值可能只读取下限而没有回钳。`SetInvincible` 只对经过 `DoDelta` 且未传 `ignore_invincible` 的伤害生效。

若需要跨入口保护，应在共同落值层检查，或分别为原版和自定义入口增加相同语义。短时受击无敌适合控制连续命中，不能替代对自定义落值的处理。

`Kill()` 与 `ForceKill()` 的边界也不同：两者都从当前血量算出 `DoDelta` 的扣血额并临时跳过单次限伤，但 `Kill()` 仍受无敌影响，`ForceKill()` 同时跳过无敌和吸收。它们仍会进入 `DoDelta`，所以包装该实例方法仍可能拦截；直接写字段或自定义落值则没有这一保证。

### 资源替代与额外生命

在致死落值前消耗召唤物、资源或充能，并把本次血量恢复，可以把“秒杀”转换成有限次数的保命机会。实现时应保证：

- 只在旧血量有效且新值致命时触发。
- 消耗、传送、特效和血量恢复的顺序固定，失败时不重复扣资源。
- 保命次数和资源量有明确上限，能够存档或在重连后恢复。
- 正常死亡和玩家主动放弃复活不会误消耗资源。

该方案属于游戏设计层的保命，不是通用不死保护。攻击若直接写字段或跳过共同落值，仍可能绕过它。

### 字段守卫

直接写 `currenthealth` 会绕过方法层。若玩法明确要求锁血，可为目标 `health` 实例安装只拦截致命下降的 `__newindex`：

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

这个模板只说明实例元表包装的方向，复制前还要按项目处理版本差异。原版 `health` 的 `maxhealth` 和 `currenthealth` 是 `Class` 属性 setter：普通赋值会更新 Replica、repairable 和百分比相关状态，`rawset` 会跳过这些同步。因此包装必须把写入交还给原来的 `__newindex`，不能直接 `rawset(self, key, value)`。也不要只手写 `{ __index = old_meta.__index }`，因为原元表还承载实例方法、类继承和其他元方法。

安装前先确认 `getmetatable(health).__newindex` 存在。当前源码的 `Class` 配置了属性 setter 时才会提供它；不同版本或实例包装若没有该入口，普通赋值本来就不经过 setter，应改用项目明确支持的统一落值入口。

`maxhealth` 守卫只保护直接字段下降，`SetPenalty/DeltaPenalty` 通过独立的 `penalty` 字段改变有效上限，需要另做同层检查。守卫会改变该实例所有直接字段写入的语义，通常等于全域锁血，并可能与已有元表、其他 mod 的守卫及后续替换元表的代码冲突。它不是默认的防秒杀方案。

```lua
local function guard_health_safely(health, resting_max, lethal_floor)
    if health == nil or type(resting_max) ~= "number"
        or type(lethal_floor or 1) ~= "number" then
        return false
    end
    return install_health_guard(health, resting_max, lethal_floor or 1)
end
```

给同一个 `health` 重复安装时，需要项目自己的守卫标记和来源列表。这里把标记写回实例后，当前 `Class` setter 只认识 `health.lua` 声明的属性；其他字段会走旧 `__newindex` 的普通字段分支，不会误触发 HUD 回调。

### 死亡事件盾与回滚

自定义落值可能先把血量钳回下限，随后仍手动推 `death`。字段保护能维持 `IsDead() == false`，却不能自动取消死亡事件。更稳妥的是在致死值进入 `SetVal` 前拦住；事件盾只能作为兜底。

当前 `Health:SetVal` 的顺序是：推 `entity_death`、推 `death`，事件处理器返回后才执行 `CanFadeOut()`，再添加 `NOCLICK`、设置 `persists = false` 并创建侵蚀任务。仅在 `death` 处理器里立即删除标签和恢复字段，会被随后执行的官方步骤再次改坏。若确实必须用事件盾，应在 `death` 处理器登记本帧恢复任务，在下一任务帧清理最终副作用；同时把 `entity_death`、玩家进度统计、幽灵/尸体转换和自定义死亡监听列为需要逐项核对的不可忽略副作用。

即使推迟清理，也不能保证“完全回滚”。处理器可能已移除实体、切换状态、发奖励或改变账号进度。只允许指定来源获救时，应携带来源信息并精确匹配；全局拦截会覆盖正常死亡和其他 mod 的流程。

### 防御端验收

- 入口拒绝：来源匹配、拒绝返回值、标记清理和目标失效。
- 伤害限制：普通伤害、超过限伤、`ForceKill` 和自定义落值。
- 生存线：原版 `SetVal`、自定义落值、直接字段写入和手动死亡事件。
- 保命资源：单次、多次、资源不足、召唤物失效和重连读档。
- 死亡流程：`death`/`entity_death` 次数、幽灵转换、侵蚀任务、正常死亡和复活。
- 兼容性：包装顺序、重复安装、其他 mod 后续覆盖以及主客机行为。

### 两端组合检查

| 攻击路径 | 常见可绕过的防御 | 仍需攻击端处理 | 防御端可补充的位置 |
| --- | --- | --- | --- |
| 原版受击加瞬态标记 | 实际被 hook 的护甲、抗性、位面和吸收 | 标记恢复、未 hook 的自定义层 | 未命中的入口拒绝、字段与事件保护 |
| 自定义受击链 | 原版受击入口及未复用的阶段 | 合法性、事件、仇恨、击杀归属、清理 | 同名入口拒绝、自定义落值保护 |
| 自定义血量落值 | `DoDelta` 的修改器、限伤、无敌和吸收 | 上下限、事件、返回值、击杀处理 | 共同落值检查、字段与事件保护 |
| 直接写 `currenthealth` | 所有方法层保护 | 事件、HUD、统一后置逻辑 | 字段守卫、外部回滚、死亡事件盾 |
| 手动推死亡事件 | 基于血量为零的死亡判定 | 避免与正常死亡流程重复 | 更早的事件盾、来源匹配和副作用恢复 |

这些检查只能证明相应静态路径；真实客户端、主机和客机表现仍需在授权测试环境中验证。

官方源码锚点：

- `components/combat.lua`：`GetAttacked` 的伤害阶段、事件和击杀归属。
- `components/health.lua`：`DoDelta`、`SetVal`、`SetMaxDamageTakenPerHit`、`SetInvincible`、`ForceKill` 和死亡事件。
- `components/inventory.lua`、`components/saddler.lua`、`components/damagetyperesist.lua`、`components/planarentity.lua`、`components/spdamageutil.lua`：常见减伤层。
- 详细结算、穿透模板、字段守卫和位面双开关见 [custom-damage-settlement-and-rollback.md](custom-damage-settlement-and-rollback.md)。
