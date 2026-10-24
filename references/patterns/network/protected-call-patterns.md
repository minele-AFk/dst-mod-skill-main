# 受保护调用模式

当任务需要 Lua 受保护调用（如 `pcall(...)` 或 `xpcall(...)`）时，请使用本文件，特别是围绕 `json.decode(...)`、`json.encode(...)`、可选的 `require(...)` 或脆弱的反序列化边界。

本页讨论的是狭义的 Lua 端错误遏制。
如果任务主要是关于持久化本地文件，请同时阅读 `references/patterns/persistence/persistent-string-patterns.md`。
如果任务主要是关于实体或世界保存生命周期，请同时阅读 `references/core/dst-persistence-migration/references/persistence-contract.md`。

## `pcall` 和 `xpcall` 的用途

当某个小边界可能失败并且您希望调用者干净地恢复而不是崩溃整个流程时，使用受保护调用。

观察到的官方适用场景：

- 从网络或缓存字符串解码 JSON
- 加载本地持久化配置文件数据
- 尝试可选的 `require(...)`
- 编码一个负载并在序列化失败时回退

## 核心形式

基本受保护调用：

```lua
local ok, result = pcall(function()
    return json.decode(data)
end)
```

参数传递形式：

```lua
local ok, speechfile = pcall(require, "speech_" .. character)
```

带有错误处理程序的受保护调用：

```lua
local ok, result = xpcall(function()
    return json.encode(moddata)
end, generic_error)
```

实用规则：

- `pcall(...)`
  - 最简单的恢复路径
- `xpcall(...)`
  - 当您还需要自定义错误处理程序或更丰富的日志路径时使用

## 观察到的官方示例

- `scripts/craftingmenuprofile.lua`
  - 在加载本地 UI 配置文件数据时保护 `json.decode(data)`
- `scripts/screens/modsscreen.lua`
  - 保护远程结果字符串的 JSON 解码
- `scripts/screens/multiplayermainscreen.lua`
  - 在使用缓存数据之前保护 MOTD JSON 解码
- `scripts/screens/redux/multiplayermainscreen.lua`
  - 保护来自通用 KV 值的存储 JSON
- `scripts/tools/getmissingstrings.lua`
  - 对可选语音文件使用 `pcall(require, ...)`
- `scripts/screens/worldgenscreen.lua`
  - 在编码模组世界生成负载时使用 `xpcall(..., generic_error)`

## 用于解码路径的 `pcall`

这是最常见的官方模式。

典型形式：

```lua
local ok, decoded = pcall(function()
    return json.decode(data)
end)

if ok and type(decoded) == "table" then
    -- use decoded data
end
```

为什么这很重要：

- 缓存文件可能为空、过时或格式错误
- 远程响应可能不是有效的 JSON
- 旧格式可能不再能干净解码

实用规则：

- 保护解码调用
- 然后在使用前验证解码类型

## 用于可选 `require(...)` 的 `pcall`

官方代码也使用直接可调用形式：

```lua
local ok, mod = pcall(require, modulename)
```

在以下情况使用：

- 文件可能不存在
- 兼容性模块是可选的
- 模块缺失应优雅降级

不要使用此方法来静默隐藏必需的硬依赖项。

## 用于重要编码步骤的 `xpcall`

观察到的官方示例：

- `scripts/screens/worldgenscreen.lua`

在以下情况使用 `xpcall(...)`：

- 序列化失败应通过已知处理程序记录
- 负载足够重要，您希望获得比简单布尔值更好的错误报告

实用规则：

- 默认使用 `pcall(...)`
- 仅当自定义错误处理程序路径实际上有用时才使用 `xpcall(...)`

## 保持受保护边界狭窄

好的做法：

- 保护 `json.decode(...)`
- 保护 `json.encode(...)`
- 保护一个可选的 `require(...)`

不好的做法：

- 将整个更新函数、界面构造函数或游戏玩法分支包装在一个巨大的 `pcall(...)` 中

原因：

- 宽泛的受保护调用隐藏了真正失败的行
- 它们使状态恢复不清晰
- 它们可能意外掩盖真正的错误

## 受保护调用加验证

成功的受保护调用并不意味着该值可用。

仍然需要验证：

- `decoded ~= nil`
- 当期望表格时，`type(decoded) == "table"`
- 使用前检查必需的键是否存在

观察到的官方风格：

- 解码
- 检查 `status`
- 检查解码值的形状
- 只有这样才分配活动状态

## 常见错误

- 调用 `pcall(json.decode(data))`
  - 错误，因为解码在 `pcall(...)` 之前运行
- 假设 `ok == true` 意味着数据形状正确
- 吞下失败然后继续使用部分无效状态
- 包装大型不相关逻辑而不是脆弱边界本身
- 使用 `xpcall(...)` 但没有有意义的错误处理程序

## 最小化模板

安全的 JSON 解码：

```lua
local ok, decoded = pcall(function()
    return json.decode(data)
end)

if ok and type(decoded) == "table" then
    state = decoded
end
```

带有回退的安全 JSON 编码：

```lua
local ok, encoded = pcall(function()
    return json.encode(tbl)
end)

if ok then
    TheSim:SetPersistentString(key, encoded, false)
else
    print("Failed to encode", key)
end
```

可选 require：

```lua
local ok, mod = pcall(require, "speech_" .. character)
if ok then
    return mod
end
```

## 经验法则

- 保护狭窄的解码、编码和可选 require 边界
- 在受保护调用后验证结果
- 默认使用 `pcall(...)`
- 当自定义错误处理程序显著改善失败路径时使用 `xpcall(...)`
