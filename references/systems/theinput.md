# TheInput 合同：注册、回调参数与句柄清理

2026-10-22 对照本机安装 scripts.zip 的 input.lua 与 events.lua。它是本地进程的输入对象；不是 scripts/global/TheInput/def.lua。输入方式的选择由 [输入模式](../patterns/runtime/input-patterns.md) 负责。

## 注册与回调签名

下面的回调参数来自实际 HandleEvent 调用点；不要把注册函数参数或 Widget 方法签名当成同一回事。

| 注册 | 实际 fn 参数 |
|---|---|
| AddKeyDownHandler(key, fn) | 无参数；key 已由注册事件键指定 |
| AddKeyUpHandler(key, fn) | 无参数 |
| AddKeyHandler(fn) | key, down |
| AddMouseButtonHandler(fn) | button, down, x, y；x/y 为屏幕位置 |
| AddMoveHandler(fn) | x, y |
| AddControlHandler(control, fn) | digitalvalue, analogvalue；不再传 control |
| AddGeneralControlHandler(fn) | control, digitalvalue, analogvalue |
| AddControlMappingHandler(fn) | deviceId, controlId, inputId, hasChanged |
| AddTextInputHandler(fn) | text |

这些入口返回事件句柄，保存后用 handle:Remove 撤销。原处理器的 RemoveHandler(handle) 也有效，但需要匹配实际 processor；不必为清理依赖 TheInput 的内部字段名。没有可直接套用的 RemoveKeyDownHandler/RemoveKeyUpHandler 或 AddMouseButtonDownHandler/UpHandler。

## 分派与返回值

- events.lua 的 EventProcessor:HandleEvent 遍历匹配句柄并调用 fn，忽略返回值；不能靠 fn 返回 true 阻止其他句柄，也不依赖 pairs 遍历的注册顺序。
- OnRawKey 先广播 key/down，再按 down 分发指定键的无参回调。
- OnControl 先交 FrontEnd；未消费且满足当前输入条件时，分发特定 control 的 digital/analog，再分发通用 control/digital/analog。
- OnMouseButton 在 mouse_enabled 时先调用 FrontEnd，再广播全局鼠标句柄；这里没有用 FrontEnd 返回值阻止该广播。
- UpdatePosition 的移动回调是屏幕 x/y，不等同于某个 Widget 父级局部坐标。

Widget/Screen 的 OnControl、OnRawKey、OnMouseButton 走另一条焦点责任链，见 [Widget 合同](../world-ui-assets/dst-ui-widget-authoring/references/widget-contract.md)。

## 有拥有者的注册与撤销

下列函数放在 modmain 环境的可视功能接入处，回调是否处理当前 Screen/聊天/暂停由调用者决定。返回的 cleanup 由功能退出时调用；示例不读取游戏资源或执行技能。

```lua
local G = GLOBAL
local function BindMyModHotkey(ontrigger)
    if G.TheNet:IsDedicated() or G.TheInput == nil then
        return nil
    end
    local handle = G.TheInput:AddKeyDownHandler(G.KEY_G, function()
        ontrigger() -- 调用者先确认当前输入上下文允许响应。
    end)
    return function()
        if handle ~= nil then
            handle:Remove()
            handle = nil
        end
    end
end
```

注册一次对应一次功能生命周期，不因每次打开又注册一份。长寿命 TheInput 上的 handler 不会仅因 Widget 隐藏或 self.inst 移除自动结束；屏幕关闭、失焦、Controls 重建、回主菜单和重连分别明确谁撤销。

## 查询与运行端

- IsKeyDown(key)、IsControlPressed(control)：当前本地输入状态。
- GetScreenPosition()：屏幕位置对象，可读取 x/y。
- GetWorldPosition()、GetWorldEntityUnderMouse()：世界位置/目标，另查平台与有效性。
- 屏幕尺寸从实际渲染接口如 TheSim:GetScreenSize 的调用点核对，不使用 TheInput:GetScreenWidth/GetScreenHeight。
- 常量从 constants.lua 取得，不维护裸数字。

HUD/前端未必有 ThePlayer；专服不创建功能输入，房主有可视端。客户端输入只提供意图，真实玩法仍经服务器验证。参见 [HUD 生命周期](../world-ui-assets/dst-hud-screens-input/references/hud-customization.md)。源码与语法检查不证明鼠标、手柄、输入法或重绑行为已验收。
