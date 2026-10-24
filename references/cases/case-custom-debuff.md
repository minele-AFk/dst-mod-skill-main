# 设计案例：可刷新、可撤销的 Buff 系统

原稿的通用管理器混合了来源键、计时与数值备份，重复/异源施加可能覆盖其他效果；它不是原版内置框架。本例保留五类效果的设计经验，优先接入 debuffable/debuff 与来源修饰接口。

## 效果身份与生命周期

先定义同源刷新、异源叠加/互斥、持续时间、净化、死亡、下线、迁移和读档政策。debuffable:AddDebuff(name, prefab, data) 中同一 name 存在时走 Extend，不能同时声称“所有来源独立”。

Attached 应用、Extended 更新/延期、Detached 撤销；外部删除、移除组件和目标移除各自明确出口。Apply/Remove 幂等，旧到期任务不得结束后来新一轮效果。

## 五类效果如何接入

| 类型 | 合同与边界 |
|---|---|
| 减速 | locomotor:SetExternalSpeedMultiplier/RemoveExternalSpeedMultiplier，同一 source/key；不备份另一个来源的标量再写回 |
| 增伤 | combat.externaldamagemultipliers 的来源列表，不直接累乘 damagemultiplier 后恢复旧值 |
| 持续伤害 | 确定是否走 combat、防御和击杀归属；直接 health:DoDelta 只在设计明确其不同语义时选用 |
| 持续理智变化 | 以模拟时间和来源推进，容忍目标缺组件/死亡；不能用 SetPercent 伪装速率 |
| 持续恢复 | 明确是否允许死亡/满值恢复，重复刷新只保留一条任务 |

```lua
-- 示例：source 是本效果实体，target 已由服务端确认具备 combat。
local function Apply(target, source, multiplier)
    target.components.combat.externaldamagemultipliers:SetModifier(
        source, multiplier, "my_mod_buff")
end

local function Remove(target, source)
    if target ~= nil and target.components.combat ~= nil then
        target.components.combat.externaldamagemultipliers:RemoveModifier(
            source, "my_mod_buff")
    end
end
```

这是配对接口，不包含效果 Prefab 或网络传输。实体 source 可由 SourceModifierList 的 onremove 清理，但提前解除仍主动撤销；字符串 source 没有实体移除通知。

## 计时与保存

计时器存在不证明 modifier/FX 仍有效。重施核对当前载体、目标、来源与句柄；外部移除后清缓存或重建实际效果，不能只延后失效任务。

保存效果类型、必要参数和剩余时长等纯数据，不序列化 vars 中的任务/实体/函数。恢复依赖组件按协调阶段应用，避免每次 OnLoad 重复叠加。死亡保留/继续倒计时是玩法政策，不从某个 foodbuff 直接继承。

普通 Buff 可用服务端非网络实体；需要夜视、滤镜或 HUD 时另接复制状态与本地生命周期，不以“服务器添加 playervision”冒充客机可见。

## 验收与来源

核对重复刷新、两个来源先后结束、外部删除、净化、目标死亡/移除、旧档缺字段、离线/分片政策。当前仅完成源码合同与文档检查，未运行游戏效果。

[生存/Buff 合同](../gameplay/dst-status-buffs-survival/GUIDE.md) · [生命周期](../core/dst-events-tasks-lifecycle/GUIDE.md) · [来源线索](../engineering/dst-mod-engineering/combat-buffs-containers.md)
