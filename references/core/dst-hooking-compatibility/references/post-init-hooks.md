# PostInit 时机与 TUNING 覆盖

本页解决“该用哪个 PostInit”和“为什么代码读到的 TUNING 不是世界设置后的值”。以当前安装版 `modutil.lua`、`worldsettings_overrides.lua` 和实际调用链为准。

## 1. 选择更窄的 Hook

| 目标 | 优先入口 | 边界 |
|---|---|---|
| 一个或少数已知 Prefab | `AddPrefabPostInit` | 构造完成的实体实例 |
| 某类组件的实例 | `AddComponentPostInit` | 组件已构造并赋给 `inst.components`，其他组件未必齐全 |
| 所有带 `player` 标签的实体 | `AddPlayerPostInit` | 本质是全局 Prefab 钩子加标签过滤，成本和作用范围都接近 `AddPrefabPostInitAny` |
| 玩家视觉、光照目标等子系统 | `AddComponentPostInit("playervision")`、`playerlightningtarget` 等 | 先确认组件实际存在和调用端 |
| 玩家控制器或本地输入 | `playercontroller` 或实际 Controls 生命周期 | 不等于所有玩家实体；专服和主机路径不同 |
| 所有 Prefab | `AddPrefabPostInitAny` | 回调先做廉价过滤，避免每个实体都执行重逻辑 |

`AddPlayerPostInit` 的源码实现会调用 `AddPrefabPostInitAny`，再在回调里检查 `inst:HasTag("player")`。因此它不是“只对本地玩家执行一次”的钩子，也不会自动保证 `ThePlayer`、HUD 或 Controls 已经存在。

需要“玩家属性”时优先找拥有该属性的组件；需要“本地 HUD”时沿 Controls/PlayerHud 构造链处理；需要“世界启动一次”时用 SimPostInit 或实际世界生命周期，不要把所有逻辑塞进玩家 Prefab 钩子。

## 2. TUNING 与世界设置

`worldsettings_overrides.lua` 定义进入世界时对部分 `TUNING` 键的覆盖。典型风险：

```lua
-- 模块加载时缓存，可能早于世界设置覆盖
local MY_SPEED = TUNING.MYMOD_SPEED

AddPlayerPostInit(function(inst)
    -- 这里继续使用旧值
end)
```

更安全的做法是：

1. 确认该键是否被 `worldsettings_overrides.lua` 或模组世界选项覆盖。
2. 在权威端、实际世界上下文已经建立后再读取 `TUNING`。
3. 需要保存的值明确记录“世界设置后的值”还是“原始默认值”。
4. 客户端如果只做展示，读取已复制状态，不直接假设服务器 TUNING。

`worldsettings_overrides.lua` 顶部的 `OverrideTuningVariables` 会写入 `ORIGINAL_TUNING` 并替换 `TUNING`；不要用模块加载时的局部变量缓存跨越这个阶段。

## 3. 组件 Hook 的上下文

`AddComponentPostInit` 拿到的是组件实例，不是 Prefab 定义。此时可以修改 `self` 字段和方法，但不能假设同一实体的其他组件已经添加。需要跨组件协调时，在回调中延迟到实际事件或 `OnEntityReplicated`/生命周期节点，并检查依赖是否存在。

`AddClassPostConstruct` 只影响之后创建的实例；已经存在的 UI 或对象需要从持有者处理。对共享类表做永久修改会影响所有实例，除非需求明确如此。

## 4. 验证清单

- 单独启用、重复初始化和不同模组加载顺序都不会重复注册。
- `AddPlayerPostInit` 没有访问不存在的 `ThePlayer`、HUD 或 Controls。
- 世界设置覆盖后，代码读取的是预期阶段的值，不是模块加载时缓存的旧值。
- 更窄 Hook 覆盖不到的实体和客户端路径有明确回退或记录。

本页于 2026-10-22 对照安装版 `modutil.lua:580-590` 与 `worldsettings_overrides.lua:2-12`；未执行多模组加载顺序或世界设置实机测试。
