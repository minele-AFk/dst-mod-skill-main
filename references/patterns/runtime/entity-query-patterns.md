# 实体查询模式

当扫描附近实体或构建 AOE（范围）逻辑时，请使用本文件。

当查询依赖于 prefab 标签或动作过滤器标签时，还请阅读 `references/patterns/prefab/tag-patterns.md`。

## `TheSim:FindEntities`

- 官方 DST 代码中最高频的运行时查询之一。
- 观察到的官方调用结构：

```lua
TheSim:FindEntities(x, y, z, radius, musttags, canttags, oneoftags)
```

- 这是从官方使用模式中观察到的调用签名，因为 `TheSim` 是引擎提供的。

## 参数含义

- `x, y, z`
  - 要扫描的世界位置
- `radius`
  - 搜索半径（世界单位）
- `musttags`
  - 实体必须拥有此列表中的所有标签
- `canttags`
  - 实体必须不拥有这些标签中的任何一个
- `oneoftags`
  - 实体必须拥有此列表中的至少一个标签

实践规则：

- 使用 `musttags` 进行强身份过滤
- 使用 `canttags` 排除常见无用实体，如特效、死亡目标、占位符或无效交互类别
- 当多个不同目标类别都可接受时，使用 `oneoftags`

## 常见调用结构

```lua
TheSim:FindEntities(x, y, z, radius)
```

```lua
TheSim:FindEntities(x, y, z, radius, MUST_TAGS, CANT_TAGS)
```

```lua
TheSim:FindEntities(x, y, z, radius, nil, CANT_TAGS, ONE_OF_TAGS)
```

观察到的官方类别：

- AOE 命中扫描
  - 通常是 `nil, CANT_TAGS, ONE_OF_TAGS`
- 建筑或站点扫描
  - 通常是 `MUST_TAGS, CANT_TAGS`
- 家族或附近数量检查
  - 通常只是 `MUST_TAGS`
- 原始占用或阻挡物检查
  - 有时只有半径，但通常在窄半径上

## 使用场景

- AOE 伤害或效果
- 附近目标选择
- 阻挡物检查
- 容器或拾取物搜索
- 基于距离的 AI 逻辑

观察到的官方文件类别：

- `scripts/brains/`
  - 目标搜索和效用搜索
- `scripts/stategraphs/`
  - AOE 命中窗口和攻击状态查询
- `scripts/components/`
  - 自动化、拾取路由、生成检查
- `scripts/prefabs/`
  - 本地游戏玩法规则和验证检查

## 当模式已存在时，优先使用 Simutil 辅助函数

官方 `scripts/simutil.lua` 封装了常见的查询模式：

- `FindEntity(inst, radius, fn, musttags, canttags, mustoneoftags)`
  - 返回第一个匹配的可见实体
- `FindClosestEntity(inst, radius, ignoreheight, musttags, canttags, mustoneoftags, fn)`
  - 返回最近的匹配可见实体
- `GetRandomInstWithTag(tag, inst, radius)`
  - 简单的随机标签实体查询
- `GetClosestInstWithTag(tag, inst, radius)`
  - 最近标签实体快捷方式

当辅助函数已经匹配所需行为时，请使用它们。除非任务需要显著不同的过滤器或排序规则，否则不要重新手动编写相同的扫描循环。

## 过滤策略

官方代码通常将标签侧的缩小范围与最终的 Lua 谓词结合使用。

典型模式：

1. 使用 `musttags`、`canttags` 和 `oneoftags` 缩小候选范围
2. 然后在 Lua 中应用游戏玩法特定的检查
3. 仅在此之后执行最终效果、目标选择或计数

实际结果：

- 标签过滤是性能控制的第一道防线
- Lua 谓词应该细化，而不是替换标签过滤
- 如果查询在更新循环、SG 滴答或周期性任务中，请在迭代前缩小范围

## 意图索引

- "伤害或影响附近的战斗目标"
  - 从 `canttags + oneoftags` 开始
  - 检查战斗 prefab 或 SG AOE 示例
- "找到最近的有效目标"
  - 检查 `scripts/simutil.lua` 中的 `FindClosestEntity(...)`
- "计数附近的阻挡物或家族成员"
  - 使用紧凑半径和 `musttags`
- "搜索附近的拾取物品"
  - 检查 `scripts/simutil.lua` 中的拾取风格 `canttags` 和 one-of-tag 过滤
- "找到附近所有一种类型的建筑或站点"
  - 从 `musttags` 开始

## 性能规则

- 优先使用紧凑的半径值。
- 优先使用 `musttags`、`canttags` 和 `oneoftags`，而非广泛扫描。
- 不要在热路径中放置未过滤的扫描。
- 如果在 `AddPrefabPostInitAny` 中，请在进行区域扫描前积极缩小范围。
- 如果查询只需要最近的匹配项，请使用最近风格的辅助函数或提前停止。
- 如果搜索重复运行，除非半径很小且经过验证，否则避免使用"无标签"扫描。