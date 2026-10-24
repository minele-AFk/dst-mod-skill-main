# 上下文陷阱

此文件记录服务器/客户端/本地玩家上下文相关的错误。

## 不要重新绑定引擎全局变量

- `GLOBAL`、`TheSim`、`TheNet`、`TheShard`、`TheInput`、`     `TheFrontEnd`、`TheMixer`、`TheCamera`、`TheFocalPoint`、`TheWorld`、`ThePlayer` 和 `AllPlayers` 是引擎拥有的全局变量。
- 读取它们，调用它们的 API，并在需要时检查它们的可用性。
- 不要覆盖它们、用表替换它们，或将它们重新定义为其他含义。
- 保持相同值的本地直通别名是可以的，例如 `local GLOBAL = GLOBAL`。
- `TheWorld` 和 `ThePlayer` 是实体引用，因此世界或玩家拥有的字段可能存在于实体上。不要替换全局绑定本身。
- 共享注册表如 `TUNING`、`STRINGS`、`ACTIONS` 和 mod RPC 注册表可以进行窄范围扩展，但不要替换整个表。

错误示例：

```lua
TheWorld = {}
local ThePlayer = inst
TheSim = nil
TUNING = {}
STRINGS = {}
RPC = {}
```

安全示例：

```lua
local player = inst

TUNING.MYMOD_SPEED = 6
STRINGS.NAMES.MYMOD_ITEM = "My Item"

if ThePlayer ~= nil and player == ThePlayer then
    -- local-player-specific logic
end
```

## `ThePlayer` 不是通用玩家句柄

- `ThePlayer` 是本地进程的玩家状态。
- 它通常存在于客户端和监听主机上。
- 在专用服务器上通常为 `nil`。
- 不要将 `TheWorld.ismastersim` 视为 `ThePlayer` 存在的证明。

安全防护：

```lua
if ThePlayer ~= nil and ThePlayer.HUD ~= nil then
    -- local-player UI logic
end
```

错误示例：

```lua
local target = ThePlayer
```

安全示例：

```lua
local target = doer or owner or inst
```

然后仅在行为是有意针对本地玩家时使用 `ThePlayer`。

## `ThePlayer` 与 `doer` 或 `owner` 不同

- 在游戏回调中，使用实际的回调参数，如 `inst`、`doer`、`owner`、`giver` 或 `attacker`。
- 仅在行为是有意针对本地玩家时使用 `ThePlayer`。

## `TheWorld.ismastersim` 和 `TheNet:IsDedicated()` 是不同的

- `TheWorld.ismastersim`
  - 权威世界模拟
- `TheNet:IsDedicated()`
  - 进程没有本地前端

这两个检查都很重要，但原因不同。

错误示例：

```lua
if TheWorld.ismastersim then
    -- assume HUD or ThePlayer exists
end
```

安全示例：

```lua
if not TheNet:IsDedicated() then
    -- local presentation path
end
```

```lua
if not TheWorld.ismastersim then
    return inst
end
```

## 监听主机混淆

监听服务器可以同时是：

- 权威模拟
- 本地玩家进程
- 前端/UI 进程

这意味着代码可能在主机上看似正常工作，但实际上对于以下情况仍然是错误的：

- 远程客户端
- 专用服务器
- 纯客户端本地 UI 流程

## 快速路由

- 如果问题是"在主机上工作但在远程客户端上不工作"
  - 阅读 `references/pitfalls/networking-pitfalls.md`
- 如果问题是"在主机上工作但在专用服务器上崩溃"
  - 阅读 `references/world-ui-assets/dst-hud-screens-input/references/hud-customization.md`
- 如果问题是"我在游戏传递给我 `doer` 的地方使用了 `ThePlayer`"
  - 首先修复回调所有权