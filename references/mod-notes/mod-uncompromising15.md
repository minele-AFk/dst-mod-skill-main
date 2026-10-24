# Uncompromising Mode 1.5.4.4 全代码研究笔记

> 研究日期：2026-08-11
> Mod 路径：`E:\神秘复苏\饥荒大型mod\2039181790\`（英文原版，完全明文无加密，约 2596 个文件）
> 用途：DST mod 开发技能文档的原始材料

---

## 1. Mod 全貌

### 1.1 基本信息

| 项目 | 内容 |
|---|---|
| 名称 | Uncompromising Mode（不妥协模式 / 硬核模式） |
| 版本 | 1.5.4.4 |
| 作者 | The Uncomp Dev Team（昵称 SCRIMBLES，代码注释里常自称） |
| API 版本 | api_version = 10，dst_compatible = true，all_clients_require_mod = true，priority = -10 |
| 规模 | 约 2596 个文件；`scripts/prefabs/` 下 429 个 prefab 文件；`scripts/components/` 58 个组件文件 |
| 定位 | 全面增强 DST 难度的硬核生存大改：新角色、新生物、新 Boss、新地皮、新天气系统、全面数值重做 |

### 1.2 完整目录树

```
2039181790/
├── modinfo.lua              (1454行) 配置文件体系（约100+配置项）
├── modmain.lua              (329行)  服务器主入口
├── modclientmain.lua        (137行)  客户端入口（只加载角色占位）
├── modworldgenmain.lua      (670行)  世界生成入口（地皮/任务/房间/静态布局）
├── tile_adder.lua           (230行)  新地皮添加工具库
├── skins_api.lua            (301行)  可皮肤角色 API
├── uncompskins_api.lua      (345行)  自定义皮肤 API
├── anim/                    (581个zip) 动画资源
├── bigportraits/            角色大头像
├── fx/                      特效纹理
├── images/                  avatars, colour_cubes, crafting_menu_avatars,
│                            inventoryimages, map_icons, saveslot_portraits,
│                            selectscreen_portraits, wet_meter
├── init/                    初始化模块（按主题拆分）
│   ├── init_assets.lua      (2231行) 全部资产注册 + RegisterInventoryItemAtlas 批量注册
│   ├── init_postinit.lua    (527行)  postinit 清单集中管理（核心组织文件）
│   ├── init_tuning.lua      TUNING.DSTU 配置映射
│   ├── init_recipes.lua     配方修改
│   ├── init_actions.lua     (402行) 新动作 + 原版动作包装
│   ├── init_containers.lua  (654行) 新容器 UI + 原版容器参数覆写
│   ├── init_durability.lua  (188行) 服装耐久/防雨/保温随耐久递减
│   ├── init_ratraid.lua     (181行) 鼠灾系统接线
│   ├── init_vetcurse.lua    (44行)  老手诅咒系统
│   ├── init_bosshealth.lua  (49行)  Boss血量乘数
│   ├── init_foodregen.lua   (86行)  食物改回复机制
│   ├── init_gamemodes/init_uncompromising_mode.lua  (218行) modimport 总序列
│   ├── init_character_changes/  19个文件（每人一个角色改动文件）
│   ├── init_creatures/          8个文件（硬核怪物/击退/暗影）
│   ├── init_food/               8个文件（烹饪/稀有食物/怪物肉）
│   └── init_weather/            10个文件（酸雨/烟雾/暴雪/花粉热/过热/龙蝇诱饵）
├── levels/
│   ├── textures/1/          noise_hoodedmoss.tex 等噪声纹理
│   └── tiles/1/             hoodedmoss.xml, um_floodwater.xml 等图集
├── postinit/                补丁目录（与 init 清单一一对应）
│   ├── components/          (56+个文件：health, combat, inventory, weapon...)
│   ├── prefabs/             (152+个文件)
│   ├── stategraphs/         (SGxxx.lua)
│   ├── brains/              (xxxbrain.lua)
│   ├── any.lua              (309行) 所有 prefab 通用后处理
│   ├── player.lua           (311行) 玩家后处理
│   └── widgets/             客户端 HUD widget 补丁
├── scripts/
│   ├── uncompromising_prefabs.lua   (471行) 约400个prefab名的纯列表
│   ├── um_preparedfoods.lua         (687行) 新烹饪配方表
│   ├── um_spicedfoods.lua           (15行)  新调味料
│   ├── um_pocketdimensioncontainers.lua  次元容器定义追加
│   ├── um_wx78_moduledefs.lua       (1349行) WX-78 新模块定义
│   ├── uncompromising_writeables.lua     可书写物种类扩展
│   ├── uncompromisingcommands.lua  (263行) 控制台命令
│   ├── messagebottletreasures_um.lu (597行) 漂流瓶宝藏表
│   ├── speech_wathom.lua / speech_winky.lua / speech_wixie.lua  角色台词
│   ├── behaviours/                 新行为（AI）
│   ├── brains/                     新大脑（AI）
│   ├── components/         (58个) 新组件（um_heatwaves, um_stormspawner, ratcheck...）
│   ├── descriptors/        components 描述文件（descriptors.xxx 客户端注册）
│   ├── map/
│   │   ├── rooms/forest/   新房间（gianttreesrooms, ratking, sunkdecidrooms...）
│   │   ├── rooms/caves/    洞穴房间
│   │   ├── static_layouts/ 静态布局（hooded_town, ricepatch, ratking...）
│   │   └── tasks/          新任务（gianttrees, newswamp, ratacombs, sunkendecid）
│   ├── prefabs/            (429个) 新 prefab
│   ├── screens/            新屏幕
│   ├── stategraphs/        新状态机
│   ├── tools/              um_commonfns.lua, upvaluehacker.lua
│   └── widgets/            vetcursewidget.lua 等自定义 HUD widget
├── sound/                  UCSounds.fev, UMMusic.fev, stmpwyfs.fev 等
├── widgets/                zero_insanity_overlay.lua 等
├── wixie_postinit/         角色 wixie 专属补丁目录（同 postinit 结构）
│   ├── components/  prefabs/  stategraphs/  widgets/
└── ~Tertiary/Soundbanks/stmpwyfs/
```

### 1.3 特色系统清单（核心卖点）

1. **3 个新角色**：Wathom（不死狂战士）、Winky（鼠王女孩）、Wixie（弹弓不良少女，可选配置）
2. **新生物群系/地皮**：HOODEDFOREST（兜帽森林）、UM_FLOODWATER（洪水）、HOODED_ANCIENT 等
3. **新 Boss**：Hooded Widow、Mock Dragonfly（赝品龙蝇）、Moonmaw、Rat King、无底洞 Pawn 等
4. **鼠灾系统**（ratcheck 组件）：开箱子/冰箱触发鼠群袭击
5. **天气环境威胁**：酸雨、烟霾（smog 咳嗽）、暴风雪、热浪、花粉热（hayfever）、龙蝇诱饵
6. **老手诅咒**（Veteran's Curse）：死亡惩罚系统，按角色定制 DEBUFF + HUD 骷髅图标
7. **老兵试炼**（feats of strength）：Boss 强化挑战
8. **食物重做**：食物不再直接回血回理智，改为持续恢复 debuff；怪物肉分级；新烹饪配方几十个
9. **Boss 血量可配置**：所有 Boss 血量乘数
10. **新装备系统**：防护服耐久衰减（雨衣/隔热服随耐久降效）、玻璃锁甲、瘟疫面具
11. **皮肤系统**：自制皮肤 API（uncompskins_api.lua）+ 可皮肤角色（skins_api.lua）
12. **WX-78 模块扩展**：1349 行新模块定义
13. **Rat 招募系统**：Winky 用哨笛招募老鼠作战
14. **口袋次元容器**：skullchest / winkyburrow 共享库存容器
15. **钢琴谜题**、**寻宝潜水钟**等世界内容

---

## 2. 框架架构

### 2.1 四文件分工

| 文件 | 职责 |
|---|---|
| modmain.lua | 服务器入口：加载 prefab 清单、资产、RPC 处理器、角色注册、皮肤初始化、技能树 |
| modclientmain.lua | 客户端入口：只加载角色占位 prefab（`winky_none` 等）、角色文案、客户端 RPC |
| modworldgenmain.lua | 世界生成：新地皮注册、任务/房间/静态布局挂载、新关卡定义（UNCOMPROMISING 模式） |
| tile_adder.lua | 地皮注册工具库（被 modworldgenmain 调用，也是独立通用模块） |

### 2.2 modmain.lua 入口骨架（原文）

```lua
local require = GLOBAL.require

require "um_pocketdimensioncontainers"

GLOBAL.UMCommonFns = require("tools/um_commonfns")

PrefabFiles = require("uncompromising_prefabs")
PreloadAssets = {Asset("IMAGE", "images/UM_tip_icon.tex"), Asset("ATLAS", "images/UM_tip_icon.xml")}
ReloadPreloadAssets()
-- Start the game mode
SignFiles = require("uncompromising_writeables")

modimport("init/init_gamemodes/init_uncompromising_mode")
modimport("init/init_descriptions/announcestrings.lua")
modimport("init/init_wathom")

if GetModConfigData("funny rat") then
    AddModCharacter("winky", "FEMALE")
    GLOBAL.TUNING.WINKY_HEALTH = 175
    ...
end

GLOBAL.FUELTYPE.BATTERYPOWER = "BATTERYPOWER"
GLOBAL.FUELTYPE.SALT = "SALT"
GLOBAL.FUELTYPE.EYE = "EYE"
GLOBAL.FUELTYPE.SLUDGE = "SLUDGE"
GLOBAL.UPGRADETYPES.ELECTRICAL = "ELECTRICAL"
GLOBAL.UPGRADETYPES.SLUDGE_CORK = "SLUDGE_CORK"
GLOBAL.MATERIALS.SLUDGE = "sludge"
GLOBAL.MATERIALS.COPPER = "copper"
```
（出处：`modmain.lua` 第 1-33 行）

要点：
- **PrefabFiles 用 require 返回的表**，而不是内联列表——把 400 个 prefab 名拆到独立文件 `uncompromising_prefabs.lua`，主文件干净。
- **扩展全局枚举常量**（FUELTYPE/UPGRADETYPES/MATERIALS）直接赋值新成员，后续新物品可以引用。
- **modimport 串行加载**，一个入口文件 init_uncompromising_mode.lua 控制全部加载顺序。
- `GLOBAL.TUNING.DSTU.MODROOT = MODROOT` 把 mod 根路径存进 TUNING 供运行时定位文件。
- 角色注册是**条件注册**：`if GetModConfigData("funny rat") then AddModCharacter("winky", "FEMALE")`——配置文件关掉就没有这个角色。

### 2.3 加载序列 init_uncompromising_mode.lua（原文骨架）

```lua
modimport("init/init_util")
modimport("init/init_assets")
modimport("init/init_widgets")
modimport("init/minimap_icons")
modimport("init/init_dynlayout")
modimport("init/init_dragonfly_bait")
modimport("init/init_names")
modimport("init/init_bonusdescriptors")
modimport("init/init_descriptions/init_default_objects")
... （共约 50 个 modimport）
```
（出处：`init/init_gamemodes/init_uncompromising_mode.lua` 第 1-218 行）

加载顺序设计：
```
工具/资产 → widget → 图标 → 命名/描述 → TUNING 数值 → postinit 清单 → 字符串 →
动作 → 容器 → 电池 → RPC 追踪 → 生物 → 生成充电 → 命令 → 食物 → 诅咒 → Boss血量 →
配方 → 鼠灾 → 击退 → 暗影 → 天气 → 耐久 → 角色改动 → 回血 → 加载提示
```

### 2.4 init_postinit.lua —— postinit 集中管理（核心组织模式，原文）

```lua
local component_post = {
    "groundpounder", "propagator", "moisture", "weapon", "kramped", "explosiveresist",
    "wildfires", "hounded", "burnable", "combat", "combat_replica", "health", ...
}  -- 56 项

local prefab_post = { "deerclops", "bearger", "dragonfly", "moose", "beequeen", ... }  -- 152 项

local stategraph_post = { "wilson", "beefalo", "pigman", "spider", ... }

local class_post = { "braincommon", "playercontroller", ... }

local brain_post = { "deerclops", "moose", "pigking", ... }

-- 条件插入
if GetModConfigData("harder_deerclops") then
    table.insert(stategraph_post, "deerclops")
    table.insert(prefab_post, "deerclops")
end
...
-- 批量加载
for _, v in pairs(component_post) do modimport("postinit/components/" .. v) end
for _, v in pairs(prefab_post) do modimport("postinit/prefabs/" .. v) end
for _, v in pairs(stategraph_post) do modimport("postinit/stategraphs/SG" .. v) end
for _, v in pairs(brain_post) do modimport("postinit/brains/" .. v .. "brain") end
for _, v in pairs(class_post) do modimport("postinit/" .. v) end
```
（出处：`init/init_postinit.lua` 第 1-527 行）

关键设计：
- **清单表 + 条件插入 + 循环 modimport**：要加一个补丁 = 在对应清单加一行 + 建一个文件。文件与清单一一对应，杜绝散落的 AddPrefabPostInit。
- 配置项作为开关控制哪些补丁生效（harder_deerclops 等）。
- postinit 目录结构镜像清单：`postinit/components/`、`postinit/prefabs/`、`postinit/stategraphs/SG*.lua`、`postinit/brains/*brain.lua`。
- wixie 角色专属补丁放独立的 `wixie_postinit/` 目录，同样镜像结构。

### 2.5 modclientmain.lua —— 客户端入口（原文）

```lua
PrefabFiles = {"winky_none", "wathom_none", "wixie_none"}  -- 客户端只加载占位prefab

GLOBAL.STRINGS.NAMES.WINKY = "Winky"
...
TUNING.WINKY_HEALTH = 175
TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT.WIXIE = {"slingshot", ...}
AddModCharacter("winky", "FEMALE")
```
（出处：`modclientmain.lua` 全文 137 行）

要点：
- 客户端不需要任何实体逻辑，只加载 `xxx_none`（幽灵占位）、角色三围数值、起始物品、STRINGS。
- 角色三围在**两端各定义一次**（modmain 和 modclientmain 都设 TUNING），保证客户端显示正确。

### 2.6 modworldgenmain.lua 入口骨架（原文摘选）

```lua
-- 新地皮注册（见 3.1 节完整代码）
AddTile("HOODEDFOREST", "LAND", { ground_name = "hoodedmoss", old_static_id = 102 },
    { name = "hoodedmoss.tex", atlas = "hoodedmoss.xml", noise_texture = "noise_hoodedmoss.tex",
      runsound = "dontstarve/movement/walk_grass", ... },
    { name = "hoodedmoss.tex", atlas = "hoodedmoss.xml", noise_texture = "mini_noise_hoodedmoss.tex" },
    { name = "hoodedmoss", anim = "hoodedmoss", bank_build = "hfturf" })
ChangeTileRenderOrder(GLOBAL.WORLD_TILES.HOODEDFOREST, GLOBAL.WORLD_TILES.DIRT)

-- 新任务挂载
AddTaskSetPreInitAny(...)
Layouts["hooded_town"] = StaticLayout.Get("map/static_layouts/hooded_town")

-- 新关卡（新的世界生成模式）
AddLevel(GLOBAL.LEVELTYPE.SURVIVAL, { id = "UNCOMPROMISING", location = "forest", version = 4, ... })

-- 扩展故事生成系统
AddGlobalClassPostConstruct("map/storygen", "Story", function(self)
    self.map_tags.Tag[v] = function(tagdata) return "TAG", v end
end)

-- 新锁/钥匙
LOCKS_KEYS 扩展：KEYS["RICE"] = keycount + 1
```
（出处：`modworldgenmain.lua` 全文 670 行）

---

## 3. 关键设计模式（代码原样 + 出处）

### 3.1 新地皮/地形全流程（tile_adder.lua + levels/ + modworldgenmain.lua）

这是整个 mod 最值得学的部分。分四步：

**第一步：AddTile 注册工具**（出处：`tile_adder.lua` 全文 230 行，核心函数）

```lua
function AddTile(id, numerical_id, name, specs, minispecs, isflooring)
    if type(numerical_id) == "string" then
        -- 处理 "LAND"/"UNDERGROUND"/"OCEAN" 类型名
        ...
    end
    -- 检查 id 合法性
    validate_ground_numerical_id(GROUND[id], numerical_id)

    GROUND[id] = numerical_id
    GROUND_NAMES[numerical_id] = name
    GROUND_FLOORING[numerical_id] = isflooring

    local real_specs = specs
    table.insert(tiledefs.ground, {GROUND[id], real_specs})

    -- 注册资产
    AddAssets({
        Asset("IMAGE", GroundNoise(...)),
        Asset("IMAGE", GroundImage(name)),
        Asset("FILE", GroundAtlas(name)),
    })

    -- 小地图渲染层
    AddPrefabPostInit("minimap", function(minimap)
        MapLayerManager:CreateRenderLayer(GROUND[id], atlas, image, noise)
    end)
end
```

具体调用形态（6 个参数：id, 类型, ground_name 表, 地表规格, 小地图规格, turf 定义；出处：`modworldgenmain.lua` 第 1-60 行）：

```lua
AddTile("HOODEDFOREST", "LAND", { ground_name = "hoodedmoss", old_static_id = 102 },
    {   -- 地表规格
        name = "hoodedmoss.tex",
        atlas = "hoodedmoss.xml",
        noise_texture = "noise_hoodedmoss.tex",
        runsound = "dontstarve/movement/walk_grass",
        ...(colors = GROUND_OCEAN_COLOR 等)
    },
    {   -- 小地图规格
        name = "hoodedmoss.tex",
        atlas = "hoodedmoss.xml",
        noise_texture = "mini_noise_hoodedmoss.tex",
    },
    {   -- turf 定义（被挖起后的地皮物品动画）
        name = "hoodedmoss",
        anim = "hoodedmoss",
        bank_build = "hfturf",
    })
```

**第二步：levels/ 下的 atlas 文件**（出处：`levels/tiles/hoodedmoss.xml`）

```xml
<Atlas>
    <Texture filename="data/levels/tiles/deciduous.tex" />
    <Elements>
        <Element name="08" u1="0.00390625" u2="0.12890625" v1="0.73828125" v2="0.86328125" variant="" />
        ...
    </Elements>
</Atlas>
```

> **关键技术点：新地皮可以复用原版纹理图集！** hoodedmoss.xml 直接引用 `data/levels/tiles/deciduous.tex`（常青林地皮纹理），um_floodwater.xml 引用 `river.tex`。你只需要新写一个 XML 定义元素映射，无需新画纹理。

**第三步：世界生成挂载**（出处：`modworldgenmain.lua`）

```lua
-- 任务（包含新地皮作为 room_bg）
AddTask("GiantTrees", {
    locks = {LOCKS.ADVANCED_COMBAT, LOCKS.MONSTERS_DEFEATED, LOCKS.TIER5},
    keys_given = {KEYS.HF},
    room_choices = {["GiantTrees"] = 1, ["AphidLand"] = function() return math.random(0,1) end},
    room_bg = WORLD_TILES.HOODEDFOREST,
    background_room = "BGGiantTrees",
    colour = {r=.1, g=.1, b=.1, a=1},
})
```
（出处：`scripts/map/tasks/gianttrees.lua` 全文 50 行）

```lua
-- 房间注册（countprefabs / countstaticlayouts 控制生成量）
AddRoomPreInit("GiantTrees", { countprefabs = {...}, countstaticlayouts = {...} })
```
（出处：`modworldgenmain.lua`）

```lua
-- 静态布局挂载（Tiled 工具导出的 json→lua 格式）
Layouts["hooded_town"] = StaticLayout.Get("map/static_layouts/hooded_town")
```
（出处：`modworldgenmain.lua`）

**第四步：可采集地皮（turf）物品**。地皮被挖起后要对应一个 turf prefab：

```lua
-- turf_hoodedmoss 等 turf prefab 在 scripts/prefabs/ 下
-- 纹理引用：images/inventoryimages/turf_hoodedmoss.xml
```
（出处：`init/init_assets.lua` 的 `turf_hoodedmoss` / `turf_ancienthoodedturf` 注册）

**附加：ChangeTileRenderOrder**（出处：`tile_adder.lua`）

```lua
function ChangeTileTypeRenderOrder(tiletypeid, targettiletypeid, moveafter)
    -- 在 tiledefs.ground 中把 tiletypeid 移到 targettiletypeid 前/后
    -- 控制渲染层级：新地皮画在旧地皮上面还是下面
end
```

### 3.2 原版改造模式：组件包装（AddComponentPostInit + 闭包保存原函数）

这是全 mod 最常用的模式，出现几百次。标准三段式：

```lua
local env = env
GLOBAL.setfenv(1, GLOBAL)

env.AddComponentPostInit("health", function(self)
    if not TheWorld.ismastersim then return end

    local _DoDelta = self.DoDelta
    function self:DoDelta(amount, overtime, cause, ignore_invincible, afflicter, ignore_absorb, ...)
        if MayKill(self, amount) and HasLLA(self) then
            TriggerAmulet(self)      -- 守护者护符：致命伤时复活
            return 49
        else
            return _DoDelta(self, amount, overtime, cause, ignore_invincible, afflicter, ignore_absorb, ...)
        end
    end
end)
```
（出处：`postinit/components/health.lua` 第 133-173 行）

要点：
- 开头两行 `local env = env; GLOBAL.setfenv(1, GLOBAL)` 是 UM 的标准头：**之后写 AddComponentPostInit 不用加 GLOBAL. 前缀，但保存的原函数仍在当前环境**。
- 包装函数签名完整透传，`...` 保持可变参数。
- **拦截逻辑全部前置，原逻辑兜底**——`return _OldFn(self, ...)` 是万能逃生门。

同类实例：
- **combat 包装**（出处：`postinit/components/combat.lua` 第 4-18 行）：

```lua
local _GetAttacked = self.GetAttacked
function self:GetAttacked(attacker, damage, weapon, stimuli, ...)
    if attacker ~= nil and attacker:HasTag("shadow_aligned") and self.inst.prefab == "wanda" then
        damage = damage * 1.25
        return _GetAttacked(self, attacker, damage, weapon, stimuli, ...)
    else
        return _GetAttacked(self, attacker, damage, weapon, stimuli, ...)
    end
end
```

- **在包装里定义全新方法**（同一文件 23-123 行）：`function self:DoNaughtAttack(...)` 完整重实现攻击流程（计算反射伤害、AOE、投射物），说明包装不仅改旧方法，也可以**给组件添加新方法**。

- **原版动作 fn 包装**（出处：`init/init_actions.lua` 第 141-159 行）：

```lua
local _RummageFn = GLOBAL.ACTIONS.RUMMAGE.fn
GLOBAL.ACTIONS.RUMMAGE.fn = function(act)
    local target = act.target or act.invobject
    if target == nil then return end
    if target.prefab == "portablecookpot" and ... then
        -- 特殊逻辑：任何角色都能开沃利的便携锅
        target.components.container:Open(act.doer)
        return true
    end
    return _RummageFn(act)
end
```

- **原版 action.strfn 包装**（同一文件 207-212 行）：

```lua
local _UpgradeStrFn = GLOBAL.ACTIONS.UPGRADE.strfn
GLOBAL.ACTIONS.UPGRADE.strfn = function(act)
    if act.target ~= nil and act.target:HasTag(GLOBAL.UPGRADETYPES.SLUDGE_CORK .. "_upgradeable") then
        return "SLUDGE_CORK"
    end
    return _UpgradeStrFn(act)
end
```

- **配方 test 函数覆盖**（出处：`init/init_crockpot.lua`）：

```lua
recipes.koalefig_trunk.test = function(cooker, names, tags) ... end  -- 覆写判定
recipes.koalefig_trunk.priority = X  -- 调整优先级
```

### 3.3 新动作注册完整流程（init/init_actions.lua）

**标准三步：AddAction → 设置属性 → AddComponentAction 挂上下文**

```lua
local createburrow = AddAction("CREATE_BURROW", GLOBAL.STRINGS.ACTIONS.CREATE_BURROW, function(act)
    local act_pos = act:GetActionPoint()
    if act.doer.components.hunger.current > 15 and not GLOBAL.TheWorld.Map:GetPlatformAtPoint(act_pos.x, act_pos.z) then
        local burrow = GLOBAL.SpawnPrefab("uncompromising_winkyburrow")
        burrow.Transform:SetPosition(act_pos.x, 0, act_pos.z)
        act.doer.components.hunger:DoDelta(-15)
        return true
    end
end)
createburrow.priority = HIGH_ACTION_PRIORITY
createburrow.rmb = true
createburrow.distance = 2
createburrow.mount_valid = false
```
（出处：`init/init_actions.lua` 第 108-122 行）

**手工构造 Action 对象（优先级非默认时）**：

```lua
local SET_CUSTOM_NAME = GLOBAL.Action({ distance = 2, mount_valid = true, priority = 1})
SET_CUSTOM_NAME.id = "SET_CUSTOM_NAME"
SET_CUSTOM_NAME.str = STRINGS.ACTIONS.SET_CUSTOM_NAME
AddAction(SET_CUSTOM_NAME)
SET_CUSTOM_NAME.fn = function(act) ... end
```
（出处：同一文件 268-291 行）

**把动作挂到物品/组件上**（AddComponentAction，USEITEM/INVENTORY 两种上下文）：

```lua
AddComponentAction("USEITEM", "drawingtool", function(inst, doer, target, actions, right)
    if target:HasTag("telebase") or target.prefab == "pocketwatch_recall" or target.prefab == "pocketwatch_portal" then
        table.insert(actions, GLOBAL.ACTIONS.SET_CUSTOM_NAME)
    end
end)
```
（出处：同一文件 298 行）

**新动作需要玩家状态机支持**：

```lua
AddStategraphActionHandler("wilson", GLOBAL.ActionHandler(GLOBAL.ACTIONS.BREAK_DOWN_MODULE, "dolongaction"))
AddStategraphActionHandler("wilson_client", GLOBAL.ActionHandler(GLOBAL.ACTIONS.BREAK_DOWN_MODULE, "dolongaction"))
```
（出处：同一文件 347-348 行）

**新动作的客户端串**：`GLOBAL.STRINGS.ACTIONS.RAT_ORDER = "..."` 在 init_strings.lua 里定义。

**通用可激活物品动作**（设计亮点，同一文件 376-401 行）：

```lua
local UM_ACTIVATABLE_ITEM = Action({ mount_valid = true, priority = 1, rmb = true })
UM_ACTIVATABLE_ITEM.id = "UM_ACTIVATABLE_ITEM"
UM_ACTIVATABLE_ITEM.str = STRINGS.ACTIONS.UM_ACTIVATABLE_ITEM
ENV.AddAction(UM_ACTIVATABLE_ITEM)
UM_ACTIVATABLE_ITEM.strfn = function(act)
    return act.invobject ~= nil and act.invobject.actiontype ~= nil and act.invobject.actiontype or STRINGS.ACTIONS.UM_ACTIVATABLE_ITEM.GENERIC
end
UM_ACTIVATABLE_ITEM.fn = function(act)
    local item = act.invobject
    if item ~= nil and item.components.um_activatable_item ~= nil then
        item.components.um_activatable_item:Activate(act.doer)
        return true
    end
end
ENV.AddComponentAction("INVENTORY", "um_activatable_item", function(inst, doer, actions, right)
    if inst ~= doer then
        table.insert(actions, ACTIONS.UM_ACTIVATABLE_ITEM)
    end
end)
```

> 注意此处用了 `local ENV = env` 保存原环境再 setfenv 的技巧——前面文件里 env 已用过，这里先存再切。

### 3.4 客户端/服务器代码组织

**三端 RPC 分工**（出处：`modmain.lua`）：

```lua
-- 1. 跨 shard（洞穴↔地表）
AddShardModRPCHandler("UncompromisingSurvival", "CaveTornado", function(def, x, z, wise, dest_can_move)
    if GLOBAL.TheWorld ~= nil and GLOBAL.TheWorld:HasTag("cave") then
        GLOBAL.TheWorld:PushEvent("spawncavetornado", { xdata = x, zdata = z, wisedata = wise, dest_can_movedata = dest_can_move })
    end
end)

-- 2. 服务器端 handler（客户端发到服务器）
AddModRPCHandler("UncompromisingSurvival", "GetTargetFocus", GetTargetFocus)

-- 3. 客户端 handler（服务器广播到客户端）
AddClientModRPCHandler("UncompromisingSurvival", "UpdateAllFocuses", UpdateAllFocuses)
```
（出处：`modmain.lua` 第 70-218 行）

**跨 shard 热浪同步**（出处：`scripts/components/um_heatwaves.lua` + `modmain.lua` 第 206-218 行）：

```lua
-- 地表端（um_heatwaves.lua）：
TheWorld:AddTag("heatwavestart")
TheWorld.net:AddTag("heatwavestartnet")
TheWorld:PushEvent("heatwavestart")
SendModRPCToShard(GetShardModRPC("UncompromisingSurvival", "ToggleCaveHeatWave"), nil, true)

-- 洞穴端（modmain.lua 的 AddShardModRPCHandler）：
AddShardModRPCHandler("UncompromisingSurvival", "ToggleCaveHeatWave", function(sender_list, toggle)
    if toggle then
        GLOBAL.TheWorld:AddTag("heatwavestart")
        GLOBAL.TheWorld.net:AddTag("heatwavestartnet")
        GLOBAL.TheWorld:PushEvent("heatwavestart")
    else
        GLOBAL.TheWorld:RemoveTag("heatwavestart")
        GLOBAL.TheWorld.net:RemoveTag("heatwavestartnet")
        GLOBAL.TheWorld:PushEvent("heatwaveend")
    end
end)
```

> **模式要点**：`TheWorld:AddTag`（服务器逻辑）+ `TheWorld.net:AddTag`（客户端同步）双管齐下；世界 tag 既当状态存储又当事件触发器（PushEvent）。

**客户端设置服务器端世界状态**（ToggleLagCompOn/Off，modmain.lua 114-162 行）：一个"LagComp 失效"机制——夜晚影子出现时通过 AddClientModRPCHandler 关闭玩家的移动预测，制造恐怖感。这是纯客户端作弊检测应用。

**玩家位置 RPC 双端处理**（Wixie 技能，modmain.lua 222-244 行）：

```lua
local function HandlerFunction(player, mouseposx, mouseposy, mouseposz)
    if GLOBAL.TheWorld.ismastersim then
        if mouseposx ~= nil then player.wixiepointx = mouseposx end
        ...
    else
        local wixieposition = GLOBAL.TheInput:GetWorldPosition()
        player.wixiepointx = wixieposition.x
        ...
    end
end
AddModRPCHandler("WixieTheDelinquent", "GetTheInput", HandlerFunction)
```

### 3.5 新生物/Boss 模板（prefabs/hoodedwidow.lua 完整结构）

**标准 prefab fn() 结构**（出处：`scripts/prefabs/hoodedwidow.lua` 全文 330 行）：

```lua
local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddSoundEmitter()
    inst.entity:AddLightWatcher()
    inst.entity:AddDynamicShadow()
    inst.entity:AddNetwork()

    MakeCharacterPhysics(inst, 1000, 1)   -- 质量/碰撞半径

    inst.Transform:SetFourFaced()

    inst:AddTag("largecreature")
    inst:AddTag("epic")
    inst:AddTag("monster")
    inst:AddTag("hostile")
    inst:AddTag("hoodedwidow")
    ...

    inst:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    -- 以下全部是 master 端逻辑
    inst:AddComponent("health")
    ...
    inst:SetBrain(brain)                   -- 挂 AI 大脑
    inst:SetStateGraph("SGhoodedwidow")    -- 挂状态机

    return inst
end

return Prefab("hoodedwidow", fn, assets, prefabs)
```

**Boss 特有技巧**：
- **动态生成非网络武器**（EquipWeapons）：`local weapon = SpawnPrefab("hoodedwidow_claw")` 然后用 `weapon.entity:SetParent(inst.entity)` 而非放进 inventory——避免网络同步开销。
- **技能计时器**：`inst:DoPeriodicTask(interval, fn)` + `inst.components.timer:StartTimer` 驱动 PowerMove。
- **护甲粉碎**：OnHitOther 中 `armorcrunch` 直接扣 armor 耐久 200。

**双 prefab 返回模式**（出处：`scripts/prefabs/rice.lua` 第 150-158 行）：

```lua
return Prefab("rice", fn, assets, prefabs),
       Prefab("rice_cooked", fn_cooked, assets_cooked)
```

**新生物通用组件组合清单**（参考 ratcheck.lua / um_stormspawner.lua）：
- `combat`（攻击）、`health`（血量）、`locomotor`（移动）、`inspectable`、`knownlocations`、`sanityaura`（暗影光环）、`lootdropper`（掉落表 `SetSharedLootTable`）、`sleeper`、`frozen`、`burnable`、`explosive`（可炸）、`freezable`。

**共享掉落表**（出处：`scripts/prefabs/um_pawn.lua` 第 14 行）：

```lua
SetSharedLootTable('um_pawn', {{'nightmarefuel', 0.2}, {'thulecite_pieces', 0.1}, {'trinket_6', 0.4}})
```

### 3.6 新烹饪配方（um_preparedfoods.lua + init_crockpot.lua）

**配方表结构**（出处：`scripts/um_preparedfoods.lua` 第 98-127 行）：

```lua
local um_preparedfoods =
{
    beefalowings =
    {
        test = function(cooker, names, tags)
            return tags.veggie and names.horn and
                ((names.batwing and names.batwing > 1) or (names.batwing_cooked and names.batwing_cooked > 1) or (names.batwing and names.batwing_cooked))
        end,
        hunger = 62.5,
        health = 30,
        sanity = 30,
        foodtype = FOODTYPE.MEAT,
        perishtime = 5 * TUNING.PERISH_TWO_DAY,
        priority = 20,
        weight = 30,
        cooktime = 2.4,
        floater = { "med", nil, 0.6 },
        tags = { "honeyed" },
        oneat_desc = STRINGS.UI.COOKBOOK.UM_BEEFALOWINGS,
        oneatenfn = function(inst, eater)
            if eater.components.debuffable ~= nil and eater.components.debuffable:IsEnabled() and
                not (eater.components.health ~= nil and eater.components.health:IsDead()) and
                not eater:HasTag("playerghost") then
                eater.components.debuffable:AddDebuff("buff_knockbackimmune", "buff_knockbackimmune")
            end
        end,
        card_def = { ingredients = { { "carrot", 1 }, { "horn", 1 }, { "batwing", 1 } } },
    },
    ...
}
```

要点：
- `test` 判定：`names.X`（食材名表）+ `tags.X`（属性计数表），支持数量判断 `tags.egg > 1`。
- `oneatenfn` 是吃下后的效果——UM 大量用 `AddDebuff` 做**持续效果**而非即时回血。
- `card_def` 是烹饪书卡片显示用的配方。
- `priority` 决定同配比时哪个配方优先。

**冰/树枝填充限制**（出处：`scripts/um_preparedfoods.lua` 第 1-36 行）：

```lua
local function LimitIceTestFn(tags, ice_limit)
    if tags ~= nil and tags.frozen ~= nil and TUNING.DSTU.GENERALCROCKBLOCKER then
        return (not tags.frozen or (tags.frozen + (tags.foliage ~= nil and tags.foliage or 0) <= ice_limit))
    end
    return true
end
```

**食材属性添加**（出处：`init/init_crockpot.lua`）：

```lua
AddIngredientValues({...}, {meat = 1, monster = 2.0}, true, true)
```

### 3.7 新容器（init_containers.lua 完整模式）

**新容器三步：modparams 定义 → widgetsetup 包装 → 槽位数上限**（出处：`init/init_containers.lua`）：

```lua
modparams.um_blowgun =
{
    widget =
    {
        slotpos = { Vector3(0, 32 + 4, 0) },
        animbank = "ui_cookpot_1x2",
        animbuild = "ui_cookpot_1x2",
        pos = Vector3(0, 15, 0),
    },
    itemtestfn = CheckDart,          -- 只能装飞镖
    acceptsstacks = true,
    type = "hand_inv",
}

-- 关键：包装 widgetsetup，新 prefab 走 modparams，旧的走原逻辑
local old_wsetup = containers.widgetsetup
function containers.widgetsetup(container, prefab, data, ...)
    local t = modparams[prefab or container.inst.prefab]
    if t ~= nil then
        for k, v in pairs(t) do container[k] = v end
        container:SetNumSlots(container.widget.slotpos ~= nil and #container.widget.slotpos or 0)
    else
        return old_wsetup(container, prefab, data, ...)
    end
end

if containers.MAXITEMSLOTS == nil or containers.MAXITEMSLOTS < 25 then
    containers.MAXITEMSLOTS = 25
end

-- 新容器网络槽位补丁（超过原版槽位上限时必须）
local function addItemSlotNetvarsInContainer(inst)
    if (#inst._itemspool < containers.MAXITEMSLOTS) then
        for i = #inst._itemspool + 1, containers.MAXITEMSLOTS do
            table.insert(inst._itemspool,
                net_entity(inst.GUID, "container._items[" .. tostring(i) .. "]", "items[" .. tostring(i) .. "]dirty"))
        end
    end
end
AddPrefabPostInit("container_classified", addItemSlotNetvarsInContainer)
```
（出处：`init/init_containers.lua` 第 294-310、456-476、644-654 行）

要点：
- `itemtestfn` 过滤可放物品（tag 或 prefab 白名单）。
- 深拷贝原版容器参数再改：`modparams.skullchest = GLOBAL.deepcopy(containers.params.shadowchester)`。
- 槽位图标 `slotbg` 可以定义每个槽的专用背景图（`wardrobe_hat_slot.tex` 等）。
- **动态槽位生成用循环**：`for y = 2.5, -1.5, -1 do for x = 0, 4 do table.insert(...) end end`。
- 手部容器类型 `hand_inv` + `issidewidget = true`。

### 3.8 环境威胁/天气系统（核心大系统）

**8.1 系统接线模式**（出处：`init/init_harder_weather.lua` 全文 142 行）：

```lua
-- 给世界（地表）添加系统组件
AddPrefabPostInit("forest", function(inst)
    if not TheWorld.ismastersim then return end
    if TUNING.DSTU.STORMSPAWNER then
        inst:AddComponent("um_stormspawner")    -- 风暴生成器
    end
    if TUNING.DSTU.HEATWAVES then
        inst:AddComponent("um_heatwaves")       -- 热浪
    end
    ...
end)

-- 洞穴端组件（洞穴有独立的世界 prefab "cave"）
AddPrefabPostInit("cave", function(inst)
    ...
    inst:AddComponent("um_snow_stormspawner")   -- 洞穴暴雪
end)

-- 与其他 mod 兼容开关（IA = Island Adventures）
function TestForIA() ... end
```

要点：**天气系统全部是挂在世界 prefab 上的组件**，用 `TheWorld:AddComponent("xxx")` 注入，而不是新建实体。世界组件天然是全图作用域。

**8.2 热浪组件**（出处：`scripts/components/um_heatwaves.lua` 全文 178 行）：

```lua
-- 世界组件标准写法：AddComponent 时注册定时器
inst:AddComponent("worldsettingstimer")   -- 或组件内部使用
-- 组件内：
self.inst.components.worldsettingstimer:AddTimer("um_heatwave_timer",
    TUNING.DSTU.HEATWAVE_INTERVAL, nil, "um_heatwave_timer_end")
```

**8.3 风暴生成器**（出处：`scripts/components/um_stormspawner.lua` 全文 275 行）：

```lua
-- 轮流选择多个固定生成点（_locationtags 表驱动）
self._locationtags = {"siren_bird_spawner", "siren_speaker_spawner", "siren_fish_spawner"}
local tag = self._locationtags[self._currentlocation] ...
-- 生成龙卷风：两个实体（本体+目的地标记），danumber 记录角度
SpawnPrefab("um_tornado") / SpawnPrefab("um_tornado_destination")
-- 洞穴端龙卷风跨 shard
SendModRPCToShard(GetShardModRPC("UncompromisingSurvival", "CaveTornado"), nil, x, z, wise, dest_can_move)
```

**8.4 烟霾系统**（出处：`init/init_smog.lua` 全文 172 行）：

```lua
-- 烧毁物产生烟（包装 onignite）
AddPrefabPostInitAny(function(inst)
    if inst.components.burnable then
        local _onignite = inst.components.burnable.onignite
        inst.components.burnable.onignite = function(...)
            _onignite(...)
            -- 冒烟逻辑（限制最多 150 个烟实体）
        end
    end
end)

-- 玩家咳嗽状态机（新状态 + 事件）
AddStategraphState("wilson", State{ name = "um_smog_cough", ... })
AddStategraphPostInit("wilson", function(sg)
    sg.events["um_smog_cough"] = EventHandler("um_smog_cough", function(inst) ... end)
end)
```

**8.5 暴雪**（出处：`init/init_snowstorm.lua` 全文 64 行）：

```lua
-- 玩家组件挂载 + 覆盖层
AddPlayerPostInit(function(inst) inst:AddComponent("snowstormwatcher") end)
-- 通过 GetSandstormLevel 检测掩蔽物（墙/火/庇护所/防暴雪装备）
-- HUD 覆盖层（沙暴屏/暴雪屏/热浪屏）
AddClassPostConstruct("screens/playerhud", function(self)
    -- CreateOverlays 追加 Um_StormOver / SnowOver / HeatwaveOver
end)
```

### 3.9 鼠灾系统（完整事件驱动范例）

**接线**（出处：`init/init_ratraid.lua` 全文 181 行）：

```lua
-- 世界加组件
AddPrefabPostInit("forest", function(inst) inst:AddComponent("ratcheck") end)

-- 开容器/收获触发（包装 onclosefn / onharvest）
AddPrefabPostInit("treasurechest", function(inst)
    local _onclosefn = inst.components.container.onclosefn
    inst.components.container.onclosefn = function(...)
        _onclosefn(...)
        TheWorld:PushEvent("activeraid", {container = inst, doer = doer, amount = 1})
    end
end)
-- 同样处理 wardrobe/icebox/dragonflychest/saltbox/cookpot
```

**组件核心**（出处：`scripts/components/ratcheck.lua` 全文 369 行）：

```lua
-- 触发条件：周边实体 >= 20 才触发（避免前期灭门）
-- 警告倒计时（ratwarning 1/3/10 三档）
-- SpawnRaid：按玩家生成鼠群
-- WatchWorldState("cycles")：监听天数周期
-- OnSave/OnLoad 保存进度
```

### 3.10 皮肤系统（两层 API）

**官方 API 层 skins_api.lua**（出处：`skins_api.lua` 全文 301 行）：
- `SKINNABLE_CHARACTERS` 表 + `AddSkinnableCharacter(name)`：把 mod 角色注册进官方皮肤系统。
- **`DoAddClassPostConstructBefore`**（核心技术）：包装 classdef._ctor，让 postfn 在 Klei 自己的构造代码**之前**运行：

```lua
function DoAddClassPostConstructBefore(Class, name, postfn)
    local _ctor = Class._ctor
    Class._ctor = function(self, ...)
        postfn(self, ...)      -- 先跑我们的
        return _ctor(self, ...)  -- 再跑 Klei 的
    end
end
```
- 包装 `_LoadSavedSkins` / `Close` / `OnLoad` 方法，重定义 `GLOBAL.IsDefaultSkinOwned`、`ValidateItemsLocal`、`SpawnNewPlayerOnServerFromSim`。
- RPC：`AddModRPCHandler(modname, "moddedskins", function(inst, base) inst.components.skinner.skin_name = base end)`。

**自研 API 层 uncompskins_api.lua**（出处：`uncompskins_api.lua` 全文 345 行）：
- `UNCOMP_SKINS` 全局表存自定义皮肤定义。
- **`ModManager.RegisterPrefabs` 包装**收集 OFFICIAL_PREFABS。
- **BuilderSkinPostInit**：玩家建造时临时把 `AllRecipes[recname].product` 换成皮肤 prefab，build 完还原——在配方系统上做皮肤。
- **ReskinModEntity**：`GetSaveRecord → data.prefab = skin → Remove → SpawnSaveRecord → PushEvent("reskined_spawn")`——换皮 = 拆掉重生成。
- `CreateModPrefabSkin(item, info)`：包装 prefab.fn，设置 `inst.skinname / inst.base_prefab / inst.reskinable`，并 `rawset(_G, info.base_prefab.."_clear_fn", ...)` 注册清理函数。
- `MadeRecipeSkinnable(rec_name, data)`：`rec.skinnable = true; rec.skin_img_data = ...`。
- `InventoryProxy:CheckClientOwnership` 补丁：`IsSkinModded(item)` 返回 true。

### 3.11 UpvalueHacker —— 取上值工具（亮点工具）

```lua
UpvalueHacker = {}

local function GetUpvalueHelper(fn, name)
    local i = 1
    while debug.getupvalue(fn, i) and debug.getupvalue(fn, i) ~= name do
        i = i + 1
    end
    local name, value = debug.getupvalue(fn, i)
    return value, i
end

-- 追踪函数链取局部变量（writeables.makescreen 的 kinds 表）
function UpvalueHacker.GetUpvalue(fn, ...)
    local _fn = fn
    for i, v in ipairs({...}) do
        local _fn_i, scope_fn = GetUpvalueHelper(_fn, v)
        ...
    end
end

-- 注入新函数到闭包上值
function UpvalueHacker.SetUpvalue(start_fn, new_fn, ...)
    local _fn, _fn_i, scope_fn = UpvalueHacker.GetUpvalue(start_fn, ...)
    debug.setupvalue(scope_fn, _fn_i, new_fn)
end
```
（出处：`scripts/tools/upvaluehacker.lua` 全文 98 行）

**实际使用**（出处：`scripts/uncompromising_writeables.lua` 全文 42 行）：

```lua
local SignGenerator = require"signgenerator"
local UpvalueHacker = require("tools/upvaluehacker")
local writeables = require("writeables")

local kinds = UpvalueHacker.GetUpvalue(writeables.makescreen, "kinds")

if kinds == nil then return end

-- 往 kinds 表塞新书写类型（牌匾 UI 定制）
kinds["umss_general"] = {
    prompt = STRINGS.SIGNS.MENU.PROMPT,
    animbank = "ui_board_5x3",
    animbuild = "ui_board_5x3",
    menuoffset = Vector3(6, -70, 0),
    cancelbtn = {...}, middlebtn = {...}, acceptbtn = {...},
}
-- 复用已有类型
kinds["telebase"] = kinds["homesign"]
kinds["pocketwatch_portal"] = kinds["homesign"]
kinds["pocketwatch_recall"] = kinds["homesign"]
```

### 3.12 口袋次元容器（um_pocketdimensioncontainers.lua，全文件 20 行）

```lua
local POCKETDIMENSIONCONTAINER_DEFS = require("prefabs/pocketdimensioncontainer_defs").POCKETDIMENSIONCONTAINER_DEFS

local UM_POCKETDIMS = {
    { name = "skull", prefab = "skullchest", ui = "anim/ui_portal_shadow_3x4.zip", widgetname = "skullchest" },
    { name = "winky", prefab = "uncompromising_winkyburrow_master", ui = "anim/ui_portal_shadow_3x4.zip", widgetname = "uncompromising_winkyburrow_master" },
}

for k,v in pairs(UM_POCKETDIMS) do
    table.insert(POCKETDIMENSIONCONTAINER_DEFS, v)
end
```
> 模式：**往原版定义表 table.insert 追加条目**，零侵入扩展次元容器系统。

### 3.13 Boss 血量乘数（init_bosshealth.lua，全文 49 行）

```lua
local bosses = { "MINOTAUR", "STALKER_ATRIUM", ... }
for k, v in pairs(bosses) do
    TUNING[v .. "_HEALTH"] = TUNING[v .. "_HEALTH"] * GetModConfigData(string.lower(v) .. "_health_")
end
-- 特例：ALTERGUARDIAN_PHASE1_HEALTH、TWIN1_HEALTH、
-- SHADOW_ROOK.HEALTH = {1000*x, 4000*x, 10000*x}（表型血量）
```
（出处：`init/init_bosshealth.lua` 全文 49 行）

### 3.14 服装耐久系统（init_durability.lua）

```lua
-- 核心：给防水/保温装备加 4 段衰减
local function onfuelchangehigh(newsection, oldsection, inst, doer)
    if newsection <= 1 then inst.components.waterproofer:SetEffectiveness(0.4)
    elseif newsection <= 2 then inst.components.waterproofer:SetEffectiveness(0.6)
    elseif newsection <= 3 then inst.components.waterproofer:SetEffectiveness(0.75)
    elseif newsection <= 4 then inst.components.waterproofer:SetEffectiveness(0.9)
    end
end

AddPrefabPostInit("rainhat", function (inst)
    inst:AddTag("um_durability")
    if inst ~= nil and inst.components ~= nil and inst.components.waterproofer ~= nil and inst.components.fueled ~= nil then
        inst.components.fueled:SetSections(4)
        inst.components.fueled:SetSectionCallback(onfuelchangemedium)
    end
end)
```
（出处：`init/init_durability.lua` 全文 188 行）

> 模式：**复用 fueled 组件的 sections 机制**——耐久掉档时回调动态改属性值，把"耐久"变成"性能衰减"。

### 3.15 食物恢复机制重做（init_foodregen.lua，全文 86 行）

```lua
-- 食物不直接回血/回理智，改持续恢复
AddPlayerPostInit(function(inst)
    inst.components.eater:SetAbsorptionModifiers(0, hunger, 0)  -- 回血/回san吸收率清零
end)

-- oneat 事件：转化为 debuff 持续恢复
inst:ListenForEvent("oneat", function(inst, data)
    if data.food.components.edible then
        local health_delta = data.food.components.edible:GetHealth()
        if health_delta > 3 then
            inst.components.debuffable:AddDebuff("healthregenbuff_vetcurse_" .. prefab,
                "healthregenbuff_vetcurse",
                { duration = health_delta * 0.1, max_hp = maxhp_heal })
        else
            inst.components.health:DoDelta(health_delta)
        end
    end
end)
```

### 3.16 静态布局文件格式（Tiled 导出）

```lua
return {
  version = "1.1",
  luaversion = "5.1",
  orientation = "orthogonal",
  width = 24, height = 24,
  tilewidth = 16, tileheight = 16,
  tilesets = { { name = "ground", firstgid = 1,
    filename = "../../../../tools/tiled/dont_starve/ground.tsx", ... } },
  layers = {
    { type = "tilelayer", name = "BG_TILES", ..., data = { 0,0,0,...,6,0,0,0,2,... } },
    { type = "objectgroup", name = "FG_OBJECTS", ..., objects = {
        { type = "wall_stone", x = 104, y = 359, width = 0, height = 0 },
        { type = "gravestone", x = 146, y = 138 },
        { type = "grass", x = 140, y = 273 },
        ...
    } }
  }
}
```
（出处：`scripts/map/static_layouts/hooded_town.lua` 全文 751 行）

要点：BG_TILES 的 data 数组是 tile id（0=空，2/6=不同地皮 id）；FG_OBJECTS 的 objects 每个条目就是一个生成的 prefab（type = prefab 名，x/y 像素坐标，用 `--[[ ]]` 注释掉的就是"美术上删掉但留着参考"的）。

### 3.17 新世界关卡定义（AddLevel）

```lua
AddLevel(GLOBAL.LEVELTYPE.SURVIVAL, {
    id = "UNCOMPROMISING",
    location = "forest",
    version = 4,
    ...（地形/资源参数，overrides 配置）
})
```
（出处：`modworldgenmain.lua`）

### 3.18 技能树接入（modmain.lua 第 284-298 行）

```lua
local skilltree_defs = require("prefabs/skilltree_defs")
local BuildSkillsData = require("prefabs/skilltree_wixie")
if BuildSkillsData then
    local data = BuildSkillsData(skilltree_defs.FN)
    skilltree_defs.CreateSkillTreeFor("wixie", data.SKILLS)
    skilltree_defs.SKILLTREE_ORDERS["wixie"] = data.ORDERS
    RegisterSkilltreeBGForCharacter(GLOBAL.resolvefilepath("images/wixie_skilltree.xml"), "wixie")
    for k, v in pairs(data.SKILLS) do
        if v.icon then
            RegisterSkilltreeIconsAtlas("images/wixie_skilltree.xml", v.icon .. ".tex")
        end
    end
end
```

### 3.19 资产批量注册（init_assets.lua 第 317-319 行）

```lua
for k, v in ipairs(inventoryitems) do
    RegisterInventoryItemAtlas(GLOBAL.resolvefilepath("images/inventoryimages/" .. v .. ".xml"), v .. ".tex")
end
```
> 约定：atlas 文件名 = 图片名 = prefab 名，循环注册 300+ 物品图标。Assets 表里只需注册 anim + 特殊资产。

### 3.20 客户端 HUD widget（vetcursewidget.lua）

```lua
local Vetcursewidget = Class(Widget, function(self, owner)
    self.owner = owner
    Widget._ctor(self, "Vetcursewidget")
    self.bg2 = self:AddChild(ImageButton("images/vetskull.xml", "vetskull.tex"))
    self.bg2:SetVAnchor(ANCHOR_MIDDLE)
    self.bg2:SetHAnchor(ANCHOR_MIDDLE)
    self.bg2:SetPosition(880, -380, 0)
    self.bg2:SetScaleMode(0.01)
    self.bg2:SetScale(.33, .33, .33)
    self.bg2:SetTooltip(STRINGS.VETS_WIDGET)
    self:StartUpdating()
    self:Show()
    self.bg2:SetOnClick(function() self:Disable() self:Hide() end)
end)

function Vetcursewidget:OnUpdate(dt)
    if self.owner:HasTag("vetcurse") then
        self:Show()
    else
        self:Hide()
    end
end
return Vetcursewidget
```
（出处：`scripts/widgets/vetcursewidget.lua` 全文 132 行）

> 模式：Class(Widget) 子类 + StartUpdating + OnUpdate 按玩家 tag 显隐。挂载到 HUD 的方式在 `init/init_widgets.lua`（AddClassPostConstruct("widgets/playerstatus") 或 playerhud overlay）。

### 3.21 新树木 prefab（giant_tree.lua 要点）

- **canopy 阴影系统**：`TheWorld.shadetiles[key]` 引用计数 + `DespawnLeafCanopy`；树倒下时递减玩家 `canopytrees` 计数并 PushEvent。
- **闪电掉落**：`_lightning_drop_task` 定时掉落 twigs/leaves。
- **三张掉落表**：choploots（砍伐）/ felloots（倒下）/ infestedloots（感染态），带概率 `log = 0.5`。
- **落地检测**：`_GroundDetectionUpdate` 轮询 y <= .2 时播放 land 动画（浮空树机制）。
（出处：`scripts/prefabs/giant_tree.lua` 第 1-160 行）

---

## 4. 特色专题补充：岛屿/植物/地形

### 4.1 特色植物全清单（scripts/prefabs/ 扫描）

按类型分组。全部 429 个 prefab 中植物相关约 28 个文件（含生成器/装饰）。

**A. 新作物 / 食材**

| 文件名 | prefab | 类型 | 生长机制 | 收获物 | 用途 |
|---|---|---|---|---|---|
| `riceplant.lua` | riceplant | 水域作物 | pickable 再生（REEDS_REGROW_TIME），船碰撞自动收获（`on_collide` 事件），冬季不生长 | rice | 生米（FOODTYPE.HORRIBLE +9.8 饥饿）/ 熟米 VEGGIE +12.5，可作鱼饵（bait） |
| `rice.lua` | rice / rice_cooked | 食材 | —（可烹饪，cookable） | — | 煮饭原料，随机改名（possiblenames RICE1/RICE2） |
| `riceplantspawner.lua` | riceplantspawner / _large | 水域播种器 | 找水面+靠近岸边的点递归重试（FindValidPositionByFan）后刷 riceplant | — | 世界生成用，沼泽边稻田 |
| `zaspberry.lua` | zaspberry | 发光浆果 | —（可采可藏，haunt 变异成 wormlight） | zaspberry | +20 血 -20 理智，吃后挂 wormlight_light 光源；wormlight 燃料（LARGE_FUEL*1.33）；WX78 充电 |
| `viperfruit.lua` | viperfruit | 毒果 | 同上，haunt 变异 | viperfruit | +15 血 +37.5 饥饿 -33 理智，吃后 3 连发 `viperprojectile` 攻击友军（整蛊/危险品） |
| `um_sorrel.lua` | um_sorrel | 草药 | 春天 bloom 切 loot 表（见 4.2） | greenfoliage / petals | 绿叶+花瓣 |
| `um_foliage.lua` | greenfoliage | 食材杂物 | —（perishable 快速腐烂） | — | SetPrefabNameOverride("foliage") 改名，0.5 血素食，猫玩具 |
| `honey_log.lua` | honey_log | 食物 | — | — | plantkin/werehuman +10 饥饿，全角色 SetNextSneezeTime(300~400) 抗花粉热（hayfever 联动，见 4.4） |
| `giant_blueberry.lua` | giant_blueberry | 果实 | 蓝莓地雷爆炸产物 | — | +12.5 饥饿，吃后 +5 湿度（moisture） |

**B. 威胁性 / 毒植物**

| 文件名 | prefab | 类型 | 生长机制 | 收获物 | 用途 |
|---|---|---|---|---|---|
| `um_pyre_nettles.lua` | um_pyre_nettles + _stage_1~5 + blocker | 火毒草 | 5 阶段生长，热浪/岩浆洞限定（见 4.2 精读） | firenettles（火荨麻叶，武器材料） | 触碰/被攻击施 `umdebuff_pyre_toxin`，stage>3 喷 `um_smolder_spore`；岩浆洞区域威胁 |
| `blueberryplant.lua` | blueberryplant | 地雷植物 | 海星陷阱 mine 改造，冬季冻结变矿点（见 4.2） | giant_blueberry / ice | 怪物踩爆 AOE 伤害 + 3 格连锁引爆其他蓝莓；10% 生成 fruitbat |
| `pitcherplant.lua` | pitcherplant | 食虫植物 | childspawner 白天生 fruitbat（仿 beebox 结构） | honey | 沼泽地区随机 1-2 个，白天蝙蝠飞出攻击 |
| `snapdragon.lua` | snapdragon（prime）+ snapdragon_buddy | 移动食人花 | 兽群（herdmember），夏天狂暴攻击；喂食 2 次产 whisperpod/种子呕吐物 | plantmeat / pale_vomit / whisperpod | 夏季威胁；喂食驯化，抱走 pods 可得宠物 |
| `whisperpod.lua` + `whisperpod_normal.lua` | whisperpod / whisperpod_normal_ground | 种荚植物 | 种植后喂种子：crop 组件 StartGrowing("snapdragon", SEEDS_GROW_TIME) | snapdragon_buddy 宠物 | 按种子类型变色（Colors() 映射到 build 变体），成熟后 spawn buddy+snapplant 绑定 |
| `snapplant.lua` | snapplant | 绑定植物 | —（不可再生） | — | 与 buddy 绑定，buddy 死则一起死（Bind/Die） |
| `trapdoorgrass.lua` | trapdoorgrass / depleted_trapdoorgrass | 陷阱草丛 | pickable 3 连采 + witherable，TUNING.DSTU.TRAPDOORSPIDERS 关闭时直接 Remove | cutgrass ×3 / dug_grass | 伪装草丛下躲陷阱蜘蛛（trapdoor 生物相关） |
| `marsh_grass.lua` | marsh_grass | 沼泽装饰 | 无交互（纯装饰 bush_marsh） | — | 沼泽填充 |

**C. 树**

| 文件名 | prefab | 类型 | 生长机制 | 收获物 | 用途 |
|---|---|---|---|---|---|
| `giant_tree.lua` | giant_tree / giant_tree_infested | 巨型树 | 24 斧、闪电掉落、debris 弹射（3.21 已详述） | log/twigs/leaves/鸟巢/蛙/蛛 | 巨型树区域主体，感染态产 aphid（childspawner） |
| `giant_tree_birdnest.lua` | giant_tree_birdnest | 树巢 debris | 落地产蛋动画（egg 1-3） | — | 巨型树倒下掉落物 |
| `hooded_mushtree.lua` | hooded_mushtree_small/medium/tall + _stump/_burntfx | 蘑菇树 | 季节开花 + growable 3 阶段循环（见 4.2） | log + 各色 cap / spore | 遮面森林主要树种，开花期周期喷孢子 |
| `cinnamon_tree.lua` | cinnamon_tree + _stump/_burnt | 肉桂树 | 用 beard 组件"剃毛"采果（见 4.2） | log/twigs | 洞穴香蕉树动画改造的树，3 斧砍倒 |
| `honey_log.lua` | honey_log | 蜜木 | — | — | 食物（见 A 组） |

**D. 藤 / 水草 / 岩石植物**

| 文件名 | prefab | 类型 | 生长机制 | 收获物 | 用途 |
|---|---|---|---|---|---|
| `kelpstack.lua` | kelpstack / mossstack | 海岩 | 船撞可挖（OnCollide 按船速折算伤害） | rocks ×4 + kelp / um_brineishmoss | 海带/盐水苔来源 |
| `hooded_fern.lua` | hooded_fern / depleted_hooded_fern | 遮面蕨 | pickable 20 循环 + playerprox 触发蚜虫（onnear 5% 出 aphid） | greenfoliage + 20% cutgrass/twigs | 巨型树区域地面植被；玩家经过会刷蚜虫 |
| `blueberryplantbuncher.lua` | blueberryplantbuncher | 地块生成器 | 网格撒蓝莓地雷+酢浆草后自毁 | — | 巨型树区域生成蓝莓雷阵 |
| `snapdragon_fertilizer.lua` | snapdragon_fertilizer | 肥料 | — | — | 食人花相关道具 |

**E. FX / 环境物**

| 文件名 | prefab | 类型 | 说明 |
|---|---|---|---|
| `um_smolder_spore.lua` | um_smolder_spore | 阴燃孢子 | 火荨麻喷出，飘散引燃 |
| `mushroomsprout_overworld.lua` | mushroomsprout_overworld | 地表毒蘑菇芽 | 会烧毁/喷 sporecloud_toad，酸雨系统相关（4.4） |
| `nightglow.lua` | （空文件） | — | 空占位 |

**原版植物改造（AddPrefabPostInit 包装）**：植物类主要走"新 prefab 而非包装"路线，唯一系统级包装在 `init/init_weather/init_smog.lua` 第 19 行——`AddPrefabPostInitAny` 给所有带 plant/tree tag 且非 PyreNettle 的实体包 burnable.onignite，夏天着火时刷 smog（见 4.4）。另外 `postinit/any.lua` 有全局 postinit（hayfever 相关）。

### 4.2 生长机制精读（5 种）

**① 火荨麻 um_pyre_nettles：阶段生长 + 种群密度抑制 + 热浪联动**（`scripts/prefabs/um_pyre_nettles.lua`）

核心是 `OnGrow`（第 195-254 行）：按 50 单位半径内同阶段数量决定能否生长——这是**种群密度抑制**生长，防爆刷：

```lua
local findnettles = TheSim:FindEntities(x, y, z, 50, {"PyreNettle"..targetstage})
-- 各阶段上限：stage2<16、stage3<8、stage4<4、stage5<2、stage6 无条件
if not next(findnettles) or #findnettles == 0 then growsuccess = true
elseif targetstage == 2 and #findnettles < 16 then growsuccess = true
...
-- 关键环境限制：非岩浆洞/热浪/熔岩旁，stage>2 永远长不上去
if growsuccess
    and not HOME_TILES[tile_at_position]
    and not TheWorld:HasTag("heatwavestart") -- 热浪中允许生长
    and not nearextremeheat -- 或熔岩旁（Dfly 岩浆池/熔岩洞穴 lava tag）
    and (targetstage > 2 or (targetstage == 2 and math.random() > 0.5)) then
    growsuccess = false
end
```

- 阶段标签 `PyreNettle1..5` + 每阶段独立 loot 表 `um_pyre_nettles_1..5`（firenettles 掉落递增）；
- `SetStage`（144-192 行）：stage>3 时不可拾取、可被攻击（去 notarget）、喷孢子弹窗（`bump_task` 每 10 帧检测）；
- 孢子：`NaturalSporeSpawnTimer`（60-90 秒）+ 被攻击随机喷；`um_smolder_spore` 是阴燃引燃孢子；
- 毒：`umdebuff_pyre_toxin` debuff（stage>3 时 10 秒，否则 6 秒）；
- 燃烧**促进生长**：`burnable:SetOnBurntFn(OnGrow)`（第 469 行），烧完反而升级；
- 爆炸清场：`OnExplosion`（307 行）按阶段循环掉落所有 loot 表 + 2-5 个孢子；
- 再生抑制：`um_pyre_nettles_blocker`（507 行）带 NettleBlockerTimer（3~8 天），防止原地立刻重刷；
- `StageSpawner`（379 行）：一个工厂函数生成 5 个指定阶段 prefab + 本体，世界生成直接用 `um_pyre_nettles_stage_N`。

**② 遮面蘑菇树 hooded_mushtree：季节开花 + 孢子周期生成**（`scripts/prefabs/hooded_mushtree.lua`）

- `data` 表（137-179 行）驱动 3 个 prefab：small=绿/春季/spore_small、medium=红/夏季/spore_medium、tall=蓝/冬季/spore_tall——**每棵树一个固定季节**；
- 开花：`WatchWorldState("is" .. data.season, onisinseason)`（534 行），进季节后随机延迟 `math.random()*3*SEG_TIME` 换 bloom build 并 `StartSpores`（periodicspawner 周期喷对应孢子，孢子落地再长小蘑菇）；出季节换回 normal build；
- 生长：`growable` 组件 3 阶段循环（short/normal/tall 复用 EVERGREEN_GROW_TIME 时间，loopstages=true，growonly=true）；
- 树桩：`makestump`（356 行）切到 decay 计时器（MUSHTREE_REGROWTH.DEAD_DECAY_TIME），到期清理 6 半径内的 log/cap/charcoal 后消失（`ontimerdone` 62-83 行）；
- 睡眠/唤醒孢子续期：`onentitysleep/onentitywake`（247-271 行）保存 periodicspawner 目标时间，LongUpdate 补齐——离线不掉进度。

**③ 蓝莓地雷 blueberryplant：海星陷阱 mine 组件改造**（`scripts/prefabs/blueberryplant.lua`）

```lua
-- 冬季（冻结）：变成可 MINE 的冰点，产出 ice + 给玩家 +5 湿度
local function MakeWinter(inst)
	inst.components.mine:SetRadius(TUNING.STARFISH_TRAP_RADIUS*0)  -- 半径归零=失效
	if inst.harvestable == "full" then
		inst.components.workable:SetWorkAction(ACTIONS.MINE)  -- 采矿动作
		...
-- 非冬季：mine 陷阱激活，爆炸=动画 snap 延迟 40 帧后 AOE 1.1*STARFISH_TRAP_RADIUS
local function do_snap(inst)
	-- FindEntities 1.1*RADIUS 内 _combat 目标 GetAttacked(STARFISH_TRAP_DAMAGE)
	-- 再连锁 3*RADIUS 内其他蓝莓 Explode（地雷阵连环爆炸）
```

- 状态机：`harvestable = "full"/"regrow"`，被炸后 `start_reset_task` 3840 秒重生长（`CheckTimeRegrow` 冬季挂起 pendingregrow）；
- 玩家挖（DIG）= 引爆（`on_blueberry_dug_up`，挖完炸）；爆炸 10% 掉 giant_blueberry，90% 掉果蝠 fruitbat；
- 保存/加载恢复爆炸计时（`on_save` 存 `reset_task_time_remaining`）。

**④ 水稻 riceplant：水域 pickable + 船碰撞收获**（`scripts/prefabs/riceplant.lua`）

```lua
inst.components.pickable:SetUp("rice", TUNING.REEDS_REGROW_TIME)
-- 船撞（on_collide 事件）→ 直接产 rice 并 Pick()
local function OnCollide(inst)
	if inst.components.pickable ~= nil then
        inst.components.lootdropper:SpawnLootPrefab("rice")
		inst.components.pickable:Pick()
	end
end
```

再生长时 `onregenfn` 检查 1.5 半径内有无船（`{"boat"}`），有船不重生；`MakeNoGrowInWinter` 冬季停长。播种器 `riceplantspawner.lua` 的 `GetSpawnPoint` 要求：水面 + 非沼泽 tile + 不可通行 + 6 半径内必有岸（`FindLandNextToWater` 扇面搜索），失败递归重试——**水质条件播种**。

**⑤ 酢浆草 um_sorrel：春天换 loot 表**（`scripts/prefabs/um_sorrel.lua` 24-40 行）

```lua
local function bloom(inst)
    if TheWorld.state.isspring then
        inst:AddTag("blooming")
        inst.components.lootdropper:SetChanceLootTable('sorrel_blooming')  -- 绿叶×3 + petals
    else
        ...
        inst.components.lootdropper:SetChanceLootTable('sorrel')  -- 只有绿叶
    end
end
inst:WatchWorldState("isspring", bloom)
```

onharvest 里留有注释 `--MAKE THIS A HAYFEVER THINGFGAAA`（未实现的春花致敏联动，见 4.4）。

**⑥ 低语荚生态链（附带）**：`whisperpod_normal_ground` 用 trader 组件收种子 → `crop:StartGrowing("snapdragon", SEEDS_GROW_TIME)` 模拟作物生长 → 成熟刷 snapdragon_buddy + snapplant 并 `Bind` 绑定；种子类型经 `Colors()` 映射到 `snapdragon_build_<color>` 8 种 build 变体——**用 crop 组件做宠物孵化器**。

### 4.3 特色地形 / 岛屿区域

**世界生成任务（scripts/map/tasks/）**：

| task 文件 | 任务名 | 锁链 | 区域 | 内容 |
|---|---|---|---|---|
| `gianttrees.lua` | GiantTrees | ADVANCED_COMBAT + MONSTERS_DEFEATED + TIER5，给 KEYS.HF | 遮面森林 | 房间：GiantTrees / SnapDragons（4-5 食人花）/ SpideryGiantTrees / WalrusGiantTrees / MoonBaseGiantTrees / AphidLand（蚜虫地） |
| `newswamp.lua` | RiceSqueltch | TIER3 | 沼泽 | room_bg=MARSH，sparsericepatch 稀疏稻田房 |
| `sunkendecid.lua` | SunkDecid | ENTRANCE_OUTER | HOODEDFOREST | 沉没落叶林（水下树），room_bg=HOODEDFOREST |
| `ratacombs.lua` | Ratty_Entrance → Ratty_Link → Ratty_Maze → Ratty_Shallow_2/3 | TIER1→2→1→3 锁链递进 | region_id="ratacombs" | 鼠灾地牢链，room_tags = {"RoadPoison", "nohunt", "nohasslers", "not_mainland"}——毒路 + 无猎犬/骚扰 |

**静态布局特色地点（scripts/map/static_layouts/，3.16 已有格式）**：

| 文件 | 尺寸 | 内容（object 统计） | 定位 |
|---|---|---|---|
| `hooded_town.lua` | 24×24 | wall_stone×48 围城 + grass×6 + gravestone×2 + mound×2 + twiggy_tall×2 + spear×1 | 遮面老树精古镇（防御型 setpiece） |
| `rose_garden.lua` | 16×16 | flower_withered×9 + flower_rose×5 + 大理石雕像×4 + **screecher_trinket×1**（尖叫者饰品） | 玫瑰园，尖叫者 boss 线索 |
| `ratkinggate.lua` | 40×40 | tentacle×31 + marsh_bush×8 + marsh_tree×1 + **ratacombslock×1** | 鼠灾地牢大门（触手沼泽防线） |
| `ratacombs_lock1.lua` | — | evergreen×5 + grass×5 + sapling×4 + ratacombs_cleanair×3 + cavelight + **ratacombslock** | 地牢锁区 + 新鲜空气点（毒气区生存点） |
| `ratacombs_airpocket_1.lua` | — | 同上无锁 | 毒气区空气口袋 |
| `moose_nest.lua` | 16×16 | randomtree×5 + berrybush×5 + pond×1 + moose_nesting_ground×1 | 驼鹿巢 |
| `ricepatchsmall1-4.lua` / `ricepatchlarge1-2.lua` | 24×24 | riceplantspawner×4 / _large×9 | 沼泽稻田（新作物区域） |
| `brine_bogs.lua` / `specter_sea.lua` / `rusted_reef.lua` | 30×30 | 各仅 1 个 `um_*_areahandler` | **动态区域处理器**（见下） |
| `utw_biomespawner.lua` | 30×30 | utw 生物群系生成器 | 未开发（umss_utw_inactivebiome 相关） |
| `umss_basefrag_*.lua`、`umss_moonfrag.lua`、`umss_biometable.lua`、`umss_sunkenboat.lua` | — | umss_general / ums_biometable 等 | 月球碎裂地块事件系列 |
| `wixie_puzzle.lua` | 4×4 | 钢琴谜题（wixie_piano 触发） | 新角色 wixie 专属 |

**区域处理器机制**（`scripts/prefabs/um_areahandler.lua`）：brine_bogs / specter_sea / rusted_reef 三个布局只放一个 prefab，运行时由它完成整区布置——`ClearSeastacks`（清 80 半径海岩）、`ClearInactiveBiome`/`ClearActiveBiome`（清 `umss_utw_inactivebiome`/`activebiome` 标签实体）、`SpawnSiren`（刷海妖点）——**setpiece 与运行时生成解耦，布局文件极简**。

### 4.4 环境威胁系统与植物的联动（对照 3.8）

| 威胁系统 | 联动植物 | 机制 |
|---|---|---|
| 热浪 heatwave | **um_pyre_nettles** | `TheWorld:HasTag("heatwavestart")` 时允许长出岩浆洞上限阶段；`OnHeatwaveStart` 开 60+random(30~60) 秒周期 OnGrow 加速生长，结束取消（352-363 行）；燃烧完成后反而 OnGrow 升级 |
| 雾霾 smog | **所有 plant/tree 类**（PyreNettle 豁免） | `init/init_weather/init_smog.lua` 第 19 行：AddPrefabPostInitAny 包装 burnable.onignite，夏天植物着火 → 延迟 0.5-1.5 秒生成 smog 污染雾团（上限 150 个）；`not inst:HasTag("PyreNettle")` 显式豁免火荨麻 |
| 酸雨 acid rain | **mushroomsprout_overworld** | `init_acid_rain_effects.lua` 第 8-51 行：按 `acidrain_mushroom` tag 实体数量（2/4/6/8 档）动态缩放酸雨伤害；第 28 行起整段注释掉的原版毒蘑菇 count 逻辑被替换为酸雨蘑菇 |
| 花粉热 hayfever | **honey_log / pollenmites / um_sorrel（未完成）** | honey_log 吃后 SetNextSneezeTime(300~400)（plantkin/werehuman 额外回饥饿）；pollenmites 是过敏源生物；sorrel 的 bloom 回调留有 "MAKE THIS A HAYFEVER THING" 注释（4.2-⑤），春花致敏未实装 |
| 冬季 | **riceplant / trapdoorgrass / blueberryplant** | MakeNoGrowInWinter 停长；blueberryplant 冻结变冰矿点（MINE 动作，4.2-③） |
| 鼠灾毒气 | 无直接植物 | ratgas / ratpoison 走 debuff 路线（3.9 已述） |

### 4.5 美术分析（tex 实际解码）

**方法**：`E:\神秘复苏\tools\dst_tex_analyze.py`（KTEX 头 + 0x20 族 DXT5 解码，mip 链 7-12 级）；anim zip 内嵌 `atlas-0.tex`；本专题用其解码逻辑统计 64~128px 小 mip 的色板/饱和度/明度/alpha 覆盖（脚本存于 `E:\神秘复苏\dist\tex_samples\um_art_analysis.py`，样本 PNG 已输出到 `E:\神秘复苏\dist\tex_samples\`）。

**① 特色植物画风**（anim/atlas-0.tex，DXT5）：

| 植物 | 饱和度 | 明度 | 黑描边占比 | 主色板 | 画风结论 |
|---|---|---|---|---|---|
| sorrel 酢浆草 | 0.31 | 0.17 | 74% | #000000 黑 + #D8D8D8 白花 + #183018 深绿 | 暗底绿叶丛+白花点缀，贴地装饰 |
| pyre_nettles 火荨麻 | **0.91** | 0.12 | 50% | #483000/#603000/#784800 橙棕系 | **全 mod 最高饱和**，橙红火焰系，无亮部（阴影重） |
| riceplant 水稻 | 0.15 | 0.16 | 73% | 灰阶 #181818~#787878 | 低饱和灰绿，贴近原版 reeds 风格 |
| blueberryplant 蓝莓地雷 | 0.32 | 0.21 | 50% | #304818 黄绿 + #184878 蓝紫 | 暗黄绿植株+蓝紫莓点缀 |
| giant_tree1 巨型树 | 0.22 | 0.18 | 50% | #483030/#604848 红棕 | 暖红棕巨木，与遮面苔原棕绿色调一致 |
| snapdragon_build 食人花 | 0.25 | 0.19 | 58% | **#9078A8 淡紫** + #603030 深棕 | 粉紫配色在 mod 中独一份（花=紫粉） |
| whisperpod 低语荚 | 0.24 | 0.16 | 66% | #603030/#301830 紫红暗色 | 紫黑荚果，低调危险感 |
| pitcher 猪笼草 | 0.33 | 0.15 | 63% | #786030/#606030 黄绿棕 | 黄绿捕虫笼 |
| blueberry_fruit / um_goo_blue 蓝莓果/黏液 | 0.56-0.64 | 0.20 | 15-34% | #184878/#003060 深蓝系 | **高饱和深蓝**，地面落果高辨识度 |

**共性画风**：① 全部重黑描边（纯黑像素占比 34%~74%，均值 ~55%）——UM 的描边比原版 DST 更重，暗色调（lum 普遍 0.12~0.21）；② 危险植物用高饱和撞色（火荨麻橙红 0.91、蓝莓深蓝 0.64），无害作物低饱和（水稻 0.15）；③ alpha 覆盖 0.19~0.52（地面贴图稀疏布局），软边 alpha 占比（soft）6%~21%——叶片边缘用半透明 alpha 而非硬切。

**② 特殊地形区域纹理**（levels/tiles/ + levels/textures/）：

- **重大发现：3 个新地皮 tile tex 字节完全相同**（ancienthoodedturf / hoodedmoss / jungle 的 `levels/tiles/*.tex` MD5 全为 `932b5d578ea4963617e43429e95a119b`，1024² 全白底 lum=0.96）——它们是**未引用的白模占位**；
- **真正渲染**：`levels/tiles/*.xml` 的 `<Texture filename="data/levels/tiles/deciduous.tex"/>` 直接指向**原版 deciduous 图集**，48 个 `<Element name="01"~"48">` 按 0.12890625（=128/1024）网格切 UV——**新地皮零自绘 tile 贴图**，视觉 = 原版 tile 结构 + `tile_adder.lua`/`modworldgenmain.lua` 的 AddTile 色板（GROUND_OCEAN_COLOR：primary 黑底、secondary #001421 深青、minimap #2E2012 棕）+ noise 纹理混合；
- **noise 纹理是唯一自绘部分**（各 tile 独立 MD5，512~1024²）：`noise_hoodedmoss`（暗橄榄 #484818/#303000，sat 0.49）、`noise_jungle`（黄绿 #486018/#484818，sat 0.39）、`noise_um_floodwater`（1024² 黑白噪点，dark 0.555）——地皮的斑驳细节全靠 noise 层，风格与"遮面森林=暗黄绿苔"设定一致；
- **实际观感色**看 64×64 图标：`images/inventoryimages/turf_ancienthoodedturf.tex` = 暗橄榄绿 #304818/#484818 + 黑描边（dark 0.563）——遮面苔原不是灰白而是**暗黄绿苔**；`um_floodwater` tile = 灰白 #D8D8C0 底 + #484848 黑噪点（洪水沼泽的脏水感）；
- **XML atlas 组织惯例**：`<Atlas><Texture filename="..."/>` 指向实际纹理文件（可跨 mod 引用原版路径）+ `<Element name="tile编号" u1/v1/u2/v2="UV">`（0-1 归一化坐标，variant 属性留空）——与 anim zip 内的 atlas-0.tex（DXT5 单文件 mip 链）是两套系统：地形走 XML 图集引用，模型动画走 zip 内嵌 KTEX。

---

## 5. 亮点技术（最有价值的 5 个技巧）

### 技巧 1：AddTile 全链路 + 复用原版纹理图集

`tile_adder.lua` 的 AddTile 一次调用完成：GROUND 表注册、tiledefs.ground 插入（影响渲染）、地面噪声/图集资产注册、minimap 渲染层注册。**而新地皮的 XML 可以直接引用原版 `data/levels/tiles/deciduous.tex` / `river.tex` 纹理**（见 `levels/tiles/hoodedmoss.xml`、`um_floodwater.xml`）——做新地皮零美术成本。这是整个 DST mod 社区里最完整的自定义地皮方案。

### 技巧 2：postinit 清单集中管理（init_postinit.lua）

56 个组件补丁 + 152 个 prefab 补丁 + 状态机/大脑/类补丁全部由一张清单表驱动，配置项做条件插入，循环 modimport。要加补丁 = 清单加一行 + 建一个同名文件。**文件系统与清单表一一镜像**，任何补丁都能在 10 秒内定位。大规模 mod 的组织典范。

### 技巧 3：UpvalueHacker 取闭包上值

用 `debug.getupvalue` 追踪函数链，直接拿到 Klei 闭包内部的局部表（如 `writeables.makescreen` 的 `kinds`），往里面塞自己的条目。**不需要改原文件就能扩展被闭包锁死的配置**。配合 `debug.setupvalue` 还能注入替换函数。

### 技巧 4：组件包装三件套（存原函数 → 前置拦截 → 兜底透传）

`local _Old = self.Fn; function self:Fn(...) ... return _Old(self, ...) end` 在 health/combat/actions/recipes/containers 里用了几百次。配合 `local env = env; GLOBAL.setfenv(1, GLOBAL)` 双环境技巧，代码既干净又不会污染 GLOBAL。

### 技巧 5：世界组件模式驱动全图天气系统

天气系统不做实体，而是 `AddPrefabPostInit("forest"/"cave")` + `TheWorld:AddComponent("um_heatwaves")`。全图系统 = 世界 prefab 上的组件，天然拥有全局作用域、OnSave/OnLoad、timer 组件支持。跨 shard 同步用 `SendModRPCToShard` + `AddShardModRPCHandler` + 世界 tag（`TheWorld:AddTag` + `TheWorld.net:AddTag`）双通道。这个"服务器 tag + 网络 tag + 事件"三合一状态传播模式极干净。

---

## 6. 可复用的模板代码

### 模板 A：新地皮完整四件套（复制可用）

**A1. tile_adder.lua 修改**：把 AddTile 函数复制进你的 mod（230 行，直接复用，无需改动）。

**A2. modworldgenmain.lua**：

```lua
AddTile("MYTILE", "LAND", { ground_name = "mytile", old_static_id = 103 },
    {   -- 地表规格
        name = "mytile.tex",                    -- 纹理名（放 levels/tiles/ 或引用原版）
        atlas = "mytile.xml",                   -- 图集 XML（levels/tiles/mytile.xml）
        noise_texture = "noise_mytile.tex",     -- 噪声（levels/textures/）
        runsound = "dontstarve/movement/walk_grass",
        ...colors...
    },
    {   -- 小地图规格
        name = "mytile.tex",
        atlas = "mytile.xml",
        noise_texture = "mini_noise_mytile.tex",
    },
    {   -- 可采集 turf
        name = "mytile", anim = "mytile", bank_build = "myturf" },
)
```

**A3. levels/tiles/mytile.xml**（复用原版纹理的关键格式）：

```xml
<Atlas>
    <Texture filename="data/levels/tiles/deciduous.tex" />
    <Elements>
        <Element name="01" u1="0.00390625" u2="0.12890625" v1="0.12890625" v2="0.25390625" variant="" />
    </Elements>
</Atlas>
```

**A4. 挂载任务/房间**：

```lua
-- modworldgenmain.lua
AddTaskSetPreInitAny(function(task_set)
    -- 或 AddTask 定义新任务，room_bg = WORLD_TILES.MYTILE
end)
Layouts["mytown"] = StaticLayout.Get("map/static_layouts/mytown")
```

### 模板 B：新组件 + 世界组件天气系统（复制可用）

```lua
-- scripts/components/myweather.lua
local MyWeather = Class(function(self, inst)
    self.inst = inst
end)

function MyWeather:OnUpdate(dt)
    if self.inst:HasTag("myweather_ready") then
        self:TriggerEvent()
    end
end

function MyWeather:TriggerEvent()
    local x, y, z = self.inst.Transform:GetWorldPosition()
    local ents = TheSim:FindEntities(x, y, z, 50, {"player"}, {"playerghost"})
    if #ents > 0 then
        TheWorld:PushEvent("myweatherevent", { targets = ents })
    end
end

function MyWeather:OnSave() return {} end
function MyWeather:OnLoad(data) end

return MyWeather
```

```lua
-- init 接线（条件开关 + 服务器/洞穴 + 兼容检测）
if GetModConfigData("myweather") then
    AddPrefabPostInit("forest", function(inst)
        if TheWorld.ismastersim then
            inst:AddComponent("myweather")
            inst:DoPeriodicTask(10, function() inst.components.myweather:OnUpdate() end)
        end
    end)
end
```

### 模板 C：组件包装（最常用，复制可用）

```lua
local env = env
GLOBAL.setfenv(1, GLOBAL)

env.AddComponentPostInit("health", function(self)
    if not TheWorld.ismastersim then return end

    local _DoDelta = self.DoDelta
    function self:DoDelta(amount, overtime, cause, ignore_invincible, afflicter, ignore_absorb, ...)
        if amount < 0 and self.inst:HasTag("mytag") then
            return _DoDelta(self, amount * 0.5, overtime, cause, ignore_invincible, afflicter, ignore_absorb, ...)
        end
        return _DoDelta(self, amount, overtime, cause, ignore_invincible, afflicter, ignore_absorb, ...)
    end
end)
```

### 模板 D：新动作（复制可用）

```lua
-- init/init_actions.lua 追加
local myact = AddAction("MY_ACTION", GLOBAL.STRINGS.ACTIONS.MY_ACTION, function(act)
    if act.doer and act.target and act.target.components.mine ~= nil then
        act.target.components.mine:DoSomething(act.doer)
        return true
    end
end)
myact.priority = HIGH_ACTION_PRIORITY
myact.rmb = true
myact.distance = 2
myact.mount_valid = false

AddComponentAction("USEITEM", "myitem", function(inst, doer, target, actions, right)
    if target and target:HasTag("mytarget") then
        table.insert(actions, GLOBAL.ACTIONS.MY_ACTION)
    end
end)

-- 别忘了（同一文件内）给玩家状态机挂 handler：
AddStategraphActionHandler("wilson", GLOBAL.ActionHandler(GLOBAL.ACTIONS.MY_ACTION, "dolongaction"))
AddStategraphActionHandler("wilson_client", GLOBAL.ActionHandler(GLOBAL.ACTIONS.MY_ACTION, "dolongaction"))
```

### 模板 E：新容器（复制可用）

```lua
-- init/init_containers.lua 追加
modparams.mybackpack =
{
    widget =
    {
        slotpos = {},
        slotbg = { { image = "inv_slot_morsel.tex" } },
        animbank = "ui_icepack_2x3",
        animbuild = "ui_icepack_2x3",
        pos = Vector3(-5, -70, 0),
    },
    issidewidget = true,
    type = "pack",
}
for y = 0, 2 do
    table.insert(modparams.mybackpack.widget.slotpos, Vector3(-162, -75 * y + 75, 0))
    table.insert(modparams.mybackpack.widget.slotpos, Vector3(-162 + 75, -75 * y + 75, 0))
end

-- 在 containers.widgetsetup 包装函数里，你的 prefab 名会命中 modparams 分支
```

### 模板 F：新 Boss 骨架（复制可用）

```lua
local brain = require "brains/mybossbrain"

local function OnAttacked(inst, data)
    inst.components.combat:SetTarget(data.attacker)
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddSoundEmitter()
    inst.entity:AddNetwork()

    MakeCharacterPhysics(inst, 1000, 1)
    inst.Transform:SetFourFaced()

    inst:AddTag("monster")
    inst:AddTag("hostile")
    inst:AddTag("epic")
    inst:AddTag("boss")
    inst:SetPristine()

    if not TheWorld.ismastersim then return inst end

    inst:AddComponent("health")
    inst.components.health:SetMaxHealth(20000)
    inst:AddComponent("combat")
    inst.components.combat:SetDefaultDamage(100)
    inst.components.combat:SetAttackPeriod(3)
    inst.components.combat:SetRange(4)
    inst:AddComponent("lootdropper")
    inst.components.lootdropper:SetLoot({ "myitem", "myitem2" })
    inst:AddComponent("sleeper")
    inst:ListenForEvent("attacked", OnAttacked)
    inst:DoPeriodicTask(10, function() -- 技能计时器
        if inst.components.combat.target then
            inst.components.combat:DoAttack(inst.components.combat.target)
        end
    end)

    inst:SetBrain(brain)
    inst:SetStateGraph("SGmyboss")
    return inst
end

return Prefab("myboss", fn, assets)
```

### 模板 G：新烹饪配方（复制可用）

```lua
-- scripts/um_preparedfoods.lua 表内追加（然后由 init 遍历注册）
mypie =
{
    test = function(cooker, names, tags)
        return names.myfruit and tags.egg and tags.egg >= 1 and not tags.meat
    end,
    hunger = 75, health = 20, sanity = 15,
    foodtype = FOODTYPE.VEGGIE,
    perishtime = TUNING.PERISH_SLOW,
    priority = 10, weight = 30, cooktime = 1.8,
    floater = { "med", 0.05, 0.65 },
    oneatenfn = function(inst, eater)
        eater.components.debuffable:AddDebuff("buff_mypie", "buff_mypie")
    end,
    card_def = { ingredients = { { "myfruit", 1 }, { "bird_egg", 1 } } },
}
```

---

## 7. 附：其他值得记的细节

1. **`RemapSoundEvent`**（modmain.lua 35-38 行 / init_assets.lua 第 1 行起）：把原版音乐/音效事件替换成 mod 自己的 fsb 声音——无需改任何代码，一行换一个声音。
2. **加载提示系统**（init_loadingtips）：UM 有自己的一套 Loading tips。
3. **描述文件**：`scripts/descriptors/` 里是 components 描述文件（`descriptors.mylogic.lua` 给组件做 description 描述，用于 client 端）。
4. **`wixie_shove.lua`**：角色专属机制的独立根目录脚本。
5. **generatorcharging.lua**：发电机充电（Winona 新发电机系统）。
6. **`umss_tables.lua`**：技能树字符串表（wixie_skilltree_strings.lua 对应）。
7. **`capture_output.json` / `example_modularsetpiece.json`**：mod 自带的开发辅助文件，说明作者用工具生成 setpiece。
8. **`messagebottletreasures_um.lua`**（597 行）：漂流瓶宝藏扩展，格式 `{ prefab = "xx", weight = X }` 表驱动。
9. **代码风格惯例**：所有新 prefab 名带 `um_` 前缀；自定义组件也带 `um_` 前缀（um_heatwaves、um_stormspawner）；系统组件名简洁（ratcheck）。
10. **兼容性代码**：`ia_check = GLOBAL.KnownModIndex:IsModEnabled("workshop-1467214795")`（init_tuning.lua）——检测特定 mod 是否启用，启用时调整自己的行为（Island Adventures 兼容）。
11. **角色衣服适配**：modmain.lua 278-282 行，把 walter 的 `symbol_overrides_by_character` 复制给 wixie（新角色穿旧衣服的 symbol 覆写）。
12. **`GLOBAL.TUNING.DSTU` 是全部 mod 配置的运行时映射表**（init_tuning.lua），任何代码里直接 `TUNING.DSTU.XXX` 取配置值，比到处调 GetModConfigData 高效。

---

## 8. 文件索引（按主题速查）

| 主题 | 文件 |
|---|---|
| 地皮系统 | `tile_adder.lua`、`modworldgenmain.lua`、`levels/tiles/*.xml`、`init/init_assets.lua`(turf) |
| postinit 组织 | `init/init_postinit.lua`、`postinit/**`、`wixie_postinit/**` |
| 动作系统 | `init/init_actions.lua`、`init/init_strings.lua`(STRINGS.ACTIONS) |
| 容器系统 | `init/init_containers.lua`、`scripts/um_pocketdimensioncontainers.lua` |
| 天气 | `init/init_harder_weather.lua`、`init/init_smog.lua`、`init/init_snowstorm.lua`、`scripts/components/um_heatwaves.lua`、`um_stormspawner.lua`、`snowstormwatcher.lua` |
| 鼠灾 | `init/init_ratraid.lua`、`scripts/components/ratcheck.lua` |
| 烹饪 | `scripts/um_preparedfoods.lua`、`init/init_crockpot.lua`、`init/init_foodregen.lua`、`init/init_food/*` |
| 配方 | `init/init_recipes.lua` |
| 皮肤 | `skins_api.lua`、`uncompskins_api.lua` |
| 角色 | `scripts/prefabs/wixie.lua`、`wixie_postinit/**`、`init/init_character_changes/**`、`scripts/speech_*.lua` |
| Boss | `scripts/prefabs/hoodedwidow.lua`、`uncompromising_toad.lua`、`scripts/stategraphs/SGhoodedwidow.lua`、`scripts/brains/hoodedwidowbrain.lua` |
| 世界生成 | `scripts/map/tasks/*.lua`、`scripts/map/rooms/forest/*.lua`、`scripts/map/static_layouts/*.lua` |
| WX-78 模块 | `scripts/um_wx78_moduledefs.lua` |
| 控制台命令 | `scripts/uncompromisingcommands.lua` |
| HUD | `scripts/widgets/vetcursewidget.lua`、`widgets/zero_insanity_overlay.lua`、`init/init_widgets.lua` |
| 特色植物 | `scripts/prefabs/`（清单见 4.1）：`um_pyre_nettles.lua`、`blueberryplant.lua`、`hooded_mushtree.lua`、`riceplant.lua`、`snapdragon.lua`、`whisperpod.lua`、`um_sorrel.lua`、`giant_tree.lua`、`kelpstack.lua` 等 |
| 特色地形/布局 | `scripts/map/tasks/*.lua`（GiantTrees/RiceSqueltch/SunkDecid/ratacombs）、`scripts/map/static_layouts/*.lua`（hooded_town/rose_garden/ratkinggate 等，见 4.3） |
| 植物美术 | `anim/*.zip`（内嵌 atlas-0.tex KTEX/DXT5）、`levels/tiles/*.tex+xml`、`levels/textures/noise_*.tex`（分析见 4.5） |
| 工具 | `scripts/tools/upvaluehacker.lua`、`scripts/tools/um_commonfns.lua` |

（完）
