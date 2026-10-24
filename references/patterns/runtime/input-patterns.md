# 输入模式：热键、映射控制与 Widget 焦点

本页负责选择输入入口；完整注册/回调签名、分派顺序与句柄清理由 [TheInput 合同](../../systems/theinput.md) 统一维护，不再保存第二份 API 清单。

## 按输入所有权选择

| 需求 | 入口 | 需要核对 |
|---|---|---|
| 一个本地进程热键 | AddKeyDownHandler/AddKeyUpHandler | 聊天、当前屏、暂停、重复注册；指定键回调无参数 |
| 真正需要原始 key/down 流 | AddKeyHandler | 不假定与映射 control 相同，也不依赖回调注册顺序 |
| 主/次操作、确认/取消等可重绑操作 | Widget/Screen OnControl，或 AddControlHandler | 优先尊重玩家映射；全局特定 control 回调为 digitalvalue、analogvalue |
| 当前聚焦控件内的鼠标/键盘/手柄 | OnControl/OnRawKey/OnMouseButton 等覆写 | 保留基类与未消费路径，不另建永久全局 handler |
| 本地功能确需全局鼠标/移动 | AddMouseButtonHandler/AddMoveHandler | 屏幕坐标与父级 UI 坐标换算、打开时注册、退出时撤销 |
| 设置页监听重绑 | AddControlMappingHandler | 当前设备/控制/输入 ID 与 hasChanged |
| 文字输入 | 优先现有文字控件；底层用 AddTextInputHandler | 文本焦点、输入法和前端路由，不能用裸键码代替文字流 |

常量取自当前 constants.lua：MOUSEBUTTON_LEFT/RIGHT/MIDDLE/SCROLLUP/SCROLLDOWN 和 CONTROL_PRIMARY/SECONDARY/ACCEPT/CANCEL 等；不维护裸数字映射表。

## 可视端与游戏权限

TheInput 是本地进程输入，不是服务器权威。专服不创建功能输入，房主仍有客户端 UI；not ismastersim 不能代表全部可视客户端。非专服也不保证 ThePlayer 或 HUD 已就绪。

输入若只开关面板，留在 UI；需要技能、物品、资源等真实变化时经 [Action](../../core/dst-action-authoring/GUIDE.md) 或 [RPC](../../core/dst-networking-rpc/GUIDE.md) 发送意图，服务器重新验证。

## 消费与屏蔽

Widget/Screen 的 OnControl 返回 true 可消费该 UI 责任链。TheInput 句柄由 EventProcessor 广播，忽略回调返回值；返回 true 不会撤销其他全局 handler，也不保证屏蔽聊天或原版操作。

当前 Input:OnControl 仅在 FrontEnd 未消费后继续全局 control 事件；鼠标路径先调用 FrontEnd，再广播鼠标句柄，没有同一返回值门槛。根据具体入口检查焦点/聊天/暂停条件，不能套用一个通用“return true 即拦截”口诀。

## 绑定与退出

由明确的 Widget、Screen 或功能对象拥有 handler，在该功能有效时注册、关闭/换绑/销毁时 handle:Remove 并清引用。重复打开、Controls 重建、返回主菜单和重连分别检查；Hide 不自动撤销全局注册。

可复制注册/清理片段、回调参数与查询方法见 TheInput 合同；布局/拖拽见 [Widget 合同](../../world-ui-assets/dst-ui-widget-authoring/references/widget-contract.md)，HUD owner 就绪与重建见 [HUD 合同](../../world-ui-assets/dst-hud-screens-input/references/hud-customization.md)。

2026-10-22 核对当前安装 input.lua/events.lua/widget.lua。没有运行键鼠、手柄、重绑、输入法、暂停或重连测试。
