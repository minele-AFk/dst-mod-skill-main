# 设计案例：技能轮盘从 UI 到权威执行

本例保留轮盘布局、选择、鼠标/手柄与施法链的设计经验；旧稿把 Widget.inst 当玩家，在 UI 直接访问主组件，并混入不存在的屏幕/移动方法，不作为可复制成品。

## 先选择原生接入

已有 spellbook/aoetargeting/CASTAOE 能满足需求时先读当前同类物品，不重复造一套输入协议。自定义轮盘有特殊显示或交互需求时，只承担选择、预览和请求。

| 层 | 输入/输出 |
|---|---|
| 数据定义 | 稳定技能 ID、图标、名称、冷却展示、合法载体 |
| Widget | 持有明确 owner 与已复制展示数据；self.inst 是 UI 实体 |
| 输入 | 当前面板活跃时选择/取消；聊天和其他 Screen 保留原路由 |
| 发送 | 技能 ID 与必要目标/落点，不发送最终伤害、价格或资源余额 |
| 服务端 | 请求者、载体归属、技能解锁、距离、冷却、资源、目标再验证 |
| 动作/SG | 原生移动/预测、执行帧与中断 |
| 结果 | 成功/失败由真实结果更新表现，不凭点击提前承诺成功 |

## UI 树与布局

用 Class(Widget, ...) 并显式 require 依赖，AddChild 接入 Controls 适当锚点；全屏模态则使用 Screen 并 PushScreen/PopScreen，不是 TheFrontEnd:AddScreen(Widget(...))。

布局用父级局部坐标，动画/插值仅在过渡时 StartUpdating，结束即停。鼠标屏幕坐标、HUD scale 与父级累计缩放分别处理；手柄焦点与鼠标命中是独立入口。

## 施法合同

aoespell:SetSpellFn 的回调是 item、doer、pos；spellbook onselect 的入参是载体。CanCast 对 inventoryitem 的 GrandOwner/玩家载体有实际限制，不假定任意隐藏 FX 都能当法典。

DoAreaAttack 第四参是 validfn，不是伤害数字；locomotor 没有本文旧稿的 Teleport。加伤走 combat.externaldamagemultipliers 的私有来源，不把旧值清为 1。需要冲刺/传送时选择对应 Action/SG/物理合同，先查当前源码。

重复点击、目标消失或服务器拒绝不能导致多扣费、假冷却或卡在瞄准；主机快速路径同样验证。

## 清理与验收

保存 TheInput handler，面板关闭、失焦、Controls 重建和 Kill 时结束拖拽/更新/监听；Widget 被移除不会自动撤销注册在长寿命外部对象上的全部资源。

验证远端鼠标/手柄、初次复制、预测开关、取消、资源不足、非法目标、重复输入与重连。普通 Lua 与静态检查不能证明真实按键已经到服务器或动画正确。

- [HUD/输入](../world-ui-assets/dst-hud-screens-input/GUIDE.md)
- [动作全链](../core/dst-action-authoring/references/action-pipeline.md)
- [施法来源线索](../engineering/dst-mod-engineering/ui-actions-controls.md)
