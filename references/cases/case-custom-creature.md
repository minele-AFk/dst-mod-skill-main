# 设计案例：随从生物的完整职责链

本例用于串联 Prefab、Follower、Brain、SG 与保存。旧稿中的 CombatNodes、StateGraphEventHandler、SG:AddState 及若干睡眠/跟随方法没有对应的通用 DST 合同，不能作为可运行成品复制。

## 规格与文件

保留的能力范围：跟随、战斗/工作模式、升级、掉落、网络和读档。资源、数值、目标阵营与死亡政策由项目确定，不能把案例私有名称和 TUNING 当内置数据。

| 文件/系统 | 责任 |
|---|---|
| Prefab | 公共网络/动画/标签、主机组件、依赖声明 |
| 自定义成长组件 | 等级与模式等持久事实，重算派生数值 |
| Follower/Leader | 权威所属关系，换主人/离开时双向一致 |
| Brain | 跟随、恐慌、追击、工作等优先级 |
| SG | 动作实际执行帧、受击/死亡/取消与恢复 |
| Replica/网络字段 | 客户端真正需要的模式/表现，不复制全部服务端表 |

## 关系与 AI

Follower:SetLeader(leader) 建立关系；实际距离移动由 Follow 等 Behaviour 完成，没有 FollowLeader()。睡眠查询使用 IsAsleep 等，主动睡眠为 GoToSleep；不是 IsAwake/Sleep。攻击用 TryAttack/SG 的实际 DoAttack，而不是不存在的 combat:Attack。

Follow 的目标可以是返回当前 leader 的函数，避免构造时捕获 nil 后永远不变。没有 leader、leader 移除或跨分片时按已定政策等待、解除或重建。不要把添加 follower 标签当作建立关系。

Brain 建树后 AddBrainPostInit 才执行；重启/休眠可能重建。优先插入当前树的窄补丁并幂等，保留恐慌、死亡和无目标的兜底。

## SG 必须真正可达

SG 文件返回 StateGraph(internal_name, states, events, initialstate, actionhandlers)。它是构造表，不是逐个 AddState 的对象。SetStateGraph 使用文件模块名，PostInit 使用内部名；二者核实后再注册。

工作模式要有对应 BufferedAction/ActionHandler/执行状态；仅在 Brain 里调用一个“采集函数”不证明动作完成。攻击状态在正确服务端帧结算一次，并为目标失效、受击、取消和死亡提供退出。

## 升级、生命与掉落

保存独立等级、模式及引用，不每次用当前上限乘升级倍率。SetMaxHealth 的当前生命副作用需要明确处理，读档不能先满血再把错误状态留住。组件 OnLoad 不保证跨组件顺序，依赖按后置协调阶段恢复。

死亡、召回、收起、变身与移除不是同一事件；是否掉落、随从是否保存及内部物品去向分别定义。一个出口不重复 DropLoot，不把所有召唤物强制删除当作通用政策。

## 验收链

先验证资源可加载与最小移动，再验证跟随、目标选择、SG 命中、升级保存，最后走远端客户端。覆盖换主人、目标删除、休眠唤醒、保存重启与迁移失败。

本轮是源码合同与文档检查，不代表已有可玩的随从成品。参见 [生物编排](../gameplay/dst-creature-boss-authoring/GUIDE.md)、[随从](../gameplay/dst-followers-mounts-pets/GUIDE.md)、[Brain](../gameplay/dst-brain-authoring/GUIDE.md)、[SG](../gameplay/dst-stategraph-authoring/GUIDE.md)。
