# 《道诡异仙》DST Mod 逆向研究笔记

> 研究对象：E:\神秘复苏\饥荒大型mod\3155177428\（Steam Workshop 3155177428）
> 规模：约 783 个文件；所有 .lua 均被"风雪"加密器（frostxx@qq.com）加密，本笔记为完整解密还原后的分析。
> 主题：国产克苏鲁/民俗恐怖修仙题材。核心卖点：诡异生物（吃人鬼、鬼新娘、尸树）、灵草种植（人参/灵芝）、青云寺特色岛屿、危险之地任务区、SAN 值侵蚀氛围。

---

## 第 1 章 mod 全貌

### 1.1 基本信息

| 项 | 值 |
|---|---|
| Workshop ID | 3155177428 |
| modinfo.lua | 声明 PrefabFiles / modimport / 配置项（GetModConfigData） |
| modmain.lua | 内联 VM 解密器 + 30 个加密 chunk（_dec_1 ~ _dec_30） |
| modworldgenmain.lua | 内联 VM + 1 个世界生成 chunk（2 万字节） |
| main/*.lua、scripts/*.lua | 二进制流加密（位置相关流密码 + RLE marker 0x02/0x03/0x19/0x1b） |
| 字符串二次混淆 | 所有中文字符运行时按字符级替换为密文字符（"钠""砌""瞿"高频，原始 GBK 字节） |

### 1.2 内容清单（从 PrefabFiles 还原）

- 角色（2 个自定义 + 双神系统）：daogui_blm（白灵淼）、daogui_lhw（李火旺）、daogui_twogods
- 恐怖生物群：chomper（吃人鬼）、corpse_tree（尸树，含头/手/脚/心/体部位）、crow（乌鸦鬼）、colourfuldeer（彩色鹿）、batherd（鸡群）、demon、eyedevil（眼魔）、ghostbride（鬼新娘）、reddragon、spiderman、danyangzi（丹阳子）、december18（十二月十八）、dancing_lion（舞狮）、blacktaisui、abbess（师太）、bingjiexian（兵解仙）
- 诡异植物：corpse_flower（尸花/食人花）、demonflower（魔花）、eyefruit（眼果）、wheat（道诡麦）、sharp_berrybush（尖刺灌木）、mystic_tree（神秘树）、red_webtree（红蛛树）、qingtitree（青提树）、skulltree（骷髅树）、byg（鬼阴树）、gys、dioptase（翠榴石）、farm_plants_herbs（人参/灵芝灵草）
- 恐怖建筑/装饰：doomsdoor（末日门）、bloodpond（血池）、bloodwell（血井）、bloodcarpet（血毯）、maxwelllight、dragoncoffin（龙棺）、ghostpainting（鬼画）、whitebone_tribute_table（白骨供桌）、chandelier、grave（道诡坟墓）、bonefence（骨篱笆）、palanquin（轿子）
- 装备/道具：backbone_sword（脊骨剑）、copper_sword（铜钱剑）、spikesword/spinesword、feather_bone_fan（骨扇）、yuehuarobe、soulumbrella（魂伞）、shroud（裹尸布）、bottle（瓶）、coin（铜钱）、drum（鼓）、gourd（葫芦）、pendant、xuanpin（玄牝）、scroll_dql（大千录功法卷轴）
- 系统组件（components/）：daogui_age（年龄/寿命）、daogui_ominous（凶兆）、daogui_shroud、daogui_score（任务积分）、daogui_regrowthmanager（妖植再生长）、daogui_forestresourcespawner（麦田再生）、daogui_pickable（妖植采摘）、daogui_plantpotseed（种植盆）、daogui_flyer（飞行）、daogui_book/reader/spellbookcooldowns（法术书冷却）、daogui_npc（NPC 对话）、daogui_twogods_ai、daogui_bigfooter、daogui_lhw_upgrade（李火旺升级）、daogui_transfer_god（神降）

### 1.3 加密架构（逆向结论）

三层防御：
1. 入口文件为明文 wrapper，内联"LOL!"解码器 + 自定义 VM（opcode 100+，解释器 v29 内联）。wrapper 反调试：检查 `debug.getinfo(loadstring,'S').source == '=[C]'`（loadstring 必须为 C 函数）。
2. VM 内部解密主逻辑（modmain 30 chunks、worldgen 1 chunk），解密后 loadstring 执行。
3. scripts/ 子文件由 VM 安装的 require shim 按需解密加载（shim 从 `MODROOT.."scripts/"..gsub(name,"%.","/")..".lua"` 读取 → 流解密 → loadstring）。hook loadstring 即可在任意执行前捕获源码，无需破解算法。

---

## 第 2 章 框架架构

### 2.1 模块组织

```
modmain.lua                -- 明文 wrapper：LOL! 解码 + VM 执行主逻辑
modworldgenmain.lua        -- 明文 wrapper：VM 执行世界生成逻辑（2 万字节）
scripts/
  daogui_turf_defs.lua     -- 自定义地皮 tile 定义表（2 个）
  daogui_food_defs.lua     -- 食物定义（MakeMeat 等工厂）
  daogui_abbess_items.lua  -- 师太交易物品表
  daogui_xuanpin_*.lua     -- 玄牝系统（动画/积分/任务）
  map/daogui_qingfengtemple.lua -- 青云寺岛屿 retrofit 逻辑
  map/static_layouts/      -- 6 个 Tiled 格式静态布局（岛屿/危险地/农田）
  prefabs/                 -- 约 110 个 prefab（生物/植物/建筑/物品）
  components/              -- 约 36 个自定义组件
  stategraphs/ brains/ widgets/
main/                      -- VM 内部的 main 文件（modmain 通过 modimport 引用）
images/  anim/             -- atlas（xml+tex 配对）与动画 zip
```

### 2.2 modmain 骨架（解密后 _dec_1）

```lua
GLOBAL.setmetatable(env, {__index = function(t, k) return GLOBAL.rawget(GLOBAL, k)end})

_G.DAOGUIAPI = env

PrefabFiles = {
    "daogui_backbone_sword",
    "daogui_batherd",
    ...
    "daogui_abbess",
    "daogui_blacktaisui",
    ...
    -- 带皮肤的角色/物品在第二区段注册
}

local mainfiles =
{
    --"daogui_map_modifier",
    -- "daogui_seamlessplayerswapper_modifier",
}

for _, file in ipairs(mainfiles) do
    modimport("main/" .. file)
end

Assets = {
    Asset("ANIM", "anim/daogui_researchlab3.zip"),
    Asset("ANIM", "anim/daogui_turfs.zip"),
    ...
}
```

关键点：
- **`_G.DAOGUIAPI = env`**：把 VM 的隔离环境（含所有 require shim、解密函数）暴露为全局 API，后续 chunk 共享同一环境。
- **PrefabFiles 分段注册**：第一段为恐怖生物/基础物品，第二段为青云寺 DLC 内容（带注释分隔），被注释的是未启用的（ghostbride、skulltree 等）。
- **数值集中配置**：`_G.DAOGUI = { BLM = {HEALTH=120,...}, CHOMPER = {HEALTH=6000, DAMAGE=50, ATTACK_PERIOD=2.5}, ... }`（_dec_3），所有 prefab 从这张表取数。

### 2.3 TUNING 注入模式（_dec_1）

```lua
TUNING.DAOGUI_BLM_HEALTH = DAOGUI.BLM.HEALTH
TUNING.DAOGUI_BLM_SANITY = DAOGUI.BLM.SANITY
TUNING.DAOGUI_BLM_HUNGER = DAOGUI.BLM.HUNGER
TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT.DAOGUI_BLM = {
    ...
}
TUNING.STARTING_ITEM_IMAGE_OVERRIDE["daogui_drum"] = {
    atlas = "images/inventoryimages/daogui_drum.xml",
    image = "daogui_drum.tex"
}
```

### 2.4 对原版系统的动态扩展（AddMoreVeggie / AddMorePlant，_dec_1）

```lua
AddSimPostInit(function()
    for k, v in pairs(DAOGUI_VEGGIES) do
        ...
    end
end)

local function AddMoreVeggie(name, hng1, san1, hp1, time1, hng2, san2, hp2, time2, chance)
    ...
end
AddMoreVeggie("daogui_hmg", 4, 15, 3.5, TUNING.PERISH_MED, 6, 16, 7, TUNING.PERISH_SUPERFAST, TUNING.SEED_CHANCE_RARE)

local PLANT_DEFS = require("prefabs/farm_plant_defs").PLANT_DEFS
local function AddMorePlant(name, bank)
    for k, v in pairs(PLANT_DEFS.watermelon) do
        ...
    end
end
```

即：不直接改原版 farm_plant_defs，而是以 `watermelon` 为模板复制出新的植物定义（含季节/生长/种子权重），运行时挂进 PLANT_DEFS。

### 2.5 世界生成架构（_wgen_1 = modworldgenmain 解密）

完整链路（详见第 3 章与专题章节）：
```
daogui_turf_defs（tile 表）
  └─ AddTile 循环注册 2 个自定义地皮
  └─ ChangeTileRenderOrder / ChangeMiniMapTileRenderOrder
StaticLayout.Get（6 个布局）
  └─ Layouts["DaoGui_DangerLand"] 等
AddRoom（DaoGui_Doomsdoor_Area / DaoGui_DangerLand / DaoGui_DangerLand_Empty）
AddTask / AddTaskPreInit / AddTaskSetPreInit("default")
AddLevelPreInitAny（岛屿塞进 ocean_prefill_setpieces）
retrofit hook（DoRetrofitting 包装 → TurnOfTidesRetrofitting）
房间后置注入（Forest 房间加 daogui_gys_tall；GreenMushPonds 加 daogui_octopus）
```

---

## 第 3 章 关键设计模式

### 3.1 地皮 / 地形 / 世界生成

#### 3.1.1 自定义地皮 tile 定义表

出处：scripts/daogui_turf_defs.lua（解密文件 drafts/_s_2.lua）

```lua
local turfs = {
    {
        tile_name = "DAOGUI_QINGFENGTEMPLE",
        tile_range = "LAND",
        tile_data = {
            ground_name = "daogui_qingfengtemple",
        },
        ground_tile_def = {
            name = "grass",-- 地表样式文件，对照 data/levels/tiles/grass.xml
            noise_texture = "daogui_qingfengtemple.tex",-- 噪声图 512*512
            runsound ="dontstarve/movement/run_dirt",
            walksound ="dontstarve/movement/run_dirt",
            snowsound ="dontstarve/movement/run_ice",
            mudsound ="dontstarve/movement/run_mud",
        },
        minimap_tile_def = {
            name = "map_edge",
            noise_texture = "mini_daogui_qingfengtemple.tex",-- 小地图噪声图 256*256
        },
    },
    {
        tile_name = "DAOGUI_RAIN_FOREST",
        tile_range = "LAND",
        tile_data = {
            ground_name = "daogui_rain_forest",
        },
        ground_tile_def = {
            name = "grass",
            noise_texture = "Ground_noise_rainforest.tex",
            runsound ="dontstarve/movement/run_dirt",
            walksound ="dontstarve/movement/run_dirt",
            snowsound ="dontstarve/movement/run_ice",
            mudsound ="dontstarve/movement/run_mud",
        },
        minimap_tile_def = {
            name = "map_edge",
            noise_texture = "mini_noise_rainforest.tex",
        },
        -- turf_def =  -- 可选的 turf 物品定义（踩上去能挖地皮）
        -- {
        --     name = "daogui_rain_forest",
        --     anim = "daogui_rain_forest",
        --     bank_override = "daogui_turfs",
        --     build_override = "daogui_turfs",
        -- }
    },
}

return turfs
```

要点：tile_name 进 `WORLD_TILES` 表；ground_tile_def.name 决定地表渲染管线；turf_def 被注释掉说明该地皮不可被铲子采集（岛内地皮保护）。

#### 3.1.2 AddTile 循环注册 + 渲染顺序

出处：modworldgenmain.lua（解密 drafts/_wgen_1.lua）

```lua
local daogui_turf_defs = require "daogui_turf_defs"

for k, data in pairs(daogui_turf_defs) do
    AddTile(data.tile_name, data.tile_range, data.tile_data, data.ground_tile_def, data.minimap_tile_def, data.turf_def)
    if data.turf_def ~= nil then
        AddPrefabPostInit("turf_"..data.turf_def.name, function (inst)
            if not TheWorld.ismastersim then
                return
            end
            if inst.components.inventoryitem ~= nil then
                inst.components.inventoryitem.atlasname = "images/inventoryimages/turf_"..data.turf_def.name..".xml"
                inst.components.inventoryitem.imagename = "turf_"..data.turf_def.name
            end
        end)
    end
end

ChangeTileRenderOrder(WORLD_TILES.DAOGUI_QINGFENGTEMPLE, WORLD_TILES.MOSAIC_GREY)
ChangeMiniMapTileRenderOrder(WORLD_TILES.DAOGUI_QINGFENGTEMPLE, WORLD_TILES.MOSAIC_GREY)
ChangeTileRenderOrder(WORLD_TILES.DAOGUI_RAIN_FOREST, WORLD_TILES.FOREST)
ChangeMiniMapTileRenderOrder(WORLD_TILES.DAOGUI_RAIN_FOREST, WORLD_TILES.FOREST)
```

#### 3.1.3 布局 → 房间 → 任务三级挂载

出处：modworldgenmain.lua（_wgen_1.lua）

```lua
Layouts["DaoGui_Doomsdoor_Area"] = StaticLayout.Get("map/static_layouts/daogui_doomsdoor_area", {
    start_mask = GLOBAL.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    fill_mask = GLOBAL.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    layout_position = GLOBAL.LAYOUT_POSITION.CENTER,
})

AddRoom("DaoGui_Doomsdoor_Area", {
    colour={r=0,g=.9,b=0,a=.50},
    value = WORLD_TILES.DECIDUOUS,
    tags = {"ExitPiece", "Chester_Eyebone", "Astral_2"},
    required_prefabs = {"daogui_doomsdoor"},
    contents =  {
        countstaticlayouts={
            ["DaoGui_Doomsdoor_Area"] = 1,
        },
    }
})

AddTaskPreInit("Speak to the king", function(task)  -- 给原版猪王任务插入自定义房间
    task.room_choices["DaoGui_Doomsdoor_Area"] = 1
end)
```

危险之地任务（完整自定义任务链）：

```lua
AddRoom("DaoGui_DangerLand", {
    colour = {r = 0.5, g = 0.8, b = 0.5, a = 0.5},
    value = WORLD_TILES.FOREST,
    tags = {"RoadPoison", "nohunt", "daogui_dangerland"},
    internal_type = NODE_INTERNAL_CONNECTION_TYPE.EdgeCentroid,
    contents = {
        countstaticlayouts = {
            ["DaoGui_DangerLand"] = 1,
        },
        countprefabs = {
            daogui_chomper = 2,
            daogui_grave = 1,
            daogui_colourfuldeer = 2,
        },
        distributepercent = 0.3,
        distributeprefabs = {
            daogui_mystic_tree = 0.1,
            daogui_byg_tall = 0.2,
            grass = 0.3,
            sapling = 0.2,
            beehive = 0.05,
            pighouse = 0.05,
            evergreen_short = 0.2,
            evergreen_normal = 0.2,
            evergreen_tall = 0.2,
            flower = 0.3,
            daogui_wheat = 0.3,
            skeleton = 0.25,
            daogui_sharp_berrybush = 0.1,
        },
    },
})

AddRoom("DaoGui_DangerLand_Empty", {
    colour = {r = 0.5, g = 0.8, b = 0.5, a = 0.5},
    value = WORLD_TILES.FOREST,
    tags = {"RoadPoison", "nohunt", "daogui_dangerland"},
    internal_type = NODE_INTERNAL_CONNECTION_TYPE.EdgeCentroid,
    contents = {
        countprefabs = {
            daogui_corpse_flower = 1,
            daogui_batherd = function() return math.random(2, 3) end,
            daogui_grave = 1,
            daogui_chomper = 2,
            daogui_colourfuldeer = 2,
        },
        distributepercent = 0.3,    -- 撒点密度（0~1）
        distributeprefabs = {
            daogui_mystic_tree = 0.2,
            daogui_byg_tall = 0.2,
            grass = 0.5,
            sapling = 0.4,
            ...
            daogui_wheat = 0.35,
            skeleton = 0.15,
            daogui_sharp_berrybush = 0.2,
        },
    },
})

AddTask("DaoGui_DangerLand", {
    colour = {r = 0.6, g = 0.6, b = 0.0, a = 1},
    locks = {LOCKS.NONE},
    keys_given = {},
    room_tags = {"RoadPoison", "nohunt", "daogui_dangerland"},
    room_choices = {
        ["DaoGui_DangerLand"] = 1,
        ["DaoGui_DangerLand_Empty"] = 2,
    },
    room_bg = WORLD_TILES.FOREST,
    entrance_room = "DaoGui_DangerLand_Empty",
    hub_room = "DaoGui_DangerLand",
    background_room = "DaoGui_DangerLand_Empty",
})

AddTaskSetPreInit("default", function(task)
    table.insert(task.tasks, "DaoGui_DangerLand")
    -- table.insert(task.tasks, "DaoGui_Doomsdoor_Area")
end)
```

套路总结：
- countprefabs 的 value 可以是函数（`function() return math.random(2,3) end`）→ 动态数量
- distributepercent + distributeprefabs（权重表）→ 房间内随机撒资源
- AddTaskSetPreInit("default") 插任务 → 无锁任务（LOCKS.NONE）保证必出
- 自定义房间 tag 需要注册：maptags 包装 + Story 类后置（见下）

```lua
local __MakeTags = _G.package.loaded[pule]
_G.package.loaded[pule] = function()
    local tb = __MakeTags()
    tb.Tag["daogui_dangerland"] = function(tagdata) return "TAG", "daogui_dangerland" end
    tb.Tag["DaoGuiQingFengTempleArea"] = function(tagdata) return "TAG", "DaoGuiQingFengTempleArea" end
    return tb
end

AddGlobalClassPostConstruct("map/storygen", "Story", function(self)
    self.map_tags.Tag["daogui_dangerland"] = function(tagdata) return "TAG", "daogui_dangerland" end
    self.map_tags.Tag["DaoGuiQingFengTempleArea"] = function(tagdata) return "TAG", "DaoGuiQingFengTempleArea" end
end)
```

（这是给自定义房间 tag 注入 maptags 的标准做法——否则任务生成器不认识自定义 tag 会崩溃。）

#### 3.1.4 房间后置注入（不新建房间，往原版房间塞内容）

```lua
local Marsh = rooms.GetRoomByName("Forest")
if Marsh then
    if not Marsh.contents then
        Marsh.contents = {}
        Marsh.contents.countprefabs = {}
    end
    if not Marsh.contents.countprefabs then
        Marsh.contents.countprefabs = {}
    end
    Marsh.contents.countprefabs.daogui_gys_tall = function() return math.random(1, 2) end
end

local fungitree_rooms = { "GreenMushPonds" }
for _, roomname in ipairs(fungitree_rooms) do
    local R = rooms.GetRoomByName(roomname)
    if R then
        ...
        R.contents.countprefabs.daogui_octopus = 1
    end
end
```

### 3.2 建筑 / 物品 / 配方

#### 3.2.1 配方（AddRecipe2 统一，_dec_13）

```lua
AddRecipe2(
    "daogui_bottle",
    {
        Ingredient("daogui_shard", 4)
    },
    TECH.SCIENCE_ONE,
    {
        atlas = "images/inventoryimages/daogui_bottle.xml",
        image = "daogui_bottle_empty.tex"
    },
    {
        CRAFTING_FILTERS.REFINE.name
    }
)

AddRecipeFilter({
    name = "DAOGUI",
    atlas = "images/inventoryimages/daogui_tab.xml",
    image = "daogui_tab.tex",
})

AddRecipeToFilter("daogui_bottle", "DAOGUI")
```

要点：自定义制作页签（RecipeFilter + AddRecipeToFilter），全部配方归入 DAOGUI 页，不污染原版页签。

#### 3.2.2 数值配置表（_dec_3）

```lua
_G.DAOGUI = {
    BLM = {
        HEALTH = TUNING.DAOGUI_BLM_HEALTH,
        HUNGER = TUNING.DAOGUI_BLM_HUNGER,
        SANITY = TUNING.DAOGUI_BLM_SANITY,
    },
    BACKBONE_SOWRD = {-- 脊骨剑
        DAMAGE = 68,
        USES = 100,
    },
    COPPER_SWORD = {
        DAMAGE = 70,
        USES = 200,
        WEAPONS_SETBONUS_PLANAR_DAMAGE = 20
    },
    CHOMPER = {-- 吃人鬼
        HEALTH = 6000,
        DAMAGE = 50,
        ATTACK_PERIOD = 2.5,
    },
    COLOURFULDEER = {
        HEALTH = 1200,
        DAMAGE = 50,
        SPAWN_TIME = 3 * TUNING.TOTAL_DAY_TIME
    },
    ...
}
```

#### 3.2.3 皮肤/外观系统包装（_dec_4）

```lua
GLOBAL.SpawnPrefab = function(prefab, skin, skinid, userid, ...)
    -- 包装原版 SpawnPrefab，自定义皮肤/用户逻辑
end
local oldCreatePrefabSkin = GLOBAL.CreatePrefabSkin
```

大量 mod 用"包装原版全局函数"的方式扩展皮肤系统（GetSkinInvIconName、GetPortraitNameForItem、GetFrameSymbolForRarity、IsDefaultCharacterSkin）。

#### 3.2.4 批量 prefab 工厂（HERBS_DEFS 模式）

出处：scripts/prefabs/daogui_herbs_defs（解密 _p_4.lua）+ daogui_farm_plants_herbs（_p_3.lua）

```lua
local HERBS_DEFS = {}

HERBS_DEFS.daogui_ginseng = {
    prefab = "farm_plant_daogui_ginseng",
    seed = "daogui_ginseng_seeds",
    product = "daogui_ginseng",
    anim = "idle_full",
    build = "daogui_ginseng",
    bank = "daogui_ginseng",
    scale = 0.8,
    grow_time = {
        3 * TUNING.TOTAL_DAY_TIME,
        9 * TUNING.TOTAL_DAY_TIME
    },
    sounds = {
        grow_seed = "farming/common/farm/grow_oversized",
        grow_small = "farming/common/farm/grow_full",
        grow_large = "farming/common/farm/rot",
    }
}

HERBS_DEFS.daogui_ganoderma = { ... 同上结构 ... }
HERBS_DEFS.daogui_ginseng_npc = {  -- NPC 固定 10 天长成
    grow_time = { 10 * TUNING.TOTAL_DAY_TIME, 10 * TUNING.TOTAL_DAY_TIME },
}
HERBS_DEFS.daogui_ganoderma_npc = { ... }

return HERBS_DEFS
```

### 3.3 恐怖氛围系统

#### 3.3.1 SAN 侵蚀光环（尸花）

出处：prefabs/daogui_corpse_flower（_p_6.lua）

```lua
local function CalcSanityAura(inst, observer)
    return -2
end

local function SetState(inst, state)
    inst._state:set(state)
    inst.AnimState:PushAnimation("idle"..state, true)
end

local function OnCyclesChanged(inst)
    if inst.grow_day < 5 then
        inst.grow_day = math.min(5, inst.grow_day + 1)
        if inst.grow_day >= 5 then
            inst.AnimState:PlayAnimation("flower", false)
            SetState(inst, 2)
        end
    end
end

local function launchitem(item, angle)
    local speed = math.random() * 4 + 2
    angle = (angle + math.random() * 60 - 30) * DEGREES
    item.Physics:SetVel(speed * math.cos(angle), math.random() * 2 + 8, speed * math.sin(angle))
end

local function OnPicked(inst, doer)
    local x, y, z = inst.Transform:GetWorldPosition()
    y = 3
    local angle
    if doer ~= nil and doer:IsValid() then
        angle = 180 - doer:GetAngleToPoint(x, 0, z)
    else
        ...
    end
    local item1 = SpawnPrefab("daogui_human_bone")
    local item2 = SpawnPrefab("daogui_human_meat")
    ...
end
```

氛围设计：尸花种下 5 天开花，持续 -2 SAN/秒；采摘时向玩家方向喷出人骨/人肉（物理抛物线弹射）——恶心+恐怖双管齐下。

#### 3.3.2 场景恐怖元素（地图布局层）

- doomsdoor_area：末日门 + 3 个 daogui_maxwelllight（马克斯韦灯柱，紫色光）围成祭坛，入口处放 daogui_xuanpin、daogui_misaka_sickle 物品（_s_5）
- abyssland（30x30 阿鼻地狱）：daogui_dragoncoffin（龙棺）、daogui_bloodcarpet（血毯）、daogui_mummy、daogui_spiderman、daogui_soulumbrella、daogui_molebat_spawner、daogui_passion；地面 2=焦土迷宫结构，边缘动态长 evergreen_tall/grass/sapling/daogui_demonflower/眼果（makeobj 函数按格子邻接方向生成）（_s_6）
- dangerland：血池（bloodpond @ 5,5）+ 鸡群随机 4~32 格 + 8 只彩色鹿 + 4 尸花 + 3 吃人鬼 + 8 骷髅（_s_4）

#### 3.3.3 血腥特效与音效

- daogui_bloodfx / daogui_bloodwell / daogui_bloodcarpet / daogui_black_tear_soul_fx（黑泪魂 fx）
- 血池 daogui_bloodpond：可交互容器（"血池" 无内容配置注释为 BLOOD_POND 配置项）
- 跑步音效复用 dontstarve/movement/run_dirt 等原版，但地皮 runsound 独立配置

#### 3.3.4 文本氛围（STRINGS 注入）

所有物品/生物都有 NAMES + GENERIC.DESCRIBE 双文本（_dec_2，632 行），运行时二次混淆成密文，显示层解密。例如：

```lua
STRINGS.NAMES.DAOGUI_CHOMPER = "<密文-吃人鬼>"
STRINGS.CHARACTERS.GENERIC.DESCRIBE.DAOGUI_CHOMPER = "<密文-描述>"
STRINGS.NAMES.DAOGUI_CORPSE_TREE = "<密文-尸树>"
STRINGS.NAMES.DAOGUI_CORPSE_TREE_HEAD = "<密文-头>"
STRINGS.NAMES.DAOGUI_CORPSE_TREE_HAND = "<密文-手>"
STRINGS.NAMES.DAOGUI_CORPSE_TREE_FOOT = "<密文-脚>"
STRINGS.NAMES.DAOGUI_CORPSE_TREE_HEART = "<密文-心>"
STRINGS.NAMES.DAOGUI_CORPSE_TREE_BODY = "<密文-躯干>"
```

（注：STRINGS 值为运行时字符级替换的密文，原样展示无意义；模式是"角色名/物品名/描述"三件套齐全，含 RECIPE_DESC、ACTIONFAIL 定制文本。）

### 3.4 叙事 / 事件系统

#### 3.4.1 任务链（世界生成层）

- AddTaskPreInit("Speak to the king") → 把 DaoGui_Doomsdoor_Area 房间塞进原版猪王任务（叙事入口：玩家找猪王触发）
- AddTask("DaoGui_DangerLand") + AddTaskSetPreInit("default") → 无锁必出危险之地任务
- daogui_score 组件（积分）+ daogui_tasktoken（任务令牌）→ 任务进度物
- 青云寺岛屿 retrofit：存档级事件（见专题章节）

#### 3.4.2 NPC 交易（师太 abbess）

出处：scripts/daogui_abbess_items.lua（_p_24.lua，交易表）

```lua
local items =
{
    twigs = {
        need = 5,
        give = 6,
        ...
    },
    ...
}
```

#### 3.4.3 玄牝（xuanpin）系统

scripts/daogui_xuanpin_anims.lua / daogui_xuanpin_scores.lua / daogui_xuanpin_tasks.lua——动画/积分/任务三文件分离，配合 doomsdoor 区域使用（xuanpin 物品出现在 _s_5 布局中）。玄牝为小说核心道具（大门内取物），mod 里做成任务积分制。

#### 3.4.4 角色升级（daogui_lhw_upgrade + 组件）

- daogui_lhw_upgrade / daogui_lhw_upgrade_replica：李火旺专属升级（主/客端复制组件对）
- daogui_age（年龄/寿命系统）+ daogui_age_replica：修仙年龄机制，TUNING.DAOGUI_AGE_MAX = 240
- daogui_transfer_god（神降）：双神附体玩法，TWOGODS.HEALTH = 1000

### 3.5 特色植物与生长机制（核心）

#### 3.5.1 灵草种植（farm_plant 系统复用 + 法术催生）

出处：scripts/prefabs/daogui_farm_plants_herbs（_p_3.lua）

```lua
local function RepeatMagicGrowth(inst)
    inst._magicgrowthtask = nil
    if inst:IsValid() then
        inst.components.growable:DoMagicGrowth()
    end
end

local function domagicgrowthfn(inst)
    if inst._magicgrowthtask ~= nil then
        inst._magicgrowthtask:Cancel()
        inst._magicgrowthtask = nil
    end
    if inst.magic_growth_delay ~= nil then
        inst:AddTag("magicgrowth")
        inst._magicgrowthtask = inst:DoTaskInTime(inst.magic_growth_delay, RepeatMagicGrowth)
        inst.magic_growth_delay = nil
    else
        inst:AddTag("magicgrowth")
        inst._magicgrowthtask = inst:DoTaskInTime(3 + math.random(), RepeatMagicGrowth)
    end
end
```

植物本体构造（挂 growable 关键配置）：

```lua
inst:AddComponent("growable")
inst.components.growable.growoffscreen = true
inst.components.growable.stages = GROWTH_STAGES
inst.components.growable:SetStage(1)
inst.components.growable.domagicgrowthfn = domagicgrowthfn
inst.components.growable.magicgrowable = true
inst.components.growable:StartGrowing()
inst.components.growable:Pause()
```

黑暗暂停生长（夜间无光则不生长）：

```lua
local CANGROW_TAGS = { "daylight", "lightsource" }
local function IsTooDarkToGrow(inst)
    if TheWorld.state.isnight and not inst.components.growable:GetCurrentStageData().night_grow then
        local x, y, z = inst.Transform:GetWorldPosition()
        for i, v in ipairs(TheSim:FindEntities(x, 0, z, TUNING.DAYLIGHT_SEARCH_RANGE, CANGROW_TAGS)) do
            local lightrad = v.Light:GetCalculatedRadius() * .7
            if v:GetDistanceSqToPoint(x, y, z) < lightrad * lightrad then
                return false
            end
        end
        return true
    end
    return false
end

local function UpdateGrowing(inst)
    if inst.components.growable ~= nil and (inst.components.burnable == nil or not inst.components.burnable:IsBurning()) and not IsTooDarkToGrow(inst) then
        inst.components.growable:Resume()
    else
        inst.components.growable:Pause()
    end
end

local function OnIsDark(inst)
    UpdateGrowing(inst)
    if TheWorld.state.isnight then
        if inst.nighttask == nil then
            inst.nighttask = inst:DoPeriodicTask(5, UpdateGrowing, math.random() * 5)
        end
    else
        if inst.nighttask ~= nil then
            inst.nighttask:Cancel()
            inst.nighttask = nil
        end
    end
end

inst:WatchWorldState("isnight", OnIsDark)
inst:DoTaskInTime(0, OnIsDark)
```

防守机制（被摘时呼叫植物守卫）：

```lua
local function call_for_reinforcements(inst, target)
    if target ~= nil and not target:HasTag("plantkin") then
        local x, y, z = inst.Transform:GetWorldPosition()
        local defenders = TheSim:FindEntities(x, y, z, TUNING.FARM_PLANT_DEFENDER_SEARCH_DIST, {"farm_plant_defender"})
        for _, defender in ipairs(defenders) do
            if defender.components.burnable == nil or not defender.components.burnable.burning then
                defender:PushEvent("defend_farm_plant", {source = inst, target = target})
                break
            end
        end
    end
end
```

#### 3.5.2 妖植再生长（RegrowthManager 组件）

出处：scripts/components/daogui_regrowthmanager.lua（_p_19.lua）

机制：全 mod 单实例组件挂在 TheWorld 上，监听 beginregrowth 事件，用链表计时器管理重生；重生时在原位置 20 格半径内抖动、检查地皮类型/可否种植/是否道路/实体密度/玩家距离。

```lua
local UPDATE_PERIOD = 29 -- 与其他系统错帧
local BASE_RADIUS = 20
local EXCLUDE_RADIUS = 3
local JITTER_RADIUS = 20
local MIN_PLAYER_DISTANCE = 64 * 1.2
local RETRY_MULT = 0.25

local REGROWBLOCKER_ONEOF_TAGS = { "structure", "wall", "regrowth_blocker" }
local function TestForRegrow(x, y, z, orig_tile)
    if _map:GetTileAtPoint(x, y, z) ~= orig_tile or
        not _map:CanPlantAtPoint(x, y, z) or
        (RoadManager ~= nil and RoadManager:IsOnRoad(x, 0, z)) then
        return false
    end
    local ents = TheSim:FindEntities(x, y, z, EXCLUDE_RADIUS)
    if #ents > 0 then return false end
    local ents = TheSim:FindEntities(x, y, z, BASE_RADIUS, nil, nil, REGROWBLOCKER_ONEOF_TAGS)
    if #ents > 0 then return false end
    return true
end

local function DoRegrowth(key, product, position)
    local x, y, z = position:Get()
    local orig_tile = _map:GetTileAtPoint(x, y, z)
    local theta = math.random() * 2 * PI
    local radius = math.random() * JITTER_RADIUS
    local x = x + radius * math.cos(theta)
    local z = z - radius * math.sin(theta)
    if not IsAnyPlayerInRange(x, y, z, MIN_PLAYER_DISTANCE, nil) then
        if TestForRegrow(x, y, z, orig_tile) then
            local instance = SpawnPrefab(product)
            if instance ~= nil then
                instance.Transform:SetPosition(x, y, z)
            end
            return REGROW_STATUS.SUCCESS
        else
            return REGROW_STATUS.FAILED
        end
    else
        return REGROW_STATUS.CACHE
    end
end
```

注册规则（吃人鬼采摘眼果/魔花后触发重生，3 天周期）：

```lua
self:SetRegrowthForType("daogui_eyefruit_planted", TUNING.TOTAL_DAY_TIME * 3, "daogui_eyefruit_planted", function()
    return 1
end)

self:SetRegrowthForType("daogui_demonflower", TUNING.TOTAL_DAY_TIME * 3, "daogui_demonflower", function()
    return 1
end)
```

支持 OnSave/OnLoad（剩余时间序列化），LongUpdate 按 `dt * TUNING.REGROWTH_TIME_MULTIPLIER * prefabtimemult` 累计。

#### 3.5.3 麦田再生（ForestResourceSpawner 组件）

出处：scripts/components/daogui_forestresourcespawner.lua（_p_22.lua）

机制：危险之地房间内的麦子可再生。spawnpoint 注册制（实体带"renewable" tag 被找附近麦子补种），仅限 `daogui_dangerland` 节点 tag 内。

```lua
local RENEWABLES =
{
    {
        spawns = { "daogui_wheat" },
        matches = { "daogui_wheat", "daogui_wheat" },
    },
}

local function DoPrefabRenew(x, z, ents, renewable_set, max)
    for i, v in ipairs(ents) do
        if renewable_set.matches[v.prefab] then
            return
        end
    end
    if #renewable_set.spawns > 0 then
        for i = math.random(max), 1, -1 do
            local theta = math.random() * 2 * PI
            local radius = math.random() * RENEW_RADIUS
            local x1 = x + radius * math.cos(theta)
            local z1 = z - radius * math.sin(theta)
            if inst.Map:CanPlantAtPoint(x1, 0, z1) and
                not (RoadManager ~= nil and RoadManager:IsOnRoad(x1, 0, z1)) then
                local prefab = renewable_set.spawns[math.random(#renewable_set.spawns)]
                if inst.Map:CanPlacePrefabFilteredAtPoint(x1, 0, z1) and inst.Map:NodeAtPointHasTag(x1, 0, z1, "daogui_dangerland") then
                    SpawnPrefab(prefab).Transform:SetPosition(x1, 0, z1)
                end
            end
        end
    end
end
```

再生周期：`TUNING.SEG_TIME + math.random() * TUNING.SEG_TIME`；用 `easing.inQuint` 选 spawnpoint（越靠前概率越大）。事件 `ms_registerspawnpoint` / `ms_enableresourcerenewal`。

#### 3.5.4 特殊植物行为

- 眼果（daogui_eyefruit）：pickable SetUp("daogui_eyefruit", 10)，quickpick + remove_when_picked；有 planted / 物品两种形态（_p_5）
- 魔花（daogui_demonflower）：摘取掉 petals（花瓣），halloweenmoonmutable 可变月圆突变（_p_7）
- 尸花（daogui_corpse_flower）：-2 SAN 光环 + 5 天开花 + 喷人骨/人肉（_p_6）
- 翠榴石树（daogui_dioptase）：3 阶段 growable 树（twigs→log→log+log→log x3 + daogui_byg_seed），烧毁→灰烬，砍倒→树桩，lootsetfn 按 size/burnt 状态给掉落（_p_16）
- 尖刺灌木（daogui_sharp_berrybush）：BERRY_TYPES = { "berries", "berriesmore", "berriesmost" } 三档果子（_p_9）；尖刺莓（daogui_sharp_berries）edible 微量恢复 + PERISH_FAST（_p_10）
- 青提（daogui_qingtitree）：青提果实，PERISH_SUPERSLOW（_p_12）

---

## 第 4 章 亮点技术（5 个技巧）

### 技巧 1：Tiled 静态布局 + 代码动态撒点（GetRandomItem + removearrayvalue）

出处：scripts/map/static_layouts/daogui_qingfengtemplearea.lua（_s_9.lua）

Tiled 编辑器的 24x24 网格（1=OCEAN_ROUGH 海、2=岛、3=核心区）存为 BG_TILES data，然后**用代码在返回前往 FG_OBJECTS 里动态插入对象**，插入位置从"内部合法格子"池子里不重复抽取：

```lua
local poses = {}
for k, v in ipairs(data) do
    if v == 2 then
        local insert = true
        if data[k - 1] == 1 or data[k + 1] == 1 or data[k - 24] == 1 or data[k + 24] == 1 then
            insert = false
        end
        if data[k - 1] == 3 or data[k + 1] == 3 or data[k - 24] == 3 or data[k + 24] == 3 then
            insert = false
        end
        if insert then
            local x = k % 24
            local y, _ = math.modf(k / 24)
            if x ~= 7 and y ~= 15 then
                table.insert(poses, { x = x, y = y })
            end
        end
    end
end
...
for i = 1, 6 do
    local pos = GetRandomItem(poses)
    table.insert(layer.layers[2].objects, {
        name = "", type = "tree_area",
        shape = "rectangle",
        x = (pos.x - 1) * 64 + 32,
        y = (pos.y - 1) * 64 + 32,
        width = 32, height = 32,
        visible = true, properties = {}
    })
    table.removearrayvalue(poses, pos)
end
```

好处：布局文件同时给 Tiled 编辑器和游戏用；每次开局撒点随机，岛屿不完全一样。area 对象（tree_area/grass_area/rocks_area）还能被 StaticLayout.Get 的 `areas` 参数接管（见技巧 3），实现**布局内区域与 prefab 池解耦**。

### 技巧 2：存档级岛屿注入（DoRetrofitting 包装 + 拓扑手写）

出处：modworldgenmain.lua（_wgen_1.lua）+ scripts/map/daogui_qingfengtemple.lua（_s_3.lua）

旧存档没有新岛屿。mod 包装 `retrofiting.DoRetrofitting`，检查存档里没有 `daogui_qingfengtemple_center` 时手动往世界刷一座岛：找纯 rough ocean 区域、清掉阻塞实体（船/皇冠鸟/格罗姆花/钥匙等）、Place 布局、**手工构造 topology 节点**（AddSquareTopolopy：ids/nodes/neighbours/poly 全手写）。这是"老存档无缝加入新岛屿"的标准答案，比 AddLevelPreInitAny 的 prefill 更稳（prefill 只对新档生效）。

### 技巧 3：StaticLayout.Get 的 areas 参数（区域→生物群系绑定）

出处：modworldgenmain.lua（_wgen_1.lua）

```lua
Layouts["DaoGuiQingFengTempleArea"] = StaticLayout.Get("map/static_layouts/daogui_qingfengtemplearea",
{
    start_mask = GLOBAL.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    fill_mask = GLOBAL.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    layout_position = GLOBAL.LAYOUT_POSITION.CENTER,
    disable_transform = true,
    add_topology =
    {
        room_id = "StaticLayoutIsland:DaoGuiQingFengTempleArea",
        tags = { "RoadPoison", "nohunt", "nohasslers", "not_mainland", "DaoGuiQingFengTempleArea" },
    },
    areas =
    {
        tree_area = function()
            return PickSomeWithDups(1, { "daogui_red_webtree" })
        end,
        grass_area = function ()
            return PickSomeWithDups(1, { "grass", "sapling", "daogui_eyefruit_planted" })
        end,
        rocks_area = function ()
            return {"daogui_dioptase"}
        end
    },
})

Layouts["DaoGuiQingFengTempleArea"].ground_types =
{
    WORLD_TILES.OCEAN_ROUGH,
    WORLD_TILES.DAOGUI_QINGFENGTEMPLE,
    WORLD_TILES.FARMING_SOIL,
}
```

- `disable_transform = true`：岛不参与地形变换
- `add_topology`：手工声明房间拓扑（island 房间 id + 自定义 tag）
- `areas`：函数返回 prefab 池 → 布局内的 tree_area/grass_area/rocks_area 方块自动变成红蛛树/草+树苗+眼果/翠榴石
- ground_types 覆盖布局的地皮混合——岛屿专属地皮在这里生效

### 技巧 4：原版系统"模板复制"扩展（AddMoreVeggie / AddMorePlant / 批量 Prefab 工厂）

不修改原版 farm_plant_defs，而是以原版表为模板动态复制新条目；不手写 N 个 prefab 文件，而是用 def 表 + 工厂函数批量生成（HERBS_DEFS 4 个条目 → 4 个 prefab）。npc 变体只是 grow_time 固定 10 天——同一个工厂，不同配置。这是**数据驱动 prefab** 的典型：加一种灵草 = 加一行表。

### 技巧 5：反调试 + 全链路加密（安全壳参考）

- 入口明文 wrapper 内联 LOL! hex + 自定义 VM（opcode 100+，解释器内联，防静态 dump）
- `debug.getinfo(loadstring,'S').source == '=[C]'` 反调试：非 C 实现 loadstring 直接失败
- scripts 用位置相关流密码 + RLE marker（0x02/0x03/0x19/0x1b），非纯 ASCII 字节扩展
- 字符串运行时字符级二次混淆（中文全密文化）
- 弱点（供参考）：VM 必须在内存里解密出明文再 loadstring，hook loadstring / 复制环境即可捕获源码，无需破解算法。

---

## 第 5 章 可复用模板代码

### 5.1 自定义地皮 + 岛屿（组合拳）

```lua
-- turf_defs.lua
local turfs = {
    {
        tile_name = "YOUR_TILE",
        tile_range = "LAND",
        tile_data = { ground_name = "your_tile" },
        ground_tile_def = {
            name = "grass",
            noise_texture = "your_tile.tex",
            runsound = "dontstarve/movement/run_dirt",
            walksound = "dontstarve/movement/run_dirt",
            snowsound = "dontstarve/movement/run_ice",
            mudsound = "dontstarve/movement/run_mud",
        },
        minimap_tile_def = {
            name = "map_edge",
            noise_texture = "mini_your_tile.tex",
        },
    },
}
return turfs

-- modworldgenmain.lua
local defs = require "your_turf_defs"
for k, data in pairs(defs) do
    AddTile(data.tile_name, data.tile_range, data.tile_data, data.ground_tile_def, data.minimap_tile_def, data.turf_def)
end
ChangeTileRenderOrder(WORLD_TILES.YOUR_TILE, WORLD_TILES.MOSAIC_GREY)
ChangeMiniMapTileRenderOrder(WORLD_TILES.YOUR_TILE, WORLD_TILES.MOSAIC_GREY)

Layouts["YourIsland"] = StaticLayout.Get("map/static_layouts/your_island", {
    start_mask = GLOBAL.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    fill_mask = GLOBAL.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    layout_position = GLOBAL.LAYOUT_POSITION.CENTER,
    disable_transform = true,
    add_topology = {
        room_id = "StaticLayoutIsland:YourIsland",
        tags = { "not_mainland", "YourIsland" },
    },
    areas = {
        tree_area = function() return PickSomeWithDups(1, { "your_tree" }) end,
        rocks_area = function() return { "your_rock" } end,
    },
})
Layouts["YourIsland"].ground_types = {
    WORLD_TILES.OCEAN_ROUGH, WORLD_TILES.YOUR_TILE,
}

AddLevelPreInitAny(function(level)
    if level.location == "forest" and level.ocean_prefill_setpieces ~= nil then
        level.ocean_prefill_setpieces["YourIsland"] = 1
    end
end)
```

### 5.2 旧存档岛屿 retrofit 模板（TurnOfTidesRetrofitting 简化版）

```lua
-- modworldgenmain.lua
local retrofiting = require("map/retrofit_savedata")
local old_DoRetrofitting = retrofiting.DoRetrofitting
retrofiting.DoRetrofitting = function(savedata, world_map, ...)
    old_DoRetrofitting(savedata, world_map, ...)
    local entities = savedata.ents
    local isnotinmap = true
    for prefab, ents in pairs(entities) do
        if prefab == "your_island_center" then
            isnotinmap = false
            break
        end
    end
    if isnotinmap then
        require("map/your_retrofit").TurnOfTidesRetrofitting(TheWorld.Map, savedata)
        savedata.map.tiles = world_map:GetStringEncode()
        savedata.map.nodeidtilemap = world_map:GetNodeIdTileMapStringEncode()
    end
end

-- map/your_retrofit.lua
local function is_rough_ocean(map, left, top, size)
    for x = 0, size do
        for y = 0, size do
            if map:GetTile(left + x, top + y) ~= GROUND.OCEAN_ROUGH then
                return false
            end
        end
    end
    return true
end

local function AddSquareTopolopy(topology, left, top, size, room_id, tags)
    local index = #topology.ids + 1
    topology.ids[index] = room_id
    topology.story_depths[index] = 0
    local node = {}
    node.area = size * size
    node.c = 1
    node.cent = {left + (size / 2), top + (size / 2)}
    node.neighbours = {}
    node.poly = { {left, top}, {left + size, top}, {left + size, top + size}, {left, top + size} }
    node.tags = tags
    node.type = NODE_TYPE.Default
    node.x, node.y = node.cent[1], node.cent[2]
    node.validedges = {}
    topology.nodes[index] = node
end

local function TurnOfTidesRetrofitting(map, savedata)
    local obj_layout = require("map/object_layout")
    local topology = savedata.map.topology
    local map_width, map_height = savedata.map.width, savedata.map.height
    local entities = savedata.ents
    local add_fn = { fn=function(prefab, points_x, points_y, current_pos_idx, entitiesOut, width, height, prefab_list, prefab_data, rand_offset)
        local x = (points_x[current_pos_idx] - width/2.0)*TILE_SCALE
        local y = (points_y[current_pos_idx] - height/2.0)*TILE_SCALE
        x, y = math.floor(x*100)/100.0, math.floor(y*100)/100.0
        entitiesOut[prefab] = entitiesOut[prefab] or {}
        local save_data = {x=x, z=y}
        if prefab_data then
            if prefab_data.data then
                if type(prefab_data.data) == "function" then
                    save_data["data"] = prefab_data.data()
                else
                    save_data["data"] = prefab_data.data
                end
            end
            if prefab_data.id then save_data["id"] = prefab_data.id end
            if prefab_data.scenario then save_data["scenario"] = prefab_data.scenario end
        end
        table.insert(entitiesOut[prefab], save_data)
    end, args={entitiesOut=entities, width=map_width, height=map_height, rand_offset = false, debug_prefab_list=nil} }

    local layout = obj_layout.LayoutForDefinition("YourIsland")
    local tile_size = #layout.ground
    local candidates = {}
    local num_steps = math.floor((map_width - tile_size) / tile_size)
    for x = 0, num_steps do
        for y = 0, num_steps do
            local left = 8 + (x > 0 and ((x * math.floor(map_width / num_steps)) - tile_size - 16) or 0)
            local top  = 8 + (y > 0 and ((y * math.floor(map_height / num_steps)) - tile_size - 16) or 0)
            if is_rough_ocean(map, left, top, tile_size) then
                table.insert(candidates, {top = top, left = left})
            end
        end
    end
    if #candidates > 0 then
        shuffleArray(candidates)
        local c = candidates[1]
        local world_top  = (c.left - 0)*4 - (map_width * 0.5 * 4)
        local world_left = (c.top - 0)*4 - (map_height * 0.5 * 4)
        obj_layout.Place({c.left, c.top}, "YourIsland", add_fn, nil, map)
        if layout.add_topology ~= nil then
            AddSquareTopolopy(topology, world_top, world_left, (tile_size + 2)*4, layout.add_topology.room_id, layout.add_topology.tags)
        end
        return true
    end
    return false
end
return { TurnOfTidesRetrofitting = TurnOfTidesRetrofitting }
```

### 5.3 可再生妖植组件模板（RegrowthManager 单例）

```lua
-- components/your_regrowthmanager.lua
return Class(function(self, inst)
    assert(TheWorld.ismastersim, "RegrowthManager should not exist on client")
    local UPDATE_PERIOD = 29
    local BASE_RADIUS = 20
    local EXCLUDE_RADIUS = 3
    local JITTER_RADIUS = 20
    local MIN_PLAYER_DISTANCE = 64 * 1.2

    local _internaltimes = {}
    local _regrowthvalues = {}
    local _lists = {}

    local function AppendTimer(key, timer)
        if _lists[key] == nil then _lists[key] = LinkedList() end
        _lists[key]:Append(timer)
    end

    local REGROWBLOCKER_ONEOF_TAGS = { "structure", "wall", "regrowth_blocker" }
    local function TestForRegrow(x, y, z, orig_tile)
        if TheWorld.Map:GetTileAtPoint(x, y, z) ~= orig_tile or
            not TheWorld.Map:CanPlantAtPoint(x, y, z) or
            (RoadManager ~= nil and RoadManager:IsOnRoad(x, 0, z)) then
            return false
        end
        if #TheSim:FindEntities(x, y, z, EXCLUDE_RADIUS) > 0 then return false end
        if #TheSim:FindEntities(x, y, z, BASE_RADIUS, nil, nil, REGROWBLOCKER_ONEOF_TAGS) > 0 then return false end
        return true
    end

    local function DoRegrowth(key, product, position)
        local x, y, z = position:Get()
        local orig_tile = TheWorld.Map:GetTileAtPoint(x, y, z)
        local theta = math.random() * 2 * PI
        local radius = math.random() * JITTER_RADIUS
        x = x + radius * math.cos(theta)
        z = z - radius * math.sin(theta)
        if not IsAnyPlayerInRange(x, y, z, MIN_PLAYER_DISTANCE, nil) then
            if TestForRegrow(x, y, z, orig_tile) then
                local instance = SpawnPrefab(product)
                if instance ~= nil then instance.Transform:SetPosition(x, y, z) end
                return 0 -- SUCCESS
            else
                return 1 -- FAILED
            end
        end
        return 2 -- CACHE
    end

    local timer_i = 0
    local function OnBeginRegrowth(src, target)
        if _regrowthvalues[target.prefab] == nil then return end
        local timer = {
            product = _regrowthvalues[target.prefab].product,
            regrowtime = _internaltimes[target.prefab] + _regrowthvalues[target.prefab].regrowtime,
            position = target:GetPosition(),
            i = timer_i,
        }
        timer_i = timer_i + 1
        AppendTimer(target.prefab, timer)
    end

    function self:SetRegrowthForType(prefab, regrowtime, product, timemult)
        _regrowthvalues[prefab] = { regrowtime = regrowtime, product = product, timemult = timemult }
        _internaltimes[prefab] = 0
    end

    inst:ListenForEvent("beginregrowth", OnBeginRegrowth, TheWorld)
    inst:DoPeriodicTask(UPDATE_PERIOD, function() self:LongUpdate(UPDATE_PERIOD) end)

    -- 用法：self:SetRegrowthForType("your_plant", TUNING.TOTAL_DAY_TIME * 3, "your_plant", function() return 1 end)

    function self:LongUpdate(dt)
        for k, list in pairs(_lists) do
            local prefabtimemult = _regrowthvalues[k].timemult()
            if prefabtimemult > 0 then
                _internaltimes[k] = _internaltimes[k] + dt * TUNING.REGROWTH_TIME_MULTIPLIER * prefabtimemult
                local timer = list:Head()
                while timer ~= nil do
                    if timer.regrowtime > _internaltimes[k] then break end
                    local success = DoRegrowth(k, timer.product, timer.position)
                    if success == 0 then
                        list:RemoveCurrent()
                    elseif success == 2 then
                        -- retry next update
                    else
                        list:RemoveCurrent()
                        timer.regrowtime = _internaltimes[k] + _regrowthvalues[k].regrowtime
                        list:Append(timer)
                    end
                    timer = list:Next()
                    if timer == list:Head() then break end
                end
            end
        end
    end

    function self:OnSave()
        local timers = {}
        for k, list in pairs(_lists) do
            timers[k] = {}
            local it = list:Iterator()
            local timer = it:Next()
            while timer ~= nil do
                table.insert(timers[k], {
                    product = timer.product,
                    regrowtime = timer.regrowtime - _internaltimes[k],
                    position = { x = timer.position.x, z = timer.position.z },
                })
                timer = it:Next()
            end
        end
        return { timers = timers }
    end

    function self:OnLoad(data)
        for k, group in pairs(data.timers) do
            for i, timerdata in ipairs(group) do
                if _internaltimes[k] ~= nil then
                    AppendTimer(k, {
                        product = timerdata.product,
                        regrowtime = _internaltimes[k] + timerdata.regrowtime,
                        position = Point(timerdata.position.x or 0, 0, timerdata.position.z or 0),
                        i = timer_i,
                    })
                    timer_i = timer_i + 1
                end
            end
        end
    end
end)
```

### 5.4 灵草批量 prefab 工厂模板

```lua
-- prefabs/your_herbs_defs.lua
local HERBS_DEFS = {}
HERBS_DEFS.your_ginseng = {
    prefab = "farm_plant_your_ginseng",
    seed = "your_ginseng_seeds",
    product = "your_ginseng",
    anim = "idle_full",
    build = "your_ginseng",
    bank = "your_ginseng",
    scale = 0.8,
    grow_time = { 3 * TUNING.TOTAL_DAY_TIME, 9 * TUNING.TOTAL_DAY_TIME },
    sounds = {
        grow_seed = "farming/common/farm/grow_oversized",
        grow_small = "farming/common/farm/grow_full",
        grow_large = "farming/common/farm/rot",
    }
}
return HERBS_DEFS

-- prefabs/your_farm_plants.lua（工厂）
local plant_defs = require "prefabs/your_herbs_defs"
local plant_prefabs = {}
for name, plant_def in pairs(plant_defs) do
    local function fn()
        local inst = CreateEntity()
        -- ... 通用 farm_plant 构造（AnimState/plant_def/growable/workable/燃烧/存取）...
        inst:AddComponent("growable")
        inst.components.growable.growoffscreen = true
        inst.components.growable.stages = GROWTH_STAGES
        inst.components.growable:SetStage(1)
        inst.components.growable.domagicgrowthfn = domagicgrowthfn
        inst.components.growable.magicgrowable = true
        inst.components.growable:StartGrowing()
        inst.components.growable:Pause()
        inst:WatchWorldState("isnight", OnIsDark)
        return inst
    end
    table.insert(plant_prefabs, Prefab(plant_def.prefab, fn, assets))
end
return unpack(plant_prefabs)
```

### 5.5 自定义房间 tag 注入模板

```lua
-- modworldgenmain.lua
local pule = "map/maptags"
require(pule)
local __MakeTags = _G.package.loaded[pule]
_G.package.loaded[pule] = function()
    local tb = __MakeTags()
    tb.Tag["your_zone"] = function(tagdata) return "TAG", "your_zone" end
    return tb
end

AddGlobalClassPostConstruct("map/storygen", "Story", function(self)
    self.map_tags.Tag["your_zone"] = function(tagdata) return "TAG", "your_zone" end
end)
```

---

## 特色岛屿 / 植物 / 地形专题（任务补充）

### 一、特色岛屿：青云寺（DaoGuiQingFengTempleArea）

#### 1. 岛屿布局（static_layouts/daogui_qingfengtemplearea.lua，_s_9.lua）

24x24 Tiled 网格：**1 = OCEAN_ROUGH（海）、2 = 岛地、3 = 内部 3x3 核心区**（山门/庙址）。

固定物件（FG_OBJECTS 静态段，坐标 = 格子*64+32）：

| 格子 | 物件 | 说明 |
|---|---|---|
| (11,11) | daogui_qingfengtemple_center | 岛屿锚点（retrofit 检查的就是它） |
| (16,7) | daogui_abbess | 师太 NPC |
| (8,16) | daogui_bronzepot_npc | 铜锅 NPC |
| (6,14) | daogui_qingfengtemple | 青云寺主体建筑 |
| (5,13) | daogui_octopus | 章鱼（海产 NPC） |
| (9~11, 3~5) | farm_plant_daogui_ginseng_npc x9 | 人参田（3x3） |
| (15~17, 16~18) | farm_plant_daogui_ganoderma_npc x9 | 灵芝田（3x3） |

动态撒点（代码段，从 poses 池不重复抽取）：6 x tree_area（→红蛛树）、2 x daogui_corpse_flower（尸花）、18 x grass_area（→草/树苗/眼果）、18 x rocks_area（→翠榴石）。

#### 2. 岛屿世界生成接线

- `AddLevelPreInitAny`：`level.ocean_prefill_setpieces["DaoGuiQingFengTempleArea"] = 1`（新档海上直接生成）
- retrofit hook：`TurnOfTidesRetrofitting(TheWorld.Map, savedata)`（老档补岛，详见第 5.2 模板）
- 拓扑 tag：`RoadPoison / nohunt / nohasslers / not_mainland / DaoGuiQingFengTempleArea`
- 专属地皮：全岛地面 = DAOGUI_QINGFENGTEMPLE tile，核心区 + FARMING_SOIL（可种田）

#### 3. 岛屿专属地皮（scripts/daogui_turf_defs.lua）

- **DAOGUI_QINGFENGTEMPLE**：noise_texture = daogui_qingfengtemple.tex（512x512），小地图 mini_daogui_qingfengtemple.tex（256x256），跑动音 run_dirt，无 turf_def（不可挖皮）
- **DAOGUI_RAIN_FOREST**（雨林，用于阿鼻地狱岛）：noise_texture = Ground_noise_rainforest.tex，turf_def 注释掉（不可挖皮）

两 tile 都渲染序挂在 MOSAIC_GREY / FOREST 后面（ChangeTileRenderOrder），保证接缝不闪。

### 二、特色地形：危险之地（DaoGui_DangerLand）与阿鼻地狱（DaoGui_AbyssLand）

#### 1. 危险之地（static_layouts/daogui_dangerland.lua，_s_4.lua）

9x9 布局，中央 5x5 是 FOREST 地皮（BG_TILES 值 7）。固定物件：
- 血池 daogui_bloodpond @ (5,5)
- daogui_batherd x3（鸡群，坐标 math.random(4,32) 动态）
- daogui_colourfuldeer x8（彩色鹿群）+ daogui_colourfuldeerherd
- daogui_corpse_flower x4（尸花）
- daogui_chomper x3（吃人鬼）
- skeleton x8（满地白骨——叙事：这里死过很多人）
- daogui_mystic_tree（神秘树）在任务级 distribute 里 0.1~0.2 权重

房间级：DaoGui_DangerLand（hub）+ DaoGui_DangerLand_Empty（入口）双房间任务链，LOCKS.NONE 必出，distributepercent 0.3。

#### 2. 阿鼻地狱（static_layouts/daogui_abyssland.lua，_s_6.lua）

30x30 地狱岛。结构：2=焦土地面迷宫（环状通道），1=不可通行/DAOGUI_RAIN_FOREST 地皮（Layouts["DaoGui_AbyssLand"].ground_types = {WORLD_TILES.IMPASSABLE, WORLD_TILES.DAOGUI_RAIN_FOREST}）。
固定物件：daogui_doomsdoor @ (15,29) + 3 个 daogui_maxwelllight（紫色祭坛光）、daogui_dragoncoffin（龙棺）、daogui_bloodcarpet（血毯）、daogui_mummy、daogui_spiderman、daogui_soulumbrella、daogui_molebat_spawner、daogui_passion（passion 花沿通道撒）。
边缘格子按邻接方向长植被：`makeobj` 沿通道边缘 50% 概率生成 evergreen_tall/grass/sapling/daogui_demonflower，5% 概率升级为眼果——**迷宫通道两侧自动长恐怖植物的算法**。

#### 3. 末日门祭坛（static_layouts/daogui_doomsdoor_area.lua，_s_5.lua）

16x16 极小布局：daogui_doomsdoor（末日门）+ daogui_xuanpin（玄牝）+ daogui_misaka_sickle（美坂镰刀）。房间 tags：ExitPiece / Chester_Eyebone / Astral_2，required_prefabs = {"daogui_doomsdoor"}，通过 AddTaskPreInit("Speak to the king") 塞进猪王任务。

### 三、特色植物清单（含生长机制）

| 植物 | prefab | 机制 |
|---|---|---|
| 人参 | farm_plant_daogui_ginseng(_npc) | grow_time 3~9 天（npc 版固定 10 天），魔法催生 |
| 灵芝 | farm_plant_daogui_ganoderma(_npc) | 同上，灵芝田 3x3 |
| 眼果 | daogui_eyefruit / daogui_eyefruit_planted | pickable(10) quickpick；采摘后 3 天由 RegrowthManager 在 20 格半径重生；grass_area 里与草/树苗混生 |
| 魔花 | daogui_demonflower | 摘得花瓣；月圆可变异（halloweenmoonmutable）；3 天重生；沿阿鼻地狱通道自动长 |
| 尸花 | daogui_corpse_flower | 5 天开花（grow_day 机制），-2 SAN/秒光环，采摘喷人骨/人肉 |
| 道诡麦 | daogui_wheat / daogui_cutwheat | 危险之地特产；ForestResourceSpawner 按 SEG_TIME 周期在 daogui_dangerland 节点 tag 内补种 |
| 尖刺灌木 | daogui_sharp_berrybush / daogui_sharp_berries | BERRY_TYPES 三档浆果，果实 PERISH_FAST |
| 红蛛树 | daogui_red_webtree | 青云寺岛 tree_area 专属树 |
| 青提树 | daogui_qingtitree | 青提果实，PERISH_SUPERSLOW |
| 骷髅树 | daogui_skulltree | 树形态 + 砍伐/燃烧/树桩完整生命周期（lootsetfn 按 size 给掉落） |
| 尸树 | daogui_corpse_tree | 部位收集玩法（头/手/脚/心/躯干 5 部位掉落 + CORPSE_TREE_KIT 组装） |
| 翠榴石 | daogui_dioptase / daogui_dioptase_rock | 3 阶段成长树（twigs→log→logx3+daogui_byg_seed）；rocks_area 专属 |
| 鬼阴树 | daogui_byg / daogui_byg_tall | 危险之地 distribute 0.2 权重；掉落 daogui_byg_seed |
| 神秘树 | daogui_mystic_tree | 危险之地专属树（0.1~0.2 权重） |
| 鬼槐 | daogui_gys_tall | 往原版 Forest 房间后置注入（math.random(1,2) 棵） |

**灵草生长机制总结（mod 独创点）**：
1. 复用 DST 官方 farm_plant 管线（plant_def + growable + farm_plant_defs），以数据表批量生成
2. **法术催生**（domagicgrowthfn）：任何灵草可被法术强制推进生长阶段，3+random() 秒一跳，带 magicgrowth tag 视觉标记
3. **黑暗休眠**：夜间无光源（daylight/lightsource tag 半径检测）growable 暂停，5 秒一查
4. **区域再生长**：妖植（眼果/魔花）不靠原版 regrowth 组件，而是专属 RegrowthManager 单例（位置抖动、密度/道路/基地排斥、存档计时）
5. **麦田补种**：ForestResourceSpawner 只在带 daogui_dangerland tag 的地图节点内补种——把再生限制在自己的专属地形里

### 四、专属地皮使用总结（三处）

1. 青云寺岛：DAOGUI_QINGFENGTEMPLE（全岛）+ FARMING_SOIL（核心区 3x3 种植区）
2. 阿鼻地狱岛：IMPASSABLE + DAOGUI_RAIN_FOREST（焦土迷宫 + 雨林混搭）
3. 两 tile 均不可采集（无 turf_def）——岛屿地皮是"护城河"设计，防止玩家把岛拆走

---

## 附：解密工作记录（供复现）

- 主 harness：drafts/tools/daogui_full.py（modmain 30 chunks → _dec_1~_dec_30.bin）
- worldgen harness：drafts/tools/daogui_worldgen.py（→ _wgen_1.bin，10187B）
- scripts harness：drafts/tools/daogui_scripts.py（8 文件 → _s_1~_s_9.bin）
- plants harness：drafts/tools/daogui_plants.py（24 chunks → _p_1~_p_24.bin）
- 核心手段：VM 执行时 hook loadstring 捕获解密后源码；VM 安装的 require shim 用于按需解密任意 scripts 文件；debug.getinfo spoof 过反调试
