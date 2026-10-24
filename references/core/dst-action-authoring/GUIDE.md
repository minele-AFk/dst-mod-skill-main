---
name: dst-action-authoring
description: Create and integrate custom Don't Starve Together actions. Use when adding Action definitions, component action collectors, BufferedAction flows, action strings, range checks, right-click or point actions, stategraph ActionHandlers, client prediction, or diagnosing actions that appear but cannot execute.
---

# DST Action 编写

把动作发现、可用性、客户端预测、SG 表演和服务器执行视为一条完整链路。

## 工作流

1. 定义动作语义、doer、target、invobject、position、距离、优先级、鼠标按钮和是否允许骑乘或平台操作。
2. 用 AddAction 创建 Action（已写默认 STRINGS.ACTIONS 文本，按需覆盖本地化）；动作执行函数在服务器再次验证所有条件。
3. 用 AddComponentAction 把动作加入正确的 SCENE、USEITEM、POINT、EQUIPPED、INVENTORY 或其他收集阶段；收集函数只追加候选，不产生玩法副作用。
4. 为服务器 SG 添加 ActionHandler；玩家预测动作同时核对客户端 SG、预览状态和 server state matching。
5. 管理 BufferedAction 的开始、成功、失败、清除与目标失效，确保物品消耗只发生一次。
6. 复用原版距离和平台坐标模式；客户端显示条件与服务器权威条件保持一致。
7. 测试左/右键、物品栏/世界目标、远端客户端、高延迟、目标移除和动作中断。

## 源码锚点

- actions.lua：Action 定义、距离、执行函数和预测标记。
- componentactions.lua：动作收集类型与组件映射。
- bufferedaction.lua：执行、成功、失败和有效性。
- stategraphs/SGwilson.lua、客户端玩家 SG：ActionHandler 与预测。
- modutil.lua：AddAction、AddComponentAction、AddStategraphActionHandler。

## 不变量

- 动作收集函数不得消耗物品、生成实体或修改服务器状态。
- 客户端请求不能替代服务器的距离、所有权、冷却和目标验证。
- 不要让两个路径同时完成同一个 BufferedAction。
- 自定义动作 ID、字符串键和组件名必须避免与其他模组冲突。
- `invalid_hold_action=true` 会让动作在持有无效/不可持续物品时被取消。当前 `STARTCHANNELING`、`STOPCHANNELING`、`START_CHANNELCAST`、`STOP_CHANNELCAST` 都设置了该字段；包装这些动作或复制相近流程时要保留原定义，不要只凭动作名假定持续交互会自然中断。

## 验证

- 动作只在预期上下文出现，不能执行时不会留下错误光标或状态。
- 主机玩家和远端客户端执行结果相同。
- 中断、目标消失、物品移动和服务器拒绝后 SG 与 BufferedAction 都能复位。

## 按需资源

- 需要完整链路时读取 [action-pipeline.md](references/action-pipeline.md)。
- [feed-to-upgrade.md](references/feed-to-upgrade.md) - 投喂升级（触发机制）：手持物品 `USEITEM` 作用于目标触发升级，`receiver` 组件 + `AddAction` 双层校验 + 满级拦截/存档重放；能力本身不归属本系统，仅作各能力的解锁入口。

- 需要注册示例、动作字段边界和 BufferedAction 回调时读取 [动作实战](../../patterns/action/action-practical-guide.md)。
