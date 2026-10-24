# StateGraph 合同

## 定义与实例

`State` 接收包含 name 的单个表；模块返回 `StateGraph(name, states, events, defaultstate, actionhandlers)`。定义可被多个实体共用，每个实体的运行实例在 `inst.sg`。

```lua
local states = {
    State {
        name = "idle",
        tags = { "idle", "canrotate" },
        onenter = function(inst)
            -- 需要宿主真实提供 idle 动画；本例不提供资源。
            inst.AnimState:PlayAnimation("idle", true)
        end,
    },
}
local events = {}
local actionhandlers = {}
return StateGraph("my_mod_entity", states, events, "idle", actionhandlers)
```

文件放在 `scripts/stategraphs/SGmy_mod_entity.lua` 时，Prefab 调用 `SetStateGraph("SGmy_mod_entity")`；Mod 钩子针对返回定义的内部 name `my_mod_entity`。模块名与内部名是两种标识，不要求相等。SetStateGraph 会立即进入默认状态，先装配该状态所需的组件。

定义字段为 `sg.states`、`sg.events`、`sg.actionhandlers`、`sg.defaultstate`；运行实例通过 `inst.sg.sg` 引用定义，不使用虚构的 `sg_events/sg_actionhandlers`。

## 对象、时间与状态数据

| 对象/字段 | 契约 |
|---|---|
| `ActionHandler(action, state, condition)` | 动作到状态映射；state 可是字符串或返回状态名/nil 的函数，另有 condition |
| `EventHandler(name, fn)` | 响应事件；注意消费返回值 |
| `TimeEvent(time, fn)` | 时间单位是秒，常写 `n * FRAMES` |
| `FrameEvent(frame, fn)` | 帧数包装，内部乘 FRAMES |
| `SoundTimeEvent(time, sound)` / `SoundFrameEvent(frame, sound)` | 对应时间单位的声音包装，需要 SoundEmitter |
| `State{ name, tags, onenter, onexit, onupdate, ontimeout, events, timeline }` | name 必需；tags 数组转集合，timeline 按时间排序 |
| `onenter(inst, data)` / `onexit(inst, nextstate)` | 进入参数与退出目的状态；按回调实际需要使用 |
| `inst.sg.statemem` | 每次 GoToState 清空，只供当前状态；跨状态显式传 data |
| `inst.sg.mem` | 可跨状态保留，自己管理失效和清理；不自动成为存档数据 |

`SetTimeout(time)` 触发当前状态的 ontimeout；不是要求在 events 注册名为 timeout 的事件。`AddStateTag/RemoveStateTag/HasStateTag/HasAnyStateTag` 操作当前标签；没有通用 `ClearStateTag` 方法。

busy、nointerrupt、caninterrupt、canrotate 等由调用者/handler 检查；它们不会自动阻止所有 `GoToState`。生命、攻击、移动、预测标签要按具体 SG 消费者查证。

## 事件消费

当前状态的 `State.events` 先接收事件；handler 未返回真值时，才继续 SG 全局同名 handler。需要阻止后续处理时显式 `return true`，不能仅凭状态已切换认定消费成功。

事件 data 为表且含 `state` 时，它只限制当前状态 handler 的匹配，不会自动切到该状态；不匹配后仍可能进入全局 handler。timeline 是按状态时间运行的回调，与上述事件分派分开。

## 钩子选择

以下为 modmain 环境 API，参数 stategraph 使用定义内部名。

| 变更 | API |
|---|---|
| 新动作映射 | `AddStategraphActionHandler(stategraph, handler)` |
| 新状态 | `AddStategraphState(stategraph, state)` |
| 新全局事件 | `AddStategraphEvent(stategraph, event)` |
| 修改已有定义/处理器 | `AddStategraphPostInit(stategraph, fn)` |

修改已有 ActionHandler 时，`.deststate` 是可调用的目的状态函数；包装前保留旧函数、完整转发参数和返回值，保留不属于本改动的路径。新增状态名避免覆盖已有定义。

## BufferedAction 与执行点

收集器决定动作是否出现；非 instant BufferedAction 通过 ActionHandler 选状态。脑侧可返回 BufferedAction，再交 locomotor:PushAction；状态在约定时间调用 PerformBufferedAction。普通 doaction 事件不能替代该映射。

伤害/消耗可位于 timeline、组件或投射物命中，选一个正确结算点。单纯 UI 按钮不因此需要 SG。动作分层见 [Action 完整链路](../../../core/dst-action-authoring/references/action-pipeline.md)。

## CommonStates 复用

常见系列在 `stategraphs/commonstates.lua`，按宿主动画、组件和 handler 所需目标状态选择：

- `AddIdle`、`AddSimpleState`、`AddSimpleActionState`：空闲/单状态/缓冲动作。
- `AddRunStates/AddWalkStates` 及 Simple 版本：移动状态。
- `AddSleepStates/AddSleepExStates`、`AddFrozenStates`：睡眠/冻结。
- `AddCombatStates/AddHitState/AddDeathState`：战斗/受击/死亡。

`AddSimpleActionState` 的自定义 timeline 会替换默认 PerformBufferedAction 时间线；提供后须自行包含执行点。`AddCombatStates` 的 attacktimeline 默认为空，添加 attack 状态不等于自动造成伤害。具体签名与配套示例见 [实战指南](../../../patterns/ai/stategraph-practical-guide.md)，设计取舍见 [源自源码的模式](stategraph-patterns.md)。

## 玩家预测与退出

服务端 `SGwilson` 执行权威行为，`SGwilson_client` 负责预览与协调。客户端状态可声明 `server_states` 和 `forward_server_states`；服务器状态可声明 `no_predict_fastforward`，不能把它们当成同一端字段。结合相近官方状态核对 PerformPreviewBufferedAction、ServerStateMatches 和 FlattenMovementPrediction。

不要在发送前清掉必要 BufferedAction，也不要将服务器扣费/伤害直接复制到客户端。每个状态有可达入口和可靠退出；冻结、死亡、目标移除、timeout、取消与强制切换分别考虑。onexit 只撤销自己拥有的临时控制/物理/FX，跨状态资源明确转移拥有者。

| 症状 | 检查 |
|---|---|
| 动作不出现 | Action 收集层 |
| 出现但无动画 | ActionHandler、目的状态存在与进入条件 |
| 有动画无效果 | 权威时间线/PerformBufferedAction |
| 客机弹回或仅主机有效 | 预测状态、server_states、发送与拒绝 |
| 状态卡死 | animover/AnimDone、timeout、退出路径 |
| 中断后失控 | onexit、声音/物理/控制器恢复 |

2026-10-21 核对本机安装包 stategraph.lua、commonstates.lua、entityscript.lua、bufferedaction.lua 和玩家 SG。声明/语法检查不证明动画、远端高延迟、预测开关或网络行为已通过。完整入口见 [SG 专题](../GUIDE.md)。
