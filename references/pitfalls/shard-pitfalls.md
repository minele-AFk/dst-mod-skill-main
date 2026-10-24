# 分片常见陷阱

当逻辑在一个分片上正常工作，但在洞穴、次要分片或迁移过程中出现问题时，请参考此文件。

## 常见失败模式

- 功能在主世界正常但在洞穴中不正常
  - 可能假设了仅主分片状态或本地 `AllPlayers`
- 传送门或召回目标看起来有效但在运行时失败
  - 未检查目标分片的可用性
- 玩家数据在迁移过程中丢失
  - 把消失和迁移当作相同的清理路径处理
- 跨分片操作使用了错误的 RPC 通道
  - 需要分片 mod RPC 或现有的迁移流程
- 保存的位置在错误的分片上重新加载
  - 从未存储或比较 `worldid`

## 实用规则

- 不要假设 `TheWorld.ismastersim` 意味着主分片
- 不要仅从本地 `AllPlayers` 计算集群总数
- 不要在没有分片 ID 的情况下使用同分片位置数据
- 在没有 `Shard_IsWorldAvailable(...)` 的情况下不要承诺跨分片目的地

## 快速排查

- 分片运行时结构不清楚
  - 阅读 `references/patterns/network/shard-patterns.md`
- 普通的单分片复制问题
  - 阅读 `references/core/dst-networking-rpc/references/network-contract.md`
- 迁移和保存行为混合在一起
  - 同时阅读 `references/core/dst-persistence-migration/references/persistence-contract.md`