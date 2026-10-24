---
name: dst-followers-mounts-pets
description: Create Don't Starve Together followers, leaders, pets, mounts, domestication systems, and companion persistence. Use when working with leader, follower, follower_replica, rideable, rider, domesticatable, pet brains and stategraphs, ownership, loyalty, mounted actions, or migrating companions across caves and reconnects.
---

# DST 随从、宠物与坐骑

把所有权、跟随 AI、骑乘状态、忠诚度、跨分片迁移和清理设计成一致的关系生命周期。

## 工作流

1. 定义拥有者类型、唯一性、招募、解散、死亡、掉线、跨分片和重新绑定规则。
2. 使用 leader/follower 建立关系；客户端需要显示时通过 follower_replica 或最小网络字段读取。
3. Brain 处理跟随、距离、战斗和回家意图；SG 处理召回、攻击、骑乘与不可中断动画。
4. 坐骑使用 rideable、rider、domesticatable 等现有契约，分别处理上马、下马、被打断和装备。
5. 把长期忠诚、驯化和关联实体引用保存，并在 Component:LoadPostPass、Prefab OnLoadPostPass 或迁移事件中恢复。
6. 拥有者移除时根据设计选择等待、传送、解除、保存或销毁，避免孤儿实体。
7. 测试多个玩家争抢、断线重连、死亡复活、洞穴迁移、远距离和坐骑上的自定义动作。

## 源码锚点

- components/leader.lua、follower.lua、follower_replica.lua。
- components/rideable.lua、rider.lua、rider_replica.lua、domesticatable.lua。
- brains/ 与 stategraphs/ 中 beefalo、chester、宠物和跟随者范例。
- components/migrationpetsoverrider.lua、entitytracker.lua。

## 不变量

- 服务器拥有关系权威，客户端不能自行认主或上马。
- 同一随从不得同时属于多个 leader，切换前先解除旧关系。
- 跨分片恢复必须处理主人或宠物任一方缺失。
- Brain 的传送追赶要检查平台、地形和可见性。

## 验证

- 关系建立、切换和解除不会留下双方残余引用。
- 保存重载、断线和换洞穴后按设计恢复。
- 骑乘中的动作、受击、死亡和强制下马都能回到合法状态。
