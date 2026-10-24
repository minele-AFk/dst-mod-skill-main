# Screen：可入栈的 Widget 子类

来源：widgets/screen.lua 与 frontend.lua，复核于 2026-10-18。

## 构造与栈

```lua
local Screen = require("widgets/screen")
local MyScreen = Class(Screen, function(self)
    Screen._ctor(self, "MyModScreen")
    -- 创建子 Widget，设置 default_focus。
end)

function MyScreen:OnControl(control, down)
    if MyScreen._base.OnControl(self, control, down) then
        return true
    end
    if not down and control == CONTROL_CANCEL then
        TheFrontEnd:PopScreen(self)
        return true
    end
    return false
end

return MyScreen
```

调用者用 TheFrontEnd:PushScreen(MyScreen()) 打开、PopScreen(screen) 关闭。不是 AddScreen，也不通过单纯 Hide 退出屏幕栈。示例未创建美术或可聚焦子控件，需按实际面板补齐。

## 生命周期

OnBecomeInactive 记录 last_focus，OnBecomeActive 尝试恢复已有/default_focus。SetDefaultFocus() 使用已配置的 default_focus，它的当前签名不是 SetDefaultFocus(widget)。

OnDestroy 默认 self:Kill()。自定义覆写应先清自己的全局输入、拖拽和长寿命 owner 任务，再保留基类销毁。Hide 与 Kill 不等价。

AddEventHandler/RemoveEventHandler 是 Screen 自己的事件表；与 EntityScript:ListenForEvent、TheInput 的返回句柄不是同一套 API，不混用清理方式。

## 验证

验证点击、键盘和控制器默认焦点、确认/取消、重复开关、暂停、重连与父界面恢复。源码和语法确认不证明布局或真实输入结果。

- [前端屏幕栈](../systems/thefrontend.md)
- [HUD 与输入](../world-ui-assets/dst-hud-screens-input/GUIDE.md)
