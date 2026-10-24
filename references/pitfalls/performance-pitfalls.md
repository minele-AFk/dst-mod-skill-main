# 性能常见陷阱

用于处理热点路径和广泛钩子的错误。

## `TheSim:FindEntities` 可能很快变得昂贵

- 使用较小的半径值。
- 积极使用标签过滤器。
- 避免在周期性任务或广泛触发的钩子中进行广泛扫描。

观察到的使用模式：

```lua
TheSim:FindEntities(x, y, z, radius, musttags, canttags, oneoftags)
```

常见的昂贵模式：

```lua
inst:DoPeriodicTask(FRAMES, function()
    local ents = TheSim:FindEntities(x, y, z, 30)
end)
```

更安全的模式：

```lua
inst:DoPeriodicTask(period, function()
    local ents = TheSim:FindEntities(x, y, z, radius, MUST_TAGS, CANT_TAGS, ONE_OF_TAGS)
end)
```

然后尽可能保持 `period`、`radius` 和标签过滤的严格性。

## `AddPrefabPostInitAny` 可能成为陷阱

- 它会为每个生成的预制件运行。
- 立即使用标签或预制件名称等廉价检查进行缩小范围。
- 当只需要单个预制件系列时，使用 `AddPrefabPostInit`。

常见的昂贵模式：

```lua
AddPrefabPostInitAny(function(inst)
    -- 对所有预制件执行繁重工作
end)
```

更安全的模式：

```lua
AddPrefabPostInitAny(function(inst)
    if inst.prefab ~= "target_prefab" then
        return
    end
    -- 缩小范围后的工作
end)
```

## 周期性任务需要合理理由

官方 DST 使用许多 `DoPeriodicTask(...)` 循环，但通常带有以下一个或多个约束：

- 狭窄的所有权范围
- 粗粒度的更新间隔
- 小半径查询
- 廉价的早期退出

实用规则：

- 如果任务每帧或每隔几帧运行一次，假设它对性能敏感
- 如果任务扫描世界，证明半径和过滤器是严格的
- 如果行为可以由事件驱动，优先使用事件驱动而不是轮询

## 快速排查

- 如果问题是广泛区域扫描，请阅读 `references/patterns/runtime/entity-query-patterns.md`
- 如果问题是钩子选择过于广泛，请检查 `references/mod-api-map.md`
- 如果问题实际上是权威或本地 UI 混淆，不要首先归咎于性能