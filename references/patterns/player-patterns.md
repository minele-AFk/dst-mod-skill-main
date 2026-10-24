# 玩家模式

当任务需要将玩家作为一个类进行修改，而不是构建某个特定的可玩角色时，请使用本文件。

典型触发场景：

- `AddPlayerPostInit(...)`
- "将此应用于每个玩家"
- 玩家生命周期事件，如 `playerentered`、`ms_playerjoined`、`playeractivated` 或 `playerdeactivated`
- 在全局玩家修改和角色本地预制体修改之间做选择

如果任务主要是关于一个可玩角色预制体，请阅读 `references/patterns/character/character-patterns.md`。
如果任务涉及本地 HUD 或界面，请同时阅读 `references/world-ui-assets/dst-hud-screens-input/references/hud-customization.md`。
如果任务涉及玩家动作状态或预测，请同时阅读 `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`。
如果任务需要玩家拥有的复制状态或 `player_classified`，请同时阅读 `references/patterns/network/player-network-patterns.md`。

## 选择最窄的玩家钩子

这些钩子用法不同：

- `AddModCharacter(...)`
  - 注册一个新的可玩角色
- `AddPrefabPostInit("<character>", fn)`
  - 修改一个特定的玩家预制体
- `AddPlayerPostInit(fn)`
  - 修改所有带有玩家标签的实例

在 `scripts/modutil.lua` 中观察到的官方定义：

- `AddPlayerPostInit(fn)` 实现为 `AddPrefabPostInitAny(...)`
- 它仅通过 `inst:HasTag("player")` 进行过滤

实际影响：

- 这是一个宽泛的钩子，不是特定于角色的钩子
- 它同时影响原版角色和模组角色
- 它本身不区分本地玩家、远程玩家、存活玩家或幽灵
- 由于它基于 `AddPrefabPostInitAny(...)` 构建，回调应保持狭窄且高效

## `player_common.lua` 已包含的内容

在 `scripts/prefabs/player_common.lua` 中观察到：

- 在 `SetPristine()` 之前调用 `common_postinit(inst)`
- 在客户端 `inst.entity:SetPristine()` 之后提前返回
- 在 `master_postinit(inst)` 之前添加大型服务器基础设置

观察到的基础组件包括：

- `talker`
- `skilltreeupdater`
- `combat`
- `inventory`
- `inspectable`
- `temperature`
- 玩家可燃烧和可冻结的辅助组件

实际影响：

- 不要在 `AddPlayerPostInit(...)` 内部重建普通玩家基础设置
- 如果更改属于某个角色的身份、属性或特殊能力，优先使用该角色的预制体回调
- 使用玩家级别的修改来实现应该真正影响每个玩家实例的行为

## 本地玩家与远程玩家

每个玩家实体都可以匹配 `AddPlayerPostInit(...)`，但只有一个本地玩家拥有 HUD。

实用规则：

- 所有玩家
  - `AddPlayerPostInit(...)`
- 仅限活跃的本地玩家
  - 本地守卫加上 `playeractivated` 或 `inst == ThePlayer`
- 仅限权威游戏逻辑
  - `TheWorld.ismastersim`

不要假设 `AddPlayerPostInit(...)` 意味着"我的本地玩家"。

## 值得记住的玩家生命周期事件

在 `scripts/prefabs/player_common.lua` 中观察到：

- `playerentered`
  - 当玩家实体在本地变为相关时，在客户端和服务器上都会触发
- `ms_playerjoined`
  - 仅在玩家加入后在主模拟上触发
- `playeractivated`
  - 当本地活跃玩家变为活跃状态时触发
- `playerdeactivated`
  - 当该活跃玩家被拆除或切换时触发

实际影响：

- 如果功能是"每当任何玩家实体出现时执行操作"，使用 `playerentered` 或玩家 post-init
- 如果功能是"在服务器上为真实连接的玩家执行操作"，使用服务器端加入或权威回调
- 如果功能是 HUD、相机或仅限本地玩家的设置，应基于 `playeractivated` 而不是任何随机玩家实体的存在

## 最小化全局玩家修改

```lua
AddPlayerPostInit(function(inst)
    inst:AddTag("my_mod_player")

    if not TheWorld.ismastersim then
        return
    end

    inst:ListenForEvent("death", function(player)
        -- authoritative player-wide behavior
    end)
end)
```

## 最小化本地活跃玩家钩子

```lua
AddPlayerPostInit(function(inst)
    if TheNet:IsDedicated() then
        return
    end

    inst:ListenForEvent("playeractivated", function(player)
        if player == ThePlayer and player.HUD ~= nil then
            -- local HUD or screen setup
        end
    end)
end)
```

## 常见失败点

- 当任务只针对一个角色时使用 `AddPlayerPostInit(...)`
- 忘记幽灵和远程玩家可能仍会匹配钩子
- 在没有本地客户端守卫的情况下访问 HUD 或 `ThePlayer`
- 在宽泛的全玩家回调中执行昂贵的逻辑
- 重复 `player_common.lua` 已经包含的基础玩家设置

## 快速路由

- "用相同的游戏规则修改每个玩家"
  - `AddPlayerPostInit(...)`
- "只修改一个角色预制体"
  - `AddPrefabPostInit("<character>", fn)` 或角色预制体回调
- "构建一个新的可玩角色"
  - `references/patterns/character/character-patterns.md`
- "只访问本地活跃玩家的 HUD 或界面"
  - `playeractivated` 加上 `references/world-ui-assets/dst-hud-screens-input/references/hud-customization.md`
- "同步仅限所有者的玩家 HUD 或控制器状态"
  - `references/patterns/network/player-network-patterns.md`
