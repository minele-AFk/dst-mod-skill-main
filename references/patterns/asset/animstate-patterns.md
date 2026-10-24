# AnimState 模式

当任务需要 `inst.AnimState` 行为、动画播放控制、符号覆盖或动画驱动的 UI 状态时，请使用本文件。

`AnimState` 本身是引擎端的，不是普通的 Lua 模块。`scripts.zip` 中没有可供读取的 `scripts/animstate.lua`。

要获取脚本级别的权威信息，请检查以下位置的实际用法：

- `scripts/prefabs/*.lua`
- `scripts/stategraphs/*.lua`
- `scripts/widgets/*.lua`
- `scripts/screens/*.lua`

下面的方法列表以及 `layer` 与 `symbol` 的解释也参考了公开教程 `https://atjiu.github.io/dstmod-tutorial/#/animstate`。将该页面视为实用的补充指南，而非引擎行为的权威来源。

## 从这些概念开始

- `bank`
  - 实体使用的动画集名称
- `build`
  - 提供符号和美术资源的构建或皮肤源
- animation name（动画名称）
  - 传递给 `PlayAnimation(...)` 或 `PushAnimation(...)` 的具体片段
- `symbol`
  - 由 `OverrideSymbol(...)`、`HideSymbol(...)` 和 `ShowSymbol(...)` 使用的命名美术通道
- `layer`
  - 由 `Hide(...)` 和 `Show(...)` 使用的命名动画层

实践规则：

- 如果要交换装备美术或特定精灵部件，请考虑 `symbol`
- 如果要切换动画数据中的整个动画层，请考虑 `layer`

## 高频方法

### 基本设置

大多数 prefab 构造函数遵循以下结构：

```lua
inst.entity:AddAnimState()

inst.AnimState:SetBank("my_item")
inst.AnimState:SetBuild("my_item")
inst.AnimState:PlayAnimation("idle")
```

在许多官方 prefab（如 `scripts/prefabs/mosquitomusk.lua`）中都能观察到这种模式。

### 队列动画

使用 `PlayAnimation(...)` 播放当前立即执行的片段。使用 `PushAnimation(...)` 将下一个片段排队到当前片段完成后播放。

来自 `scripts/prefabs/oceanfishingbobber.lua` 的官方示例：

```lua
inst.AnimState:PlayAnimation("spin_pre", false)
inst.AnimState:PushAnimation("spin_loop", true)
```

来自 `scripts/prefabs/spiderden.lua` 的官方示例：

```lua
inst.AnimState:PlayAnimation("cocoon_enter")
inst.AnimState:PushAnimation(inst.anims.idle, true)
```

### 隐藏或显示一个层

当目标名称是动画数据中的层时，使用这些方法：

```lua
inst.AnimState:Hide("HORROR")
inst.AnimState:Show("CHEMICAL")
```

在 `scripts/prefabs/winona_battery_low.lua` 中观察到。

公开教程在这里很有用，因为它解释了层名称来自动画数据（如 `anim.bin`）。仅从官方脚本用法来看，这种区别并不明显。

### 隐藏或显示一个符号

当目标是具体的符号通道时，使用这些方法：

```lua
inst.AnimState:HideSymbol("bedazzled_flare")
```

观察到的官方用法：

- `HideSymbol(...)` 在 `scripts/prefabs/spiderden.lua` 中
- `ShowSymbol(...)` 在 `scripts/prefabs/nightmarefissure.lua` 中

### 覆盖一个符号

当一个符号应该从另一个 build 渲染时，使用 `OverrideSymbol(oldsymbol, newbuild, newsymbol)`。

常见的装备模式：

```lua
owner.AnimState:OverrideSymbol("swap_body", "swap_icepack", "swap_body")
owner.AnimState:ClearOverrideSymbol("swap_body")
```

在 `scripts/prefabs/icepack.lua`、`scripts/prefabs/candybag.lua`、`scripts/prefabs/raincoat.lua` 以及类似的可穿戴 prefab 中观察到。

常见的冰冻覆盖层模式：

```lua
inst.AnimState:OverrideSymbol("swap_frozen", "frozen", "frozen")
inst.AnimState:ClearOverrideSymbol("swap_frozen")
```

在 `scripts/prefabs/spiderden.lua` 中观察到。

### 在进度点冻结动画

当动画应该表示进度条或片段中的固定点而非正常播放时，使用 `SetPercent(animname, percent)`。

来自 `scripts/widgets/ringmeter.lua` 的官方 UI 示例：

```lua
self.meter:GetAnimState():SetPercent("progress", self.t / self.duration)
```

来自 `scripts/prefabs/worm_boss.lua` 的官方世界示例：

```lua
inst.AnimState:SetPercent(anim, time - adjust)
```

实践规则：

- 用于进度条、仪表、生长视觉效果和同步姿势更新
- 不要期望 `SetPercent(...)` 单独就能逐帧持续播放动画；它通常用于将动画放置在特定点

### 改变播放速度

当当前动画应该更快或更慢播放时，使用 `SetDeltaTimeMultiplier(mult)`。

观察到的官方用法：

- `scripts/prefabs/pocketwatch_common.lua`
- `scripts/components/anchor.lua`
- `scripts/stategraphs/SGtentacle_arm.lua`

实践规则：

- 当速度覆盖应该结束时，将其恢复为 `1`
- 避免在一次性操作后让共享实体卡在自定义倍率上

### 查询当前播放状态

来自脚本用法的常见读取端辅助方法：

- `AnimDone()`
  - 当代码需要知道片段是否完成时使用
- `IsCurrentAnimation(animname)`
  - 当逻辑依赖于当前片段名称时使用

观察到的示例：

- `scripts/widgets/ringmeter.lua`
- `scripts/prefabs/worm_boss.lua`

## 典型模式

### 最小 Prefab 动画设置

```lua
local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    inst.AnimState:SetBank("my_item")
    inst.AnimState:SetBuild("my_item")
    inst.AnimState:PlayAnimation("idle", true)

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    return inst
end
```

### 一次性播放然后循环

```lua
inst.AnimState:PlayAnimation("place")
inst.AnimState:PushAnimation("idle", false)
```

这种结构常见于放置、受击、解冻、爆发和过渡视觉效果。

### 装备或皮肤符号交换

```lua
local function onequip(inst, owner)
    owner.AnimState:OverrideSymbol("swap_object", "swap_myweapon", "swap_myweapon")
end

local function onunequip(inst, owner)
    owner.AnimState:ClearOverrideSymbol("swap_object")
end
```

当这是针对玩家手持物品时，在假设 `swap_object`、`swap_body` 或 `backpack` 之前，请从官方装备 prefab 确认真实的符号名称。

### 进度驱动的仪表

```lua
local percent = math.clamp(current / max, 0, 1)
inst.AnimState:SetPercent("meter", percent)
```

这是仪表、作物生长视觉效果和径向 UI 条的常见结构。

## 在哪里验证名称

当动画名称或符号名称不确定时：

1. 检查使用相同美术系列的最接近的官方 prefab 或 widget。
2. 如果动画是角色驱动的，检查相关的 stategraph。
3. 如果区别具体是 `layer` 与 `symbol`，使用动画工具检查资源包。

实际情况：

- 官方脚本告诉你哪些名称实际被使用
- 资源工具告诉你动画包中存在哪些名称

## 常见陷阱

- `SetBank(...)` 和 `SetBuild(...)` 不能互换。
- 使用错误的 bank 复用 build 通常会静默失败，表现为"动画不播放"。
- `PlayAnimation(...)` 没有后续的 `PushAnimation(...)` 通常会导致过渡动画在结尾卡住。
- 如果 `newbuild` 或 `newsymbol` 不存在，`OverrideSymbol(...)` 会在视觉上失败。
- `Hide(...)` 针对层名称，而 `HideSymbol(...)` 针对符号名称。
- UI widget 通常在子 widget 上调用 `GetAnimState()`，而非 `inst.AnimState`。
- 调整播放速度时，记得恢复 `SetDeltaTimeMultiplier(1)`。

## 经验法则

- 对于 prefab 启动视觉效果，从 `SetBank`、`SetBuild` 和 `PlayAnimation` 开始。
- 对于过渡流程，添加 `PushAnimation`。
- 对于可穿戴或皮肤视觉效果，首先检查 `OverrideSymbol` 模式。
- 对于进度条或固定姿势，检查 `SetPercent`。
- 如果名称看起来不确定，在假设教程命名与你的资源匹配之前，先对照官方脚本用法进行验证。