# 玩家网络模式

当任务需要玩家特定的复制状态、所有者范围的 HUD 数据、`player_classified` 或玩家端副本设置时，请使用本文件。

如果任务只是"将此应用于每个玩家"，请先阅读 `references/patterns/player-patterns.md`。
如果任务是通用 RPC、网络变量或副本设计，请同时阅读 `references/core/dst-networking-rpc/references/network-contract.md`。

## 快速路由

- 一个或两个小的玩家值，所有相关客户端都可以读取
  - 将网络变量放在玩家实体上
- 玩家功能应暴露一个清晰的客户端 API，如 `inst.replica.<name>`
  - 使用副本组件，网络变量放在玩家或分类子实体上
- 所有者专用或分组玩家状态，用于 HUD、控制器或相机逻辑
  - 使用分类子实体模式
- 纯粹的本地 UI 状态，没有权威意义
  - 保持本地，不要进行网络同步
- 客户端希望请求服务器修改玩家状态
  - 使用动作流程或 RPC，然后将结果复制回来

## 官方玩家流程

在 `scripts/prefabs/player_common.lua`、`scripts/prefabs/player_classified.lua` 和 `scripts/entityreplica.lua` 中观察到：

- 主模拟生成 `player_classified` 并将其父化到玩家
- 在分配用户 ID 后，`player_common.lua` 调用 `inst.player_classified.Network:SetClassifiedTarget(inst)`
- `player_classified.lua` 在分类实体本身上定义了许多玩家特定的网络变量
- `player_classified.lua` 调用 `SetPristine()` 并在客户端上分配 `inst.OnEntityReplicated = OnEntityReplicated`
- `EntityScript:ReplicateEntity()` 在副本组件创建后调用 `OnEntityReplicated()`
- `player_classified:OnEntityReplicated()` 将自身附加回父玩家，然后将相同的分类路由到选定的副本或玩家端组件

实际影响：

- 不要假设在最早的客户端构建点存在 `inst.player_classified`
- 如果客户端设置依赖于副本或分类数据，请等待复制准备就绪
- `OnEntityReplicated()` 是依赖分类数据的客户端连接的安全点

## 在主实体网络变量、副本和分类之间选择

### 主实体网络变量

在以下情况使用：

- 状态很小
- 状态自然属于玩家实体本身
- 所有附近的客户端都可以读取它

适用场景：

- 紧凑的模式标志
- 微小的计数器
- 一个公开的布尔值或字节大小的状态

避免使用：

- 数据应该只由拥有玩家读取
- 多个相关值和脏事件一起传输
- 功能需要附加或分离生命周期

### 副本组件

在以下情况使用：

- 功能应该通过 `inst.replica.<name>` 读取
- 状态在概念上是一个组件，而不仅仅是一个松散的字段
- 客户端需要辅助方法而不是直接访问网络变量

观察到的官方结构：

- `EntityScript:ReplicateComponent(name)` 加载 `components/<name>_replica.lua`
- `AddReplicableComponent(name)` 扩展了模组拥有组件的允许副本集
- 玩家副本组件如 `sanity_replica` 仍然附加到 `player_classified`

实际影响：

- 副本和分类通常是互补的，而不是竞争的
- 玩家副本可以暴露客户端 API，而实际的网络变量存储在分类子实体上

### 分类子实体

在以下情况使用：

- 状态是所有者范围的
- 多个相关值属于一起
- 客户端需要附加、分离或脏事件编排
- 本地 HUD、动作可见性、相机或控制器代码应响应权威玩家数据

观察到的官方结构：

- `player_common.lua` 拥有 `AttachClassified`、`DetachClassified` 和清理逻辑
- `player_classified.lua` 将自身附加到选定的玩家副本组件
- `inventory_replica.lua` 和 `sanity_replica.lua` 监听脏事件并在移除时分离

实际影响：

- 这是分组玩家状态、所有者专用 HUD 状态或类似库存的客户端呈现的正确模式
- 如果只需要一个公开的布尔值，分类过于重量级

## 所有者范围的数据

观察到的官方行为：

- `player_common.lua` 通过 `Network:SetClassifiedTarget(inst)` 给予拥有玩家访问 `player_classified` 的权限
- `inventory_replica.lua` 使用 `Network:SetClassifiedTarget(...)` 加上脏事件来切换分类访问和可见性

实用规则：

- 如果只有拥有玩家应该读取数据，优先使用分类目标模式
- 如果每个客户端都可以读取相同的值，优先使用普通玩家网络变量

## 推荐的模组模式

优先使用以下升级路径：

1. 小型公开玩家状态
   - 玩家网络变量
2. 具有清晰客户端 API 的玩家功能
   - 模组拥有的服务器组件加上副本组件
3. 所有者专用或结构化玩家状态
   - 模组拥有的分类子实体，可选地通过副本组件附加

只有当功能真正属于玩家类并且您理解其附加生命周期时，才修改官方的 `player_classified` 路径。

## 常见失败点

- 尝试在客户端上读取 `inst.player_classified` 之前它已附加
- 在客户端上读取 `inst.components` 而不是 `inst.replica` 或分类数据
- 使用分类子实体来存储一个小的公开值
- 当客户端呈现应该响应时忘记脏监听器
- 忘记在移除时分离和清理
- 对只需要普通网络变量的非玩家预制体使用玩家分类模式

## 快速示例

- 所有者专用自定义耐力条
  - 玩家分类风格
- 附近客户端可见的公开连击计数器
  - 玩家网络变量或副本加网络变量
- 具有多个 HUD 辅助组件的玩家拥有系统
  - 组件加副本加分类
