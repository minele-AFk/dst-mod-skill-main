# perishable：腐烂时间与新鲜度

源码签名复核：2026-10-18，components/perishable.lua；原版物品定义示例应查 prefabs/meats.lua、prefabs/veggies.lua，不能按 Prefab 名猜同名文件。

## 当前接口

| 接口 | 合同 |
|---|---|
| SetPerishTime(time) | 设置总时长，同时初始化剩余时间；不是只换上限 |
| SetNewMaxPerishTime(newtime) | 改最大时长的独立路径，具体比例/剩余值效果读当前实现 |
| GetPercent() / SetPercent(percent) | 新鲜度比例；不是独立存储 percent 字段 |
| AddTime(time) | 改剩余秒数，上限按 perishtime |
| ReducePercent(amount) | 减少比例；当前不存在通用 DoDelta |
| SetLocalMultiplier(newMult) | 局部腐烂速率倍率，不等于所有环境修正 |
| StartPerishing() / StopPerishing() / IsPerishing() | 调度生命周期 |
| IsFresh() / IsStale() / IsSpoiled() | 当前阈值判断 |
| SetOnPerishFn(fn) | 完全腐烂的业务回调 |

剩余字段为 perishremainingtime，总时长为 perishtime；当前没有 GetTimeLeft()，需要剩余秒数时核对字段和业务上下文，不把 timer 的接口套过来。

```lua
-- 仅为已有物品服务端初始化片段；完整 Prefab 仍需网络和资源骨架。
inst:AddComponent("perishable")
inst.components.perishable:SetPerishTime(300)
inst.components.perishable:SetOnPerishFn(function(item)
    -- 根据设计处理腐烂产物/移除；这里不假装已有产品资源。
end)
inst.components.perishable:StartPerishing()
```

## 容器、堆叠与事件

组件会按持有者、容器标签、温度等计算速率。冰箱保鲜不普遍等于 StopPerishing；不要监听未经生产端确认的 onenter/onexit 冻结整条腐烂管线。按当前原版容器和组件调用链接入。

perishchange 的 data 含 percent，完全腐烂有 perished；强制刷新还有独立事件。堆叠合并通过 Dilute 等处理剩余时间，不保证每件物品独立隐藏状态。

## 验证

检查地面/背包/冰箱转移、堆叠拆分、相同比例修改、完全腐烂与回调中移除，以及磁盘重启。语法与声明检查不代表腐烂时间已经实机验证。

- [食物与烹饪](../../gameplay/dst-food-cooking/GUIDE.md)
- [stackable](stackable.md)
