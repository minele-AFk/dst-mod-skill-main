# temperature：设置、固定温度与环境修正

源码复核：2026-10-18，components/temperature.lua。

## 当前合同

| 接口 | 作用 |
|---|---|
| GetCurrent() | 当前温度 |
| SetTemperature(value) | 立即夹在 mintemp/maxtemp 内，更新状态与事件；不是平滑动画 |
| SetTemp(temp) | 额外记录 settemp，并在非 nil 时调用 SetTemperature；更新流程按该设定处理 |
| DoDelta(delta, skipinsulation) | 默认根据升温/降温方向使用不同隔热值 |
| SetModifier(name, value) / RemoveModifier(name) | 温度来源修正，按对应消费者理解，不是直接改当前温度 |
| GetInsulation() | 返回冬季与夏季隔热两个值 |
| IsFreezing() / IsOverheating() | 当前冻伤/过热判定 |
| SetTemperatureInBelly(delta, duration) | 进食等内部温度效果，计时与刷新另查 |

旧文把 SetTemp/SetTemperature 描述成“瞬间/过渡”区别错误。固定温度的解除要按 settemp 路径明确清除，不把一次 SetTemperature 恢复默认值当作撤销持续效果。

## 字段与通知

关键字段包括 current、mintemp、maxtemp、overheattemp、hurtrate、inherentinsulation、inherentsummerinsulation。旧表的 min/max/neutral/freezingrate/overheatrate 不是这份组件对应字段，直接赋值可能完全不影响玩法。

SetTemperature 在跨阈值时推 startfreezing/stopfreezing、startoverheating/stopoverheating，并推 temperaturedelta（last/new/hasrate）。监听世界季节/温度应查 WatchWorldState 或实际生产事件，不虚构 weathertick。

## 来源、环境与恢复

SetModifier 使用本机制私有键并在所有结束路径 RemoveModifier；不要抢占其他系统的 fire 等通用键。多个“锁定当前温度”的机制不是天然来源栈，需先定义拥有者/优先级和失效恢复。

温度还涉及世界、装备、湿度、睡眠和固定设定。动态改上限或固定值时分别验证；只改变 current 不证明整个温度系统已冻结。

## 验证

检查升/降温、两类隔热、固定与解除、多个来源、死亡/睡眠、读档与远端显示。当前核实源码合同，未执行游戏温度测试。

[moisture](moisture.md) · [生存/Buff](../../gameplay/dst-status-buffs-survival/GUIDE.md)
