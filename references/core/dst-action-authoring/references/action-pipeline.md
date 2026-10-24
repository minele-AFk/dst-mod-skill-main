# Action 完整链路与动作收集回调

## 注册与运行分层

1. `AddAction(id, str, fn)` 定义语义：写入 `ACTIONS[id]`、`STRINGS.ACTIONS[id]` 及模组动作代码映射，返回 Action。
2. `AddComponentAction(type, component, fn)` 提供候选；客户端使用可见标签和 Replica 预检。
3. 玩家选择器或 AI 构造 `BufferedAction`，记录 doer、target、invobject 和落点。
4. 非 instant 动作通过 SG `ActionHandler` 选状态；客户端可预览/预测。
5. 服务器重新验证并执行 `Action.fn`，BufferedAction 完成成功或失败，状态退出清理。

收集器决定是否出现，SG 决定如何表演与何时执行，Action/组件决定权威结果。普通 `doaction` 事件不能替代 ActionHandler 注册。可复制的注册示例见 [动作实战](../../../patterns/action/action-practical-guide.md)。

## Action 字段与注册形式

当前 `actions.lua` 的 `Action` 构造器接受一个数据表；位置参数已弃用。常用字段包括：

```lua
local action = Action({
    priority = 0,
    rmb = true,
    distance = 2,
    mindistance = 1,
    instant = false,
    mount_valid = false,
    encumbered_valid = false,
    ghost_valid = false,
    canforce = true,
    rangecheckfn = function(inst, action, target)
        return true
    end,
    customarrivecheck = nil,
    do_not_locomote = false,
    silent_fail = true,
})
```

`AddAction(id, str, fn)` 既可接收三个参数创建动作，也可传入已构造的 `Action` 对象。动作 ID 不会自动转大写；必须与组件收集器、SG ActionHandler 和调用方使用的字符串完全一致。`strfn` 返回 `STRINGS.ACTIONS` 的子键，不能把任意本地化文本直接塞进 `str` 后假设会动态更新。

`priority`、`rmb`、`distance`、`mindistance`、`instant`、`mount_valid`、`encumbered_valid`、`ghost_valid`、`canforce`、`rangecheckfn`、`customarrivecheck`、`do_not_locomote`、`silent_fail` 等字段影响候选排序、输入、距离和失败表现，但不替代服务器业务校验。`canforce` 只与强制动作/距离处理有关，不是通用坐标同步开关。

## 动作收集回调签名（SCENE / USEITEM / POINT / EQUIPPED / INVENTORY / ISVALID）

以下为当前 `componentactions.lua` 的参数形状；`inst` 是提供该组件动作的实体，不一定是玩家。

| 类型 | 交互入口 | 回调参数 |
|---|---|---|
| SCENE | 空手点击世界对象 | `inst, doer, actions, right` |
| USEITEM | 物品对世界对象 | `inst, doer, target, actions, right` |
| POINT | 物品对地面点 | `inst, doer, pos, actions, right, target` |
| EQUIPPED | 装备对自身/目标 | `inst, doer, target, actions, right` |
| INVENTORY | 物品栏上下文 | `inst, doer, actions, right` |
| ISVALID | 检查动作资格 | `inst, action, right` |

前五类只向 `actions` 插入候选，不扣费、不改目标。`ISVALID` 返回布尔，不接收 actions 表；当前 `IsActionValid` 在任一适用 validator 返回 true 时接受，因此不能把一个返回 false 的自定义 validator 当作所有其他来源的否决器。服务器执行校验仍必需。

同一模组、同类型、同组件重复注册会替换该回调；需要多个分支时合到一个 collector，跨模组命名与冲突另外核对。客户端不能直接读取只存在于服务器的 `inst.components`。

## 复用与子系统选择

先核对官方动作语义和对应组件：`HAMMER/CHOP/MINE/DIG/PICK/HARVEST/GIVE/DEPLOY/STORE` 等可复用时无需新建同义动作。具体组件与资格查 `actions.lua` 和 `componentactions.lua`，不能只插入 ID 就认为行为完整。

| 需求 | 起点 |
|---|---|
| 点击世界对象提供上下文操作 | 本文收集器与 Action 链 |
| HUD 按钮开关本地面板 | [UI 模式](../../../world-ui-assets/dst-ui-widget-authoring/GUIDE.md) |
| 按键请求服务端技能 | 输入 + RPC 或已有动作链，见 [联机专题](../../dst-networking-rpc/GUIDE.md) |

## 状态机注册边界

`AddStategraphActionHandler` 是 modmain 环境的注册 API，`ActionHandler` 是动作到状态的映射对象。玩家动作核对 `wilson` 和 `wilson_client` 两条路径；生物按实际 `SetStateGraph` 选择目标。已有状态还要满足它对装备、动画、参数的依赖，不能随便把法术映射到 `shoot`。

自定义状态、钩子选择与预测字段见 [SG 合同](../../../gameplay/dst-stategraph-authoring/references/stategraph-contract.md)。

## 落点、预览与拒绝

`BufferedAction.pos` 是 DynamicPosition；世界落点使用 `GetActionPoint()`，可为空，不当普通 Vector3。`canforce` 与强制动作/距离处理有关，不是通用坐标同步开关。

客户端预测后仍需发送当前动作；过早 ClearBufferedAction 会让预览发送链失去数据。服务器执行时重新核对目标、距离、资源、冷却与物品 GrandOwner；主机本地快速路径走同一业务校验。

最终由 `action.fn`/组件业务返回成功失败。失败或中断撤销本次临时控制；资源、产物、冷却只能在约定的成功点结算，不能在收集器、预测和服务器重复结算。

CASTAOE/spellbook 分别核对载体、owner、选择项和落点：aoespell 回调为 item、doer、pos，onselect 参数是书/载体。支持范围查当前 CanCast，不根据隐藏 FX 案例推导任意实体都支持。

## 症状定位

| 症状 | 优先检查 |
|---|---|
| 动作不出现 | 收集类型、组件动作注册、公共标签/Replica、资格 |
| 出现但不表演 | SG ActionHandler、目的状态、状态标签与距离 |
| 有动画无效果 | PerformBufferedAction 执行点、最终业务返回值 |
| 主机可用客机失败 | Replica/netvar、客户端 SG、预览发送与服务器拒绝 |
| 执行两次 | 预测和服务器副作用、重复时间线/回调 |
| 动作后卡住 | BufferedAction 完成路径、SG 退出与清理 |

2026-10-21 核对本机安装包 `modutil.lua`、`componentactions.lua`、`actions.lua`、`bufferedaction.lua` 及玩家 SG；来源补充见 [动作与输入参考](../../../engineering/dst-mod-engineering/ui-actions-controls.md)。未进行远端鼠标/手柄、预测开关、目标中途删除和服务端拒绝的实机验收。
