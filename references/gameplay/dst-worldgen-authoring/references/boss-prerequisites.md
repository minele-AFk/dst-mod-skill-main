> 来源：吸收自 [rafaelpadovezi/dst-mods-ai-skills](https://github.com/rafaelpadovezi/dst-mods-ai-skills) 的 worldgen。生成脚本见本 skill `tools/dump_options.lua`，存档检查见 `tools/save_inspect.lua`。

# Boss 前置链 —— 世界里必须有什么

行号引用均对应 DST 自带的 `data/scripts/`。

有些 Boss 根本不由 worldgen 直接放置：它们由一串物品、建筑和运行时系统解锁，链条上每一环都必须在某处生成。裁剪过的 task set 或自定义 setpiece 可能弄断某一环，且**没有任何 worldgen 报错**，问题要过很多游戏日才暴露。应审计整条链，再用 `tools/save_inspect.lua` 对照真实存档确认（见 [save-files.md](save-files.md)）。

---

## 天体英雄（Celestial Champion，`alterguardian_phase1`）

### 从 Boss 倒推链条

| 步骤 | 代码 |
|---|---|
| 由建成的 `moon_device` 召唤 | `prefabs/moon_device.lua:314` |
| `moon_device_construction1` → `…2` → `moon_device` | `prefabs/moon_device.lua:52-55` |
| 建造 `construction1`：4 `wagpunk_bits`、5 `moonstorm_spark`、2 `transistor`；蓝图为 `TECH.LOST` | `recipes.lua:577` |
| 阶段 1 材料：4 `wagpunk_bits`、10 `moonstorm_spark`、10 `moonglass_charged` | `recipes.lua:1185` |
| 阶段 2 材料：1 `moonstorm_static_item`、20 `moonglass_charged`、1 `moonrockseed` | `recipes.lua:1186` |
| 建在 `moon_altar_link` 点上；该点仅在三座祭坛完成连结后存在 | `prefabs/moon_altar_link.lua:28-33` |
| 连结会启动月亮风暴（`ms_startthemoonstorms`） | `components/moonstormmanager.lua:195-201` |

### 三座祭坛

三座都要把部件嵌进 **`moon_fissure`**（`prefabs/moon_fissure.lua:71-83`）；部件带 `_socket_product`（`prefabs/moon_altar_pieces.lua:226-236`）：

| 祭坛 | 嵌入部件 | 随后修复用 | 部件来源 |
|---|---|---|---|
| `moon_altar`（天体祭坛） | `moon_altar_glass` | `moon_altar_idol`、`moon_altar_seed`（各 ⅓，`moon_altar_pieces.lua:40-41`） | 开采 `moon_altar_rock_glass/idol/seed` |
| `moon_altar_cosmic`（天体贡品） | `moon_altar_crown` | — | 蟹王，见下文 |
| `moon_altar_astral`（天体圣所） | `moon_altar_icon` | `moon_altar_ward` | 用 `archive_resonator` 在 `moon_altar_astral_marker_1` / `_2` 处挖出（`prefabs/archive_resonator.lua:119-175`） |

因此世界需要：**3 处裂隙**、三块祭坛岩石、两处星象标记（由一次性房间 tag `Astral_1` / `Astral_2` 放置——`map/maptags.lua`），以及获取星象探测器的途径。

### 裂隙几何 —— 自定义 setpiece 时必须注意

连结（`components/moonaltarlinktarget.lua:32-64`）要求：

- 三座祭坛都在 `MOON_ALTAR_ESTABLISH_LINK_RADIUS` = **20** 单位内（`tuning.lua:4013`）；
- 每对祭坛间距至少 **2.5** 单位（`MOON_ALTAR_LINK_ALTAR_MIN_RADIUS_SQ`，`tuning.lua:6192`）；
- 不能近似共线——`AltarAngleTest` 要求两角 `|dot| ≤ 0.975`（`moonstormmanager.lua:155-166`，`tuning.lua:4014`）；
- 重心可通行、在地面上，2.5 内无 `antlion_sinkhole_blocker`，且不与 `deploy_extra_spacing` 重叠（`TestMoonAltarLinkPositionValid`，`moonstormmanager.lua:891-910`）。

若 mod 自布裂隙，请按上述数字检查存档里的裂隙坐标——三角形不合格会导致祭坛永不连结，链条无声断掉。连结形成时，连结点 6 单位内的一切会被摧毁（`MOON_ALTAR_LINK_AREA_CLEAR_RADIUS`）。

### 月亮风暴落点 —— 可能卡死服务器

`StartMoonstorm`（`moonstormmanager.lua:318-380`）选一个基准拓扑节点，经 `validedges` 扩散 3 步（`_nummoonstormpropagationsteps`，第 34 行），只保留能过 `NodeCanHaveMoonstorm` 的节点（第 148–153 行）：**不带 `lunacyarea` 或 `sandstorm` 标签，中心不是海洋**。然后循环：

```lua
while #new_storm_nodes < MIN_NODES do      -- MIN_NODES = 4, line 85
    first_node_index = self:CalcNewMoonstormBaseNodeIndex()
    if first_node_index == nil then return end
    propagatestorm(first_node_index, 3, new_storm_nodes)
end
```

唯一出口是「完全没有合格节点」。**若有合格节点，但没有任何一个能在 3 步内连出 4 个合格节点，此循环永不结束，服务器在祭坛连结那一刻挂死**（风暴每次移动也会再触发）。由互不连通的单房间小岛拼成的小世界正是危险形状：月岛是 `lunacyarea`，闪电崖房间是 `sandstorm`，小岛之间没有边。

推理时还有两个细节：

- 移动要求新基准是距原节点超过 50 单位的另一节点（`_basenodemindistancefromprevious`，第 36 行；第 284–312 行）。
- `NodeCanHaveMoonstorm` 本意是跳过上一场风暴的节点，但比较的是 `self.lastnodes`（节点**索引**列表，`StopCurrentMoonstorm`，`components/moonstorms.lua:30-38`）与 `node.area`（多边形面积）。二者几乎永不相等，**该排除实际是空操作**；估计移动能否成功时不要依赖它。

存档里 `topology.edgeToNodes` 不可用（存成 `false`）；运行时会按共享多边形顶点重建，并丢弃两节点间没有清晰陆地的边（`maputil.lua:245-345`）。检查世界时，应从 `map.topology.nodes[*].poly` 重建同一张图，用 tile 图检验节点中心，并从每个合格基准跑一遍扩散。

### 各原料来源

| 物品 | 来源 |
|---|---|
| `moon_altar_crown` | 蟹王死亡掉落，**仅当用珍珠镶嵌过**——`gemcount.pearl >= 1`（`stategraphs/SGcrabking.lua:842-843`） |
| `hermit_pearl` | 隐士，友谊 ≥ 10 **且** 完成 `FIX_HOUSE_3`（`prefabs/hermitcrab.lua:620-623`） |
| 隐士小屋 | 10 `cookiecuttershell` + 10 `boards` + 1 `fireflies`；再 10 `marble` + 5 `cutstone` + 3 `lightbulb`；再 10 `moonrocknugget` + 5 `rope` + 5 `turf_carpetfloor`（`recipes.lua:1179-1181`） |
| `moonrockseed` | `rock_moon_shell`（`prefabs/rocks.lua`） |
| `wagpunk_bits` / `transistor` | 垃圾场、月岛海盗相关 |
| `moonglass_charged` | 月雹、月亮风暴相关产物 |
| `moonrocknugget` | 陨石雨（大陨石可留下 `rock_moon`，`prefabs/shadowmeteor.lua:236-270`）、`moonbase`、月蜘蛛巢 |

### Worldgen 检查清单

`moon_altar_rock_glass`、`moon_altar_rock_idol`、`moon_altar_rock_seed` · 合法三角形内 3× `moon_fissure` · `moon_altar_astral_marker_1` 与 `_2` · `rock_moon_shell` · `crabking_spawner`（`CrabKing` 布局）· 隐士岛（`hermithouse_construction1`）且饼干切割虫、大理石、月岩可达 · 可取得 `wagpunk_bits`/`transistor` 的垃圾场或月岛 · 一簇 ≥ 4 个连通陆地节点，且均非 `lunacyarea` 也非 `sandstorm`。

---

## 远古织影者（Ancient Fuelweaver，`stalker_atrium`）

### 链条

`stalker_atrium` 在把 **暗影心房**（`shadowheart`）交给已完成的 **复活骨架**（`fossil_mound`）时生成——`prefabs/fossil_mound.lua:44-75`。只有满足以下条件才会变成织影者（第 25–39、48–60 行）：

- 世界是洞穴；
- 是夜晚（`TheWorld.state.isnight`）；
- 给予者站在带 **`Atrium`** 标签的节点内（`areaaware:CurrentlyInTag`）；
- **已激活的远古大门**在 `ATRIUM_RANGE` 内；
- 土堆形态正确（`inst.form == 1`）。

否则只会生成普通 `stalker`，或在地表生成 `stalker_forest`。

| 步骤 | 代码 |
|---|---|
| 土堆完整需 8 块 `fossil_piece`（`MAX_MOUND_SIZE`） | `fossil_mound.lua:16` |
| 大门放入 `atrium_key` 后激活 | `prefabs/atrium_gate.lua:141-176` |
| `atrium_key` 在远古守护者留下的箱子里 | `prefabs/minotaur.lua:602-611` |
| `shadowheart` 掉自暗影棋子（满月/新月雕塑——`prefabs/sculptures.lua:47`）或宝箱怪 | `prefabs/shadowchesspieces.lua`、`prefabs/chest_mimic.lua` |

### 化石碎片最容易断

首次织影者前需要 8 块碎片；可再生来源（普通复活骨架，掉 8 块——`prefabs/stalker.lua:68-75`）本身也需要土堆，无法自举。真实来源：

| 来源 | 产出 | 代码 |
|---|---|---|
| `spiderhole`（蜘蛛岩） | 1 + 50% 再 1 | `prefabs/spiderhole.lua:30-31` |
| `stalagmite`、`stalagmite_tall` | **各 10% 一次判定**，仅在完全挖空时 | `prefabs/stalagmite.lua:25`、`prefabs/stalagmite_tall.lua:24,36,45,50-56` |
| 岩树（`tree_rock1/2`） | 按区域加权：`CAVERN_AREA` 权重 2、`MUD_AREA` 0.25、`RUINS_ENTRANCE_AREA` 0.15、**`VENT_AREA` 无**（每树 5 次抽取） | `prefabs/tree_rock_data.lua`、`prefabs/tree_rocks.lua:50,113` |
| 巨型深渊虫（`worm_boss`） | 一次加权抽取；`fossil_piece` 权重 1/39（约 2.6%） | `prefabs/worm_boss.lua:48-68` |

石笋不会再生。蠕虫 Boss 是蠕虫袭击的*波次覆盖*（`components/hounded.lua:640-650`），因此 `wormattacks = "never"` 也会去掉它。

蜘蛛岩只生成在 `RedMushForest`、`RedMushPillars`、`RedSpiderForest`、`SpidersAndBats`、`SpillagmiteForest`、`SpillagmiteMeadow`、`StalagmiteForest`、`StalagmitesAndLights`、`ThuleciteDebris`（`map/rooms/cave/redmush.lua`、`map/rooms/cave/spillagmites.lua`）。task set 不含这些房间的洞穴可能只剩石笋。按每石笋 10%，**20 个石笋平均只有约 2 块碎片，拿到 ≥7 的概率仅 0.24%**。请数清生成洞穴中的来源；若明显到不了 8，就用房间的 `countprefabs` 补 `spiderhole` 或 `fossil_piece`。

### Worldgen 检查清单

`atrium_gate` · `minotaur_spawner`（远古守护者）· 一对 `tentacle_pillar_atrium` · 心房任务的 `room_tags` 含 `"Atrium"` · 足够凑齐 8 的化石碎片来源 · 地表有三件 `sculpture_*body` + 大理石部件（暗影棋子）。
