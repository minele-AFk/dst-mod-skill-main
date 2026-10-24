# 地皮注册、ID 与运行时地形

## 入口与名称

Mod 使用模组环境 AddTile(tile_name, tile_range, tile_data, ground_tile_def, minimap_tile_def, turf_def)。它包装 TileManager 并管理保护开关；不要直接修改 mod_protect_TileManager，也不要等待开关恰好为 false 才登记。

tile_range 使用已注册范围名，如 "LAND"、"OCEAN"、"NOISE"、"IMPASSABLE"；tiledefs 内的局部 TileRanges 不是 GLOBAL.TileRanges。AddTile 把名字转大写，注册后查 WORLD_TILES.MY_MOD_GROUND。不要硬编码数值 ID、占旧教程的公共区间或向 deprecated GROUND 增加字段。

| 参数 | 责任 |
|---|---|
| tile_data | ground_name 与必要的兼容信息；全新 tile 不随便占用 old_static_id |
| ground_tile_def | 地面纹理/噪声、脚步声、可挖/地板/道路等属性 |
| minimap_tile_def | 小地图显示资源 |
| turf_def | 可采集地皮物品的数据与表现依赖 |

各字段按 tilemanager 的 Validate 函数及同类 tiledefs 读取，不从字段英文名推断全部行为。例如 hard、flooring、roadways 是不同属性，不能都解释成“不能种植”。

## 共享注册与资源

当前 mods.lua 在普通运行时也先执行 modworldgenmain，再执行 modmain；前端启用模组时还可重复执行 modworldgenmain。优先把地皮登记集中到 modworldgenmain 入口，并用稳定的 WORLD_TILES 私有名称保护整个注册块；不要在两个入口无条件各登记一次。复用已有 LAND 范围通常无需新建范围，确需 RegisterTileRange 时连同 range 一起防重复。注册发生在消费者初始化前，不在运行回调动态造 ID。

新地皮仍需真实的地面、小地图和 turf 资源；声明表不等于资源已存在。保持源工程，沿 levels/tiles 的实际资源约定检查纹理、边缘和噪声。是否可挖、采下什么、turf 是否已注册由当前 tilemanager、prefabs/turfs.lua 与挖地调用者共同决定，不仅是给一个 name。

本专题 [turf-template.lua](../assets/turf-template.lua) 返回接入函数，由模组入口传入 AddTile 与已准备的三类定义；它不替换默认任务集，也不声称附带美术产物。

## 运行时改地形

Map:GetTileCoordsAtPoint 返回多个坐标时先显式接收 x、y，再传 Map:SetTile(x, y, tile)。不要把多返回函数放在非末尾参数位置，Lua 会只保留第一个值。

SetTile 与 ClearTileUnderneath 不是同一职责，不能宣称前者必然清除 undertile。参考 components/map.lua wrapper、terraformer 与 undertile 的实际管理者；运行时填海还涉及水陆通行、船/平台、海岸、小地图、实体安全位置、拓扑、存档和远端显示。地面颜色变了不代表完整系统成立。

## 查证与验收

2026-10-17 安装包：modutil.lua:356-375、tilemanager.lua:128-159；[源码快照](../../../core/dst-source-research/references/source-research.md#2026-10-17-知识内容复核)。跨阶段与地形边界提炼自 [世界与空间](../../../engineering/dst-mod-engineering/worldgen-spatial.md)。

验证新世界生成、两端 ID 一致、铺挖往返、turf 资源、磁盘重启及已有存档兼容。旧档迁移单独设计并在副本验证，不以重置用户世界代替迁移。
