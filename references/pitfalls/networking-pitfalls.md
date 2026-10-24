# 网络常见陷阱

当代码跨越服务器/客户端边界时，请参考此文件。

## 客户端使用 `replica`，服务器使用 `components`

- 服务器权威状态通常存储在 `inst.components` 中。
- 客户端读取通常应该来自 `inst.replica` 或网络变量。
- 不要假设在客户端专用分支中 `inst.components.foo` 是有效的。

错误模式：

```lua
if not TheWorld.ismastersim then
    local value = inst.components.mycomponent:GetValue()
end
```

更安全的模式：

```lua
if not TheWorld.ismastersim then
    local value = inst.replica.mycomponent ~= nil and inst.replica.mycomponent:GetValue() or nil
end
```

如果组件是 mod 拥有的且客户端需要读取，请同时验证 `AddReplicableComponent(...)` 和副本文件。

## 不要将服务器逻辑复制到客户端分支

- 客户端通常应该：
  - 读取副本状态
  - 播放本地特效
  - 更新本地 UI
  - 发送 RPC 或输入
- 服务器通常应该：
  - 修改权威组件
  - 生成游戏实体
  - 改变持久世界状态

如果客户端需要请求服务器更改：

- 通过操作流程或 RPC 发送意图
- 让服务器修改真实游戏状态
- 然后让客户端通过副本或网络变量观察

## 预制件初始化需要清晰的分离

许多官方预制件使用此顺序：

```lua
inst.entity:AddTransform()
inst.entity:AddAnimState()
inst.entity:AddNetwork()

inst.entity:SetPristine()

if not TheWorld.ismastersim then
    return inst
end

-- 服务器专用组件和逻辑
```

如果这个分离被破坏，复制错误和 nil 访问问题变得更可能发生。

## 网络变量不是可选装饰

官方预制件经常在主模拟分离之前声明网络变量，当客户端需要以下状态时：

- 布尔值
- 小计数器
- 目标实体
- 用于本地呈现的脏事件

实用规则：

- 如果客户端必须在不读取服务器组件的情况下做出反应，添加最小化的网络变量或副本模式
- 将权威修改保持在服务器端

## 常见失败模式

- 主机能看到，远程客户端看不到
  - 缺少副本、缺少网络变量，或客户端读取服务器组件
- 客户端发送意图但服务器从未更改
  - 错误的 RPC 方向或缺少权威处理器
- 预制件在客户端存在但在 `SetPristine()` 后因 nil 崩溃
  - 服务器专用设置泄漏到客户端分支
- 复制的外壳存在但本地呈现从未更新
  - 缺少网络变量脏事件或本地监听器

## 快速排查

- 如果任务需要实现模式，请阅读 `references/core/dst-networking-rpc/references/network-contract.md`
- 如果任务特别涉及玩家拥有或仅限所有者的玩家状态，请阅读 `references/patterns/network/player-network-patterns.md`
- 如果错误主要是权威混淆，请阅读 `references/core/dst-lua-runtime/references/module-environments.md`
- 如果错误主要是症状驱动的，请阅读 `references/patterns/diagnostic-patterns.md`