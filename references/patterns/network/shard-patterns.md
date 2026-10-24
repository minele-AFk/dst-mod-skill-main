# 碎片模式

当任务涉及主世界/洞穴运行时边界、碎片感知位置、玩家或物品迁移、集群范围碎片状态或碎片 mod RPC 时，请使用此文件。

如果任务实际上是关于世界生成或主机设置，请改为阅读 `references/patterns/world/worldgen-patterns.md`。
如果任务是单个碎片上的普通客户端/服务器复制，请改为阅读 `references/core/dst-networking-rpc/references/network-contract.md`。

## 核心检查

观察到的官方运行时检查：

- `TheShard:GetShardId()`
- `TheShard:IsMaster()`
- `TheShard:IsSecondary()`
- `TheWorld.ismastershard`
- `Shard_IsWorldAvailable(worldid)`
- `Shard_IsWorldFull(worldid)`

在 `scripts/prefabs/world.lua` 中观察到：

- `TheWorld.ismastershard = inst.ismastersim and not TheShard:IsSecondary()`

实用后果：

- 当逻辑只属于主碎片时，`TheWorld.ismastersim` 不够
- 跨碎片路由通常需要 `worldid`，而不仅仅是位置

## 快速导航

- 只需要知道存储的数据是否属于此碎片
  - 存储并比较 `worldid` 与 `TheShard:GetShardId()`
- 需要可能跨碎片的传送门、楼梯或召回目的地
  - 查看 `worldmigrator`、`recallmark` 和 `Shard_IsWorldAvailable(...)`
- 需要集群总数，而不仅仅是当前碎片计数
  - 查看主碎片聚合模式
- 需要数据在运行时从一个碎片移动到另一个碎片
  - 优先使用碎片 mod RPC 或现有迁移流程
- 需要能在碎片重新连接或保存时间点存活的持久跨碎片传输
  - 在发明自定义协议之前查看 `shardtransactionsteps.lua`

## 运行时世界分割

在官方预制件中观察到：

- `scripts/prefabs/world_network.lua`
  - 网络世界侧分类对象
- `scripts/prefabs/shard_network.lua`
  - 主模拟碎片侧分类对象

观察到的官方形状：

- `world_network.lua` 添加 `AddShardClient()` 和世界侧组件，如 `clock`、`seasons` 和 `worldreset`
- `shard_network.lua` 添加 `AddShardNetwork()` 和碎片组件，如 `shard_players`、`shard_worldreset` 和 `shard_autosaver`

实用后果：

- 集群或碎片范围的簿记默认不属于普通游戏玩法预制件
- 主碎片聚合通常存在于碎片网络组件上

## 同碎片与跨碎片数据

在 `scripts/components/recallmark.lua` 中观察到：

- 标记保存 `recall_worldid`
- 同碎片检查将其与 `TheShard:GetShardId()` 比较
- 仅当目标世界 ID 匹配当前碎片时才返回位置

实用规则：

- 如果保存的标记、死亡位置或传送点可能跨碎片，请同时保存本地坐标和 `worldid`
- 不要在没有拥有它的碎片 ID 的情况下将位置视为全局有效

## 玩家迁移

在 `scripts/components/worldmigrator.lua` 中观察到：

- 玩家激活推送 `ms_playerdespawnandmigrate`
- 物品迁移使用碎片事务流程
- 传送门状态对 `Shard_IsWorldAvailable(...)` 做出反应

在 `scripts/components/playerspawner.lua` 中观察到：

- 消失写入 `player.migration = { worldid, portalid, sessionid, ... }`
- 重生检查保存的 `migration.worldid` 是否与 `TheShard:GetShardId()` 不同
- 迁移宠物在到达后重新定位

在 `scripts/prefabs/player_common.lua` 中观察到：

- `OnSave(...)` 存储迁移数据
- `OnPreLoad(...)` 提前恢复迁移状态
- `OnDespawn(inst, migrationdata)` 在迁移发生时避免正常的丢弃所有物品行为

实用后果：

- 迁移中的玩家与普通消失的玩家不同
- 如果某个功能依赖于死亡位置、物品栏、追随者或宠物，请显式验证迁移行为

## 世界迁移器运行时

在 `scripts/components/worldmigrator.lua` 中观察到：

- `ValidateAndPushEvents()` 引发：
  - `migration_available`
  - `migration_full`
  - `migration_unavailable`
- 链接的传送门通过状态事件暴露碎片可用性和满载状态

在 `scripts/prefabs/migration_portal.lua` 和 `scripts/prefabs/cave_exit.lua` 中观察到：

- 运行时视觉效果监听这些迁移事件

实用规则：

- 如果任务是碎片传送门或跨世界楼梯，请先修补 `worldmigrator` 行为
- 不要在不检查碎片状态的情况下硬编码传送门可用性

## 集群范围计数和主碎片聚合

在 `scripts/components/shard_players.lua` 中观察到：

- 主碎片将本地 `AllPlayers` 与来自 `TheShard:GetSecondaryShardPlayerCounts(...)` 的次级碎片计数相结合
- 然后发布统一的 `ms_playercounts` 世界事件

实用后果：

- 如果用户想要集群范围的玩家总数，在一个碎片上计算本地 `AllPlayers` 是错误的
- 集群总数通常应从主碎片聚合中获取

## 碎片 Mod RPC

在 `scripts/modutil.lua` 中观察到：

- `AddShardModRPCHandler(namespace, name, fn)`
- `GetShardModRPC(namespace, name)`
- `SendModRPCToShard(id_table, ...)`

实用规则：

- 仅在数据必须在运行时跨碎片边界时使用碎片 mod RPC
- 对于单个碎片上的客户端/服务器工作，优先使用普通 mod RPC
- 当现有迁移、持久世界状态或主碎片聚合已解决问题时，优先使用它们

## 内部碎片事务

在 `scripts/components/shardtransactionsteps.lua` 中观察到：

- 官方碎片事务使用 `SendRPCToShard(SHARD_RPC...)`
- 流程跟踪初始化、接受和最终状态
- 设计显式处理保存状态和重新连接安全性

实用后果：

- 此文件是可靠跨碎片传输的权威参考
- 对于普通 mod 功能来说，复制它过于繁重
- 当某个功能真正需要可靠的碎片到碎片传输语义时，将其作为研究参考

## 常见失败点

- 当任务需要集群总数时，只计算了本地碎片玩家
- 存储坐标时没有碎片 ID
- 使用普通客户端/服务器 RPC 解决碎片到碎片问题
- 假设目标碎片始终可用
- 将迁移视为正常消失，并意外丢弃或清除了错误的状态
- 在不检查 `worldmigrator` 状态流程的情况下修补了传送门视觉效果

## 经验法则

- 当前碎片身份：`TheShard:GetShardId()`
- 仅限主碎片的集群逻辑：`TheWorld.ismastershard`
- 跨碎片目的地：保存 `worldid` 并检查 `Shard_IsWorldAvailable(...)`
- 碎片运行时传输：优先使用碎片 mod RPC 或现有迁移流程