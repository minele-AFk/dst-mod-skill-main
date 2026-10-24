---
name: dst-shards-caves-portals
description: Implement Don't Starve Together shard, surface and cave coordination, portals, player migration, and cross-shard state. Use when adding AddShardModRPCHandler logic, synchronizing world data across shards, handling cave entry and exit, migrating companions or entities, or debugging features that work only on one shard.
---

# DST 分片、洞穴与传送

把地表与洞穴视为独立服务器和独立 TheWorld，只通过持久数据或明确的 Shard 通信交换状态。

## 工作流

1. 列出每项状态的拥有分片、复制方向、冲突处理和分片离线时的行为。
2. 本分片玩法保留在本地世界组件；需要跨分片时使用 Shard RPC 或现有 shard 组件契约。
3. 发送消息包含最小稳定 ID 和纯数据；接收端验证 namespace、来源、版本、实体存在与重复消息。
4. 门户或迁移流程在离开前保存必要状态，在目标分片生成后重建引用，不跨服务器保存 EntityScript。
5. 玩家、宠物、坐骑或专属实体迁移分别处理成功、超时、目标不存在和返回原分片。
6. 世界唯一事件明确单一权威拥有者（常见为主分片），其他分片缓存或请求，不并行做最终裁决。
7. 测试仅地表、地表加洞穴、洞穴重启、消息延迟、玩家往返、回滚和版本不一致。

## 源码锚点

- shardnetworking.lua、shardindex.lua、shardsaveindex.lua。
- networkclientrpc.lua：AddShardModRPCHandler 与 SendModRPCToShard。
- components/shard_*.lua、components/migrationpetsoverrider.lua。
- 洞穴入口、出口和玩家迁移相关 Prefab。

## 不变量

- 不同分片不能共享 Lua 表、GUID 或任务句柄。
- Shard RPC 同样视为不可靠边界，处理重复、过期和目标缺失。
- 不要让两个分片同时对同一世界唯一状态作最终决定。
- 分片关闭不能阻塞主服务器核心更新循环。

## 验证

- 状态在地表和洞穴分别重启后仍能收敛。
- 玩家快速往返不会复制物品、宠物或奖励。
- 消息缺失或重复时系统可恢复并记录可诊断信息。

## 通信需求与一致性

先问状态是否真的跨分片共享：单分片局部功能不增加 Shard 服务；迁移数据优先检查原版迁移记录；非关键显示可接受短暂过期时用版本化快照即可。

只有跨分片稀缺资源、唯一奖励等需要明确权威拥有者、请求 ID、版本、确认、超时和补偿。不要把所有 Shard RPC 都机械包装成复杂事务，也不假设发送成功就是远端业务完成。断线、重试、重启及独立回滚的影响分别定义。

地表/洞穴各有自己的 TheWorld 与 GUID 空间；GUID 可以作为带来源上下文的消息字段，但不能在另一分片当作可直接查到的实体引用。世界唯一状态可选择主分片或其他明确单一权威，未必所有项目都硬编码同一拥有者。

依据 [Shard 决策候选](../../knowledge/dst-engineering-kb/decisions/candidates.md)，为 E1 单案例建议，迁移分支含 E0 待证条件；不声称这里已验证跨分片协议。
