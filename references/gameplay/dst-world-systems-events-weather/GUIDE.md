---
name: dst-world-systems-events-weather
description: Build Don't Starve Together world-level systems, seasons, weather, day and night reactions, global events, spawn managers, and world-state listeners. Use when adding world components, watching world states, controlling periodic world events, weather or temperature, scheduling global encounters, or persisting one-per-world systems.
---

# DST 世界系统、事件与天气

让 TheWorld 上的主机组件管理全局权威状态，以世界状态和事件向实体发布最小变化。

## 工作流

1. 定义系统是世界组件、世界 Prefab 附件、独立管理器还是一次性事件，并明确地表/洞穴范围。
2. 从 TheWorld.ismastersim 主机分支创建权威管理器；需要客户端表现时声明最小网络字段。
3. 用 WatchWorldState 订阅 isday、season、israining 等变量，并在初始化时主动应用当前值。
4. 周期事件使用可保存计时或世界设置计时器，明确暂停、长更新、回滚和配置覆盖。
5. 生成实体前检查世界、地形、玩家距离、密度、唯一性和已有实例；结束时清理关联对象。
6. 跨分片共享时选择 Shard RPC 或 shard 组件，并定义主分片决策和分片不可用行为。
7. 测试新世界、旧存档、地表、洞穴、空服务器、多玩家分散、季节跳转和回滚。

## 源码锚点

- prefabs/world.lua、world_network.lua 及世界初始化 Prefab。
- components/seasons.lua、weather.lua、caveweather.lua、worldtemperature.lua。
- entityscript.lua：WatchWorldState 与事件。
- worldsettingsutil.lua、worldsettings_overrides.lua：世界设置。
- components 中各类 manager 与 spawner。

## 按需参考

- [portable-cross-world-migration.md](references/portable-cross-world-migration.md) - 便携跨世界迁移：扫描 `ShardPortals` 找最近已链接传送门，`ms_playerdespawnandmigrate` 跨碎片，海洋漩涡出口上岸演出特判，含防重复锁与确认弹窗。
- [weather-control-via-world-events.md](references/weather-control-via-world-events.md) - 通过世界事件改变天气：`ms_setmoonphase` 改月相、`ms_forceprecipitation` 降雨/停雨（可顺带 `AddSoilMoistureAtPoint` 浇田）、`ms_startlunarhail` 起月雹（停止需取内部 upvalue）、`moonstormmanager:StartMoonstorm/StopCurrentMoonstorm` 月亮风暴，及 `spellbook` 轮盘 + RPC 的服务端执行链路。

## 强制重排猎犬下一波

世界事件 `hounded_forceplannewattack` 会进入 `hounded` 的 `ForcePlanNewAttack`。事件 data 可选：

- `multtimetoattack`：把本次计算出的等待时间乘上该倍率。
- `choosemintime`：与原待攻击计时比较，保留更短的一项；不提供时以本次计算值重设。

事件只重排下一次攻击计划，不会直接生成猎犬。原版 atrium ritual organ tracker 和 ritual organs 会使用它协调仪式节奏；复制时不要把原版 Boss 的具体倍率当成通用默认值，并验证空服务器、已有待攻击计时、保存重载和取消事件。

## 酸雨伤害覆写与生成落点

`acidlevel:SetOverrideAcidRainTickFn(fn)` 设置一个单次酸雨 tick 的伤害覆写函数，`GetOverrideAcidRainTickFn()` 读取它。回调发生在降雨率已乘入基础健康伤害之后；返回非零数字会替换健康伤害，返回 `nil` 保留原值，返回 `0` 跳过这次健康伤害，负值可表示治疗。它不阻止前面的酸值累积、装备腐蚀和库存腐坏，也不能替代 `rainimmunity` 或整次 tick 的忽略标记。Rocky 一类实体使用返回 0 的覆写实现免疫，但接口本身可用于普通角色和自定义规则。

运行时在陆地上生成世界实体时，不要直接把随机角度乘距离后的坐标当成最终落点。当前 `shadowcreaturespawner` 使用 `FindWalkableOffset` 在目标附近寻找合法偏移；找不到合法位置时本轮不生成，而不是把实体放进水中或障碍。自定义生成器应使用当前版本匹配的可行走/可游泳查询，保留失败安全退出，并再检查平台、目标距离、密度和唯一性。

最近地图图标的查询也属于资格筛选：当前 `FindClosestMapIconInRangeSq` 在传入 `restricted_doer` 后，会用图标限制、所有者以及 `alwaysoutsidevrs` 对应的 VRS 可见性先过滤候选，再比较距离。实现“最近可到达/可见目标”时应先排除当前玩家看不到的图标；先取全局最近点再检查，会错误返回不可用目标。`alwaysoutsidevrs` 只影响地图可见性，不提供传送许可。

## 不变量

- 不要让每个实体各自执行可由一个世界管理器完成的全局扫描。
- 地表与洞穴的 TheWorld 是不同实例，不能假设共享 Lua 状态。
- 回滚可重复外部动作，世界事件必须幂等。
- 世界设置关闭功能时取消任务并处理已存在实体。
- 强制下一波事件与已有计时合并时，明确使用更短值还是直接覆盖；`choosemintime` 不等于“立即生成”。
- 地图图标存在、进入距离和玩家可见是不同条件；最近候选必须在距离比较前完成权限与 VRS 筛选。

## 验证

- 事件在单人、空服务器和多人分散时符合生成规则。
- 保存重载与回滚不会重复唯一实体或奖励。
- 季节、天气和世界设置变化后所有订阅者能恢复一致状态。
- 酸雨覆写的返回值与酸值、装备、腐坏和免疫路径分别验证；生成落点失败时不会产生越界实体。

