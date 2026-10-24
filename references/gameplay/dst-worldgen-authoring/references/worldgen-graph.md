# 世界生成层级总览与判别

> 世界生成整体视图：层级关系、扩展点、锁钥可达性、密度上限、环境约束。补全 `worldgen-tile-terrain.md`（地皮）、`worldgen-data-and-hooks.md`（数据结构）、`worldgen-scenarios-hooks.md`（流程）的接入视角。出处以本地 `D:\mods\scripts` 源码为准。

## 层级（从大到小）

```
Location 选择生成环境（森林/洞穴/熔岩竞技场/猪镇——map/locations.lua）
  └─ Level 选择 TaskSet 与 overrides（map/levels.lua / tasksets.lua）
       └─ TaskSet 组合 Task（tasks + optionaltasks + set_pieces + ocean_population）
            └─ Task 通过锁钥图连接 Room（map/tasks.lua / lockandkey.lua）
                 └─ Room 决定地皮、内容分布与可选布局（map/rooms.lua / layouts.lua）
```

世界生成主控：`worldgen_main.lua → Level.ChooseTasks → forest_map.Generate → Story:BuildStory → Graph/Node → 输出 save.ents`。

## 常用扩展点

- 新增使用模组环境 AddLocation/AddLevel/AddTaskSet/AddTask/AddRoom/AddStartLocation；底层 AddMod* 并非同签名别名。
- 打补丁给内置对象用 `...PreInit`：`AddLevelPreInit` / `AddTaskSetPreInit` / `AddTaskPreInit` / `AddRoomPreInit`（推荐替代改 terrain 表）。
- 布局：改 `map/layouts` 的 `Layouts` 表 + `StaticLayout.Get`；scenario 注入实体。
- 密度/环境：`level.overrides` + MULTIPLY 系统；Bunches 成簇生成。

## 锁钥可达性

`locks`（进门需要，任一满足）+ `keys_given`（完成后给的钥匙）驱动 Task 间连通（`LOCKS/KEYS/LOCKS_KEYS`，lockandkey.lua）。上古钥匙：`LOCKS.NONE` 表示无条件任务；`entrance_room` / `valid_start_tasks` 控制出生可达。

## 密度上限与环境约束

- 密度：`MULTIPLY`（never/rare/uncommon/default/often/mostly/always/insane）乘算放置密度；`overrides` 里的 prefab 计数为 `"rare"` 等档位。
- 环境约束：`IsLandTile/IsOceanTile/IsImpassableTile` 过滤放置（TileGroupManager）；`required_prefabs` 保证关键实体；`keep_disconnected_tiles` / `min_dist_from_land` 控制岛屿布局。
- 地皮用环境 AddTile，当前运行也加载 modworldgenmain，可集中于此并防重入；运行回调不手改 WORLD_TILES。required_prefabs 是生成约束，仍需检查生成日志和最终存档，不代表任何空间条件下都必定成功。