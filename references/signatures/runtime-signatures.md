# 运行时签名

观察到的或混合来源的高频运行时签名。

```lua
TheSim:FindEntities(x, y, z, radius, musttags, canttags, oneoftags)
TheSim:SetPersistentString(name, data, encode, callback)
TheSim:GetPersistentString(name, callback)
TheSim:ErasePersistentString(name, callback)
TheSim:CheckPersistentStringExists(name, callback)
TheWorld:PushEvent(event, data)
TheNet:IsDedicated()
TheNet:GetIsServer()
TheFrontEnd:PushScreen(screen)
TheFrontEnd:PopScreen(screen)
TheFrontEnd:GetSound()
TheInput:AddKeyUpHandler(key, fn)
TheInput:AddKeyDownHandler(key, fn)
TheInput:AddKeyHandler(fn)
TheInput:AddMouseButtonHandler(fn)
TheInput:AddMoveHandler(fn)
TheInput:AddControlHandler(control, fn)
TheInput:AddGeneralControlHandler(fn)
TheInput:AddControlMappingHandler(fn)
TheInput:AddTextInputHandler(fn)
```

注意事项：

- `TheSim:FindEntities` 是引擎提供的，因此将其视为已观察到的官方使用形式。
- `TheSim:GetPersistentString(...)` 是回调驱动的；观察到的使用形式是 `function(success, data) ... end`。
- `TheSim:SetPersistentString(...)` 和 `ErasePersistentString(...)` 也通常与回调一起使用。
- 对于本地模组配置，`data` 通常应该是由 `json.encode(...)` 生成的 JSON 字符串，然后使用带保护的 `json.decode(...)` 恢复。
- `TheWorld.ismastersim` 是字段检查，不是函数调用。
- `ThePlayer` 是全局本地玩家引用，不是函数调用。
- `TheInput` 是本地输入状态；使用专用服务器保护，并优先使用窄范围的处理器。

## 快速路由

- 本地屏幕堆栈操作
  - `TheFrontEnd:PushScreen`、`TheFrontEnd:PopScreen`
- 跨存档本地设置或缓存
  - `TheSim:SetPersistentString`、`TheSim:GetPersistentString`
- 前端音效
  - `TheFrontEnd:GetSound()`
- 映射控制重新绑定
  - `TheInput:AddControlMappingHandler`
- 普通本地输入
  - `TheInput:Add*Handler(...)` 系列