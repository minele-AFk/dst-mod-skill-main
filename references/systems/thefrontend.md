# TheFrontEnd：屏幕栈与焦点

来源：本机 scripts.zip 的 frontend.lua、widgets/screen.lua，复核于 2026-10-18。前端管理器是 Lua 类实例，不是任意 AddScreen/HideScreen 命名都存在的引擎对象。

## 当前接口

| 接口 | 合同 |
|---|---|
| PushScreen(screen) | 入栈并走激活流程 |
| PopScreen(screen) | 从栈移除指定屏，走 OnBecomeInactive/OnDestroy 等生命周期 |
| InsertScreenUnderTop(screen) | 在栈顶下插入，按真实调用场景使用 |
| GetActiveScreen() | 当前活动屏 |
| GetOpenScreenOfType(screenname) | 查已打开类型，适合防重复 |
| GetFocusWidget() | 当前焦点控件 |

当前没有本文旧例中的 AddScreen、GetTopScreen、GetScreenByName、IsActiveScreen、HideScreen、GetPaused/SetPause 合同。活动判断可比较 GetActiveScreen()；暂停与画面隐藏是不同系统，按实际游戏暂停调用者接入。

## 开关与生命周期

```lua
-- screen 是已构造的 Screen 子类实例，不是普通 Widget 冒充的 Screen。
TheFrontEnd:PushScreen(screen)
-- 对应关闭：
TheFrontEnd:PopScreen(screen)
```

Screen:OnDestroy 默认 Kill 自己的 Widget 树。覆写时清理自己的外部资源并保留基类销毁；不要仅 Hide 留下仍在栈中的界面、输入和焦点。

单例面板重复打开先查已有屏并聚焦；关屏后清空所属 HUD/功能的缓存引用。输入中未处理的分支交回原方法，只有消费时返回 true。不能从“能打开”推导取消、焦点恢复或手柄导航已经正确。

## 可用上下文

前端/可视客户端有自己的 TheFrontEnd；专服不访问 Widget 树。主菜单未必有 TheWorld/ThePlayer，世界内 HUD 也需要等 owner 和 Controls 就绪。

UI 坐标、比例缩放及鼠标屏幕坐标不自动相等，详见 [Widget 合同](../world-ui-assets/dst-ui-widget-authoring/references/widget-contract.md)。屏幕具体类写法见 [Screen](../widgets/screen.md)。

本轮没有运行客户端；检查正常关闭、取消、重复打开、失焦、返回主菜单和重连。
