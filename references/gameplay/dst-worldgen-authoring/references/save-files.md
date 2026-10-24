> 来源：吸收自 [rafaelpadovezi/dst-mods-ai-skills](https://github.com/rafaelpadovezi/dst-mods-ai-skills) 的 worldgen。生成脚本见本 skill `tools/dump_options.lua`，存档检查见 `tools/save_inspect.lua`。

# 世界存档调试

Worldgen 日志只说明世界**是否**生成成功。要查世界实际内容——Boss 链、setpiece 真实位置、地图拓扑——请读 session 存档。行号引用均对应 DST 自带的 `data/scripts/`。

**只读操作，或操作副本。** 绝不要改服务器可能加载的存档；`tools/save_inspect.lua` 只把文件加载进空环境，不写回。

## 存档位置

```text
<Klei>/DoNotStarveTogether/<account>/Cluster_<n>/<Master|Caves>/save/session/<session id>/<nnnnnnnnnn>
```

- `<Klei>` 在 Windows 是 `Documents/Klei`（常在 OneDrive 下），Linux 是 `~/.klei`，macOS 是 `~/Documents/Klei`。
- 每个分片一个目录；**编号最大**的文件是最新存档。每个都有对应的 `.meta`。
- 以哈希用户 ID 命名的子目录放该玩家自己的文件：是裸的 `return {x=…, z=…, data={inventory=…, health=…, builder=…}}`，不是 `savedata` 表，因此 `save_inspect.lua` 会拒绝——请直接用 `loadstring` 读。
- `Cluster_<n>/<shard>/server_log.txt` 是该分片日志；顶层 `master_server_log.txt` / `caves_server_log.txt` 是最近一次运行集群的副本。注意看文件时间，它们很容易过期。

## 格式

Session 存档是纯 Lua 源码：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
local savedata = {}
local tablefunctions = {}
tablefunctions["shard_network_fn"] = function() return {persistdata={...}} end
savedata["shard_network"] = tablefunctions["shard_network_fn"]()
...
savedata["map"] = tablefunctions["map_fn"]()
return savedata
```

末尾跟一个 **NUL 字节**，因此在裁掉最终 `return savedata` 之后的内容前，`loadfile` 会报 `'<eof>' expected`。

顶层键：

| 键 | 含义 |
|---|---|
| `map` | 地块、拓扑、世界 tile 映射 |
| `ents` | 当前实体存档记录 |
| `shard_network` / `world_network` | 跨分片与世界级 persistdata |
| 其余 | 见游戏 `maputil` / 保存逻辑 |

`ents` 里的名字是**现在**存在的，不是 worldgen 放置过的：`minotaur_spawner` 产出 `minotaur` 后就没了；一对 `tentacle_pillar_atrium` 会存成两个 `tentacle_pillar`，`teleporter.target` 互相指向。容器内物品不是顶层条目——它们在持有者的 `data.container.items[n] = {prefab, x, z, data}`（如 `pandoraschest`），所以 `count` 看不到箱子里的化石碎片。玩家背包在各自的玩家文件里。

### 地块（Tiles）

`map.tiles` 是 base64。解码后是短头（`VRSN…`）+ 每格一个 little-endian **uint16**，按行排列；头长度为 `#decoded - 2 * width * height`。`map.world_tile_map` 映射 tile **名 → id**（id 每存档不同，不要写死）。

世界坐标 → tile：`tx = floor(x / 4 + width / 2)`，`tz = floor(z / 4 + height / 2)`（`TILE_SCALE` = 4）。

### 拓扑

`map.topology` 有平行数组 `ids[i]` 与 `nodes[i]`：

- `ids[i]`：任务房间为 `"<task>:<index>:<room>"`，背景节点为 `"<task>:BG_<n>:<room>"`，海上 setpiece 岛为 `"StaticLayoutIsland:<layout>"`，以及 `START`、`REGION_LINK_*`（岛屿连接）。
- `nodes[i]` 含 `tags`、`cent`（世界 x/z）、`x`/`y`、`poly`（顶点表）、`area`、`type`。

`edgeToNodes` 与 `flattenedEdges` 存成 `false`。游戏在加载时按共享多边形顶点重建连通，再移除两节点间没有清晰陆地的边（`maputil.lua:245-345`）。运行时走 `validedges` 的逻辑（例如月亮风暴落点）看到的是重建后的图，分析存档时也要同样重建。

## `tools/save_inspect.lua`

```bash
S=tools/save_inspect.lua
SAVE=".../Cluster_3/Master/save/session/<id>/0000000010"

luajit $S "$SAVE" summary                          # 地图大小、节点数、最常见 prefab
luajit $S "$SAVE" count moon_fissure,crabking,junk_pile_big
luajit $S "$SAVE" find "^moon_altar"               # Lua pattern，不是正则（无 \|
luajit $S "$SAVE" pos moon_fissure                 # 各实例坐标 + 所在 tile
luajit $S "$SAVE" data tentacle_pillar 4           # 存档组件数据，深度 4
luajit $S "$SAVE" nodes "Island"                   # 拓扑节点、中心 tile、tags
luajit $S "$SAVE" tile -30 222
luajit $S "$SAVE" network                          # shard/world network persistdata
```

常见用法：

- **setpiece 真的放下了吗？** 用 `count` 查其唯一 prefab。为 `0` 且日志无 `Could not find a spot`，通常表示后来被移除（例如 `IMPASSABLE` 上的实体会在放置后被清掉）或从未请求放置。
- **Boss 链完整吗？** 对 [boss-prerequisites.md](boss-prerequisites.md) 里每一环 `count`。
- **自定义布局几何合法吗？** `pos` 给出精确坐标，用来对照连结半径、间距与角度规则。
- **跨分片 Boss 在等哪个分片？** 看 `network`——例如 `shard_daywalkerspawner.location = "cavejail"` 表示洞穴梦魇疯猪要先被击败，地表那个才会出现。
- **这个点是什么生物群系？** `nodes` + `tile`。

命令覆盖不到的，直接复用脚本里的 `load_save` 函数，对返回表自行查询。
