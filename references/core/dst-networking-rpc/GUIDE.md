---
name: dst-networking-rpc
description: Implement and debug Don't Starve Together multiplayer replication and RPC. Use when separating master simulation from clients, declaring net variables and dirty events, writing component replicas, synchronizing UI, adding server, client, or shard Mod RPC handlers, validating requests, or fixing desync and prediction bugs.
---

# DST 联机复制与 RPC

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

由服务器保存并验证权威状态；客户端只复制展示或预测所需的最小数据。

## 工作流

1. 为每个字段标注权威所有者、读者、更新频率、初始值和能否由现有 Replica 推导。
2. 在所有端创建网络实体；在 SetPristine 前声明直接挂在实体上的 netvar、对应 dirty 监听、客户端初始视觉和必要标签。服务器和客户端必须用相同名称、相同类型声明同一个 netvar，否则实体反序列化可能失败。
3. SetPristine 后让非主机分支返回，主机添加权威 Component、保存逻辑和状态机；公共组件的实际装配按同类原版另核对。已注册为可复制的 Component 会在 AddComponent 内先触发 ReplicateComponent，其 Replica 构造函数可以在此时创建自己的 netvar。
4. 选择最小 net 类型；状态用 netvar，瞬时通知才使用 net_event，并在 dirty 回调中只更新表现或缓存。`set_local` 不触发同步或 dirty，下一次服务器 `set` 会按需要重新标脏；`net_event` 不能替代可重放的当前状态。
5. 客户端需要组件式接口时创建 Replica，并在相关实体实例化前从 modmain.lua 调用 AddReplicableComponent；保持 Replica 方法对缺失数据返回安全值。
6. 按方向选择 AddModRPCHandler、AddClientModRPCHandler 或 AddShardModRPCHandler；在接收端重新校验玩家、实体、距离、权限、冷却和参数范围。
7. 预测与非预测客户端必须汇合到同一服务端动作入口；`preview_cb` 不要绕过服务端 locomotor 直接执行依赖距离的最终逻辑。预测动作必须可由服务器结果纠正；分别测试主机玩家、远端客户端、专服和洞穴分片。

## 源码锚点

- netvars.lua：可用网络变量和 net_event。
- networkclientrpc.lua：Mod RPC 注册、发送、队列和处理。
- entityreplica.lua、components/*_replica.lua：Replica 契约。
- prefabs/ 中含 SetPristine 与 TheWorld.ismastersim 的实体。
- stategraphs/SGwilson.lua 与客户端 SG：动作预测范例。

## 不变量

- 永远不信任客户端传来的实体、坐标、物品、数值或权限声明。
- RPC 需要引用网络实体时直接传 Entity 参数，让引擎在接收端映射实体；发送前确保接收端已经复制到该实体，不要在生成实体的同一帧让 Client RPC 依赖它。禁止跨服务端与客户端传 `entity.GUID` 后再用 `Ents[guid]` 查找，因为两端 GUID/`Ents` 命名空间不能混用。收到实体后仍须在权威端校验其有效性、类型、距离和权限。
- 不要在 RPC 中传递大型表或高频连续状态。
- 不要依赖 ThePlayer 代表服务器请求者；使用处理器提供的 player 或 sender。
- dirty 回调可能在对象初始化的不同阶段到达，必须允许依赖暂缺。
- 跨分片逻辑明确目标 shard，并处理目标不可用。
- 数组类型最多 31 个元素且网络开销高；能用标量、位域或稀疏状态表达时不要传数组。
- `_<component>` 与 `__<component>` 是 Replica 的内部标记，不要手动添加、移除或据此外推完整业务状态。

## 验证

- 加入中的客户端能获得正确初始状态，而不只收到后续 dirty 更新。
- 恶意或过期 RPC 不改变服务器状态并产生可诊断结果。
- 延迟、重复输入、断线重连、换洞穴和服务器回滚后状态一致。

## 按需资源

- 需要与游戏外的 HTTP 服务器通信（QueryServer、字符串压缩与 Python 侧解析）时读取 [query-server-compression.md](references/query-server-compression.md)。
- 需要方向、权威、实体参数与 Replica 选择时读取 [network-contract.md](references/network-contract.md)。
- 需要编写组件 Replica / 表驱动复制 / 网络小字段同步（net_float / net_bool / net_tinybyte / net_event）时查阅 `references/mod-notes/` 下 [mod-dengxian.md](../../mod-notes/mod-dengxian.md)（登仙）与 [mod-tropical.md](../../mod-notes/mod-tropical.md)（热带 §3.16/§4.5）原始笔记。
