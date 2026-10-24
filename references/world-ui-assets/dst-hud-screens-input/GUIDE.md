---
name: dst-hud-screens-input
description: Create and modify Don't Starve Together client UI: HUD customization (PlayerHud, Controls anchors, status badges, SetModFocus), screen stack, event-driven widgets, focus and input routing. Use when writing widgets, screens, popups, HUD additions, or binding data events to UI.
---

# DST HUD / 屏幕 / 输入 编写

负责玩家 HUD 挂载与数据、Screen 栈和全局输入集成。单个可复用控件的构造、布局和清理从 [Widget 专题](../dst-ui-widget-authoring/GUIDE.md) 进入，避免同时读取两套基础流程。

## 工作流

1. UI 在可视客户端运行；专服用 TheNet:IsDedicated() 等实际入口排除。不要用 not TheWorld.ismastersim 代表全部客户端，房主同时拥有主模拟与 UI。
2. 先判断是持久 HUD、Screen、临时功能控件还是全局输入；扩展点不明时读 UI 补丁选择，组件自身写法交回 Widget 专题。
3. 全屏功能用 Screen，经 PushScreen/PopScreen 管理；已有暂停屏下弹窗核对 PlayerHud:OpenScreenUnderPause，不把 InsertScreenUnderTop 当作自动暂停。
4. 优先在 widgets/controls 的 ClassPostConstruct 中使用 self.owner 与已建锚点 AddChild；若按玩家激活链挂载，先核实实际事件和 HUD 就绪顺序，不把所有角色都当作名为 player 的 Prefab。
5. 绑定时从真实 Replica/netvar 读取初值，再监听实际 dirty/delta 事件。优先事件驱动；没有通知或需要连续视觉插值时再做有边界的更新，不假设服务端事件自动跨网。
6. 角色专属状态条定义 `inst.CreateHealthBadge/CreateSanityBadge/CreateHungerBadge/CreateMoistureMeter` hook。
7. 覆盖控件事件方法时先调 `MyWidget._base.OnControl(self, ...)` 保留默认行为；`return true` 表示消费事件。

## 源码锚点

- `scripts/widgets/widget.lua`：Widget 基类（树/变换/动画/事件/焦点）。
- `scripts/widgets/screen.lua`、`scripts/screens/playerhud.lua`：Screen 与游戏内 HUD。
- `scripts/widgets/controls.lua`：HUD 根容器与 8 个缩放锚点。
- `scripts/widgets/statusdisplays.lua`：角色状态条 hook。
- `scripts/frontend.lua`（TheFrontEnd）：屏幕栈 API。
- `scripts/widgets/templates.lua`：快速做 UI 的工厂。

## 不变量

- `inst.HUD` 是 PlayerHud，`inst.HUD.controls` 是 Controls 根；**没有 `FindWidget`/`AddClassified` 这类 widget API**（classified 是 net 变量系统）。
- 焦点沿 `OnControl` 责任链分发，`return true` 消费；播放/暂停时动画切换用 `UpdateWhilePaused`。
- 不要在服务器端访问客户端 widget 树；HUD 部件挂锚点 root 下才能跟随 `SetHUDSize` 缩放。
- Widget:Kill 移除自己的 inst 与子树；提前停用时撤销本功能任务、输入 handle、外部监听和拖拽，OnStop/ClearScenario 不是通用 Widget 生命周期回调。

## 验证

- 自定义 HUD 部件在对应锚点正确显示、随 HUD 缩放、事件变化时刷新。
- Screen 打开/关闭后焦点恢复正确（`default_focus`/`last_focus`）。
- 控制器/键盘能通过焦点环导航到新增控件。

## 按需资源

| 当前问题 | 只读对应材料 |
|---|---|
| HUD owner 就绪、初值、幽灵/重建、模组焦点与暂停弹窗 | [HUD 挂载与生命周期](references/hud-customization.md) |
| controls/playerhud/临时控件/Screen/frontend 层级选择 | [UI 补丁选择](../../patterns/ui/ui-patch-patterns.md) |
| Widget 定义、树、布局、时间与控件焦点 | [Widget 合同](../dst-ui-widget-authoring/references/widget-contract.md) |
| 热键、映射 control、全局输入与焦点覆写选型 | [输入模式](../../patterns/runtime/input-patterns.md) |
| 输入签名、digital/analog 参数、广播与 handle 清理 | [TheInput 合同](../../systems/theinput.md) |
| Screen 类示例 / 底层栈接口 | [Screen](../../widgets/screen.md) / [TheFrontEnd](../../systems/thefrontend.md) |
| 用户命令、`serverfn`、权限、投票与客户端命令发现 | [用户命令](references/user-commands.md) |

[HUD Widget 模板](assets/hud-widget-template.lua) 只提供自定义 Widget 类、读取函数和本地事件绑定；不附带服务器事件源、Replica 或 Screen。按 HUD 合同挂载到 Controls，业务与复制数据由项目实现。
