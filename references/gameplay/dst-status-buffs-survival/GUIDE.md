---
name: dst-status-buffs-survival
description: Implement Don't Starve Together survival stats, buffs, debuffs, timed modifiers, hunger, sanity, temperature, moisture, speed, damage-over-time, and status visuals. Use when creating status-effect prefabs, using debuffable, modifying player or creature stats, stacking timed effects, or synchronizing status UI and FX.
---

# DST 生存属性、Buff 与 Debuff

定义效果的权威状态、叠加策略、持续时间、移除条件和客户端表现，保证应用与撤销对称。

## 工作流

1. 写出效果目标、持续时间、叠加或刷新规则、数值来源、死亡/换角色/睡眠/下线行为和 UI 需求。
2. 优先使用 debuffable 与独立 Debuff Prefab 管理有生命周期的效果；简单瞬时变化直接调用对应组件。
3. 为 health、hunger、sanity、temperature、moisture、locomotor 或 combat 修改使用可移除的唯一 source key。
4. 在 attached、extended、detached 和 OnRemoveEntity 路径对称注册与撤销事件、任务、标签、数值和 FX。
5. 服务器维护剩余时间与玩法数值；客户端通过 netvar、Replica 或跟随 FX 显示。
6. 明确多个来源、重复施加、免疫、净化、离线时间和保存重载规则。
7. 测试死亡复活、换洞穴、骑乘、装备切换、极端数值和效果同时结束。

## 源码锚点

- components/debuff.lua、debuffable.lua 与 EntityScript:AddDebuff。
- components/health.lua、hunger.lua、sanity.lua、temperature.lua、moisture.lua。
- components/locomotor.lua、combat.lua 及状态类 Prefab。
- components/playervision.lua（强制夜视 / ColourCube 渲染覆盖）。
- widgets 中 badge、overlay 与状态提示。

## 按需参考

- [buff-nightvision.md](references/buff-nightvision.md) - 夜视 Buff：playervision 强制夜视栈 + ColourCube 全屏覆盖（纯客户端透明实体写法，或 `net_bool` + 事件回调的状态开关式写法）。
- [eating-stat-modification.md](references/eating-stat-modification.md) - 进食三维修改：eater 吸收系数（正负一起改）与符号过滤 hook（只改正向/只改负面）。
- [carried-passive-buffs.md](references/carried-passive-buffs.md) - 携带被动能力：周期读携带物内容并主动施加，暖石恒定体温(`SetTemp`) + 喂火把夜间/洞内光照，含睡眠暂停与 FX 子光源。

## 不变量

- 应用与撤销必须使用同一 source key，不能覆盖其他来源的修饰。
- 周期伤害和属性变化只由服务器执行。
- 视觉 FX 的移除不能反向决定权威 Buff 是否结束。
- 允许目标在回调期间死亡、移除或失去对应组件。

## 验证

- 叠加、刷新、替换、免疫和净化符合规格。
- 保存重载和跨分片后剩余时间与数值一致。
- 多个来源结束时只撤销各自贡献。

## 刷新、撤销与冷却合同

同一个 debuffable:AddDebuff 的 name 已存在时走 Extend；name 是效果身份，不等于所有来源一定独立叠层。先定义同源刷新、异源叠加、替换与上限，再实现 Attached/Extended/Detached。普通服务端 Buff 可不联网；需要夜视/HUD 时设计复制状态或独立表现。

modifier 用同一 source/key 应用与移除。实体 source 的 SourceModifierList 可借 onremove 清理，字符串 source 没有这一自动出口；提前解除仍主动撤销。不用“当前值除回倍率”或把全局倍率重设为 1，避免抹掉其他来源。

计时器存在不证明效果仍有效。外部移除 FX/Buff 后核对缓存实体、任务与 modifier，重施时幂等重建，不能只延后一个已失效效果的到期时间。死亡是否保留、离线是否计时由玩法决定，原版某个 foodbuff 的死亡清理不是通用规则。

物品冷却优先核对 rechargeable:IsCharged()/Discharge(seconds)。服务端先验证业务，成功后开始冷却；显示充能进度不等于禁止使用。读档恢复由组件合同与项目政策共同决定。

当前安装 `759671` 的 `rechargeable` 还有三个容易混用的点：`SetChargeTime(t)` 修改基础充能秒数，`SetChargeTimeMod(source,key,mod)` 以来源叠加“乘在总时长上的增量”（mod 是小数增量，不是最终秒数），`GetRechargeTime()` 返回应用增量后的秒数。`OnSave` 只在未充满时保存 `chargetime` 与 `charge`；业务需要保存额外状态时另行设计。每次实际数值变化推送 `rechargechange {percent, overtime}`，只有跨过“充满/放电”边界才调用对应回调。

## 区域减速的双端筛选

`honey_trail` 把服务器权威筛选和客户端预测筛选拆成 `server_exclude_tags` 与 `client_exclude_tags`。服务器在范围内查找带 `locomotor` 的目标，按服务器标签表排除并真正施加临时地面速度倍率；客户端只检查本地玩家，用另一套标签过滤表现或预测。两套标签当前不同，例如服务器排除飞行、离场与特定 Buff，客户端还侧重幽灵状态。

若效果改用 `registered_tags` 覆盖搜索，服务器会走 `FindEntities_Registered`，普通 `server_exclude_tags` 不再自动套用，并可由 `filterfn` 继续筛选。客户端过滤不决定远程玩家是否真的减速。自定义同类效果应分别声明权威条件与本地表现条件，验证主机、客机、预测、最终同步，以及效果移除时两端的对称清理。

本轮核对安装版 `components/rechargeable.lua:1-166`、debuffable.lua、debuff.lua；来源提炼自 [战斗与 Buff 参考](../../engineering/dst-mod-engineering/combat-buffs-containers.md)。验证外部删除后重施、两个来源先后结束、施法失败不扣费/不刷新冷却、存档缺字段。
