# 「[DST] 棱镜 Legion」源码研读笔记

> 研读对象：Steam Workshop ID 1392778117，作者 ti_Tout（中文模组，中国风题材）
> 版本：7.6.5（modinfo.lua 中 version = "7.6.5"）
> 规模：1433 个文件；其中 .lua 139 个（scripts/ 下 131 个）
> 数据来源：E:\神秘复苏\饥荒大型mod\1392778117\
> 本笔记用途：作为 DST 大型模组开发的技能文档原始材料

---

## 目录

1. [mod全貌](#1-mod全貌)
2. [框架架构](#2-框架架构)
3. [关键设计模式](#3-关键设计模式)
   - 3.1 世界生成（地皮/房间/任务/静态布局）
   - 3.2 物品/武器/装备/建筑 prefab
   - 3.3 自定义科技树与制作栏
   - 3.4 烹饪与料理注册
   - 3.5 自定义容器
   - 3.6 自定义动作（右键菜单系统）
   - 3.7 盾反系统（shieldlegion）
   - 3.8 幻化系统（dressup）
   - 3.9 电池/充能系统（batterylegion）
   - 3.10 生长/转化系统（perennialcrop / genetrans）
   - 3.11 浸泡/浴缸系统（zip_soak）
   - 3.12 皮肤/换肤系统（tools_sk / skinedlegion）
   - 3.13 存档系统（playersaver / worldsaver）
   - 3.14 多语言/汉化组织
   - 3.15 特效 prefab 模式
   - 3.16 BOSS 工厂模式
4. [亮点技术（最有价值的技巧）](#4-亮点技术最有价值的技巧)
5. [可复用的模板代码](#5-可复用的模板代码)

---

## 1. mod全貌

### 1.1 基本信息

- **名字**：[DST] 棱镜 / [DST] Legion
- **作者**：ti_Tout；特别感谢：半夏微暖半夏凉(代码指导)、羽中就是他(客串画佬)、风铃草(特殊功能支持)
- **类型**：内容型大型模组（全客户端强制加载 all_clients_require_mod = true）
- **加载优先级**：priority = -345（较后加载，便于覆盖其他模组）
- **语言**：中英双语，用 `local L = locale ~= "zh" and locale ~= "zhr"` 在 modinfo 内做条件选择；游戏内还有 Language 配置项（english/chinese）
- **API**：api_version = 10（联机版）
- **保护**：modmain.lua 为混淆发布（防抄袭），但 scripts/ 下全部源码未混淆、注释完整——这是刻意的设计：核心逻辑都在 scripts/ 的普通文件中，modmain 只做串联。

### 1.2 目录树（1433 文件）

```
1392778117/
├── modinfo.lua              # 模组信息 + 大量配置项（约70个选项）
├── modmain.lua              # 【混淆】主入口，CONFIGS_LEGION 全局配置在此定义
├── modmain1.lua             # 【二进制加密】旧版备份
├── modmain2.lua             # 【二进制加密】旧版备份
├── modmain30.lua            # 【二进制加密】旧版备份
├── modmain31.lua            # 【二进制加密】旧版备份
├── modworldgenmain.lua      # 【明文】世界生成入口（地皮/房间/任务注册）
├── mod.manifest / modicon.xml / modicon.tex
├── anim/                    # 404 个动画 zip（含 anim/skin/ 169 个皮肤 build）
├── images/                  # 874 个贴图文件（xml+tex 成对）
│   ├── cookbookimages/      # 食谱大图（每个料理一个 xml+tex）
│   ├── foodtags/            # 食材标签图标（玫瑰/百合/兰花/蝙蝠等）
│   ├── inventoryimages/     # 物品栏图标
│   ├── inventoryimages_skin/# 皮肤版物品栏图标（_skin 后缀目录）
│   ├── map_icons/           # 小地图图标
│   ├── station_recast.xml   # 科技站图标（重铸青光）
│   ├── station_siving.xml   # 科技站图标（生命子圭）
│   ├── filter_legion.xml    # 制作栏筛选图标（棱镜里）
│   ├── slot_bearspaw_l.xml  # 容器格子背景
│   └── slot_juice_l.xml
├── levels/                  # 11 个文件
│   ├── textures/            # 自定义地皮噪声贴图（Ground_bog2、mini_bog_noise 等）
│   └── tiles/               # 自定义地皮贴图（swamp.xml/water_medium.xml）
├── readme/tip_dressup.lua   # 幻化机制对外兼容说明文档（写给其他 mod 作者）
├── sound/                   # legion.fev + legion.fsb（Fmod 音频包，吉他等声音）
└── scripts/                 # 131 个 lua（全部明文）
    ├── mod_inventoryprefabs_list.lua  # 物品皮肤注册表
    ├── recipes_legion.lua             # 全部配方（70个 AddRecipe2 + AddDeconstructRecipe）
    ├── techtrees_legion.lua           # 自定义科技树
    ├── preparedfoods_legion.lua       # 烹饪锅料理（1200+行配方表）
    ├── preparedfoods_legion_spiced.lua# 调料料理（自动批量生成）
    ├── prepareditems_legion.lua       # 勋章mod兼容料理
    ├── containers_legion.lua          # 容器 UI 定义
    ├── postinit_legion.lua            # 大型后置修改（2865行）
    ├── datafix_legion.lua             # 资源注册/AddSimPostInit/数据修复（3497行）
    ├── dressup_legion.lua             # 幻化数据表 DRESSUP_DATA_LEGION
    ├── zip_soak_legion.lua            # 浸泡(浴缸)系统
    ├── sgactions_legoin.lua           # 自定义动作系统（4355行）
    ├── tools_legion.lua               # 核心工具库（1731行）
    ├── tools_plant_legion.lua         # 植物工具
    ├── tools_sk_legion.lua            # 皮肤工具（2570行）
    ├── tools_fx_legion.lua            # 特效工具
    ├── hotreload_legion.lua           # 开发热重载工具
    ├── hua_upvaluehelper.lua          # upvalue 修改工具（风铃草）
    ├── fengl_userdatahook.lua         # userdata hook 工具（风铃草，开放级授权）
    ├── languages/
    │   ├── strings_chinese.lua        # 6634行中文文本（全部角色的台词）
    │   ├── strings_english.lua        # 6418行英文文本
    │   └── recipedesc_legion_chinese.lua # 食谱说明
    ├── map/
    │   ├── rooms/forest/rooms_*.lua   # 5个房间定义文件
    │   ├── static_layouts/*.lua       # 13个 Tiled 导出的静态布局
    │   └── tasks/legionland.lua       # 自定义 task（雨硫岛）
    ├── brains/    # 7个生物脑
    ├── components/# 40个组件
    ├── prefabs/   # 41个 prefab 文件
    ├── stategraphs/# 7个 SG
    └── widgets/  # cookbookui_legion / optionlegionscreen / skinlegiondialog
```

### 1.3 特色系统清单（7个章节内容）

| 章节 | 系统 | 核心文件 |
|---|---|---|
| 花香四溢 | 三花丛(蔷薇/蹄莲/兰草)、花之武器(永不凋零)、青枝绿叶(foliageath 修复系统)、活性组织 | plants_legion, euip_hand_legion, items_legion |
| 美味佳肴 | 大量料理、食谱UI优化 | preparedfoods_legion, cookbookui_legion |
| 尘市蜃楼 | 白木(颤栗树)系列建筑、幻化机制(DressUp)、巨食草浸泡、猫线球/靠背熊 | whitewoods, dressup_*, zip_soak |
| 丰饶传说 | 子圭系列：神木岩/神木(生命之树)/转化器/土壤/垄/面具/战甲/羽毛武器、玄鸟BOSS、异种植物、松萝 | siving_base, boss_siving_phoenix, farm_plants, genetrans |
| 电闪雷鸣 | 电气重铸台、电气石电池系统、莱克阿米特BOSS、灵魂契约(沃拓克斯)、犀金甲 | elecourmaline, batterylegion, boss_elecarmet, soulbookowner |
| 祈雨祭 | 月之宝具(月藏/月炆/月轮/月折)四件套+升级、月的地下城、雨竹/雨蝇、巨人之脚、鱼之息 | moonlight_legion, moon_dungeon, raindonate |
| 黯涌 | 盾牌盾反系统、恐怖盾牌改造、艾力冈的剑、鱼人友好 | shield_legion, shieldlegion, postinit |

---

## 2. 框架架构

### 2.1 入口文件分工（重要）

模组作者把 modmain.lua 做了混淆保护，但把全部逻辑放到 scripts/ 明文文件中。从 modworldgenmain.lua 和各个 scripts/ 文件顶部的环境注释（`--环境: modmain`）可以还原 modmain 的组织方式：

```
modmain.lua（混淆）职责推断：
  1. 定义全局配置表 CONFIGS_LEGION（GetModConfigData 收集全部配置项 + ENABLEDMODS 表记录已启用的联动mod）
  2. env 环境注入：把 _G 全局表设为 env 的 metatable（`LEGIONG.setmetatable(env,{__index=function(_,k)return LEGIONG.rawget(LEGIONG,k)end})`）
  3. require 顺序：
     - require("datafix_legion")       # 资源注册(PrefabFiles/Assets) + AddSimPostInit
     - require("techtrees_legion")     # 科技树
     - require("recipes_legion")       # 配方
     - require("preparedfoods_legion") # 料理
     - require("containers_legion")    # 容器
     - require("sgactions_legoin")     # 动作
     - require("postinit_legion")      # 后置修改（客户端+服务器）
     - require("dressup_legion")       # 幻化数据
     - require("mod_inventoryprefabs_list") # 皮肤注册
```

### 2.2 全局配置表 CONFIGS_LEGION

所有配置在 modinfo 定义，modmain 收集后存全局表 CONFIGS_LEGION，各处 `local OPTS = _G.CONFIGS_LEGION` 引用。关键字段（从使用处推断）：

```lua
CONFIGS_LEGION = {
    LANGUAGES = "chinese"|"english",   -- GetModConfigData("Language")
    TECHUNLOCK = "lootdropper"|"prototyper",  -- 重铸科技解锁方式
    DRESSUP = true|false,              -- 幻化机制开关
    SHIELDRECHARGETIME, SHIELDEXCHANGETIME, AGRONRECHARGETIME, AGRONEXCHANGETIME, -- 盾冷却
    MODTERRORSHIELD, BIGGERWWBOX, BETTERCOOKBOOK, AUTOSTACKEDLOOT,
    MOUSEINFO, ...                     -- 各章节数值配置
    ENABLEDMODS = { GENESIS=?, FnMedal=?, ... },  -- 联动mod检测（rawget 全局变量判断）
    DDA_DIRTY = {},                    -- 客户端数据脏标记（SendModRPC 同步）
    DD_UIDRAG = {},                    -- UI拖拽坐标存档
    DRAGABLEUI = false,                -- 拖拽开关（运行时设置）
    SetUIDragable(), SaveClientData(), -- 客户端方法（postinit 中注入）
}
```

### 2.3 全局变量管理约定（贯穿全部文件）

所有大文件统一使用以下模式（每个文件重复声明）：

```lua
local fns = {} --lua的限制，一个域里只能有最多200个局部变量，否则会报错。通过把所有变量都存进一个主变量，来预防这个问题
local pas = {} --专门放各个prefab独特的变量
```

- `fns`：本文件共享的工具函数（也有文件间传递，如 `TOOLS_L = require("tools_legion")` 拿到其他文件的 fns 表）
- `pas`：本文件内部私有变量/回调
- 工具库之间用 `fns.AddTools(tool, tool2)` 互相注入（tools_sk_legion.lua 用延迟注入避免循环 require）

### 2.4 服务器/客户端分层

每个 prefab 构建函数统一用 `SetPristine()` 分界：

```lua
inst.entity:SetPristine()
if not TheWorld.ismastersim then return inst end
-- 以下为服务器专用代码
```

全局修改分环境执行：postinit_legion.lua 用 `local IsServer = TheNet:GetIsServer() or TheNet:IsDedicated()` 和 `if not TheNet:IsDedicated()` 分别处理服务端与客户端 hook。

### 2.5 联动兼容模式

- 配置项里直接提供联动开关（如 SivSolToMedal 兼容「能力勋章」、ENABLEDMODS.GENESIS 兼容「创世纪」）
- 用 `_G.rawget(_G, "TOOMANYITEMS")` / `_G.rawget(_G, "DRESSUP_DATA_LEGION")` 检测其他 mod 是否存在
- AddSimPostInit 内做联动判定（此时所有 mod 已加载完，判定最准确）
- 对官方数据表做"补丁式"修改而非覆盖（如 cooking.ingredients 缺失项补全、TUNING.PROTOTYPER_TREES 补键）

---

## 3. 关键设计模式

### 3.1 世界生成（地皮/房间/任务/静态布局）

**出处：modworldgenmain.lua（173行，全部明文）**

#### 3.1.1 新增混合地皮（NOISE 类型）

```lua
if WORLD_TILES.SPRINGBEACH_L_NOISE == nil then --在创建世界界面，modworldgenmain.lua会被提前加载，所以需要判空，防止日志里一直提醒重复添加tile
    AddTile(
        "SPRINGBEACH_L_NOISE", --地皮key
        "NOISE", --地皮类型 NOISE 代表一种混合地皮，会根据逻辑随机选择地皮
        {}
    )
end
NoiseTileFunctions[WORLD_TILES.SPRINGBEACH_L_NOISE] = function(noise)
    if noise < 0.1 then
		return WORLD_TILES.IMPASSABLE
    elseif noise < 0.4 then
		return WORLD_TILES.DIRT
	end
	return WORLD_TILES.PEBBLEBEACH
end
```

要点：
- `AddTile(name, "NOISE", {})` 注册混合地皮；判空防重复
- `NoiseTileFunctions[WORLD_TILES.xxx]` 按噪声值返回地皮
- 地皮贴图放 `levels/tiles/`（swamp.xml/water_medium.xml 是替换官方沼泽地皮贴图做水景）、噪声贴图放 `levels/textures/`（mini_bog_noise.tex 等，注册方式在官方 mod 教程中是 `AddGround`/`MiniMap` 相关，此处通过 maps 的 texture 列表自动扫描目录）

#### 3.1.2 静态布局（Tiled 场景）

```lua
LAYOUTS["RoseGarden"] = STATICLAYOUT.Get("map/static_layouts/rosegarden")
LAYOUTS["HelperCemetery"] = STATICLAYOUT.Get("map/static_layouts/helpercemetery"..(isChinese and "_zh" or ""), {
    start_mask = _G.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    fill_mask = _G.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    layout_position = _G.LAYOUT_POSITION.CENTER,
    disable_transform = true
})
```

要点：
- 静态布局文件是 Tiled 导出格式（BG_TILES 图层+FG_OBJECTS 对象组，type 字段为 prefab 名，x/y 为像素坐标）
- 中英文版本用 `_zh` 后缀文件（helpercemetery_zh.lua、orchidgrave_zh.lua、spartacussgrave_zh.lua）——汉化墓碑文字的做法
- `LAYOUTS["名字"] = STATICLAYOUT.Get(path, {mask...})` 注册进全局布局表

#### 3.1.3 随机房间 rooms

```lua
AddRoom("RosePatch", {
	colour = {r=.8,g=1,b=.8,a=.50},
	value = WORLD_TILES.DECIDUOUS, --季节性地皮
	contents = {
		countprefabs = {
			rosebush = function () return 2 + math.random(3) end
		},
		distributepercent = 0.2,
		distributeprefabs =	{
            fireflies = 0.1,
			flower = 0.35,
			flower_rose = 0.35,
			deciduoustree = 0.52,
		}
	}
})
```

房间内嵌静态布局用 `countstaticlayouts = { ["MoonDungeon"] = 1 }`（强制静态地形在 room 中心）。

#### 3.1.4 自定义 task（岛屿）

```lua
AddTask("L_RainIsland_Main", {
	locks = {},
	keys_given = {},
	region_id = "island_l_rain",
	level_set_piece_blocker = true,
	room_tags = { "RoadPoison", "nohasslers", "not_mainland" },
    room_choices = {
        ["L_HotSpringPot"] = 1,
		["L_SmallHotSpringPot"] = function() return math.random(1, 2) end,
		["L_SpringBeach"] = 1
    },
    room_bg = WORLD_TILES.MONKEY_GROUND,
    background_room = "Empty_Cove",
	cove_room_name = "Empty_Cove",
	cove_room_chance = 1,
	cove_room_max_edges = 2,
    colour = {r=0.6,g=0.6,b=0.0,a=1}
})
```

#### 3.1.5 把房间/静态布局塞进官方世界

```lua
--房间：AddTaskPreInit 往官方 task 的 room_choices 里加（+1 权重）
AddTaskPreInit("Speak to the king", function(task)
    task.room_choices["RosePatch"] = 1
end)
AddTaskPreInit("Squeltch", function(task) --“雨竹区域”会出现在沼泽
    task.room_choices["MonsteraPatch"] = 1
end)

--静态布局：AddTaskSetPreInit 往 taskset.set_pieces 里加
AddTaskSetPreInit("default", function(taskset)
    local tasks_all = {"Make a pick", ...}
    taskset.set_pieces["RoseGarden"] = { count = 1, tasks = tasks_all }
    table.insert(taskset.tasks, "L_RainIsland_Main") --顺便插入自定义 task
end)
AddTaskSetPreInit("cave_default", function(taskset) --洞穴也注册
    taskset.set_pieces["SpartacussGrave"] = { count = 1, tasks = {"MudLights", ...} }
end)
```

### 3.2 物品/武器/装备/建筑 prefab

**出处：scripts/prefabs/items_legion.lua、euip_hand_legion.lua、siving_base_legion.lua**

#### 3.2.1 资产声明封装

```lua
fns.GetAssets = function(name, other)
    local sets = {
        Asset("ANIM", "anim/"..name..".zip"),
        Asset("ATLAS", "images/inventoryimages/"..name..".xml"),
        Asset("IMAGE", "images/inventoryimages/"..name..".tex"),
        Asset("ATLAS_BUILD", "images/inventoryimages/"..name..".xml", 256)
    }
    if other ~= nil then
        for _, v in pairs(other) do
            table.insert(sets, v)
        end
    end
    return sets
end
```

`ATLAS_BUILD` 第三个参数 256 用于生成小木牌等需要动画格式贴图缓存的用途。`GetAssets2(name, build, other)` 支持动画 build 与物品栏图不同名（如 `fns.GetAssets2("tourmalineshard", "tourmalinecore")` 用核心的动画但自己的图标）。

#### 3.2.2 通用物品（材料）模板

```lua
table.insert(prefs, Prefab("merm_scales", function() ------鱼鳞
    local inst = CreateEntity()
    fns.CommonFn(inst, "merm_scales", nil, "idle", nil)
    fns.SetFloatable(inst, { nil, "med", 0.1, 0.77 })

    inst:AddTag("cattoy")
    inst.pickupsound = "cloth"

    inst.entity:SetPristine()
    if not TheWorld.ismastersim then return inst end

    fns.ServerFn(inst, "merm_scales")
    fns.SetEdible(inst, { hunger = 0, sanity = 0, health = 0, foodtype = FOODTYPE.HORRIBLE })
    fns.SetStackable(inst, nil)
    fns.SetTradable(inst, TUNING.GOLD_VALUES.MEAT * 2, nil)
    MakeHauntableLaunch(inst) --偏潮湿的道具，所以不会着火

    return inst
end, fns.GetAssets("merm_scales"), nil))
```

CommonFn 标准骨架：

```lua
fns.CommonFn = function(inst, bank, build, anim, isloop)
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank(bank)
    inst.AnimState:SetBuild(build or bank)
    inst.AnimState:PlayAnimation(anim or "idle", isloop)
end
fns.ServerFn = function(inst, img)
    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = img
    inst.components.inventoryitem.atlasname = "images/inventoryimages/"..img..".xml"
end
```

组件封装函数命名法（一个函数=一个组件，参数表驱动）：

```lua
fns.SetStackable = function(inst, maxsize)
fns.SetPerishable = function(inst, time, replacement, onperish)
fns.SetFuel = function(inst, value, fueltype)
fns.SetEdible = function(inst, dd)  -- dd = {foodtype, foodtype2, health, hunger, sanity, fn_eat}
fns.SetCookable = function(inst, product)
fns.SetTradable = function(inst, goldvalue, rocktribute) -- 猪王金币 / 蚁狮沙之石
fns.SetDryable = function(inst, driedname, build, time)
fns.SetDeployable = function(inst, ondeploy, mode, spacing)
fns.SetLure = function(inst, dd)  -- 海钓饵
fns.SetWeighable = function(inst, kind) -- 作物秤
fns.SetWaxable = function(inst, onwaxed)
```

工厂批量生成（活性组织，4种共用一份模板）：

```lua
pas.MakeTissue = function(name)
	local myname = "tissue_l_"..name
	table.insert(prefs, Prefab(myname, function()
        local inst = CreateEntity()
        fns.CommonFn(inst, "tissue_l", nil, "idle_"..name, nil)
        ...
        inst.components.inspectable.nameoverride = "TISSUE_L" --用同一个名称键统一描述
        ...
    end, fns.GetAssets2(myname, "tissue_l"), nil))
end
pas.MakeTissue("cactus")
pas.MakeTissue("lureplant")
pas.MakeTissue("berries")
pas.MakeTissue("lightbulb")
```

#### 3.2.3 武器模板（带耐久/修复/可种植）

出处 euip_hand_legion.lua `neverfade`（永不凋零，250耐久，攻击59.5）：

```lua
local function OnFinished_never(inst) -- 耐久归零：破损状态（降攻、换贴图、加broken标签）
    if not inst.isbroken_l then
        inst.isbroken_l = true
        inst.components.weapon:SetDamage(17)
        inst.components.weapon:SetOnAttack(nil)
        UpdateImg_never(inst)
        ...
        inst:AddTag("broken") --这个标签会让名称显示加入“损坏”前缀
        inst:PushEvent("percentusedchange", { percent = 0 }) --界面需要更新百分比
    end
end
local function OnDeploy_never(inst, pt, deployer, rot) --右键种植成花丛
    local tree = SpawnPrefab("neverfadebush")
    if tree ~= nil then
        inst.components.skinedlegion:SetLinkedSkin(tree, "bush", deployer)
        tree.Transform:SetPosition(pt:Get())
        local percent = inst.components.finiteuses:GetPercent()
        inst:Remove()
        tree.components.pickable:OnTransplant()
        if percent > 0 then -- 按耐久比例继承花丛生长度
            tree.components.pickable:LongUpdate(math.min(TUNING.TOTAL_DAY_TIME*2, TUNING.TOTAL_DAY_TIME*3*percent))
        end
        ...
    end
end
```

武器=武器组件+有限耐久+可种植 deployable 三合一；装备时 `SetDeployMode(DEPLOYMODE.NONE)`、卸下恢复 PLANT 模式。

青枝绿叶（foliageath）修复系统——用耐久缺口自动恢复（挂树数据表 + 周期检查）：

```lua
local foliageath_data_never = {
    image = "foliageath_neverfade", atlas = "images/inventoryimages/foliageath_neverfade.xml",
    bank = nil, build = nil, anim = "neverfade", isloop = nil,
    fn_recovercheck = function(inst, tag)
        return inst.components.finiteuses:GetPercent() < 1
    end,
    fn_recover = function(inst, dt, player, tag)
        if not inst.foliageath_data.fn_recovercheck(inst, tag) then return end
        local value = dt * uses_never/(TUNING.TOTAL_DAY_TIME*3)
        if value < 0.001 then return end
        inst.components.finiteuses:Repair(value)
        if inst.isbroken_l and inst.components.finiteuses:GetUses() >= 1 then
            inst.isbroken_l = nil
            inst:RemoveTag("broken")
            inst.components.weapon:SetDamage(atk_never)
            inst.components.weapon:SetOnAttack(OnAttack_never)
            UpdateImg_never(inst)
        end
    end
}
```

#### 3.2.4 建筑（可生长生命树）模板

出处 siving_base_legion.lua `siving_derivant`（子圭神木岩）：

```lua
inst:AddComponent("trader")
inst.components.trader.deleteitemonaccept = false
inst.components.trader.acceptnontradable = true
inst.components.trader:SetAcceptTest(AcceptTest_dt)
inst.components.trader.onaccept = OnAccept_dt
inst.components.trader.onrefuse = OnRefuse_dt

inst:AddComponent("growable")
inst.components.growable.stages = growth_stages_dt
inst.components.growable.magicgrowable = true --能被魔法催熟
inst.components.growable:SetStage(1)
inst.components.growable:StartGrowing()

inst:WatchWorldState("isnight", OnIsDark_dt)  --夜晚事件
inst:ListenForEvent("timerdone", TimerDone_dt)
```

喂食系统数据表（接受不同物品、分"光/生命"两种能量维度累积）：

```lua
local tradableItems_siv = {
    lightbulb = { kind = 1, value_dt = 0.1, value = 1/80, needall = true }, --荧光果【光】
    pomegranate = { kind = 2, value_dt = 0.5, value = 0.08, needall = true }, --石榴【生命】
    ...
}
```

旧版本兼容包装器（SpawnPrefab 后 1 秒内替换成新 prefab 并设置阶段）：

```lua
local function MakeDerivant(name, state)
    table.insert(prefs, Prefab("siving_derivant_"..name, function()
        local inst = CreateEntity()
        inst.entity:AddTransform()
        inst.entity:AddNetwork()
        inst.entity:SetPristine()
        if not TheWorld.ismastersim then return inst end
        inst:DoTaskInTime(1+math.random(), function(inst)
            local tree = SpawnPrefab("siving_derivant")
            if tree ~= nil then
                if state ~= 1 then
                    tree.components.growable:SetStage(state)
                    ...
                end
                tree.Transform:SetPosition(inst.Transform:GetWorldPosition())
            end
            inst:Remove()
        end)
        return inst
    end, nil, nil))
end
MakeDerivant("lvl0", 1) MakeDerivant("lvl1", 2) MakeDerivant("lvl2", 3) MakeDerivant("lvl3", 4)
```

#### 3.2.5 世界唯一容器（云青松）

出处 worldbox_legion.lua，照抄官方 pocketdimensioncontainers 模式：

```lua
local function OnAnyOpenStorage(inst, data)
	if inst.components.container.opencount > 1 then
		inst.Network:SetClassifiedTarget(nil) --多人打开→全员可见
	else
		inst.Network:SetClassifiedTarget(data.doer) --单人→只网络给该玩家
	end
end
local function MakeWorldBox(data)
    table.insert(prefs, Prefab(data.name, function()
        local inst = CreateEntity()
        if TheWorld.ismastersim then
            inst.entity:AddTransform() --按官方说法，有这个才能实行保存机制
        end
        inst.entity:AddNetwork()
        inst.entity:AddServerNonSleepable()
        inst.entity:SetCanSleep(false)
        inst.entity:Hide()
        inst:AddTag("CLASSIFIED")
        inst:AddTag("pocketdimension_container")
        inst:AddTag("irreplaceable")
        inst.entity:SetPristine()
        if not TheWorld.ismastersim then return inst end
        inst.Network:SetClassifiedTarget(inst)
        inst:AddComponent("container")
        inst.components.container:WidgetSetup(data.name)
        inst.components.container.onanyopenfn = OnAnyOpenStorage
        inst.components.container.onanyclosefn = OnAnyCloseStorage
        TheWorld:SetPocketDimensionContainer(data.boxkey, inst)
        ...
    end, data.assets, data.prefabs))
end
```

保鲜（preserver）动态倍率：入鞘/青枝绿叶类物品保鲜率 0（不腐），否则 1。

### 3.3 自定义科技树与制作栏

**出处：scripts/techtrees_legion.lua（全文123行，模板价值极高）**

```lua
--1) 声明新科技名（AVAILABLE_TECH）
local TechTree = require("techtree")
table.insert(TechTree.AVAILABLE_TECH, "ELECOURMALINE")
table.insert(TechTree.AVAILABLE_TECH, "SIVING")

--2) TechTree.Create 返回表里补默认值（防止 nil 报错）
local Create_old = TechTree.Create
TechTree.Create = function(t, ...)
	local newt = Create_old(t, ...)
	newt["ELECOURMALINE"] = newt["ELECOURMALINE"] or 0
	newt["SIVING"] = newt["SIVING"] or 0
	return newt
end

--3) 注册科技站原型（靠近解锁）
AddPrototyperDef("elecourmaline", {
	icon_atlas = "images/station_recast.xml", icon_image = "station_recast.tex",
	is_crafting_station = true,
	action_str = "RECAST", --台词已在语言文件中
	filter_text = STRINGS.UI.CRAFTING_STATION_FILTERS.RECAST
})
AddPrototyperDef("siving_thetree", {
	icon_atlas = "images/station_siving.xml", icon_image = "station_siving.tex",
	is_crafting_station = false, --不是制作台（siving_1/3 由其他方式解锁）
	action_str = "SIVING"
})

--4) 制作栏分类筛选图标
AddRecipeFilter({ name = "RECAST", atlas = "images/station_recast.xml", image = "station_recast.tex", custom_pos = true })
AddRecipeFilter({ name = "SIVING", atlas = "images/station_siving.xml", image = "station_siving.tex" })
AddRecipeFilter({ name = "LEGION", atlas = "images/filter_legion.xml", image = "filter_legion.tex" })

--5) 科技等级
_G.TECH.NONE.ELECOURMALINE = 0
_G.TECH.ELECOURMALINE_ONE = { ELECOURMALINE = 1 }
_G.TECH.ELECOURMALINE_THREE = { ELECOURMALINE = 3 }
_G.TECH.NONE.SIVING = 0
_G.TECH.SIVING_ONE = { SIVING = 1 }
_G.TECH.SIVING_THREE = { SIVING = 3 }

--6) 所有科技台的解锁树补默认值
for _, v in pairs(TUNING.PROTOTYPER_TREES) do
    v.ELECOURMALINE = 0
	v.SIVING = 0
end
TUNING.PROTOTYPER_TREES.ELECOURMALINE_ONE = TechTree.Create({ ELECOURMALINE = 1 })
TUNING.PROTOTYPER_TREES.ELECOURMALINE_THREE = TechTree.Create({ ELECOURMALINE = 3 })
TUNING.PROTOTYPER_TREES.SIVING_ONE = TechTree.Create({ SIVING = 1 })
TUNING.PROTOTYPER_TREES.SIVING_THREE = TechTree.Create({ SIVING = 3 })

--7) 全部既有配方补等级默认值（防止配方报错/被隐藏）
for _, v in pairs(AllRecipes) do
	if v.level.ELECOURMALINE == nil then v.level.ELECOURMALINE = 0 end
	if v.level.SIVING == nil then v.level.SIVING = 0 end
end
```

配方写法（recipes_legion.lua，AddRecipe2 全参数注释堪称教程）：

```lua
AddRecipe2( --永不凋零
    "neverfade", {
        Ingredient("rosorns", 1, "images/inventoryimages/rosorns.xml"),
        Ingredient("lileaves", 1, "images/inventoryimages/lileaves.xml"),
        Ingredient("orchitwigs", 1, "images/inventoryimages/orchitwigs.xml")
    }, TECH.MAGIC_THREE, {
        atlas = "images/inventoryimages/neverfade.xml",
        -- image = nil,             --默认为 product..".tex"
        -- builder_tag = "masterchef", --拥有该标签的玩家才可制作
        -- numtogive = 2,           --一次制作得到数量
        -- nounlock = true,         --不永久解锁
        -- no_deconstruction = true,--无法被绿杖拆解
        -- station_tag = "shadow_forge",
        -- product = "chum",        --制作物替换
        -- description = "transmute_log",
        -- placer = "carpet_whitewood_big_placer", --建筑需要
        -- min_spacing = 1.5,       --摆放限制半径，默认3.2
        -- testfn = function(pt, rot) end, --额外摆放限制
        -- build_distance = 2.5,    --摆放距离，默认1
    }, { "LEGION", "WEAPONS" }  --制作栏分类（可多个）
)
```

`Ingredient` 第3~5参数：`Ingredient(prefab, num, atlas, image, build_image)`——第5个参数解决"贴图和名字不一样"的问题（如 `Ingredient("rock_avocado_fruit", 3, nil, nil, "rock_avocado_fruit_rockhard.tex")`）。

NPC 交易配方（行走商人，wanderingtradershop 系列）：

```lua
AddRecipe2( --澄澈泥泉的蓝图
    "wanderingtradershop_pond_l_mud", {
        Ingredient("watermelonicle", 4)
    }, TECH.LOST, {
        image = "blueprint_rare.tex",
        limitedamount = true, nounlock = true, actionstr = "WANDERINGTRADERSHOP", sg_state = "give",
        product = "pond_l_mud_blueprint", description = "npc_beef_pond_l_mud"
    }, { "CRAFTING_STATION" }
)
```

拆解配方（绿宝石法杖分解）：`AddDeconstructRecipe("prefabname", { Ingredient(...) })`。

解锁方式配置化（lootdropper 蓝图掉落 vs prototyper 科技解锁）：

```lua
local tech_recast
local lock_recast
if OPTS.TECHUNLOCK == "lootdropper" then
    tech_recast = { TECH.LOST, TECH.LOST }
    lock_recast = nil
else
    tech_recast = { TECH.ELECOURMALINE_ONE, TECH.ELECOURMALINE_THREE }
    lock_recast = true
end
-- 使用：AddRecipe2(..., tech_recast[1], { nounlock = lock_recast, ... })
```

制作栏"显示全部对象"补丁（客户端，让 LEGION/SIVING 分类显示所有配方不论解锁）：

```lua
local craftingmenu_widget = require "widgets/redux/craftingmenu_widget"
local ApplyFilters_old = craftingmenu_widget.ApplyFilters
craftingmenu_widget.ApplyFilters = function(self, ...)
	if
		(self.current_filter_name == "LEGION" or self.current_filter_name == "SIVING") and
		CRAFTING_FILTERS[self.current_filter_name] ~= nil
	then
		self.filtered_recipes = {}
		local filter_recipes = FunctionOrValue(CRAFTING_FILTERS[self.current_filter_name].default_sort_values) or nil
		if filter_recipes == nil then
			return ApplyFilters_old(self, ...)
		end
		for i, recipe_name in metaipairs(self.sort_class) do
			local data = self.crafting_hud.valid_recipes[recipe_name]
			if data and filter_recipes[recipe_name] ~= nil then
				table.insert(self.filtered_recipes, data)
			end
		end
		...
	else
		return ApplyFilters_old(self, ...)
	end
end
```

### 3.4 烹饪与料理注册

**出处：preparedfoods_legion.lua + datafix_legion.lua**

料理表定义（字段注释本身就是教程）：

```lua
local foods_legion = {
    dish_duriantartare = { --怪味鞑靼
        test = function(cooker, names, tags) --烹饪配方判定
            return (names.durian or names.durian_cooked) and tags.meat and (tags.monster and tags.monster > 2)
        end,
        card_def = { ingredients = { {"durian",1}, {"monstermeat",2}, {"twigs",1} } }, --食谱卡
        priority = priority_med, --同条件多配方时取优先度高者
        foodtype = FOODTYPE.MEAT,
        secondaryfoodtype = FOODTYPE.MONSTER,
        hunger = 62.5, sanity = 0, health = 0,
        perishtime = times.d6,
        cooktime = 0.5, --实际时间 = cooktime*20 秒
        potlevel = "low", --锅上高度通道
        float = { nil, "small", 0.2, 1.05 }, --(本mod专属)漂浮数据
        oneatenfn = function(inst, eater) --食用特效
            if eater:HasAnyTag("monster", "playermonster") then
                if eater.components.health ~= nil then eater.components.health:DoDelta(30, nil, inst.prefab) end
                ...
            end
        end,
        -- 棱镜兼容字段（给烹饪锅UI显示配方用）
        cook_need = "(烤)榴莲 肉度 怪物度>2",
        cook_cant = nil,
        recipe_count = 4 --需要4种搭配才能完全解锁配方描述
    },
}
```

注册循环（datafix_legion.lua）：

```lua
for _, recipe in pairs(require("preparedfoods_legion")) do
    table.insert(Assets, Asset("ATLAS", "images/cookbookimages/"..recipe.name..".xml"))
    table.insert(Assets, Asset("IMAGE", "images/cookbookimages/"..recipe.name..".tex"))
    AddCookerRecipe("cookpot", recipe)
    AddCookerRecipe("portablecookpot", recipe)
    AddCookerRecipe("archive_cookpot", recipe)
    if recipe.card_def ~= nil then AddRecipeCard("cookpot", recipe) end
end
```

调料料理自动批量生成（preparedfoods_legion_spiced.lua）：遍历基础料理表，用 `shallowcopy` 复制数据、改 test/priority/name/spice 字段，给「便携香料站」注册。

食材标签注册（AddSimPostInit 内对 cooking.ingredients 做兼容补全）：

```lua
for _, ing in ipairs(fns.ingredients) do
    local cancook = ing[3]
    local candry = ing[4]
    for _, name in pairs(ing[1]) do
        if ingredients_base[name] == nil then
            ingredients_base[name] = { tags={} }
        end
        ...
        for tagname, tagval in pairs(ing[2]) do
            ingredients_base[name].tags[tagname] = tagval
            if cancook then
                ingredients_base[name.."_cooked"].tags.precook = 1
                ingredients_base[name.."_cooked"].tags[tagname] = tagval
            end
        end
    end
end
```

新食材进 VEGGIES（随机种子能长出）用 AddSimPostInit 里直接赋值 `_G.VEGGIES.pineananas = { health=..., seed_weight=TUNING.SEED_CHANCE_RARE, ... }`。

### 3.5 自定义容器

**出处：scripts/containers_legion.lua**

```lua
local slotbg_backcub = { image = "slot_bearspaw_l.tex", atlas = "images/slot_bearspaw_l.xml" }
local function MakeBackcub(name, animbuild)
    params[name] = {
        widget = {
            slotpos = {},
            slotbg = { [11] = slotbg_backcub, [12] = slotbg_backcub },
            animbank = "ui_piggyback_2x6", animbuild = animbuild,
            pos = Vector3(-5, -90, 0),
            dragtype = "pack_l_slot12" --拖拽类型：同类容器共享记忆位置
        },
        issidewidget = true,
        type = "pack",
        openlimit = 1
    }
    newbox = params[name].widget.slotpos
    for y = 0, 5 do
        table.insert(newbox, Vector3(-162     , -75*y + 170, 0))
        table.insert(newbox, Vector3(-162 + 75, -75*y + 170, 0))
    end
end
MakeBackcub("backcub", "ui_piggyback_2x6")
```

放物限制（白名单+标签兼容+世界唯一保护）：

```lua
pas.items_allowed = {
    agronssword = true, --艾力冈的剑
    terrarium = true,   --盒中泰拉
    klaussackkey = true,--麋鹿茸
    ...
}
pas.Check = function(container, item, slot)
    if pas.items_allowed[item.prefab] or item:HasTag("boxallowed_l") then --兼容其他模组
        return true
    end
    if item:HasAnyTag("irreplaceable", "nobundling", "pineopener_l") then
        return false
    end
    if item:HasTag("unwrappable") then return true end
    if not item:HasAnyTag("_container", "bundle") then return true end
end
```

`priorityfn` 排序函数（巨人之脚武器优先）：`return item.prefab == "cane" or item.prefab == "ruins_bat" or item:HasTag("weapon")`。

### 3.6 自定义动作（右键菜单系统）

**出处：scripts/sgactions_legoin.lua（4355行）**

自定义 Action 三步曲（统一修复动作例子）：

```lua
--1) 定义 Action
local REPAIR_LEGION = Action({ priority = 1, mount_valid = true })
REPAIR_LEGION.id = "REPAIR_LEGION"
REPAIR_LEGION.str = STRINGS.ACTIONS.REPAIR_LEGION
REPAIR_LEGION.strfn = function(act) --根据目标动态换台词
    if act.target ~= nil then
        if act.target:HasTag("moontreasure_l") then return "EMBED"
        elseif act.target:HasTag("eleccore_l") then return "CHARGE"
        elseif act.target.prefab == "mat_whitewood" then return "MERGE" end
    end
    return "GENERIC"
end
REPAIR_LEGION.fn = function(act) --执行逻辑（服务器）
    if act.invobject ~= nil and REPAIRERS_L[act.invobject.prefab] then
        return REPAIRERS_L[act.invobject.prefab].fn_do(act)
    end
end
AddAction(REPAIR_LEGION)

--2) 动作出现条件（USEITEM 组件钩子，显示进右键菜单）
AddComponentAction("USEITEM", "z_repairerlegion", function(inst, doer, target, actions, right)
    if right and REPAIRERS_L[inst.prefab] and REPAIRERS_L[inst.prefab].fn_try(inst, doer, target, actions, right) then
        table.insert(actions, ACTIONS.REPAIR_LEGION)
    end
end)

--3) SG 处理器（wilson + wilson_client 都要）
AddStategraphActionHandler("wilson", ActionHandler(ACTIONS.REPAIR_LEGION, function(inst, action)
    if action.invobject ~= nil and REPAIRERS_L[action.invobject.prefab] then
        return REPAIRERS_L[action.invobject.prefab].fn_sg(inst, action)
    end
end))
```

核心套路：`fn_try`(能否用) + `fn_do`(执行) + `fn_sg`(播放动作) 三个回调注册进 `REPAIRERS_L[prefab名]` 表——新修复道具只需加一条表项。

右键菜单多分支例子（SCENE 右键，根据装备切换动作）：

```lua
AddComponentAction("SCENE", "inspectable", function(inst, doer, actions, right)
    if not right then return end
    local item = doer.replica.inventory:GetEquippedItem(EQUIPSLOTS.HANDS)
    if item ~= nil then
        if item:HasTag("canshieldatk") then --举盾
            if not doer.legiontag_noshieldatk then
                table.insert(actions, ACTIONS.ATTACK_SHIELD_L)
                return
            end
        elseif item:HasTag("s_l_pull") then --羽刃合收
            if not item:HasTag("noskill_l") then
                table.insert(actions, ACTIONS.RC_SKILL_L)
            end
            return
        end
    end
    ...
end)
```

注意：客户端用 `doer.replica.xxx` 判定（不能用组件），服务端执行在 Action.fn 里。

### 3.7 盾反系统（shieldlegion 组件）

**出处：scripts/components/shieldlegion.lua（260行，全文精读）**

设计要点：
- 组件挂武器（盾）上，玩家受伤入口 `inventory_ApplyDamage` 被改写（postinit 中 `pas1.inventory_ApplyDamage_player`），先调 `hand.components.shieldlegion:GetAttacked(...)`，返回 true 则本次伤害归零
- 时间窗口判定：举盾后 `self.delta = 8 * FRAMES`（0.264秒，小于举盾 SG 动画总长 13*FRAMES）
- 反伤限次防死循环：`self.atkents[attacker] = count + 1` 必须在反击之前写
- 冷却存玩家实体 `doer.legion_shieldtime[key] = GetTime() + time_charge`（存档用 playersaverlegion 保存）
- SG 状态标签联动：成功时给 doer 的 sg 加 `nointerrupt/nosleep/nofreeze`；`canatk` setter 同步 `canshieldatk` 标签

```lua
function ShieldLegion:GetAttacked(doer, attacker, damage, weapon, spdamage, stimuli)
    if self.inst:HasTag("broken") then
        return false
    end
    local data = { damage = damage, otherdamage = 0, spdamage = spdamage,
        weapon = weapon, stimuli = stimuli, issuccess = false, isstay = false }
    if self.issuccess then --一次sg时间内盾反成功后完全无敌
        if doer.sg:HasStateTag("atk_shield") then
            if stimuli ~= "darkness" then data.issuccess = true end
            data.isstay = true
        else
            self:FinishAttack(doer)
        end
    elseif self.canatk and self.time ~= nil then
        if GetTime()-self.time <= self.delta and stimuli ~= "darkness" then --达成盾反条件
            data.issuccess = true
        else
            self:FinishAttack(doer)
        end
    end
    if data.issuccess then
        if spdamage ~= nil then data.otherdamage = ComputSpDamage(self, doer, spdamage) end
        if data.isstay then
            if self.atkstayingfn ~= nil and doer ~= attacker then
                self.atkstayingfn(self.inst, doer, attacker, data)
            end
        else
            if doer.sg:HasStateTag("atk_shield") then
                doer.sg:AddStateTag("nointerrupt") --防打断！
                doer.sg:AddStateTag("nosleep") --防催眠！
                doer.sg:AddStateTag("nofreeze") --防冻！
            end
            if self.atkfn ~= nil and doer ~= attacker then
                self.atkfn(self.inst, doer, attacker, data)
            end
            self.issuccess = true
            doer.shield_l_success = true --让玩家实体也能直接识别是否处于盾反成功中
        end
        self:SetFollowedFx(doer, self.fxdata) --盾保特效
        DoShieldSound(doer, self.inst.hurtsoundoverride)
        self:ArmorTakeDamage(doer, attacker, data)
        return true
    else
        if self.atkfailfn ~= nil then self.atkfailfn(self.inst, doer, attacker, data) end
        return false
    end
end
```

反伤（携带伤害计算、特殊伤害抵挡换算）：

```lua
function ShieldLegion:Counterattack(doer, attacker, data, radius, dmgmult)
    if attacker == nil or not attacker:IsValid() or attacker.components.combat == nil or
        attacker.components.health == nil or attacker.components.health:IsDead() or
        doer:GetDistanceSqToPoint(attacker.Transform:GetWorldPosition()) > radius*radius
    then
        return false
    end
    local count = self.atkents[attacker] or 0
    --一次举盾，对同个对象只能反击1次。必须限制次数，防止敌人的反伤逻辑导致无限循环！
    if count < (1 + (doer.num_catk_l_v or 0) + (self.num_catk or 0)) then
        self.atkents[attacker] = count + 1 --必须写在反击之前，否则无法阻止无限盾反！！！
        local dmg, spdmg, stimuli = TOOLS_L.CalcDamage(doer, attacker, self.inst, nil, nil, nil, nil, true)
        dmg = dmg * (dmgmult or 1) + ((data.damage + data.otherdamage) * 0.1)
        attacker.components.combat:GetAttacked(doer, dmg, self.inst, stimuli, spdmg)
    end
    return true
end
```

跟随特效（FollowSymbol 挂玩家骨骼）：

```lua
function ShieldLegion:SetFollowedFx(target, data)
    local fx = SpawnPrefab(data.prefab)
    fx.entity:SetParent(target.entity)
    fx.entity:AddFollower()
    fx.Follower:FollowSymbol(target.GUID, data.symbol, data.offsetx or 0, data.offsety or 0, 0)
    return fx
end
```

给官方恐怖盾牌加盾反（postinit 中 AddPrefabPostInit + 配置开关 MODTERRORSHIELD 防冲突）：

```lua
AddPrefabPostInit("shieldofterror", function(inst)
    inst:AddTag("allow_action_on_impassable")
    inst:AddTag("shield_l")
    inst:AddTag("rechargeable")
    inst:AddTag("nomimic_l") --不让拟态蠕虫进行复制
    if IsServer then
        inst:AddComponent("shieldlegion")
        inst.components.shieldlegion.armormult_success = 0
        inst.components.shieldlegion.atkfn = ShieldAtk_terror
        inst.components.shieldlegion.time_charge = OPTS.SHIELDRECHARGETIME
        inst.components.shieldlegion.time_change = OPTS.SHIELDEXCHANGETIME
        inst:AddComponent("rechargeable")
        inst.components.rechargeable:SetOnDischargedFn(OnDischarged_shield)
        inst.components.rechargeable:SetOnChargedFn(OnCharged_shield)
        inst:ListenForEvent("equipped", Equipped_shieldofterror)
        inst:ListenForEvent("unequipped", Unequipped_shieldofterror)
    end
end)
```

### 3.8 幻化系统（dressup）

**出处：scripts/components/dressup.lua（541行）+ dressup_legion.lua（数据）+ readme/tip_dressup.lua（兼容文档）**

本质：把装备"吃进"一个看不见的存档，用 `OverrideItemSkinSymbol/OverrideSymbol/Show/Hide` 把外观贴到玩家身上，实现"一件装备的外观+另一件装备的属性"。

数据驱动核心（DRESSUP_DATA_LEGION[prefab]）：

```lua
-- 某个幻化道具的prefab名 = {
--     dressslot = EQUIPSLOTS.HANDS,     -- 幻化位置（非装备类必须写）
--     isnoskin = true,                  -- 没有官方皮肤机制建议true
--     isopentop = true,                 -- 露出顶部头发的帽子
--     isfullhead = true,                -- 全覆盖头部
--     istallbody = true,                -- 高位身体（显示在衣服外层）
--     isbackpack = true,                -- 背包式
--     isshield = true,                  -- 盾牌式
--     buildfile = "swap_pillows_a", buildsymbol = "swap_object", -- 贴图数据
--     onequipfn/unequipfn/equipfn/buildfn/unbuildfn = function...
-- }
```

幻化位置系统：HANDS/HEAD/BODY+BACK+NECK 共用一位/"body_t"高位身体/"head_t"/"head_t2"两个自定义头部位（防覆盖，可同时显示两种头部幻化）。

换装优先级（priority 连续化）：后放的优先级更高；卸下时高优先级依次降 1：

```lua
local itemdataold = self.itemlist[slot]
if itemdataold ~= nil then
    self.itemlist[slot] = nil
    for slot, itemdata in pairs(self.itemlist) do
        if itemdata.priority > itemdataold.priority then
            itemdata.priority = itemdata.priority - 1
            for k, v in pairs(itemdata.swaps) do
                v.priority = itemdata.priority
            end
        end
    end
    self:TakeOff(slot, itemdataold)
end
```

实际展示更新（swaplist 统一执行）：

```lua
function DressUp:UpdateReal()
    for k,v in pairs(self.swaplist) do
        if v ~= nil then
            if v.type == "swap" then
                if v.buildskin ~= nil then
                    self.inst.AnimState:OverrideItemSkinSymbol(k, v.buildskin, v.buildsymbol, v.guid, v.buildfile)
                else
                    self.inst.AnimState:OverrideSymbol(k, v.buildfile, v.buildsymbol)
                end
                self.inst.AnimState:ShowSymbol(k)
            elseif v.type == "show" then self.inst.AnimState:Show(k)
            elseif v.type == "hide" then self.inst.AnimState:Hide(k)
            elseif v.type == "clear" then self.inst.AnimState:ClearOverrideSymbol(k)
            elseif v.type == "showsym" then self.inst.AnimState:ShowSymbol(k)
            elseif v.type == "hidesym" then self.inst.AnimState:HideSymbol(k)
            elseif k == "helmex" then self.inst.AnimState:UseHeadHatExchange(v.type == "yes") end
        end
    end
end
```

装备序列化与延迟删除：

```lua
-- 幻化时：保存 GetSaveRecord、RemoveFromScene、persists=false、DoTaskInTime(0.2, Remove) 延迟删
self.itemlist[slot] = { item = item:GetSaveRecord(), swaps = itemswap or {}, priority = prioritynew }
item:RemoveFromScene()
item.persists = false
item:DoTaskInTime(0.2, function() item:Remove() end) --必需滞后删除！

-- 还原时：SpawnPrefab + SetPersistData 重建
local function CreateItem(self, itemdata, setpos)
    local item = SpawnPrefab(itemdata.prefab, itemdata.skinname, itemdata.skin_id)
    if item ~= nil and item:IsValid() then
        if setpos then item.Transform:SetPosition(self.inst.Transform:GetWorldPosition()) end
        item:SetPersistData(itemdata.data)
        return item
    end
end
```

防双人同时幻化同物：`item.legiontag_nodress = true` 标志 + `if item.legiontag_nodress then return false end`。

### 3.9 电池/充能系统（batterylegion）

**出处：scripts/components/batterylegion.lua**

挂在"带电的晶石/电气石"上：fueled 组件为能量池 + 周期性自动充能（120秒+2.5能量）+ 对目标执行充能效果（武器修复/充羊/发电机换红宝石/子圭·育加速/电击敌人）。

节能模式（睡眠时用 LongUpdate 补算，不跑周期任务）：

```lua
function BatteryLegion:OnEntitySleep()
    if self.task ~= nil then self.task:Cancel() self.task = nil end
end
function BatteryLegion:OnEntityWake()
	if self.time_start ~= nil then
		self:LongUpdate(GetTime()-self.time_start)
	end
end
function BatteryLegion:LongUpdate(dt)
	if self.time_start == nil then return end
	self.time_start = nil
	self:Charge(dt/self.charge_period*self.charge_value, nil) --换算成能量值
end
```

成本计算（按步长+能量换算，返回 reason 用于拒绝提示）：

```lua
local function ComputCost(cpt, doer, step, now, max, mult)
	if now >= max then return 0, "NONEED" end
	local allnum
	if cpt == nil then
		allnum = math.floor(150 / mult)
	else
		allnum = math.floor(cpt.currentfuel / mult)
	end
	if allnum <= 0 then return 0, "NOENERGY" end
	local cost = math.min(now + step, max) - now
	if cost > allnum then cost = allnum end
	if cpt ~= nil then cpt:DoDelta(-cost*mult, doer) end
	return cost
end
```

### 3.10 生长/转化系统（perennialcrop / genetrans / moonsimmered）

**出处：scripts/components/perennialcrop.lua（1060行）、genetrans.lua（698行）、moonsimmered.lua（1099行）**

共性架构（三个都是"状态机+暂停原因表+LongUpdate 补算"）：

```lua
-- 暂停原因表：多个原因可叠加（黑夜、冬季、缺水、被摘...）
function PerennialCrop:SetPauseReason(key, value)
    -- key 唯一标识一个暂停原因，value 覆盖写
end
function PerennialCrop:UpdateTimeMult() -- 汇总所有倍率（季节、水肥、buff）
function PerennialCrop:TryDoGrowth()    -- 循环生长（DoPeriodicTask 驱动）
function PerennialCrop:TimePassed(time, nogrow) -- 帧推进核心
function PerennialCrop:LongUpdate(dt)   -- 睡眠补算（游戏引擎要求）
```

genetrans（子圭·育：普通作物→异种）关键概念：
- `energynum_max` 能量上限；`SetFastReason(key, value)` 外部加速源（电池给 mult=2）
- `UnlockGene(items, doer)` 基因解锁：把已转化的配方记录进实体，转化表驱动 `DropLoot(needrecipe)`
- 灯光/动画按进度更新：`UpdateFxProgress()` 播果实生长动画帧

moonsimmered（月炆宝炊：自动烹饪锅+保温+批量）关键概念：
- `_TaskCook(inst, self)` 周期任务烹饪；`TryCooking/TryRoasting/BtnCook/BtnRoast` 状态机
- 槽位数据 `SetCookData(idx, lines)`；产物 `SpawnProduct(product, perishpercent, num, slot, skins)`
- `DilutePerishTime` 保鲜稀释：`SetPerishable` 保存新鲜度百分比

### 3.11 浸泡/浴缸系统（zip_soak_legion）

**出处：scripts/zip_soak_legion.lua（1062行）**

设计文档（文件头部注释原文）：

```
设计思路：
    一个泉池最多能放入6种物品（极值都按3个来算，指就算是最厉害的物品也得至少3种才能达到完美）
    有的物品偏向于回复、有的物品偏向于提升buff时间、有的物品能提供新buff
    在数值设计上，不可能所有要求都能满足，要让玩家自己取舍！鱼和熊掌不可兼得。
数值思路：
    原本的生命、精神回复量，以及buff时间都提高到至少3倍
    添料的填写数值是-1~1之间，优劣阶梯为【0.075, 0.15, 0.225, 0.3, 0.6】
    应用buff时间系数时，如果大于0，则还需再乘以10，因为buff时间正向的变化范围是(1+0)~(1+9)倍
```

buff 时长公式：`time = 6（每秒浸泡增加6秒buff），cycle = 10（每10秒结算一次）`，泡满40秒→240秒buff；`isbad = true` 负面buff；`noforce` 时长不足不给。

数值阶梯表（暴露给其他 mod 用）：

```lua
local r = { 0.075, 0.15, 0.225, 0.3, 0.375, 0.45, 0.525, 0.6 } -- r[5]至r[8]是最顶级的属性
fns.values = r --暴露出来让其他模组用的
```

### 3.12 皮肤/换肤系统（tools_sk_legion + skinedlegion）

**出处：scripts/tools_sk_legion.lua（2570行）、components/skinedlegion.lua、mod_inventoryprefabs_list.lua**

层次：
- 物品皮肤：`mod_inventoryprefabs_list.lua` 的 InventoryPrefabsList 表（key=prefab 值=皮肤组1/2）+ 官方皮肤注册
- 实体换肤：skinedlegion 组件（`LS_C_*` 是一套工具函数：LS_C_Init/SetSkin/SetLinkedSkin/SetPersistData）
- 展示换肤：`fns.efx`（特效缩放表14种）、`fns.flt`（漂浮参数表36种）、`fns.simmer`/`fns.hide`/`fns.chestww`/`fns.elecaxe`/`fns.pot`/`fns.sivturn`/`fns.xeed`——每个是一套"皮肤换装回调组"（On_xxx/Off_xxx/SetAnim）

皮肤注册数据（mod_inventoryprefabs_list.lua 结构）：

```lua
local InventoryPrefabsList = {
    _catalog = { "images_minisign1", ... }, -- 小木牌图画
	rosorns = 1,     -- 值1：第一套皮肤表
    fimbul_axe = 2,  -- 值2：第二套（更高档）
}
```

### 3.13 存档系统（playersaver / worldsaver）

**出处：scripts/components/playersaverlegion.lua（74行）、worldsaverlegion.lua（23行）**

挂在玩家/世界上，专门保存"无法由组件保存"的散数据（实体字段）：

```lua
function PlayerSaverLegion:OnSave()
    local data = {}
    local inst = self.inst
    if inst.legion_luckdata ~= nil then --好事多蘑数据
        local newluckdd
        for itemname, v in pairs(inst.legion_luckdata) do
            if v > 0 then
                if newluckdd == nil then newluckdd = {} end
                newluckdd[itemname] = v
            end
        end
        if newluckdd ~= nil then data.legion_luckdata = newluckdd end
    end
    if inst.legion_shieldtime ~= nil then --盾反冷却：把绝对时间转成剩余秒数存档
        local timenow = GetTime()
        local timedd
        for k, timethat in pairs(inst.legion_shieldtime) do
            timethat = timethat - timenow
            if timethat > 0 then
                if timedd == nil then timedd = {} end
                timedd[k] = timethat
            end
        end
        if timedd ~= nil then data.legion_shieldtime = timedd end
    end
    return data
end
-- OnLoad 时 timedd[k] = timenow + dt 转回绝对时间
```

角色切换（猴子变身/还原）转移数据：

```lua
function PlayerSaverLegion:TransferComponent(newplayer)
    local oldinst = self.inst
    if oldinst.legion_luckdata ~= nil then
        newplayer.legion_luckdata = oldinst.legion_luckdata
        oldinst.legion_luckdata = nil
    end
    if oldinst.legion_shieldtime ~= nil then
        newplayer.legion_shieldtime = oldinst.legion_shieldtime
        oldinst.legion_shieldtime = nil
    end
end
```

worldsaver 利用 OnSave 钩子做"客户端数据脏标记下发"：

```lua
function WorldSaverLegion:OnSave()
    LS_SaveSkinFile()
    local dirty = CONFIGS_LEGION.DDA_DIRTY
    for _, v in ipairs(AllPlayers) do
        local userid = v.userid
        if userid and userid ~= "" and dirty[userid] then
            dirty[userid] = nil
            SendModRPCToClient(GetClientModRPC("LegionMsg", "tngvham_L"), userid, 0)
        end
    end
end
```

组件 OnSave 小贴士（注释原文）："如果组件中的 OnSave() 没有返回数据，则 OnLoad() 也不会执行到了"（modelegion.lua）。

### 3.14 多语言/汉化组织

- modinfo 里中英两套 configuration_options 完整复制，`L` 判断语言
- strings_chinese.lua / strings_english.lua 两套文件，内含 `STRINGS.UI_L` 命名空间（mod 自定义 UI 字符串）
- 文本批量复制工具（同一条台词给所有角色）：

```lua
local function CopyStrActionFail(newkey, key)
    for _, character in ipairs(S___CHARACTERS) do
        character.ACTIONFAIL[newkey] = character.ACTIONFAIL[key] or S______GENERIC.ACTIONFAIL[key]
    end
end
```

- 静态布局中文字版本：`LAYOUTS["OrchidGrave"] = STATICLAYOUT.Get("map/static_layouts/orchidgrave"..(isChinese and "_zh" or ""))`
- 运行时改官方字符串（AddSimPostInit 内）：`if _G.CONFIGS_LEGION.LANGUAGES == "chinese" then STRINGS.WAXEDPLANT = "影织" end`（只改中文，别的语言懒得翻译——注释原话）
- cookbookui_legion 的文案也按语言二选一表

### 3.15 特效 prefab 模式（proxy+task 双实体）

**出处：scripts/prefabs/fx_legion.lua**

```lua
local function MakeFx(data) --不需要网络功能
    local function TaskFn(proxy)
        local inst2 = CreateEntity()
        --[[Non-networked entity]]
        inst2.entity:AddTransform()
        inst2.entity:AddAnimState()
        inst2.entity:SetCanSleep(false)
        inst2.persists = false
        inst2:AddTag("FX")
        local parent = proxy.entity:GetParent()
        if parent ~= nil then
            inst2.entity:SetParent(parent.entity)
        end
        inst2.Transform:SetFromProxy(proxy.GUID)
        if data.fn_anim ~= nil then
            data.fn_anim(inst2, proxy)
        end
        if data.fn_remove ~= nil then
            data.fn_remove(inst2)
        else
            inst2:ListenForEvent("animover", inst2.Remove)
        end
    end
	table.insert(prefs, Prefab(data.name, function()
        local inst = CreateEntity()
        inst.entity:AddTransform()
        inst.entity:AddNetwork()
        inst:AddTag("FX")
        if not TheNet:IsDedicated() then --客户端才需要动画
            if data.notaskfn then
                inst._taskfn = TaskFn --延迟执行（存函数等之后调用）
            else
                inst:DoTaskInTime(0, TaskFn)
            end
        end
        if data.fn_common ~= nil then data.fn_common(inst) end
        inst.entity:SetPristine()
        if not TheWorld.ismastersim then return inst end
        inst.persists = false
        inst:DoTaskInTime(data.removetime or 1, inst.Remove)
    end, data.assets, data.prefabs))
end
```

### 3.16 BOSS 工厂模式

**出处：scripts/prefabs/boss_siving_phoenix.lua（雌雄玄鸟用一份 MakeBoss(data)）**

要点：
- 雌雄伴侣系统：`inst.mate`、`inst.tree`（子圭神木）；`fn_onGrief` 悲愤状态（改色/改攻/换掉落表 `SetChanceLootTable(name.."_rebirth")`）
- 窃血抵抗：`TOOLS_L.AddEntValue(inst, "siv_blood_l_reducer", data.name, 1, 0.75)`（可叠加的实体数值管理）
- 技能表：MagicWarble 魔音绕梁 / DiscerningPeck 啄击 / ReleaseFlowers 花寄语 / BeTreeEye 同目同心 / FeathersFlap 羽乱舞（函数式技能）
- `inst:SetPrefabNameOverride("siving_phoenix")` 统一显示名
- 武器也走工厂：MakeBossWeapon(data)（羽毛：投掷物+滞留体+丝线拉回三体模型，见 sivfeatherctl）

---

## 4. 亮点技术（最有价值的技巧）

### 4.1 「旧函数存档 + 分叉调用」的安全 hook 模式

所有 hook 都先存旧函数（`xxx_legion` 字段），新函数里按条件决定走新逻辑还是调旧函数——而不是无条件覆盖。这是全模组最核心的修改哲学：

```lua
pas1.eater_PrefersToEat_player = function(self, food, ...)
    if self.inst.legiontag_bestappetite then
        return self:TestFood(food, self.caneat)
    end
    if self.PrefersToEat_legion ~= nil then
        return self.PrefersToEat_legion(self, food, ...)
    end
end
-- 挂载处（postinit）：
pas1.PrefersToEat_legion = cpt.PrefersToEat  -- 存旧
cpt.PrefersToEat = pas1.eater_PrefersToEat_player -- 换新
```

优点：多 mod 同时改同一函数时（官方 Update 也会改），可以通过 `legiontag_xxx` 实体标志判定"是否该由我处理"，实现与官方/其他 mod 逻辑共存；也便于自己热重载。

### 4.2 玩家受伤管线钩子实现"举盾/金蝉脱壳/蝴蝶庇佑"多重防御

只改一个入口 `inventory_ApplyDamage`，按顺序串联多个防御子系统（盾反→蝴蝶庇佑→金蝉脱壳→破防攻击判定），每个子系统返回 0 即吞掉伤害。自定义防御系统的正确挂点示范：

```lua
pas1.inventory_ApplyDamage_player = function(self, damage, attacker, weapon, spdamage, ...)
    if damage >= 0 or spdamage ~= nil then
        local player = self.inst
        --盾反
        local hand = player.components.inventory:GetEquippedItem(EQUIPSLOTS.HANDS)
        if hand ~= nil and hand.components.shieldlegion ~= nil and
            hand.components.shieldlegion:GetAttacked(player, attacker, damage, weapon, spdamage, nil)
        then
            ... return 0
        end
        --蝴蝶庇佑
        if player.legionfn_butterflyblessed ~= nil and player:legionfn_butterflyblessed() then
            return 0
        end
        --金蝉脱壳
        if player.bolt_l ~= nil and not player.sg:HasStateTag("busy") ... then
            ... return 0
        end
    end
    if self.ApplyDamage_legion ~= nil then
        return self.ApplyDamage_legion(self, damage, attacker, weapon, spdamage, ...)
    end
    return damage, spdamage
end
```

### 4.3 配表驱动 + 工厂函数批量生成 prefab

一处模板、一张数据表、循环生成几十个 prefab（活性组织×4、子圭岩等级×4、调料料理×N、皮影戏幻化数据×N、BOSS雌雄×2）。新增内容只加一行表项。全 mod 各层都用这个思路：配方(REPAIRERS_L 表)、食物(foods_legion 表)、幻化(DRESSUP_DATA_LEGION 表)、容器(params 表)、皮肤(efx/flt 表)。

### 4.4 200 局部变量限制的规避 + 表即模块

```lua
local fns = {} --lua的限制，一个域里只能有最多200个局部变量，否则会报错。通过把所有变量都存进一个主变量，来预防这个问题
local pas = {} --为了不暴露局部变量，单独装一起
```

大文件超过 200 个局部变量直接报错，fns/pas 双表法绕开；同时 require 时 `TOOLS_L = require("tools_legion")` 拿到整表即拿到全部工具——比 export 清单更省事。工具文件间循环依赖用 `fns.AddTools(...)` 延迟注入解决。

### 4.5 客户端数据 RPC 同步 + 脏标记

配置修改后需要同步到客户端时（UI拖拽位置、设置），在 worldsaver 的 OnSave（世界存档时必然执行）里检查 CONFIGS_LEGION.DDA_DIRTY[userid] 脏标记，用 `SendModRPCToClient(GetClientModRPC("LegionMsg", "..."), userid, 0)` 推送，客户端收到后自行拉取/重建。

### 4.6 睡眠/唤醒的 LongUpdate 补算（节能）

所有周期生长/烹饪/充电组件都实现 `OnEntitySleep/OnEntityWake/LongUpdate`：睡眠时取消周期任务，唤醒时一次性补算 `GetTime()-time_start` 的时长。避免"建筑睡觉导致进度丢失"和"睡眠时白跑任务"。

### 4.7 右键动作系统的 fn_try/fn_do/fn_sg 三段式注册

同一组件多个道具共用一套动作（修复动作），每个道具只需在 REPAIRERS_L 表注册 3 个回调；动作的"是否出现"在客户端 replica 判定、"执行"在服务端 fn。这是可扩展右键菜单的标准做法。

### 4.8 用实体标签做运行时开关/状态位

`legiontag_xxx`（布尔）与 `legionfn_xxx`（函数引用）大量挂在实体上：`legiontag_noshieldatk`（禁用盾击）、`legiontag_bestappetite`（好胃口）、`legiontag_undefended`（破防状态）、`legionfn_butterflyblessed`（庇佑判定）。其他 mod 想兼容时只要给玩家加同名标签/函数即可——比改组件字段更松耦合。

### 4.9 UI 拖拽系统（容器界面可拖动）

客户端 AddClassPostConstruct("widgets/containerwidget") 给所有容器加右键拖拽，坐标存 `CONFIGS_LEGION.DD_UIDRAG[uikey]` + SaveClientData() 本地持久化。完整实现见 postinit_legion.lua 298-682 行（含 TheInput:AddMoveHandler 跟随鼠标、偏移修正）。

### 4.10 禁玩家黑名单（极端反作弊，不推荐模仿但可了解）

```lua
AddPlayerPostInit(function(inst)
    inst:DoTaskInTime(5, function()
        if ThePlayer and ThePlayer.userid then
            local banids = {
                ["KU_3NiPP26E"] = true, --烧家主播
            }
            if banids[ThePlayer.userid] then
                os.date("%h")
                local badbad = 1/0 --故意崩溃
            end
        end
    end)
end)
```

---

## 5. 可复用的模板代码

### 模板A：完整 mod 入口骨架（按棱镜组织还原）

```lua
-- modworldgenmain.lua（明文，运行在 modmain 之前）
local _G = GLOBAL
local isChinese = GetModConfigData("Language") == "chinese"
-- 1. 混合地皮：AddTile + NoiseTileFunctions
-- 2. 静态布局：LAYOUTS["X"] = STATICLAYOUT.Get(...)
-- 3. 房间：require("map/rooms/xxx/rooms_yyy") 内 AddRoom
-- 4. 任务：require("map/tasks/xxx") 内 AddTask
-- 5. 塞进官方世界：AddTaskPreInit / AddTaskSetPreInit
```

```lua
-- modmain.lua 骨架（逻辑全部放 scripts/）
local _G = GLOBAL
CONFIGS_LEGION = { LANGUAGES = GetModConfigData("Language"), ... }
-- 环境注入（保护 _G 可访问）
env.setmetatable(env, { __index = function(_, k) return _G.rawget(_G, k) end })
require("datafix_legion")       -- PrefabFiles/Assets 注册 + AddSimPostInit
require("techtrees_legion")
require("recipes_legion")
require("preparedfoods_legion")
require("containers_legion")
require("sgactions_legoin")
require("postinit_legion")
require("dressup_legion")
```

### 模板B：新物品三件套（prefab+配方+文本）

```lua
-- 1) prefabs/xxx.lua
local prefs = {}
table.insert(prefs, Prefab("myitem", function()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank("myitem")
    inst.AnimState:SetBuild("myitem")
    inst.AnimState:PlayAnimation("idle")
    inst.entity:SetPristine()
    if not TheWorld.ismastersim then return inst end
    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = "myitem"
    inst.components.inventoryitem.atlasname = "images/inventoryimages/myitem.xml"
    inst:AddComponent("stackable")
    inst.components.stackable.maxsize = TUNING.STACK_SIZE_SMALLITEM
    return inst
end, {
    Asset("ANIM", "anim/myitem.zip"),
    Asset("ATLAS", "images/inventoryimages/myitem.xml"),
    Asset("IMAGE", "images/inventoryimages/myitem.tex"),
    Asset("ATLAS_BUILD", "images/inventoryimages/myitem.xml", 256)
}, nil))
return unpack(prefs)
-- 2) datafix: 加入 PrefabFiles = {"xxx"} + RegisterInventoryItemAtlas("images/inventoryimages/myitem.xml","myitem.tex")
-- 3) recipes_legion.lua: AddRecipe2("myitem", { Ingredient(...) }, TECH.SCIENCE_ONE, {atlas=...}, {"LEGION","TOOLS"})
-- 4) 文本: STRINGS.NAMES.MYITEM / STRINGS.RECIPE_DESC.MYITEM / STRINGS.CHARACTERS.*.DESCRIBE.MYITEM
```

### 模板C：新科技站（复制 techtrees_legion.lua 的 7 步）

按 3.3 节顺序：AVAILABLE_TECH → Create 补默认 → AddPrototyperDef → AddRecipeFilter → TECH 等级 → PROTOTYPER_TREES → AllRecipes 补等级。

### 模板D：自定义动作三段式

```lua
local MYACT = Action({ priority = 1 })
MYACT.id = "MYACT"
MYACT.str = STRINGS.ACTIONS.MYACT
MYACT.fn = function(act) ... end
AddAction(MYACT)
AddComponentAction("USEITEM", "mycomponent", function(inst, doer, target, actions, right)
    if right and MyTry(inst, doer, target) then
        table.insert(actions, ACTIONS.MYACT)
    end
end)
AddStategraphActionHandler("wilson", ActionHandler(ACTIONS.MYACT, "doshortaction"))
AddStategraphActionHandler("wilson_client", ActionHandler(ACTIONS.MYACT, "doshortaction"))
```

### 模板E：可恢复的长流程组件（生长/烹饪/充电）

```lua
-- Class 内：
function X:Start()   -- 记录 time_start + DoPeriodicTask
function X:Stop()    -- Cancel task
function X:LongUpdate(dt) -- 睡眠补算
function X:OnEntitySleep() self:Stop() end
function X:OnEntityWake() self:LongUpdate(GetTime()-self.time_start) end
function X:SetPauseReason(key, value) -- 暂停原因表（多原因叠加）
function X:UpdateTimeMult() -- 汇总倍率
```

### 模板F：AddSimPostInit 兼容补丁（官方数据补全）

```lua
AddSimPostInit(function()
    -- 所有 mod 加载完成后才可靠判定的联动/补丁放这里
    if _G.rawget(_G, "OTHERMOD_DATA") then ... end
    -- 对官方表做"缺则补"而非覆盖
    for name, data in pairs(MyData) do
        if official[name] == nil then official[name] = data end
    end
end)
```

### 模板G：多角色台词批量复制

```lua
local function CopyStrDescribe(newkey, key)
    for _, character in ipairs(S___CHARACTERS) do
        character.DESCRIBE[newkey] = character.DESCRIBE[key] or S______GENERIC.DESCRIBE[key]
    end
end
```

### 模板H：鼠标悬停信息（MouseInfo）

tools_legion.lua `fns.InitMouseInfo(inst, fn_dealdata, fn_getdata, limitedtime)` + `fns.SendMouseInfoRPC(player, target, newdd, isfixed, newtime)`——物品上挂描述函数，玩家鼠标悬停时经 RPC 拉取特殊信息展示。实现要点：GetDescription(viewer, inst, status) 拼接字符串、`viewer:HasAnyTag("playerghost","mime")` 过滤、频控由配置 MOUSEINFO 控制。

---

## 附：资产组织规律速查

- **动画**：`anim/xxx.zip` 一个实体一个 build；`anim/skin/xxx.zip` 皮肤 build（169个）；`ui_xxx_NxM.zip` 容器 UI（N列M行，`_inf` 后缀=无上限版）；`crop_legion_xxx.zip` 异种作物；`fx` 后缀=特效；料理共享 `dishes_legion.zip`（用 overridebuild+overridesymbolname 区分）
- **贴图**：`images/inventoryimages/xxx.xml+tex` 成对；`inventoryimages_skin/` 皮肤图标；`cookbookimages/` 食谱大图；`map_icons/` 小地图；`foodtags/` 食材标签；`filter_legion`/`station_*` 制作栏与科技站图标
- **音频**：`sound/legion.fev + legion.fsb`（Fmod 包，`Asset("SOUNDPACKAGE",...)` + `Asset("SOUND",...)` 注册）
- **xml 结构**（modicon.xml 示例）：`<Atlas><Texture filename="x.tex"/><Elements><Element name="x.tex" u1=.. u2=.. v1=.. v2=../></Elements></Atlas>`——每个 Element 是 0~1 归一化 UV 矩形
- **地皮**：`levels/tiles/` 放地皮贴图（含对官方 swamp.xml 的替换做水面效果）；`levels/textures/` 放噪声贴图（Ground_/mini_ 前缀）

## 附：关键文件行数索引（精读优先级）

| 文件 | 行数 | 内容 |
|---|---|---|
| scripts/languages/strings_chinese.lua | 6634 | 全部中文文本 |
| scripts/widgets/skinlegiondialog.lua | 4906 | 皮肤 UI（换肤对话框） |
| scripts/sgactions_legoin.lua | 4355 | 动作系统 |
| scripts/prefabs/plants_legion.lua | 3750 | 植物（三花丛/雨竹/夜玫瑰） |
| scripts/datafix_legion.lua | 3497 | 资源注册+补丁 |
| scripts/prefabs/euip_hand_legion.lua | 2905 | 手持装备 |
| scripts/postinit_legion.lua | 2865 | 全mod后置修改 |
| scripts/prefabs/items_legion.lua | 2799 | 基础物品 |
| scripts/tools_sk_legion.lua | 2570 | 皮肤工具 |
| scripts/prefabs/moonlight_legion.lua | 2345 | 月之宝具四件套 |
| scripts/prefabs/fx_legion.lua | 2298 | 特效工厂 |
| scripts/prefabs/farm_plants_legion.lua | 2025 | 异种作物 |
| scripts/prefabs/buffs_legion.lua | 2010 | buff 定义 |
| scripts/prefabs/constructs_legion.lua | 1958 | 构筑/建筑 |
| scripts/prefabs/boss_siving_phoenix.lua | 1935 | 玄鸟BOSS |
| scripts/prefabs/siving_base_legion.lua | 1859 | 子圭系列核心 |
| scripts/tools_legion.lua | 1731 | 核心工具库 |
| scripts/dressup_legion.lua | 1607 | 幻化数据 |
| scripts/preparedfoods_legion.lua | 1241 | 料理表 |
| scripts/components/perennialcrop2.lua | 1379 | 异种作物组件 |
| scripts/components/moonsimmered.lua | 1099 | 月炆宝炊 |
| scripts/components/soakablelegion.lua | 1179 | 可浸泡 |
| scripts/components/perennialcrop.lua | 1060 | 作物组件 |
| scripts/zip_soak_legion.lua | 1062 | 浸泡系统 |
| scripts/containers_legion.lua | 944 | 容器 |
| scripts/recipes_legion.lua | 885 | 配方 |
| scripts/components/genetrans.lua | 698 | 基因转化 |
| scripts/components/dressup.lua | 541 | 幻化组件 |
| scripts/components/shieldlegion.lua | 260 | 盾反组件 |
| scripts/techtrees_legion.lua | 123 | 科技树（模板） |
| modworldgenmain.lua | 173 | 世界生成（模板） |

---

## 6. 特色专题补充：岛屿/植物/地形

> 本章为专题补全：特色植物全清单、代表性生长机制精读、雨硫岛等岛屿布局细节、海洋处理、补充地形、以及美术资产解码分析（KTEX DXT5/DXT1 + PIL 色彩统计）。源码根：`E:\神秘复苏\饥荒大型mod\1392778117`。

### 6.1 特色植物全清单

植物类 prefab 主要集中在四个文件：`scripts/prefabs/plants_legion.lua`（3750行，野生植物+颤栗树）、`scripts/prefabs/farm_plants_legion.lua`（2025行，异种作物/巨食草/荧光作物）、`scripts/prefabs/whitewoods.lua`（白桦树/培植盆）、`scripts/prefabs/siving_related.lua`（子圭系统）。数据表在 `scripts/datafix_legion.lua` 的 `CROPS_DATA_LEGION`（约1861行起）。

#### 野生植物（plants_legion.lua）

| 文件名（prefab） | 植物 | 生长机制 | 收获物 | 用途 |
|---|---|---|---|---|
| monstrain | 雨竹（沼泽雨岛） | pickable 6天再生 + childspawner 产雨滴馈赠 + 冬季必枯萎、夏季缺水枯萎、可汲水复活；不能施肥 | squamousfruit 鳞果（monster+fruit，饥饿25/理智-5/生命-3）+ monstrain_leaf 雨竹叶 | 鳞果料理（pasty/hardy）；挖起得 dug_monstrain 可移植 |
| monstrain_wizen | 雨竹块茎（移植苗） | moisture 组件：湿度>=95% 变回雨竹；3天未补水变 spoiled_food | dug_monstrain | 雨竹的移植形态，可打蜡 |
| rosebush | 蔷薇花丛 | pickable 6天 + max_cycles（BERRYBUSH_CYCLES+随机2）循环 + witherable + 冬季停长 + 采集被刺伤3点 | petals_rose 蔷薇花瓣 + 3% 几率 rosorns 蔷薇之刺剑；30%花瓣/65%树枝/5%蔷薇折枝 | 花瓣可晒干（dryable）；剑掉落；暗影仆从可采（bush_l_f 标签） |
| lilybush | 蹄莲花丛 | 同上（3%几率 lileaves 蹄莲剑） | petals_lily 蹄莲花瓣 | 同上；10%几率蹄莲芽束 cutted_lilybush |
| orchidbush | 兰草花丛 | 同上（3%几率 orchitwigs 兰草剑） | petals_orchid 兰草花瓣；60%几率 cutgrass 干草 | 同上；10%几率兰草种籽 cutted_orchidbush |
| neverfadebush | 永不凋零花丛 | pickable 3天 + makebarrenfn=nil（不能枯萎）+ 采集后播放动画即消失 | neverfade 永不凋零剑（必掉，1耐久） | 一次性采剑，可打蜡得坏剑 |
| nightrosebush | 夜玫瑰花丛 | pickable 6天循环 + witherable + 无冬季限制 + 采集被刺伤6点；_fruitform 花叶同图 | petals_nightrose + 3% 几率 hat_whisperose 低语蔷薇帽；65%几率 nightmarefuel | 暗影系材料；植园灯光 |
| shyerrycore | 颤栗树之心（沙漠地标） | shyerrygrow 组件：growth/moisture/nutrient1/2/3 五维培养，3 阶段，环形线路长出 1-4 棵子树（shyerrytree1-4，大中小 3 档） | shyerrylog 颤栗原木（大 50%）、shyerry 颤栗果 | 沙暴区资源；不可替换（irreplaceable 标签防被地形清除） |
| shyerrycore_planted | 培育的颤栗树之心 | shyerrygrow 简化版（growth 48/水 500/肥 500） | shyerrycore_item（挖起） | 可搬运的颤栗树核心 |
| shyerryflower | 颤栗花 | pickable 10 秒快速产物 + 周期性检测 10 格内 scarytoprey 生物、被吓到就枯萎消失（含玩家台词彩蛋） | shyerry 颤栗果；烧焦得 shyerry_cooked | 一次性惊吓资源 |
| fern_l | 耐酸蕨 | pickable 10 秒 + remove_when_picked + quickpick（采集即消失） | foliage 蕨叶 | 雨岛/温泉区地表装饰 |
| icelegume_l | 冰皂草 | 同上 | bean_l_ice 冰皂豆 | 培植盆可种（growtime 9天） |
| siving_thetree | 子圭神木岩 | 打蜡植物（waxed 状态机）：live/死 双 build，可被画刷换形 | siving_thetree_item | 子圭之源（SivingCenter）地标 |

#### 异种作物（farm_plants_legion.lua + datafix CROPS_DATA_LEGION）

| 文件名（prefab） | 植物 | 生长机制 | 收获物 | 用途 |
|---|---|---|---|---|
| plant_xxx_l（MakePlant2 批量，官方12作物） | 官方作物异种化 | perennialcrop2 组件：4 阶段+开花+枯萎掉落，总周期 12 天（发芽14/16天+平均7天+过熟4天），季节倍率 growthmults | 官方对应产物+巨型化 | 可打蜡（xeed 系统）、可浸泡 |
| plant_pineananas_l | 凤梨（mod 特有作物） | 季节倍率 {0.8,1.2,1.2,0}，regrowstage=2，cluster_size {1,1.5}；5% 掉松果 | pineananas（veggie+fruit）、pineananas_oversized | 双属性食材 |
| plant_plantmeat_l | 巨食草 | perennialcrop2 + modelegion 双形态（植物/生物互转）+ 容器吞食（吞食半径2~6、数量1~10、消化33~3秒随 cluster 缩放） | plantmeat 植物肉 + 消化后的物品 | 消化系统（不吃自己的异种/鱼骨/翅膀） |
| plant_lightbulb_l | 荧光作物 | perennialcrop2 + 发光等级随 cluster 变化 + 昼夜开关光 | lightbulb 荧光果 | 光系种植 |
| plant_log_l | 腐木 | 简单工作物（锤/砍） | log | 蘑菇森林装饰 |
| weed_firenettle（官方杂草复用） | 火荨麻 | 官方杂草（killjoystolerance=1）；mod 布置在温泉沙滩并加入勋章种子权重 | firenettles 火荨麻叶 -> firenettles_dried 干叶 | 浸泡系统材料（zip_soak_legion 469行） |

#### 可生长建筑/白桦（whitewoods.lua）

| 文件名（prefab） | 植物 | 生长机制 | 收获物 | 用途 |
|---|---|---|---|---|
| mat_whitewood | 白桦树 | upgradeable 5 阶（MAT_L 升级类型），锤1下拆除，每升 2 阶多掉 1 个基质 | mat_whitewood_item 白桦基质 | 白桦木建材/家具 |
| pot_whitewood | 稀有基质培植盆 | growable 4 阶段 + 肥料（fertility 80 上限，收肥收种双 trader）+ 可种 20+ 种植物（potPlants 表：红/绿/蓝/月/素白菇系、多肉、蕨叶、苔藓、冰皂豆）+ 同类升级（pri 优先级）+ 无上限升级（nomaxlvl）-> 无限生长；红/绿/蓝菇 4 阶段产孢子（periodicspawner） | 所种果实 + 孢子 | 室内农场/蘑菇农场 |

#### 其他相关

- `raindonate`（scripts/prefabs/raindonate.lua）：雨竹 childspawner 产出的小生物（官方蚊子模板改造），33% 掉 ahandfulofwings
- `siving_derivant`（子圭奇型岩）与 `siving_soil`（子圭垄）：岩石/种植土系统（3.2.4 已覆盖可生长建筑部分）
- `guitar_greenery`（绿意吉他）：乐器类，弹奏在沙漠/森林/洞穴/水上生成对应植被特效（非植物本体）

### 6.2 生长机制精读（代表性植物核心代码）

#### ① 雨竹 monstrain：季节枯萎 + 汲水复活 + 共生 spawner

`plants_legion.lua` 336行起。核心：pickable 6 天（`TUNING.TOTAL_DAY_TIME*6`），但季节变化强制干预：

```lua
pas.OnSeasonChange_monstrain = function(inst) --季节变化时
    if TheWorld.state.iswinter then
        inst.components.pickable:MakeBarren()
        return
    elseif TheWorld.state.issummer then
        local mo = TOOLS_P_L.CostMoisture(inst, inst.sivctls, nil, 10, false, nil)
        if mo == nil then --汲水失败，变成枯萎状态
            inst.components.pickable:MakeBarren()
            return
        else
            TOOLS_P_L.SpawnFxMoi(inst)
        end
    end
    if inst.components.pickable:IsBarren() then --判定一下，防止重置了生长进度
        inst.components.pickable:MakeEmpty()
    end
end
```

- 枯萎时 `Physics:SetActive(false)`（取消碰撞体积）、去 `barren` 标签拒绝施肥、`targettime=nil` 手动清掉 pickable 数据（注释：MakeBarren 不改这两个字段，只能手动改）
- 成长收获：

```lua
pas.OnPicked_monstrain = function (inst, picker, lootbase) --被采集时
    inst.AnimState:PlayAnimation("shake")
    inst.AnimState:PushAnimation("idle", true)
    pas.SetOnAnimOver_monstrain(inst) --动画播完才隐藏果实贴图
    local loot = {}
    local pos = inst:GetPosition()
    TOOLS_L.SpawnStackDrop("squamousfruit", 1, pos, nil, loot, { dropper = inst })
    TOOLS_L.SpawnStackDrop("monstrain_leaf", 1, pos, nil, loot, { dropper = inst })
    ...
```

- 共生：`childspawner.childname = "raindonate"`，夜晚（OnIsNight）停止产雨滴馈赠并召回
- 移植块茎 monstrain_wizen：`moisturedelta` 监听，湿度 >=95% 触发转正——`tree.components.pickable:MakeEmpty()` 后按季节设状态；3 天脱水 timer 变 spoiled_food

#### ② 三花丛 MakeBush 工厂：可循环浆果丛 + 武器彩蛋掉落

`plants_legion.lua` 700行 `pas.MakeBush(dd)` 工厂，数据表驱动。循环机制核心（官方 GetRegenTime 算法的 mod 复刻）：

```lua
pas.GetRegenTime = function(inst, time)
    local max_cycles = inst.components.pickable.max_cycles
    local cycles_left = inst.components.pickable.cycles_left or max_cycles
    local num_cycles_passed = math.max(0, max_cycles - cycles_left)
    return time
        + TUNING.BERRY_REGROW_INCREASE * num_cycles_passed
        + TUNING.TOTAL_DAY_TIME * math.random()
end
pas.GetRegenTime_bush = function(inst)
    return pas.GetRegenTime(inst, TUNING.TOTAL_DAY_TIME*6)
end
```

（采得越多再生越慢，BERRY_REGROW_INCREASE 递增——官方浆果丛经济模型）。蔷薇掉落函数摘录：

```lua
pas.SpawnLoot_rose = function(inst, picker, mustdrop)
    local rand = math.random()
    if math.random() < CONFIGS_LEGION.FLOWERWEAPONSCHANCE then --3%几率掉落剑
        pas.SpawnFlowerWeapon(inst, pos, picker, "rosorns")
    end
    if rand < 0.3 then --30%花瓣，65%树枝，5%蔷薇折枝
        TOOLS_L.SpawnStackDrop("petals", 1, pos, picker, nil, sets)
    elseif rand < 0.95 then
        TOOLS_L.SpawnStackDrop("twigs", 1, pos, picker, nil, sets)
    else
        TOOLS_L.SpawnStackDrop("cutted_rosebush", 1, pos, nil, nil, { dropper = inst })
    end
    TOOLS_L.PushLuckyEvent(inst) --幸运事件（与 mod 的幸运系统联动）
end
```

- 采集受伤判定：排除暗影仆从/盖娅/荆棘甲穿戴者/（神话 mod 联动 thorns_pill），蔷薇 3 点、夜玫瑰 6 点，受伤触发 "thorns" 事件 + 1% 台词彩蛋
- 挖起 OnFinished：枯萎时只掉 2 树枝；有果实时掉 product + dug_xxx + 武器
- 冬季停长：`MakeNoGrowInWinter(inst)`（夜玫瑰刻意不加——冬天照常结果）

#### ③ 颤栗树之心 shyerrygrow：五维培养 + 线路式子树生长

`scripts/components/shyerrygrow.lua`（组件 200 行内）+ `plants_legion.lua` 1712行。字段含义（代码注释原文）：

```lua
self.stage_max = 3    --最大生长阶段
self.growth_max = 48  --生长进度达到该值就进入下一阶段。48点最快需30天才能到最高阶段，80点则是最快50天
self.moisture_max = 500  --最大蓄水量
self.nutrient_max = 500  --最大蓄肥量
self.nutrient1 = 0 --当前肥量（加快再生频率）
self.nutrient2 = 0 --当前肥量（颤栗果积累更快）
self.nutrient3 = 0 --当前肥量（大树几率更高）
self.moisture = 0   --当前水量（再生数量更多）
```

- 子树按"线路"（linedata）生成：每条线一个随机角度 theta（±15° 抖动），沿线上 spawnRadius=2.5 生长点逐格长树，`badtile` 标记地皮不合法位置
- 大树几率 bigTreeChance = {0.3, 0.4, 0.5} 随阶段提高；fruitPoint=16 点果储结 1 果；消耗 costNutrient=4 / costMoisture=10
- 雨水事件 `OnIsRaining` 直接补 100 水；浇水分三档标签（SetTagMoisture 等）；shyerrycore 本体参数放宽（growth 80/水 1000/肥 1000）

#### ④ 培植盆 pot_whitewood：trader 收种收肥 + 同类升级 + 无限生长

`whitewoods.lua` 900行起。双通道交易：`potFerts`（肥料，含官方肥料+颤栗果酱 dish_shyerryjam）与 `potPlants`（种植物），AcceptTest 三态拒绝理由（NONEED 满肥 / WRONGITEM 非可种物）。生长时逐阶段耗肥：

```lua
local function PreGrow_pot(inst, stage, stagedata) --生长时消耗肥料
    local oldf = inst._fertility
    inst._fertility = oldf - (inst._magicgrow and 2 or 1) --魔法催熟会多消耗肥料
    if oldf > 0 and inst._fertility <= 0 then
        inst:RemoveTag("plant") --不能催熟了，不然会浪费催熟次数
        SetSoilSymbol_pot(inst, true)
        inst.components.growable:StopGrowing() --没肥料了，得停止生长
    end
end
```

- 升级链：同类升级要求新种 `pri` 更高（蘑菇帽>孢子>蘑菇本体>蘑菇皮），升级保留已生长时间（`inst._growdt` 继承）；`nomaxlvl=true` 的无限种可用 `potUpdater` 物品升级为无限生长
- 蘑菇 4 阶段产孢子：`periodicspawner` 动态加组件（红/绿/蓝 60 秒周期，月菇 spore_moon 25% 概率 `_alwaysinstantpops`）；睡眠停、醒重启
- 挖起还原：`GetFruits_pot` 先结算果实再删

#### ⑤ 异种作物 pineananas（CROPS_DATA_LEGION 数据表驱动）

`datafix_legion.lua` 2005行。生长阶段数据（4 阶段：发芽→中→熟→过熟），每阶段可独立配动画数组（随机帧）、枯萎掉落物（witheredprefab）与开花标记：

```lua
_G.CROPS_DATA_LEGION.pineananas = {
    growthmults = { 0.8, 1.2, 1.2, 0 }, --x夏秋x
    regrowstage = 2,
    bank = "crop_legion_pineananas", build = "crop_legion_pineananas",
    leveldata = {
        { anim = "level3", time = time_day1,      deadanim = "dead1", witheredprefab = nil },
        { anim = "level4", time = time_crop*0.45, deadanim = "dead2", witheredprefab = {"log"} },
        { anim = "level5", time = time_crop*0.55, deadanim = "dead2", witheredprefab = {"log", "cutgrass"}, bloom = true },
        { anim = { "level6_1", "level6_2", "level6_3" }, time = time_ripe, deadanim = "dead2", witheredprefab = {"log", "cutgrass"} }
    },
    cluster_size = { 1, 1.5 },
    lootothers = { --随机额外掉落
        { israndom=true, factor=0.05, name="pinecone", name_rot="pinecone" },
        { israndom=false, factor=0.0625, name="pinecone", name_rot="pinecone" }
    }
}
```

（time_crop=12天；time_ripe=6天过熟；枯萎掉木头+草——凤梨是"树系"作物。）

#### ⑥ 巨食草双形态（plants<->creature 转换）

`farm_plants_legion.lua` 1260行 `fn_switch`：生物形态与植物形态互换时，容器内容、cluster 数据、皮肤（skinedlegion）全部继承；植物形态是 `container`（4x4 UI `ui_nepenthes_l_4x4`），生物形态用 `modelegion` 组件驱动引诱（10.1s 周期）/吞食（4.1s）双 task；cluster 数值线性缩放吞食半径 2->6、数量 1->10、消化 33s->3s。消化名单：不吃自己的异种（seeds_plantmeat_l）、植物肉本体、鱼骨勋章、昆虫壳等。

### 6.3 特色岛屿细节（雨硫岛 L_RainIsland_Main 及其余静态布局）

#### 6.3.1 雨硫岛任务构成（scripts/map/tasks/legionland.lua）

```lua
AddTask("L_RainIsland_Main", {
    locks = {}, keys_given = {},
    region_id = "island_l_rain",
    level_set_piece_blocker = true,          --阻止其它 set_piece 落到岛上
    room_tags = { "RoadPoison", "nohasslers", "not_mainland" }, --nohasslers：熊大巨鹿不以岛上玩家为目标
    room_choices = {
        ["L_HotSpringPot"] = 1,
        ["L_SmallHotSpringPot"] = function() return math.random(1, 2) end,
        ["L_SpringBeach"] = 1
    },
    room_bg = WORLD_TILES.MONKEY_GROUND,     --月岛沙滩地皮打底
    background_room = "Empty_Cove",          --官方"空湾"房间：把岛围成被水环绕的海湾
    cove_room_name = "Empty_Cove",
    cove_room_chance = 1,
    cove_room_max_edges = 2,
    colour = {r=0.6,g=0.6,b=0.0,a=1}
})
```

三个房间的具体构成（rooms_prayforrain.lua）：

| 房间 | 地皮 | 固定布局 | countprefabs | distributeprefabs |
|---|---|---|---|---|
| L_HotSpringPot | MONKEY_GROUND | L_HotSpring（pond_l_smoke 温泉池） | 风滚草生成器1、空瓶2、硝石5、蝙蝠洞1-2、烧焦骷髅4-8、绿洲仙人掌3-5 | 硝石岩2.0、fern_l 1.5、枯萎花0.5、棕榈树（高/中/矮） |
| L_SmallHotSpringPot | MONKEY_GROUND | L_SmallHotSpring（pond_l_smoke_s 小温泉） | 风滚草1、空瓶1、硝石3、烧焦骷髅3-6、仙人掌1-3 | 同上（密度减半） |
| L_SpringBeach | SPRINGBEACH_L_NOISE | L_BeWithFirenettle（3火荨麻+烧焦骷髅+flotationcushion 冲浪浮板） | 海星陷阱4-8、messagebottle 1 | fern_l 2.0、枯萎花0.5、死海骨1.0、漂流木（小1/小2/高）2.5/2.5/3.0 |

- 温泉海滩是"沙漠绿洲"要素的海岛化：仙人掌、烧焦骷髅、空瓶、海星陷阱、漂流木
- 岛屿视觉：MONKEY_GROUND 月岛沙滩地皮 + SPRINGBEACH_L_NOISE 混合地皮（<0.1 不可通行礁石、<0.4 泥土、其余卵石滩）+ 温泉池特效
- 雨竹区域是独立房间（MonsteraPatch，MARSH 沼泽地皮）通过 `AddTaskPreInit("Squeltch")` 注入主大陆沼泽，不在雨岛上

#### 6.3.2 各静态布局（Tiled 格式）对象构成一览

| 布局 | 位置/挂载 | 主要对象 |
|---|---|---|
| RoseGarden 玫瑰园 | 地表 set_piece（16 任务随机） | 5 rosebush + 大理石柱 |
| LilyPond 荷塘 | 地表 set_piece | 5 lilybush + 4 细枝树 + 3 胡萝卜 + pond 池塘（荷塘水面） |
| OrchidForest 兰草森林 | 地表 set_piece | 26 evergreen + 5 orchidbush |
| OrchidGrave 兰草之墓 | 地表 set_piece | 1 orchidbush + 1 gravestone（_zh 版墓碑文字） |
| HelperCemetery 协助者墓园 | BigBatCave 蝙蝠地形 room 中心 | 18 gravestone + 8 marsh_tree + 8 flower_evil + 3 marsh_bush + scarecrow 稻草人 + reskin_tool + mandrake_planted 曼德拉草 + livingtree 活树 |
| MoonDungeon 月的地下城 | MoonIsland_Mine 月岛矿区 room 中心 | 12 rock_ice + moondungeon（地下城入口） |
| TourmalineBase 电气矿区 | Forest hunters 月石森林 room 中心 | elecourmaline 电气母晶（雷系资源） |
| SivingCenter 子圭之源 | GreenForest 绿菇森林 room 中心 | siving_thetree 子圭神木岩 |
| SpartacussGrave 斯巴达克斯之墓 | cave_default（洞穴，6 个官方任务随机） | gravestone + agronssword 阿格隆之剑（墓中剑） |
| L_HotSpring / L_SmallHotSpring | 雨岛房间中心 | pond_l_smoke 温泉池特效 |
| L_BeWithFirenettle | 雨岛海滩房间中心 | 3 weed_firenettle + scorched_skeleton + flotationcushion |

（type 字段为 prefab 名、x/y 为像素坐标；BG_TILES 全 0 表示地皮由宿主房间的 value 决定。）

#### 6.3.3 海洋处理

- mod 没有海面（乘船）内容；雨硫岛通过官方海湾机制实现"四面环水"：`background_room = "Empty_Cove"` + `cove_room_chance = 1` + `cove_room_max_edges = 2`——官方任务系统自动在岛屿边缘生成 Empty_Cove 水域房间把岛包住
- `level_set_piece_blocker = true` 防止官方 set_piece 生成在岛上
- 荷塘 LilyPond 的水面：替换官方 `levels/tiles/swamp.tex + water_medium.xml` 地皮贴图做浅色水面（见 6.5 美术分析），房间内固定 pond 池塘
- 月岛矿区（MoonIsland_Mine 官方任务）被注入月地下城房间，洞穴（cave_default）注入斯巴达克斯之墓

### 6.4 特色地形补充（3.1.1-3.1.5 之外）

- **NOISE 混合地皮全量**：`SPRINGBEACH_L_NOISE`（modworldgenmain.lua 21行）：`noise<0.1 -> IMPASSABLE`（岛缘礁石）、`<0.4 -> DIRT`、其余 `PEBBLEBEACH` 卵石滩。官方 `METEORMINE_NOISE` 也被 mod 复用（月地下城房间 value）
- **房间地皮对照**（每种特色区域绑定一种官方地皮）：玫瑰 DECIDUOUS、蹄莲 GRASS、兰草 FOREST、雨竹 MARSH、电气 ROCKY、颤栗树林 DIRT_NOISE（+sandstorm 标签才能出沙暴！）、子圭 FUNGUSGREEN（+Hutch_Fishbowl）、月地下城 METEORMINE_NOISE、协助者墓园 FOREST（+Mist/Hutch_Fishbowl）、雨岛 MONKEY_GROUND
- **levels/textures 噪声贴图清单**（8 张，DXT1）：`Ground_lilypond2`（荷塘混合）、`Ground_bog2`（雨岛泥沼）、`ground_ruins_slab` / `ground_ruins_slab_blue`（遗迹石板，两色板）、`mini_*` 4 张小地图噪声。均为 512x512、15-20 mip
- **levels/tiles**：`swamp.tex + swamp.xml`、`water_medium.tex + water_medium.xml` 是替换官方 DLC0003 地皮（水面效果），XML 引用 `data/DLC0003/levels/tiles/swamp.tex`
- **地皮机制要点**：noise 贴图（红/青通道对，见 6.5）决定 tile 过渡的混合权重，混合地皮每格按 NoiseTileFunctions 实时选 tile——这是"岛屿从卵石滩过渡到礁石再沉入水"渐变效果的实现基础

### 6.5 美术小节（tex 解码分析）

方法：anim zip 内 `atlas-0.tex` 与 levels 下均为 KTEX（KTEX 魔数 + u32 format + N×10B mip 头 + 连续块数据）；低 16 位 `0x2220`=DXT5、`0x2200`=DXT1（工具：`E:\神秘复苏\tools\dst_tex_analyze.py` 已破解格式，PIL 统计色彩）。

#### 6.5.1 植物画风：深底色 + 高占比黑色描边

统一特征：**强黑色轮廓 + 暗色调铺底**（DST 传统描边风格），主色板第一色全是 #000000（占比 29%~66%），不透明像素中暗像素（RGB<80）占 52%~84%。单张图集即一个 build 的完整状态集合（grow/dead/摘后等状态都排在一张 2048 图集里，12 个 mip）。

| 植物 | 图集 | 格式/mip | 透明 | 饱和 | 明度 | 主色系 |
|---|---|---|---|---|---|---|
| 蔷薇花丛 rosebush | 2048² | DXT5/12 | 82% | 0.27 | 0.18 | 灰绿 #445544/#557766 |
| 蹄莲花丛 lilybush | 2048² | DXT5/12 | 86% | 0.34 | 0.19 | 深绿 #446644/#224422 |
| 兰草花丛 orchidbush | 2048² | DXT5/12 | 94% | 0.25 | 0.12 | 蓝紫 #222233/#444477（含紫色花簇） |
| 夜玫瑰 nightrosebush | 2048×1024 | DXT5/12 | 83% | 0.31 | 0.13 | 暗紫 #112233/#333355 |
| 雨竹 monstrain | 512² | DXT5/10 | 71% | 0.42 | 0.18 | 墨绿 #335544/#113322（饱和最高） |
| 颤栗花/树 shyerrybush | 2048×1024 | DXT5/12 | 74% | 0.39 | 0.30 | 橙棕 #CC8833/#AA6611（颤栗果橙） |
| 白桦树 mat_whitewood | 1024×512 | DXT5/11 | 63% | 0.12 | 0.68 | 米白 #EEEEDD 46% + 黑描边 19% |
| 耐酸蕨 fern_l | 256² | DXT5/9 | 63% | 0.17 | 0.21 | 灰绿 #667777/#889988 |
| 冰皂草 build pot_whitewood2 | 1024² | DXT5/11 | 72% | 0.26 | 0.29 | 冰蓝紫 #556688/#6699AA + 白 |
| 培植盆 pot_whitewood | 2048×1024 | DXT5/12 | 71% | 0.31 | 0.29 | 紫水晶 #663388/#552277 |
| 异种凤梨 crop_legion_pineananas | 1024² | DXT5/11 | 80% | 0.28 | 0.15 | 深绿 #557766 |
| 异种荧光 crop_legion_lightbulb | 1024² | DXT5/11 | 84% | 0.21 | 0.35 | 灰白 #BBBBBB/#FFFFFF（荧光系） |

画风归纳：
- **三花丛**（蔷薇/蹄莲/兰草）：低明度深绿底 + 亮色花点缀（蔷薇粉、蹄莲白、兰草紫蓝），形态是官方 berrybush2 底骨架（bank 复用官方猪村浆果丛动画）+ 自绘花簇 build 覆盖符号（SetBerries_bush 用 OverrideSymbol bush_berry_build 切换 3 档果实贴图）
- **白桦树是风格异类**：米白 #EEEEDD 占 46%、明度 0.68、饱和仅 0.12——极简高亮白桦皮配色 + 黑描边，与暗色植物形成冷暖对比（雨岛白桦材质 theme）
- **颤栗树橙棕**（#CC8833/#AA6611）与**夜玫瑰暗紫**（#333355）是最具辨识度的两个色系
- 打蜡系列（waxed）复用同一 build，状态差异靠动画帧与 build 切换表达

#### 6.5.2 岛屿/地形纹理画风

| 文件 | 格式 | 尺寸 | 透明 | 饱和 | 明度 | 说明 |
|---|---|---|---|---|---|---|
| levels/tiles/swamp.tex | DXT5 | 1024² | 69% | 0.02 | 0.95 | 几乎纯白（#FFFFFF 91%）水面高光替换 |
| levels/tiles/water_medium.tex | DXT5 | 2048×1024 | 77% | 0.02 | 0.86 | 浅灰 #DDDDDD 半透明水面 |
| Ground_lilypond2（荷塘噪声） | DXT1 | 512²/15mip | 22% | 0.47 | 0.48 | 深蓝绿 #112233/#223344 + 少量红 #664444 |
| Ground_bog2（雨岛泥沼噪声） | DXT1 | 512²/16mip | 7% | 0.56 | 0.69 | 红/青通道对 #AA5555/#55AAAA |
| ground_ruins_slab / _blue | DXT1 | 512²/20mip | 10% | 0.63-0.64 | 0.62-0.64 | 红青通道石板噪声（双色板） |
| mini_bog_noise / mini_lilypond_noise | DXT1 | 256-512² | 6-12% | 0.56-0.59 | 0.71-0.75 | 小地图同款噪声 |

归纳：
- **水面地皮替换是"极简高亮"路线**：swamp/water_medium 替换图饱和 0.02、明度 0.86-0.95，几乎纯白/浅灰——模拟水面高光与半透明浅色水面，靠 alpha（69-77% 透明）透出底层 tile
- **噪声贴图是"红/青通道对"编码**：Ground_bog2、ruins_slab、mini_* 主色集中在 #AA5555（红）与 #55AAAA（青），饱和 0.56-0.64——DST 噪声图用红青双通道存两组混合权重（每通道驱动一条 tile 过渡曲线），这是混合地皮渐变的核心数据
- 荷塘噪声偏深蓝绿（#112233/#223344），是唯一带"内容色"的噪声（荷塘主题），红色通道稀疏点缀（#664444 荷花？）
- **atlas 组织规律**：`images/map_icons/*.xml` 单元素全幅 UV（u1=0.0078 u2=0.9922 一个 Element 占满整图）；`images/inventoryimages/` 378 对独立 tex+xml（一对一文件，不合并大图集）；`levels/tiles/swamp.xml` 的 Element 名为两位 tile 编号（"28"/"47"/"33"…），UV 步长 0.125=64px/512px 标准 tile 网格（8 列×6 行）

### 6.6 专题速查

- 植物文件 → 行数：plants_legion.lua 3750（雨竹 336 / 三花丛 700-1260 / 颤栗树 1350-1915 / 蕨+冰皂草 1917-1960 / siving_thetree 2693）、farm_plants_legion.lua 2025（巨食草 1414 / 腐木 1757 / 荧光 1946）、whitewoods.lua（培植盆 600-1100 / 白桦树 399）、datafix_legion.lua CROPS_DATA_LEGION 1861-2110
- 地图数据：modworldgenmain.lua 173（tile/布局/task 注册）、scripts/map/rooms/forest/*.lua 5 个房间文件、scripts/map/tasks/legionland.lua 雨岛、scripts/map/static_layouts/ 15 个 Tiled 布局
- 组件：shyerrygrow.lua（颤栗树五维）、perennialcrop2.lua（异种作物，1379行）、plantablelegion.lua（种植物）、modelegion.lua（巨食草双形态）
