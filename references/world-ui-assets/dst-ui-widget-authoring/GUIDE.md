---
name: dst-ui-widget-authoring
description: Create reusable Don't Starve Together UI widgets. Use when subclassing Widget, Image, Text, UIAnim, buttons, lists, grids, spinners, badges, overlays, or custom controls; arranging anchors and scale modes; implementing mouse, keyboard, and controller focus; or managing UI refresh, events, and cleanup. Use dst-hud-screens-input instead for PlayerHud injection, Screen stacks, popups, and global input integration.
---

# DST UI Widget 编写

负责自有控件与控件树。HUD 挂载、弹窗和全局输入先选 [HUD / 屏幕 / 输入专题](../dst-hud-screens-input/GUIDE.md)；补丁层级不明时查 [UI 补丁选择](../../patterns/ui/ui-patch-patterns.md)。源码基线为当前安装包 data/databundles/scripts.zip。

## 工作流

1. 先从用途相近的原版控件开始：静态图文查 image.lua、text.lua，交互查 button.lua、imagebutton.lua，集合查 grid.lua、scrollablelist.lua 或 pagedlist.lua。
2. 用 Class(Widget, ...) 和 AddChild 建立唯一的父子树。让构造函数只创建稳定节点；把可变数据放进 Refresh、SetValue 或 SetDataSource。
3. 为根节点选择屏幕锚点和 ScaleMode，为子节点使用父级局部 SetPosition。全屏背景、比例布局和固定屏幕布局不要混用。
4. 让装饰节点 SetClickable(false)；为可交互节点实现视觉状态、鼠标行为和可达的焦点路径。
5. 按控件优先级组织 OnControl、OnRawKey、OnMouseButton 的基类/自定义处理，保留未消费路径；仅在实际处理后返回 true；为手柄使用 SetFocusChangeDir 建立进出区域的路径。
6. 优先监听 replica 或本地 UI 数据事件并显式 Refresh。只有连续动画、按住重复或跟随效果才调用 StartUpdating。
7. 换绑实体时先移除旧事件回调；全局输入句柄必须显式移除。Kill 会销毁子树并停止更新，但不能替你修复重复注入或错误的数据源所有权。
8. 在鼠标、键盘、手柄、长文本、不同宽高比、不同 UI scale、隐藏/显示和重复创建/销毁下验证。

## 源码锚点

- widgets/widget.lua：Widget 基类。
- widgets/image.lua、widgets/text.lua：基础控件。
- widgets/button.lua、widgets/grid.lua：交互控件。
- `references/widgets/` 控件参考文档：[button.md](../../widgets/button.md) / [grid.md](../../widgets/grid.md) / [healthbadge.md](../../widgets/healthbadge.md) / [image.md](../../widgets/image.md) / [screen.md](../../widgets/screen.md) / [text.md](../../widgets/text.md)。

## 不变量

- 不要在 Widget 构造函数中执行耗时操作。
- 不要在全局作用域创建 Widget 实例。
- 每个 Widget 必须有明确的销毁路径。
- 手柄焦点路径必须连续，不能出现死胡同。

## 验证

- Widget 能在不同分辨率和 UI scale 下正确显示。
- 鼠标和手柄焦点切换正常。
- Widget 销毁后不留残留事件或定时器。

## 按需资源

- 自有模块、Class 构造、树、布局、时间、焦点、事件与清理：[widget-contract.md](references/widget-contract.md)。
- 新建可入栈界面：[Screen 合同与示例](../../widgets/screen.md)。
- controls/playerhud/containerwidget/frontend 由谁拥有改动：[UI 补丁选择](../../patterns/ui/ui-patch-patterns.md)。
- 全局热键与控件输入如何选择：[输入模式](../../patterns/runtime/input-patterns.md)；参数统一查 [TheInput 合同](../../systems/theinput.md)。
