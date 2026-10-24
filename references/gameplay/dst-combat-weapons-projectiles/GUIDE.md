---
name: dst-combat-weapons-projectiles
description: Implement Don't Starve Together combat, targeting, weapons, armor, damage types, planar damage, projectiles, area attacks, and hit effects. Use when modifying combat or health components, attack periods and ranges, damage calculation, hostility, friendly fire, ranged attacks, complexprojectile behavior, or combat stategraphs.
---

# DST 战斗、武器与弹道

由服务器计算命中与伤害，由 SG 控制攻击时序，客户端只表现可复制结果。

## 工作流

1. 定义攻击者、合法目标、阵营、射程、攻击周期、基础伤害、伤害类型、位面数值和友伤规则。
2. 配置 combat、health、weapon、armor、planardamage、planardefense、damagetypebonus 或 damagetyperesist。
3. 让 Brain 选择目标，SG 在正确帧调用攻击，Component 负责数值；避免三处重复实现命中规则。
4. 投射物明确发射者、目标或落点、速度、命中/错过/移除回调、平台坐标和重新瞄准规则。
5. 普通溅射先评估 combat:DoAreaAttack；自定义形状再做有限半径查询，保留普通/特殊伤害结算，并按设计过滤阵营和主目标。
6. 把声音、FX、震屏与服务器伤害分离，确保预测或 dirty 回调不重复造成伤害。
7. 测试无甲/有甲、位面防御、骑乘、睡眠、冰冻、平台、目标死亡和多个攻击者。

## 源码锚点

- components/combat.lua、components/weapon.lua：战斗与武器核心。
- components/health.lua、components/armor.lua：生命与护甲。
- prefabs/weapons/、prefabs/projectiles/：武器和投射物范例。
- stategraphs/ 中的攻击状态和 TimeEvent 伤害帧。

## 不变量

- 伤害只在服务器计算；客户端只同步结果。
- 每次攻击只在所选权威执行点结算；该点可以是 timeline、组件或投射物命中，不机械限定 onenter/onexit。
- 投射物命中回调中再次校验目标仍然存在。
- 明确发射时快照与命中时复查哪些条件；目标有效性、PvP/友伤等不得因动画延迟绕过，语义由玩法决定。

## 2026-10-23 受击入口与偏转复核

本机安装 `759671` 中，`Combat:GetAttacked` 只向 `GetAttacked_Internal` 转发；`DoAttack`、普通范围攻击与 `Projectile:Hit` 实际直接进入内部入口并传入 `from_doattack=true`。因此只包装 `GetAttacked` 的“穿透、免疫、记录伤害”逻辑对普通攻击不完整。优先使用受击事件或目标实例的明确包装入口；若必须包装内部方法，同时保存旧函数、覆盖公开入口和内部入口，并回归普通近战、范围、投射物、重定向、反伤及第三方自定义伤害。

`attacked`、`blocked`、`onhitother`、`killed` 当前包含 `from_doattack`。不要把直接 `GetAttacked` 传入的 nil 误判为一次普通的“非真实攻击”；它也可能来自合法自定义伤害。`ShouldRecoil` 的 `tough` 判定只对 `toughfighter` 标签或 `weapon:CanDoToughFight()` 放行，不能据武器名字猜测。

击杀归属要区分受害者与攻击者收到的事件。受害者 `death` 的 data 当前只有 `cause`、`afflicter`、`corpsing`，没有 `attacker`；记录玩家参与者时优先用 `data.afflicter`，以实体 `isplayer` 验证身份。攻击者 `killed` 才提供 `victim`、`attacker` 和 `from_doattack`。自定义直接扣血应把真实攻击者传入 `health:DoDelta` 第五个参数 `afflicter`，否则可能扣血成功却漏记击杀来源。

`Projectile:Deflect(deflector)` 与 `ComplexProjectile:Deflect(deflector)` 只调用偏转回调，并在 `keepondeflect` 不为真时移除投射物；它们不生成反弹弹道，也不扣伤害。反弹效果要单独检查反射位置、归属、合法目标、重复命中、声音与 FX。

原版标准火把给出了“组件回调 + Prefab 自行反弹”的完整例子：`complexprojectile:SetOnDeflect` 先 `Cancel()`，以偏转者为参照把当前位置沿远离方向外推约 3 格，用短距离、低弧线重新 `Launch()`，再恢复常规水平速度、发射偏移和高弧线；同时 `SetKeepOnDeflect(true)` 防止组件在回调后立刻删除投射物。自定义反弹要沿用“先停旧运动，再建立新弹道，最后恢复后续配置”的顺序，并限制递归偏转、失效目标和重复命中。

多来源特殊伤害应合并后再判断。`SpDamageUtil.CollectSpDamage(ent, tbl)` 会把结果累加进第二参并返回该表；当前 Pure Brilliance 先收集攻击者，再调用 `CollectSpDamage(data.weapon, spdmg)` 把武器收集到同一表，只有合并结果仍含 `spdmg.planar` 才触发。它的内部触发实体还带 `notarget`，HorrorFuel 被偏转后只在实体仍有效时播放闪光。把“攻击者有位面伤害”和“武器有位面伤害”分开判空，会漏掉合并或来源失效的语义。

## 验证

- 不同护甲类型、位面防御和伤害类型叠加后结果正确。
- 同一次攻击不会因两条命中路径重复伤害；不同攻击者各自合法命中仍分别结算。
- 投射物错过、被阻挡和命中后的行为符合预期。

## 位面伤害（Planar Damage）

英文源码用 `planar`，官中翻译为**位面伤害**（不是"平面伤害"），对应"位面伤害 / 位面防御"体系。位面伤害是独立于普通伤害的一套数值，**不受护甲百分比吸收影响**，主要与其自身的位面防御相抵消。

官方源码：`components/planardamage.lua`、`components/planardefense.lua`、`components/planarentity.lua`、`components/spdamageutil.lua`

### 三个核心组件

| 组件 | 职责 |
|------|------|
| `planardamage` | 攻击方的位面伤害数值（基础值 × 倍率 + 加成） |
| `planardefense` | 防守方的位面防御数值（基础值 × 倍率 + 加成） |
| `planarentity` | 位面实体，会压制普通伤害并对非位面攻击产生抵抗表现 |

### 数值公式

```text
-- planardamage.lua
位面伤害 = basedamage * externalmultipliers:Get() + externalbonuses:Get()

-- planardefense.lua
位面防御 = basedefense * externalmultipliers:Get() + externalbonuses:Get()
```

倍率是乘法（默认 1），加成为加法（默认 0）。

### 位面实体压制普通伤害

[planarentity.lua L7-13](file:///d:/mods/scripts/components/planarentity.lua#L7-L13)：位面实体（如部分 Boss）会把传入的**普通伤害**压缩成一个非线性值，使普通攻击收益递减：

```lua
function PlanarEntity:AbsorbDamage(damage, attacker, weapon, spdmg)
    damage = (math.sqrt(damage * 4 + 64) - 8) * 4
    if spdmg == nil or spdmg.planar == nil then
        self:OnResistNonPlanarAttack(attacker)  -- 非位面攻击触发抵抗特效
    end
    return damage, spdmg
end
```

### 位面伤害的防御结算

[spdamageutil.lua L95-115](file:///d:/mods/scripts/components/spdamageutil.lua#L95-L115)：位面伤害在被计入总伤害前，会先减去敌方 `planardefense:GetDefense()`：

```lua
if v > def then
    v = (v - def) * mult + bonus    -- 穿透部分继续结算
else
    v = bonus - (def - v)           -- 防御完全挡下，甚至能抵消附加伤害
end
```

- 当前受击链只在本次 `spdamage.planar` 存在、攻击者具有 `planarentity`，且受击者装备缺少对应特殊防御时，调用攻击者的 `OnPlanarAttackUndefended`。没有位面伤害不会触发；该回调是单独的表现/机制分支，不能直接称为所有位面攻击的“免伤规则”。
- 防御实际数值继续沿 Inventory、SpDamageUtil.ApplySpDefense 与目标组件读取链核对，不能用某个表现回调代替伤害计算。

### 在减伤链中的位置

位面伤害在普通伤害完成护甲结算 `inventory:ApplyDamage`、抗性倍率之后，于 `health:DoDelta` 之前统一并入最终伤害（见 [combat.lua L640-649](file:///d:/mods/scripts/components/combat.lua#L640-L649)）：

```
普通伤害路径：护甲吸收 → 类型抗性 → 承受倍率 → 位面实体压制(planarentity) → +位面伤害(planar) → health:DoDelta
位面伤害路径：数值合并 → planardefense 抵消 → 计入总伤害
```

### 修改示例

```lua
-- 给攻击者加位面伤害
inst.components.planardamage:AddBonus(inst, 30, "my_skill")
-- 给防守者加位面防御
inst.components.planardefense:AddBonus(inst, 15, "my_skill")
-- 移除
inst.components.planardamage:RemoveBonus(inst, "my_skill")
inst.components.planardefense:RemoveBonus(inst, "my_skill")
```

来源：DST 源码 `components/planardamage.lua`、`components/planardefense.lua`、`components/planarentity.lua`、`components/spdamageutil.lua`。

## 按需参考

- [threshold-reflect-damage.md](references/threshold-reflect-damage.md) - 反伤（阈值超标）：单次伤害超过阈值时反弹超出部分 `GetAttacked(nil, damage-threshold)`；attacker 传 nil 防盾反套娃；需阈值/限次/单向之一防互弹（实证：棱镜子圭玄鸟、盾反限次）。
- [deflectable.md](../../components/combat/deflectable.md) - 可偏转实体、owner 与偏转回调；偏转后是否移除由组件决定，反弹要另建攻击。
- `prefabs/torch.lua:325-342,479-487`；`components/complexprojectile.lua:213-220`：保留投射物并由 Prefab 回调重建反弹弹道。
- `components/spdamageutil.lua:52-60`；`prefabs/slingshotammo_debuffs.lua:140-170,230-245`：攻击者与武器的特殊伤害合并、`notarget` 和偏转后有效性。
- [custom-damage-death-layers.md](../../core/dst-hooking-compatibility/references/custom-damage-death-layers.md) - 自定义伤害入口与致死保护分层：先追踪实际受击入口，再核对护甲、抗性、位面、无敌、限伤、血量落值及死亡事件；包含原版标记攻击、自定义受击链和防御端验证矩阵。
- [custom-damage-settlement-and-rollback.md](../../core/dst-hooking-compatibility/references/custom-damage-settlement-and-rollback.md) - 完整结算与回滚：真实伤害穿透模板、类型抗性增伤保留、血上限与落值保护、字段 setter 守卫、死亡副作用和位面免疫双开关。

## 范围、投射物与归属

DoAreaAttack 的普通范围分支排除主目标和攻击者，并保留 CalcDamage 返回的普通/特殊伤害；onlyontarget 是另一分支。IsValidTarget 不自动表达项目所有友伤规则，仍需 validfn/PvP/随从等设计条件。

Projectile:Hit 已调用 combat:DoAttack，自定义 onhit 不再无条件手动扣完整伤害。has_damage_set 影响武器伤害来源，不是防重复开关。直接 health:DoDelta 可能绕过护甲、位面防御、受击、仇恨和击杀归属，不能当普通攻击捷径。

当前远程判定使用 `IsRangedWeapon(weapon or attacker)`，没有武器时可从攻击者自身识别；不要假定远程必定来自 `weapon`。`CanExtinguishTarget` 与 `CanLightTarget` 能参与动作收集，使没有 `combat` 组件但可点燃/熄灭的目标生成 `ATTACK`。目标 `shouldavoidaggrofn` 返回 true 时，`Combat:ShouldAggro` 反而允许仇恨；这一历史语义保留在当前源码。

damagetypebonus:AddBonus 的数值是乘数：1 不变、2 为两倍；planardamage 维护数值，由战斗链结算，不存在可据名字猜出的伤害 DoDelta。

本轮复核安装版 `combat.lua:570-730,1212-1235,1252-1270,1320-1333`、`projectile.lua:236-265,532-541`、`weapon.lua:105-120,159-165`；来源 [战斗参考](../../engineering/dst-mod-engineering/combat-buffs-containers.md)。验证普通近战/范围/投射物均命中同一入口，一个目标的普通/位面/护甲结果、主目标重复、失效目标与归属；此处未执行游戏战斗测试。
