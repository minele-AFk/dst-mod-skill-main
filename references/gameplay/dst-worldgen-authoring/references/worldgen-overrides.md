> 来源：吸收自 [rafaelpadovezi/dst-mods-ai-skills](https://github.com/rafaelpadovezi/dst-mods-ai-skills) 的 worldgen。生成脚本见本 skill `tools/dump_options.lua`，存档检查见 `tools/save_inspect.lua`。

# Worldgen overrides —— 全部选项与合法取值

**类别：`LEVELCATEGORY.WORLDGEN`。** 这些选项在**地图生成过程中**被消费（`map/forest_map.lua`），并写入存档。世界已生成后再改无效——必须重新生成世界。

下表由游戏自带的 `map/customize.lua` 经 `tools/dump_options.lua` 生成。游戏补丁后请重新运行该脚本。

- **worlds** —— 哪些世界会提供该选项。写在错误的世界上永远不会被读取。
- **default** —— level 未设置时继承的值。优先取 `map/locations.lua` 里的按世界默认值（`task_set`、`start_location`、`world_size`、`season_start`、`roads`），否则取 `map/customize.lua` 中该选项自身的 `value`。
- **values** —— 完整合法词表。词表之外一律无效。超出词表的取值会被静默忽略或导致生成失败，不要自造取值。

注意：`ocean_waterplant` 与 `ocean_seastack` 使用带 `ocean_` 前缀的词表（`ocean_never` … `ocean_insane`），而 `ocean_otterdens`、`ocean_wobsterden`、`ocean_shoal`、`ocean_bullkelp` 使用普通词表。

```text
taskgrouplist:	classic	S.UI.CUSTOMIZATIONSCREEN.TASKSETNAMES.CLASSIC
taskgrouplist:	cave_default	S.UI.CUSTOMIZATIONSCREEN.TASKSETNAMES.CAVE_DEFAULT
taskgrouplist:	lavaarena_taskset	S.UI.CUSTOMIZATIONSCREEN.TASKSETNAMES.LAVA_ARENA
taskgrouplist:	quagmire_taskset	S.UI.CUSTOMIZATIONSCREEN.TASKSETNAMES.QUAGMIRE
```

# WORLDGEN（生成期）

## animals（动物）

| option | worlds | default | values |
|---|---|---|---|
| `beefalo` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `bees` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `bunnymen` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `buzzard` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `catcoon` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `lightninggoat` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moles` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `monkey` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_carrot` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_fruitdragon` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `ocean_otterdens` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `ocean_shoal` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `ocean_wobsterden` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `pigs` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `rabbits` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `rocky` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `slurper` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `slurtles` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |

## global（全局）

| option | worlds | default | values |
|---|---|---|---|
| `season_start` | forest + cave | `default` | `default` `winter` `spring` `summer` `autumn\|spring` `winter\|summer` `autumn\|winter\|spring\|summer` |

## misc（杂项）

| option | worlds | default | values |
|---|---|---|---|
| `balatro` | forest | `default` | `never` `default` |
| `boons` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `branching` | forest + cave | `default` | `never` `least` `default` `most` `random` |
| `cavelight` | cave | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `junkyard` | forest | `default` | `never` `default` |
| `loop` | forest + cave | `default` | `never` `default` `always` |
| `moon_fissure` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `prefabswaps_start` | forest + cave | `default` | `classic` `default` `highly random` |
| `roads` | forest | `default` | `never` `default` |
| `stageplays` | forest | `default` | `never` `default` |
| `start_location` | cave | `caves` | `caves` |
| `start_location` | forest | `default` | `darkness` `default` `plus` |
| `task_set` | cave | `cave_default` | `cave_default` |
| `task_set` | forest | `default` | `classic` `default` |
| `terrariumchest` | forest | `default` | `never` `default` |
| `touchstone` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `world_size` | forest + cave | `default` | `small` `medium` `default` `huge` |

## monsters（怪物）

| option | worlds | default | values |
|---|---|---|---|
| `angrybees` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `bats` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `cave_spiders` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `chess` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `fissure` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `houndmound` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `merm` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_spiders` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `ocean_waterplant` | forest | `ocean_default` | `ocean_never` `ocean_rare` `ocean_uncommon` `ocean_default` `ocean_often` `ocean_mostly` `ocean_always` `ocean_insane` |
| `spiders` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `tallbirds` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `tentacles` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `walrus` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `worms` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |

## resources（资源）

| option | worlds | default | values |
|---|---|---|---|
| `banana` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `berrybush` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `cactus` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `carrot` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `cave_ponds` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `fern` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `flint` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `flower_cave` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `flowers` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `grass` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `lichen` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `marshbush` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `meteorspawner` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_berrybush` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_bullkelp` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_hotspring` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_rock` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_sapling` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_starfish` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `moon_tree` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `mushroom` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `mushtree` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `ocean_bullkelp` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `ocean_seastack` | forest | `ocean_default` | `ocean_never` `ocean_rare` `ocean_uncommon` `ocean_default` `ocean_often` `ocean_mostly` `ocean_always` `ocean_insane` |
| `palmconetree` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `ponds` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `reeds` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `rock` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `rock_ice` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `sapling` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `trees` | forest + cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `tumbleweed` | forest | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |
| `wormlights` | cave | `default` | `never` `rare` `uncommon` `default` `often` `mostly` `always` `insane` |

