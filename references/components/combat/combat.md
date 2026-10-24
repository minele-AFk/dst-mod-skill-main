# combat：目标、攻击时序与伤害链

源码复核：2026-10-23，本机安装 `759671` 的 components/combat.lua、weapon.lua、spdamageutil.lua、projectile.lua。API 10 不是接口永久兼容保证。

## 常用入口

| 需求 | 当前方法/字段 |
|---|---|
| 默认伤害、间隔、范围 | SetDefaultDamage(damage)、SetAttackPeriod(period)、SetRange(attack, hit) |
| 目标 | SetTarget(target)、DropTarget(hasnexttarget)、HasTarget() |
| 目标筛选 | SetRetargetFunction(period, fn)、SetKeepTargetFunction(fn)、IsValidTarget(target) |
| 发起攻击意图 | TryAttack(target) |
| 实际攻击 | DoAttack(targ, weapon, projectile, stimuli, instancemult, instrangeoverride, instpos) |
| 对外受击入口 | GetAttacked(attacker, damage, weapon, stimuli, spdamage) |
| 普通攻击实际结算 | GetAttacked_Internal(attacker, damage, weapon, stimuli, spdamage, from_doattack) |
| 数值查询 | CalcDamage(target, weapon, multiplier)，返回普通与特殊伤害 |
| 溅射 | DoAreaAttack(target, range, weapon, validfn, stimuli, excludetags, onlyontarget) |
| 伤害来源倍率 | externaldamagemultipliers |
| 受击来源倍率 | externaldamagetakenmultipliers |

这些入口不等价：TryAttack 与 Brain/SG 协作，DoAttack 进入攻击结算；当前 `DoAttack`、范围攻击和投射物命中会直接调用 `GetAttacked_Internal(..., true)`，而 `GetAttacked` 只是转发到内部入口并传入 `from_doattack=nil`。只在实例上包装 `GetAttacked` 会漏掉普通 `DoAttack` 路径；需要覆盖全部原版攻击时，同时核对内部入口或改用事件/更稳定的组件层。不要把每层都执行一次当作“确保命中”。

## 攻击速度与动画

SetAttackPeriod 设置攻击间隔，倍率 m 对应 interval/m。攻击动画前摇、SG 执行帧、busy 和移动锁是其他限制，缩短冷却不自动加快动画或完成动作。

多个装备/效果改同一间隔时要由明确拥有者重算；保存旧值后卸装无条件写回，会覆盖期间另一来源的改变。不要把示例的直接字段恢复推广成通用叠加框架，也不虚构原版 attack-speed modifier 接口。

## 伤害输入与防御

1. 攻击者、武器、坐骑等选择伤害来源，CalcDamage 组合普通与特殊伤害。
2. GetAttacked/GetAttacked_Internal 路径可涉及重定向、装备/坐骑护甲、类型抗性与承伤倍率。
3. planarentity 对普通伤害的处理，与 planardefense/SpDamageUtil 的特殊防御分别结算。
4. 最终生命变化、受击、仇恨、击杀归属与相关事件按对应路径产生。

因此直接 health:DoDelta 不等同普通攻击。spdamage 不可忽略；stimuli="electric" 也不自动等于完整武器电击倍率。固定伤害加值不能无条件用“bonus/base”塞进倍率：base 为零、动态伤害和特殊伤害会改变含义。

`attacked`、`blocked`、`onhitother` 和 `killed` 的数据含 `from_doattack`。普通攻击、范围攻击和投射物命中经 `DoAttack` 结算时为 true；直接调用公开 `GetAttacked` 时为 nil。监听者若把 nil 当成 false，不能据此断言“来自普通攻击”。原始与最终伤害还分别放在 `original_damage`、`damage`、`damageresolved`，不要用三者互相替代。

`death` 与 `killed` 的归属字段不同。受害者 `death` 当前提供 `cause`、`afflicter`、`corpsing`，没有 `attacker`；统计玩家参与者应优先读取 `afflicter`，并用实体字段 `isplayer` 验证。`killed` 推给攻击者，data 含 `victim`、`attacker`、`from_doattack`。直接 `health:DoDelta` 需要把真实来源放到第五个参数 `afflicter`，否则死亡链可能无法识别玩家。

类型抗性不是护甲吸收；damagetyperesist 的 AddResist/RemoveResist 按 tag/source/multiplier/key 合同核对，不存在本文旧例的 SetResist("技能", 0.5)。位面伤害也不是无条件真实伤害。

攻击者是否被记录为远程攻击，当前使用 `IsRangedWeapon(weapon or attacker)`：没有武器时，攻击者自身具备远程特征也能进入远程命中分支。不要把判断写死为“只有 weapon 组件才可能是远程”。当目标没有对应特殊防御且本次 `spdamage.planar` 存在时，攻击者的 `planarentity:OnPlanarAttackUndefended` 才会触发；没有位面伤害、已有位面防御或攻击者没有该组件时都不应调用。这个回调是额外机制/表现入口，不是普通伤害是否生效的开关。

## 范围与投射物

普通 DoAreaAttack 分支排除主目标和攻击者，以 validfn 补项目的 PvP/阵营/随从规则；onlyontarget 分支另查。第三参是武器、第四参是函数，不能把固定伤害数字塞进 validfn。

Projectile:Hit 已调用 combat:DoAttack，自定义命中回调再扣完整伤害会重复。自定义形状/落点需保留普通与特殊伤害、合法目标、平台与归属；调用者先保证中心目标仍有效。`Projectile:Deflect` 只执行偏转回调并按 `keepondeflect` 决定移除，不自动反弹或结算伤害；反弹需要项目自己生成合法的后续攻击。

## 多来源增益

```lua
-- 已确认服务端 inst 有 combat；source/key 属于当前效果。
local combat = inst.components.combat
combat.externaldamagemultipliers:SetModifier(inst, 1.5, "my_mod_power")
-- 对称结束；不清整个列表，不直接把倍率写回 1。
combat.externaldamagemultipliers:RemoveModifier(inst, "my_mod_power")
```

字符串 source 没有实体 onremove 自动清理；提前解除效果也要撤销。不同来源/重复施加政策先定义，不照抄固定平衡数值。

## 特殊攻击、闪避与反伤

熔炉遗留 multithruster 等名字并不构成普通 DST 任意武器自动拥有的完整合同。新增连续穿刺需核对当前动作、SG、组件、公共标签、次数/耐久与中断；不能在所有 equippable 的 PostInit 删除/替换同名组件。

自动格挡先确认真实敌人前摇、伤害发生帧和当前玩家可进入状态。被攻击事件的时机可能已经晚于扣血；不能以一个估算的剩余动画时间保证躲掉所有攻击。瞬时减伤、反伤另定义来源与递归终止条件，默认不全局吞事件。

火焰、持续伤害、反弹与普通攻击不同，按机制明确是否走护甲/归属/无敌及何时结算；不凭“固定伤害”名字推导穿透全部防御。

`CanExtinguishTarget` 要求目标有 `burnable`、正在阴燃或燃烧，且武器或攻击者带 `extinguisher`；`CanLightTarget` 要求武器带 `rangedlighter`，目标可点燃且未燃烧/烧焦。动作收集可在目标没有 `combat` 组件时，仍因这两个能力生成 `ATTACK`。若项目要拦截或扩展点燃/熄灭，必须同时覆盖这两条动作来源；只包装目标 `combat:CanBeAttacked` 会漏掉它们。

`Combat:ShouldAggro` 的 `shouldavoidaggrofn` 语义反直觉：该回调返回 true 时源码允许仇恨，返回 false 时阻止。源码注释明确保留这一历史行为；实现或审查时必须按实际返回值接入，不能按函数名猜。

## 原版定位与验收

当前本机源码锚点：`combat.lua:424-430,593,626,669-686,1037-1067,1212-1235,1252-1270,1320-1333`；`health.lua:565-610,613-648`；`projectile.lua:236-265,532-541`；`weapon.lua:105-120,159-165`。源码复核只证明接口和调用顺序，未启动游戏。

验证普通/位面/护甲/无敌、主目标与溅射、两个来源结束、远端动作与中断、投射物目标移除和击杀归属。更多见 [战斗专题](../../gameplay/dst-combat-weapons-projectiles/GUIDE.md)、[weapon](weapon.md)、[damagetyperesist](damagetyperesist.md)。
