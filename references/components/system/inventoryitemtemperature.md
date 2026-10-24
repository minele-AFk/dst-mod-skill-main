# `inventoryitemtemperature`：物品温度扩展

> 源码复核：2026-10-23，本机安装 `759671` 的 `components/inventoryitemtemperature.lua` 与 `components/inventoryitem.lua`。未做游戏温度实测。

该组件扩展 `inventoryitem`，用于让单个物品拥有温度、温度范围、绝缘与潮湿温度惩罚。通过 `inventoryitem:EnableTemperature(true)` 建立，服务端包装再连接 `inventoryitem_replica`；不应在客户端或没有 `inventoryitem` 的实体上独立添加。

## 接口

| 接口 | 合同 |
|---|---|
| `SetTemperature(temp)` | 夹到 `mintemp..maxtemp` 并推送 `temperaturedelta` |
| `DoDelta(delta)` | 按冬/夏绝缘缩放增量后写入；不是逐帧环境模拟 |
| `SetMinTemperature(v)` / `SetMaxTemperature(v)` | 修改范围并推送刷新事件 |
| `SetModifier(name, value)` / `RemoveModifier(name)` | 同 name 的加性温度修饰，value 为 0 时移除 |
| `SetMaxMoisturePenalty(v)` / `SetNoWetPenalty(bool)` | 配置潮湿温度惩罚 |
| `SetPercentAtMost(percent)` / `GetPercent()` | percent 相对当前 min/max 范围，不是绝对温度 |
| `GetInsulation()` | 返回冬、夏绝缘，各自下限为 0 |

`OnEntitySleep` 会保存剩余更新时间，`OnEntityWake` 先补算睡眠期间温度，再重建周期任务。组件自身提示：若在实体醒来后启用温度，本次清醒周期不会自动启动更新任务；创建时应在正确生命周期调用 `EnableTemperature`，并显式回归睡眠/唤醒。

`GetTemperatureAtXZ(x,z)` 依次使用最近且覆盖该点的 `temperatureoverrider`、世界 `fumarolelocaltemperature` Replica、最后回退到 `TheWorld.state.temperature`；不能把世界温度直接当成每个物品的当前温度。

## 验证

检查启用前后字段、地面/背包/冰箱转移、堆叠合并、modifier 来源结束、睡眠跨过完整周期、重进存档和远端客户端显示。静态声明与事件存在不代表温度结果已实机通过。
