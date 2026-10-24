# moisture：湿度数值、来源与通知

源码签名复核：2026-10-18，本机 scripts.zip 的 components/moisture.lua。API 10 是模组加载版本，不证明组件接口永久不变。

## 读取、设置与速率

| 需求 | 当前接口 | 边界 |
|---|---|---|
| 当前值/比例/上限 | GetMoisture() / GetMoisturePercent() / GetMaxMoisture() | 不猜 current/max 字段 |
| 改变量 | DoDelta(num, no_announce) | 权威端执行，仍走组件限制 |
| 设置绝对值 | SetMoistureLevel(num) | 不是 SetMoisture |
| 设置比例 | SetPercent(per) | 先确定 0–1 业务范围 |
| 追加/撤销速率 | AddRateBonus(src, bonus, key) / RemoveRateBonus(src, key) | 同一来源/键；不是 AddMoistureRate |
| 当前速率 | GetRate() / GetRateScale() | 不是最终湿度值 |
| 是否湿身 | IsWet() | 由组件分段状态计算，不冻结为任意单一阈值 |
| 防水来源 | waterproofnessmodifiers | SourceModifierList，撤销自己的来源 |

组件推送 moisturedelta，data 包含 old/new；不是本文旧例的 moisturechange。客户端 HUD 读取实际 Replica/复制事件，不把服务端 PushEvent 当广播。

```lua
-- 已确认目标具备 moisture 的服务端片段。
local moisture = inst.components.moisture
moisture:SetMoistureLevel(50)
moisture:AddRateBonus(inst, 0.5, "my_mod_wet_rate")
-- 效果提前结束、移除组件等出口使用同一来源和键：
moisture:RemoveRateBonus(inst, "my_mod_wet_rate")
```

这些数值仅解释接口，不是推荐平衡值。持续潮湿减速通过 locomotor 的私有来源管理；绑定先刷新一次，随后监听 moisturedelta，并在提前移除效果时撤销。

## 容易造成错误的实现

不要每次湿度变化都 sanity:SetPercent：这会直接重写理智当前值，不是“添加理智下降速率”。需要持续影响时按时间与来源建立对应效果，保留其他来源并定义清理政策。

湿度速率综合天气、装备、睡袋和外部加值；不通过直接改一个不存在的 moisturerate 字段替代这些管线。ForceDry、游泳与防水语义分别追实际调用者。

## 验证与延伸

检查设定/增加/减少、两个来源先后撤销、达到上下界、睡眠、保存重启，以及真实客机初值与通知。当前完成的是源码合同核对和示例语法检查，未运行游戏。

- [生存属性与 Buff](../../gameplay/dst-status-buffs-survival/GUIDE.md)
- [sanity](sanity.md)
