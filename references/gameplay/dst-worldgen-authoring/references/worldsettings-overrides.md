> 来源：吸收自 [rafaelpadovezi/dst-mods-ai-skills](https://github.com/rafaelpadovezi/dst-mods-ai-skills) 的 worldgen。生成脚本见本 skill `tools/dump_options.lua`，存档检查见 `tools/save_inspect.lua`。

# World settings overrides —— 全部选项与合法取值

**类别：`LEVELCATEGORY.SETTINGS`。** 这些**不塑造地图**。每一项映射到 `worldsettings_overrides.lua` 中的处理器（`Pre` 在世界加载前、`Post` 在之后），通过 `OverrideTuningVariables` 修改 `TUNING`。它们按世界存储，可在已生成的世界上更改。

`hounds = "never"` 与 `antliontribute = "never"` 都属于此类——改的是刷怪计时与献祭需求，不是地形。

下表由游戏自带的 `map/customize.lua` 经 `tools/dump_options.lua` 生成。游戏补丁后请重新运行该脚本。

- **worlds** —— 哪些世界提供该选项。
- **default** —— 未设置时继承的值。
- **values** —— 完整合法词表。词表外的取值是**静默无效**：`OverrideTuningVariables(nil)` 会立刻返回（`worldsettings_overrides.lua:2-12`），界面上像已应用，但 `TUNING` 从未改变。

多数选项使用 5 档 `frequency_descriptions` 词表（`never` `rare` `default` `often` `always`）——注意**没有** `uncommon`、`mostly`、`insane`，与 worldgen 的 8 档词表不同。更窄或无关的取值列表见下表各行。

## animals（动物）

| option | worlds | default | values |
|---|---|---|---|
| `bees_setting` | forest | `default` | `never` `rare` `default` `often` `always` |
| `birds` | forest | `default` | `never` `rare` `default` `often` `always` |
| `bunnymen_setting` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `butterfly` | forest | `default` | `never` `rare` `default` `often` `always` |
| `catcoons` | forest | `default` | `never` `rare` `default` `often` `always` |
| `dustmoths` | cave | `default` | `never` `rare` `default` `often` `always` |
| `fishschools` | forest | `default` | `never` `rare` `default` `often` `always` |
| `gnarwail` | forest | `default` | `never` `rare` `default` `often` `always` |
| `grassgekkos` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `lightfliers` | cave | `default` | `never` `rare` `default` `often` `always` |
| `moles_setting` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `monkey_setting` | cave | `default` | `never` `rare` `default` `often` `always` |
| `mushgnome` | cave | `default` | `never` `rare` `default` `often` `always` |
| `otters_setting` | forest | `default` | `never` `rare` `default` `often` `always` |
| `penguins` | forest | `default` | `never` `rare` `default` `often` `always` |
| `perd` | forest | `default` | `never` `rare` `default` `often` `always` |
| `pigs_setting` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `rabbits_setting` | forest | `default` | `never` `rare` `default` `often` `always` |
| `rocky_setting` | cave | `default` | `never` `rare` `default` `often` `always` |
| `slurtles_setting` | cave | `default` | `never` `rare` `default` `often` `always` |
| `snurtles` | cave | `default` | `never` `rare` `default` `often` `always` |
| `wobsters` | forest | `default` | `never` `rare` `default` `often` `always` |

## events（事件）

| option | worlds | default | values |
|---|---|---|---|
| `crow_carnival` | forest + cave | `default` | `default` `enabled` |
| `hallowed_nights` | forest + cave | `default` | `default` `enabled` |
| `winters_feast` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_beefalo` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_bunnyman` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_carrat` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_catcoon` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_dragonfly` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_gobbler` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_pig` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_snake` | forest + cave | `default` | `default` `enabled` |
| `year_of_the_varg` | forest + cave | `default` | `default` `enabled` |

## giants（巨人/Boss）

| option | worlds | default | values |
|---|---|---|---|
| `antliontribute` | forest | `default` | `never` `rare` `default` `often` `always` |
| `bearger` | forest | `default` | `never` `rare` `default` `often` `always` |
| `beequeen` | forest | `default` | `never` `rare` `default` `often` `always` |
| `crabking` | forest | `default` | `never` `rare` `default` `often` `always` |
| `daywalker` | cave | `default` | `never` `rare` `default` `often` `always` |
| `daywalker2` | forest | `default` | `never` `rare` `default` `often` `always` |
| `deciduousmonster` | forest | `default` | `never` `rare` `default` `often` `always` |
| `deerclops` | forest | `default` | `never` `rare` `default` `often` `always` |
| `dragonfly` | forest | `default` | `never` `rare` `default` `often` `always` |
| `eyeofterror` | forest | `default` | `never` `rare` `default` `often` `always` |
| `fruitfly` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `goosemoose` | forest | `default` | `never` `rare` `default` `often` `always` |
| `klaus` | forest | `default` | `never` `rare` `default` `often` `always` |
| `liefs` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `malbatross` | forest | `default` | `never` `rare` `default` `often` `always` |
| `sharkboi` | forest | `default` | `never` `rare` `default` `often` `always` |
| `spiderqueen` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `toadstool` | cave | `default` | `never` `rare` `default` `often` `always` |

## global（全局）

| option | worlds | default | values |
|---|---|---|---|
| `autumn` | forest + cave | `default` | `noseason` `veryshortseason` `shortseason` `default` `longseason` `verylongseason` `random` |
| `beefaloheat` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `day` | forest + cave | `default` | `default` `longday` `longdusk` `longnight` `noday` `nodusk` `nonight` `onlyday` `onlydusk` `onlynight` |
| `ghostenabled` | forest + cave | `always` | `none` `always` |
| `ghostsanitydrain` | forest + cave | `always` | `none` `always` |
| `krampus` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `portalresurection` | forest + cave | `none` | `none` `always` |
| `resettime` | forest + cave | `default` | `none` `slow` `default` `fast` `always` |
| `spawnmode` | forest + cave | `fixed` | `fixed` `scatter` |
| `specialevent` | forest + cave | `default` | `none` `default` |
| `spring` | forest + cave | `default` | `noseason` `veryshortseason` `shortseason` `default` `longseason` `verylongseason` `random` |
| `summer` | forest + cave | `default` | `noseason` `veryshortseason` `shortseason` `default` `longseason` `verylongseason` `random` |
| `winter` | forest + cave | `default` | `noseason` `veryshortseason` `shortseason` `default` `longseason` `verylongseason` `random` |

## misc（杂项）

| option | worlds | default | values |
|---|---|---|---|
| `acidrain_enabled` | cave | `always` | `none` `always` |
| `alternatehunt` | forest | `default` | `never` `rare` `default` `often` `always` |
| `atriumgate` | cave | `default` | `veryslow` `slow` `default` `fast` `veryfast` |
| `earthquakes` | cave | `default` | `never` `rare` `default` `often` `always` |
| `frograin` | forest | `default` | `never` `rare` `default` `often` `always` |
| `hounds` | forest | `default` | `never` `rare` `default` `often` `always` |
| `hunt` | forest | `default` | `never` `rare` `default` `often` `always` |
| `lightning` | forest | `default` | `never` `rare` `default` `often` `always` |
| `lunarhail_frequency` | forest | `default` | `never` `rare` `default` `often` `always` |
| `meteorshowers` | forest | `default` | `never` `rare` `default` `often` `always` |
| `petrification` | forest | `default` | `none` `few` `default` `many` `max` |
| `rifts_enabled` | forest | `default` | `never` `default` `always` |
| `rifts_enabled_cave` | cave | `default` | `never` `default` `always` |
| `rifts_frequency` | forest | `default` | `never` `rare` `default` `often` `always` |
| `rifts_frequency_cave` | cave | `default` | `never` `rare` `default` `often` `always` |
| `summerhounds` | forest | `default` | `never` `default` |
| `wanderingtrader_enabled` | forest | `always` | `none` `always` |
| `weather` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `wildfires` | forest | `default` | `never` `rare` `default` `often` `always` |
| `winterhounds` | forest | `default` | `never` `default` |
| `wormattacks` | cave | `default` | `never` `rare` `default` `often` `always` |
| `wormattacks_boss` | cave | `default` | `never` `rare` `default` `often` `always` |

## monsters（怪物）

| option | worlds | default | values |
|---|---|---|---|
| `bats_setting` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `chest_mimics` | cave | `default` | `never` `rare` `default` `often` `always` |
| `cookiecutters` | forest | `default` | `never` `rare` `default` `often` `always` |
| `frogs` | forest | `default` | `never` `rare` `default` `often` `always` |
| `hound_mounds` | forest | `default` | `never` `rare` `default` `often` `always` |
| `itemmimics` | cave | `default` | `never` `rare` `default` `often` `always` |
| `lureplants` | forest | `default` | `never` `rare` `default` `often` `always` |
| `merms` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `molebats` | cave | `default` | `never` `rare` `default` `often` `always` |
| `moon_spider` | forest | `default` | `never` `rare` `default` `often` `always` |
| `mosquitos` | forest | `default` | `never` `rare` `default` `often` `always` |
| `mutated_hounds` | forest | `default` | `never` `default` |
| `nightmarecreatures` | cave | `default` | `never` `rare` `default` `often` `always` |
| `penguins_moon` | forest | `default` | `never` `default` |
| `pirateraids` | forest | `default` | `never` `rare` `default` `often` `always` |
| `sharks` | forest | `default` | `never` `rare` `default` `often` `always` |
| `spider_dropper` | cave | `default` | `never` `rare` `default` `often` `always` |
| `spider_hider` | cave | `default` | `never` `rare` `default` `often` `always` |
| `spider_spitter` | cave | `default` | `never` `rare` `default` `often` `always` |
| `spider_warriors` | forest + cave | `default` | `never` `default` |
| `spiders_setting` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `squid` | forest | `default` | `never` `rare` `default` `often` `always` |
| `walrus_setting` | forest | `default` | `never` `rare` `default` `often` `always` |
| `wasps` | forest | `default` | `never` `rare` `default` `often` `always` |

## portal_resources（传送门资源）

| option | worlds | default | values |
|---|---|---|---|
| `bananabush_portalrate` | forest | `default` | `never` `rare` `default` `often` `always` |
| `lightcrab_portalrate` | forest | `default` | `never` `rare` `default` `often` `always` |
| `monkeytail_portalrate` | forest | `default` | `never` `rare` `default` `often` `always` |
| `palmcone_seed_portalrate` | forest | `default` | `never` `rare` `default` `often` `always` |
| `portal_spawnrate` | forest | `default` | `never` `rare` `default` `often` `always` |
| `powder_monkey_portalrate` | forest | `default` | `never` `rare` `default` `often` `always` |

## resources（资源）

| option | worlds | default | values |
|---|---|---|---|
| `basicresource_regrowth` | forest + cave | `none` | `none` `always` |
| `cactus_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `carrots_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `deciduoustree_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `evergreen_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `flower_cave_regrowth` | cave | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `flowers_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `lightflier_flower_regrowth` | cave | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `moon_tree_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `mushtree_moon_regrowth` | cave | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `mushtree_regrowth` | cave | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `palmconetree_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `reeds_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `regrowth` | forest + cave | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `saltstack_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |
| `twiggytrees_regrowth` | forest | `default` | `never` `veryslow` `slow` `default` `fast` `veryfast` |

## survivors（生存）

| option | worlds | default | values |
|---|---|---|---|
| `brightmarecreatures` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `darkness` | forest + cave | `default` | `nonlethal` `default` |
| `dropeverythingondespawn` | forest + cave | `default` | `default` `always` |
| `extrastartingitems` | forest + cave | `default` | `0` `5` `default` `15` `20` `none` |
| `healthpenalty` | forest + cave | `always` | `none` `always` |
| `hunger` | forest + cave | `default` | `nonlethal` `default` |
| `lessdamagetaken` | forest + cave | `none` | `always` `none` `more` |
| `seasonalstartingitems` | forest + cave | `default` | `never` `default` |
| `shadowcreatures` | forest + cave | `default` | `never` `rare` `default` `often` `always` |
| `spawnprotection` | forest + cave | `default` | `never` `default` `always` |
| `temperaturedamage` | forest + cave | `default` | `nonlethal` `default` |

