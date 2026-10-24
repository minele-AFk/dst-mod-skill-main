# follower：所属关系、忠诚与跟随行为

源码复核：2026-10-18，components/follower.lua、leader.lua。

## 关系接口

SetLeader(new_leader)/GetLeader() 管理当前关系，StopFollowing() 解除；AddLoyaltyTime(time)/GetLoyaltyPercent() 处理忠诚，IsNearLeader(dist) 查询距离。关系写入在服务端，客户端通过实际 Replica/复制信息展示。

只添加 follower 标签不会建立所属关系；没有通用 FollowLeader 方法替实体移动。实际移动由 Brain 的 Follow 等行为及 locomotor/SG 完成，目标读取应能响应 leader 更换。

## 忠诚与受击

targettime 是用于计时的目标时刻，不能当作剩余秒数。实际忠诚上限/持续时间取决于字段与调用者，AddLoyaltyTime 不是所有随从永久有效的“喂食接口”。

KeepLeaderOnAttacked/LoseLeaderOnAttacked 的具体政策沿原版调用者确认；不要仅凭肉类食材名认为喂食任何物品都建立跟随。

StartLeashing/StopLeashing 会管理牵引状态并推 startleashing/stopleashing，具体移动与回归效果仍由消费者决定。

## 事件与保存

当前事件包括 leaderchanged（new/old）、gainloyalty/loseloyalty（leader）等，旧表的 newleader/loseleader/leaderattacked 不是本组件在这些路径推送的通用事件。

保存 leader 的引用/稳定身份与必要忠诚依据，LoadPostPass/缓存玩家重绑按实际实现与宿主政策处理；不同分片不能直接使用同一个 GUID 查实体。

主人死亡、掉线、随从变身/召回/移除分别决定保存、解除或重建；切换前后保持 leader 与 follower 双向关系一致，别只改一个 Lua 字段。

## 验证

检查两玩家切换、leader 移除、忠诚到期、Brain 重启/休眠、保存重启与洞穴迁移。组件声明、关系成立与客户端看到的移动分开验收。

[随从编排](../../gameplay/dst-followers-mounts-pets/GUIDE.md) · [生物案例](../../cases/case-custom-creature.md)
