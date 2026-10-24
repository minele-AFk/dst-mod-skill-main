# Tropical Experience（热带体验）mod 技术笔记

> 精读对象：`E:\神秘复苏\饥荒大型mod\1505270912\`（约3485个文件、1657个lua）
> modinfo.lua 实名：**Tropical Experience | SW HAM Biomes : From Beyond**
> 作者：Vagner da Rocha Santos（巴西人，代码里有葡萄牙语注释 `--tempo para renascer em dias`、`--adicionado por vagner`）
> 版本：v3.9.11，priority = -20
> 本质：把单机版**海难 DLC（Shipwrecked）+ 哈姆雷特 DLC（Hamlet）+ 熔炉（Forge）+ 盛宴/戈奇（Gorge/Quagmire）**的内容整体移植进 DST 的巨型 mod。冰霜岛屿内容灵感来自 Uncompromising Mode（mod 内注释标 `--umcompromissing`，且检测 `workshop-2039181790` 是否启用以插入 `GiantTrees` 任务）。
> 本文是技能文档原始材料，代码片段均原样复制自 mod 文件并标注出处。

---

## 目录

1. [mod 全貌](#1-mod-全貌)
2. [框架架构](#2-框架架构)
3. [关键设计模式](#3-关键设计模式)
4. [亮点技术](#4-亮点技术)
5. [可复用的模板代码](#5-可复用的模板代码)
6. [特色岛屿/植物/地形专题](#6-特色岛屿植物地形专题)（用户点名专题）

---

## 1. mod 全貌

### 1.1 身份与规模

- 世界种类由 `kindofworld` 配置决定（modinfo.lua 60+ 配置项之一）：
  - `5` = 哈姆雷特世界（Porkland，猪镇+雨林+平原）
  - `10` = 海难世界（Shipwrecked，岛屿+海洋+火山）
  - `15` = 自定义/火山世界（TROPICAL 系列任务，salasvolcano/salasbeach/salasjungle 房间池）
  - `20` = 域外海洋世界（OceanWorld，全海图）
- 顶级配置项（modinfo.lua）：`continentsize`、`howmanyislands`（岛数量）、`Shipwreckedworld_plus`、`frost_islandworld`、`Moonshipwrecked`、`tropicalshards`（跨世界碎片开关，0/30=lobby）、`startlocation`、`Volcano`、`forge`、`underwater`（水下世界）、`hamlet_caves`、`togethercaves_*`、`Waves`、`whirlpools`、`kraken`、`octopusking`、`mangrove`、`lilypad`、`shipgraveyard`、`coralbiome`、`bosslife`、`flood`、`wind`、`hail`、`volcaniceruption`、`fog`、`hayfever`、`automatic_disembarkation`、`boatlefthud`、`disablecharacters`、`enableallprefabs` 等。
- 文件分布：`scripts/prefabs` 1002 个、`scripts/components` 149 个、`scripts/stategraphs` 168 个、`scripts/brains` 129 个、`scripts/widgets`+`screens` 若干、`scripts/tools` 7 个、`scripts/Languages` 15 个（stringsCh 404KB 等）、`scripts/map/static_layouts` 80+ 个 Tiled 格式静态布局。

### 1.2 核心系统清单

| 系统 | 说明 |
|---|---|
| 海难移植 | 岛屿世界生成、船（raft/log/boat）、海浪、龙卷风（twister）、虎鲨、鲸鱼、克拉肯（kraken）、章鱼王（octopusking）、毒系统、湿度、氧气/潜水 |
| 哈姆雷特移植 | 猪城（pig_city）、商店经济（oinc/猪币）、房间系统（室内相机）、野猪王（wildboreking）、蛇王（pugalisk）、蚁后、Aporkalypse 血月 |
| 水下世界 | 水下 tile（underwater_sandy/rocky）、氧气系统（oxygen 组件群）、水下生物群系、海王（gnarwail） |
| 熔炉/盛宴移植 | TFWP 武器套件（9参数 CustomPrefab 工厂）、Gorge 食谱/烹饪（gorge_foods.lua 70 食谱）、Quagmire 货币经济 |
| 女神内容包 | goddess 系（喷泉→传送门→湖→鹿驯养→祭坛→法杖闭环）、windy1-5 套装标签组合 |
| 新世界生成 | 4 分支世界、445 个 AddTask、29 个新地皮 tile、80+ 静态布局 |
| 多语言 | stringsCh/EU/RU/FR/HUN/IT/KO/PT/SP 等 15 个语言文件（每个 200-400KB） |

---

## 2. 框架架构

### 2.1 modmain.lua（5515 行）骨架

**开头 env 劫持**（第一行，本 mod 所有文件通用的地基）：

```lua
GLOBAL.setmetatable(env, { __index = function(t, k) return GLOBAL.rawget(GLOBAL, k) end })
```

此后整个 modmain 内的裸标识符（AddPrefabPostInit、TUNING、GROUND...）全部自动回落到 GLOBAL。

**PrefabFiles 条件注册**（L1-272）：按配置项把对应 prefab 文件插入 `PrefabFiles` 表：

```lua
if GetModConfigData("whirlpools") then
    table.insert(PrefabFiles, "whirlpool")
end

table.insert(PrefabFiles, "pigbanditexit")
if GetModConfigData("tropicalshards") ~= 0 then
    table.insert(PrefabFiles, "porkland_sw_entrance")
end

if GetModConfigData("kindofworld") == 10 or GetModConfigData("raftlog") then
    table.insert(PrefabFiles, "boatraft_old")
    table.insert(PrefabFiles, "boatlog_old")
end
table.insert(PrefabFiles, "boatraft")
```

**TUNING.tropical 配置聚合**（L628-653）：

```lua
TUNING.tropical = {
    kindofworld                = GetModConfigData("kindofworld"),
    howmanyislands             = GetModConfigData("howmanyislands"),
    bosslife                   = GetModConfigData("bosslife"),
    tropicalshards             = GetModConfigData("tropicalshards"),
    ...
}
```

**关键 GLOBAL 扩展**：
- `GLOBAL.EQUIPSLOTS.BARCO` —— 自定义船装备槽（巴葡语 "barco"=船）
- 新 RECIPETABS：`OBSIDIANTAB` / `CITY` / `HOME` / `GODDESSTAB` / `GORGE`（含 `crafting_station = true` 的 GORGE 用法）
- 新 FUELTYPE / MATERIALS / TOOLACTIONS
- `TECH.AVAILABLE_TECH` + `PROTOTYPER_TREES` 扩展、`AddPrototyperDef`
- 18 处 `AddPrefabPostInit`（改造原版生物/物品）
- builder 组件 oinc 货币全量重写（L4614-5122）
- 书架系统（L5124-5244，inventoryitem 扩展）
- 自动上下船（L5246-5332）
- 哈姆雷特云海着色器（L5407-5461）

**尾部 modimport 汇总**（L5463-5515）：

```lua
modimport "postinit/components/birdspawner"
modimport "postinit/components/butterflyspawner"
modimport "postinit/components/drownable"
modimport "postinit/components/hounded"
modimport "postinit/components/map"
modimport "postinit/components/plantregrowth"
modimport "postinit/components/spooked"
modimport "main/error_prevent"
```

### 2.2 目录职能分工

| 目录 | 职能 |
|---|---|
| `modworldgenmain.lua`（28006行） | 世界生成全量：4 分支、445 AddTask、LOCKS/KEYS 扩展、StartLocation、ocean 房间、LevelPreInit/TasksetPreInit |
| `tileadder.lua` + `tiledescription.lua` | 新地皮 tile 注册（29 个）与描述表 |
| `scripts/main/` | assets.lua（资源清单）、containers.lua（容器参数）、error_prevent.lua（报错拦截） |
| `scripts/postinit/components/` | 8 个原版组件 PostInit（birdspawner/butterflyspawner/drownable/hounded/map/plantregrowth/spooked + 其他） |
| `scripts/functions/` | DataProvider.lua、MagicStore.lua（数据/商店存储） |
| `scripts/tools/` | utils.lua（FnDecorator 等 686 行）、upvaluehelper.lua（冰冰羊）、spawnutil.lua（世界生成工具）、physics.lua（FnDecorator on SetVel/Teleport）、loadutils.lua（Runar 热重载）、tableutil.lua、waffles1.lua（俄罗斯核心） |
| `scripts/map/` | graph.lua、static_layouts/（80+ Tiled 格式布局） |
| `scripts/Languages/` | 15 个语言文件 |

### 2.3 世界生成挂钩（modworldgenmain.lua）

```lua
AddGlobalClassPostConstruct("map/storygen", "Story", function(self)
	for k, v in pairs(MapTags) do
		self.map_tags.Tag[v] = function(tagdata) return "TAG", v end
	end
end)
local MapTags = { "frost", "hamlet", "tropical", "underwater", "folha" }
```

新增 5 个地图 TAG，配合 `area_aware` 组件的 `CurrentlyInTag("tropical"/"hamlet"/"frost"/"nohasslers")` 做区域感知。

---

## 3. 关键设计模式

### 3.1 原版系统改造模式（三层递进 hack 手法，来自 scripts/postinit/）

1. **方法级包装（最温和）**：`AddComponentPostInit` 保存旧方法后替换（birdspawner、hounded 部分）。
2. **装饰器工具（工具化）**：`FN.FnDecorator(obj, key, beforeFn, afterFn)` 统一"前置拦截/后置改写/跳过原函数"（drownable、map）。
3. **upvalue 注入（最暴力）**：`debug.getupvalue/setupvalue` 沿闭包链改内部局部函数/表（butterflyspawner 替换闭包内 SpawnButterflyForPlayer、hounded 改 _spawndata 表、map 改 GOODOCEANARENAPOINTS 常量）。

FN.FnDecorator 核心实现（scripts/tools/utils.lua，绯世行）：

```lua
function FN.FnDecorator(obj, key, beforeFn, afterFn, isUseBeforeReturn)
    local oldVal = obj[key]
    obj[key] = function(...)
        local retTab, isSkipOld, newParam, r
        if beforeFn then retTab, isSkipOld, newParam = beforeFn(...) end
        if type(oldVal) == "function" and not isSkipOld then
            if newParam ~= nil then r = { oldVal(unpack(newParam)) }
            else r = { oldVal(...) } end
            if not isUseBeforeReturn then retTab = r end
        end
        if afterFn then retTab = afterFn(retTab, ...) end
        if retTab == nil then return nil end
        ...
    end
end
```

约定：**beforeFn 返回 `{假返回值}, true` 即跳过原函数**；afterFn 收 `rets` 表改写返回值。

upvalue 链查找（utils.lua）：

```lua
function FN.ChainFindUpvalue(fn, ...)
    local val = fn
    local i
    for _, name in ipairs({ ... }) do
        val, i = FN.FindUpvalue(val, name)
        if i == nil then return nil end
    end
    return val
end
```

配套 `HideFn`（把被 hook 的函数映射进 `GLOBAL.UpvalueHackerHiddenFns` 防止重复 hook）、`ListenForTableVal`（proxyTable + `__index/__newindex` 元表代理监听表变化）。

### 3.2 地皮/地形注册模式（tileadder.lua）

- 顶部 `modimport 'tiledescription.lua'` 取 `SetInfo()` 描述表，`minStartID = 33`（1-32 留给原版）。
- 为每个 tile 自动分配自增 ID，并检测冲突（含 MultiWorlds mod 的 50-67 保留段）：

```lua
local numid = minStartID
local j = 1
while chk do
    chk = false
    for _, val2 in pairs (tiledefs.ground) do
        if val2[1] == numid or (is_multiworlds_enabled and numid >= 50 and numid < 68) then
            numid = numid + 1
            chk = true
        end
    end
end
```

- 三表同步：`GROUND[string.upper(tilename)] = numid`、`GROUND_NAMES[numid] = tilename`、`GROUND_FLOORING[numid] = data.isfloor`。
- 每个 tile 带默认地图规格（name/runsound/walksound/snowsound/mudsound/flashpoint_modifier/四色 colors），`tiledefs.ground` 按 layer 插入（`table.insert(tiledefs.ground, layer, { numid, realMapspecs })`）。
- `GroundImage/GroundAtlas` 把新 tile 映射到原版纹理图集（beach→levels/tiles/beach.tex、jungle→jungle.tex、deeprainforest→deeprainforest.tex 等），找不到才回落 `"levels/tiles/" .. name`。

### 3.3 LOCKS/KEYS 自动扩展（modworldgenmain.lua L36-183）

原版 `LOCKS`/`KEYS` 是数值，遍历找当前最大值后从 `max+1` 连续分配新锁：

```lua
local locks = 1
for _, v in pairs(LOCKS) do
	if v >= locks then locks = v + 1 end
end
local keys = 1
for _, v in pairs(KEYS) do
	if v >= keys then keys = v + 1 end
end

LOCKS.JUNGLE_DEPTH_1 = locks
KEYS.JUNGLE_DEPTH_1 = keys
LOCKS_KEYS[LOCKS.JUNGLE_DEPTH_1] = { KEYS.JUNGLE_DEPTH_1 }
LOCKS.JUNGLE_DEPTH_2 = locks + 1
KEYS.JUNGLE_DEPTH_2 = keys + 1
LOCKS_KEYS[LOCKS.JUNGLE_DEPTH_2] = { KEYS.JUNGLE_DEPTH_2 }
-- ... CIVILIZATION_1..3、LAND_DIVIDE_5、SACRED 等
```

### 3.4 新配方/科技树模式

- 新 RECIPETABS：`GLOBAL.RECIPETABS['GORGE'] = { str = "GORGE", sort = 94, icon = "tab_portal_key.tex", icon_atlas = "images/tabs.xml", crafting_station = true }`
- `AddRecipeFilter` 6 个新过滤器：NAUTICAL / OBSIDIAN / LEGACY / INTERIOR / CITY / GORGE（scripts/recipes.lua 910 行，约 250 个 SortAfter/SortBefore）
- 新科技树（custom_tech_tree.lua `AddNewTechTree` 8 步：TECH 常量 → AVAILABLE_TECH → PROTOTYPER_TREES → builder → builder_replica → prototyper → player_classified → recipepopup 全链路）
- 手动版（modmain L1234-1360）：`TUNING.PROTOTYPER_TREES.OBSIDIAN_ONE = TechTree.Create({ OBSIDIAN = 1 })` + `AddPrototyperDef("quagmire_portal_key", { action_str = "GORGE", icon_image = "tab_portal_key.tex", icon_atlas = "images/tabs.xml", is_crafting_station = true })`

### 3.5 商店经济模式（oinc 货币）

- `economy.lua` 的 `TRADER` 表驱动：pigman_collector 收垃圾给 oinc×3、banker 给 oinc10、queen 给 key_to_city。
- `shop_pedestals.lua`（916 行）：货架 restock 逻辑、`OverrideSymbol("SWAP_SIGN"/"SWAP_COST")` 显示价格、`teleporter.hamlet = true` 镇内传送。
- 客户端购物走 ModRPC：`SendModRPCToServer(GetModRPC("ServerStore", "Purchased"/"ShutStore"), ...)`。
- `ModStoreData.lua`：CoinsPrefab/GoodsPrefab 96 种商品。
- builder 组件 oinc 货币重写（modmain L4614-5122）：制作消耗 oinc。

### 3.6 分段 Boss 模式（multibody 组件）

pugalisk（蛇王，PUGALISK_HEALTH 10000×bosslife）：`multibody:Setup(5, "pugalisk_body")` 五段身体，头部 SG 驱动（SGpugalisk_head），尾部通过 `HasTag("tail")` 分流 death 事件：

```lua
EventHandler("death", function(inst)
    if inst:HasTag("tail") then
        inst.sg:GoToState("tail_exit")
    else
        if inst.sg:HasStateTag("underground") then
            inst.sg:GoToState("death_underground")
        else
            inst.sg:GoToState("death")
        end
    end
end),
```

移动：`startmove` 状态 PushEvent("startmove") → prefab 侧 `components.multibody:SpawnBody(inst.angle,0.3,pos)` 生成蛇身 → `underground` 状态 Hide+Physics:SetActive(false) 潜入地下。

### 3.7 水下系统模式

- 水下 tile：`GROUND.UNDERWATER_SANDY / UNDERWATER_ROCKY`（cave 纹理 + layer 5）。
- 氧气组件群：oxygen（玩家氧气条，net_byte 同步）、oxygenapparatus/oxygenitem/oxygensupplier（供氧设备）、氧气泡。
- 水下生物限制组件：`UnderwaterSpawner`、`creeps.lua`（574 行：每个角色按 prefab 配氧气上限、水下刷怪器挂在 cave、水下 tile 的 Ignite 覆盖、AddIngredientValues）。
- 水下判定宏（10+ 处复用）：

```lua
if ground == GROUND.UNDERWATER_SANDY or ground == GROUND.UNDERWATER_ROCKY or
   (ground == GROUND.BEACH and TheWorld:HasTag("cave")) or ... then
```

- 水下 UI：oxygenbadge.lua（`Badge._ctor` 氧气表，naagua 5 点取样）、oxygendisplay.lua（AddClassPostConstruct widgets/statusdisplays，oxydelta 事件 PulseGreen/Red）。

### 3.8 多语言系统

`local STRINGS = GLOBAL.STRINGS` + 按 DLC 分节注释（`--SW`/`--HaM`/`--Forge`）的巨型 STRINGS 表；`notusedscripts.lua`（64791 行）是纯翻译文件不是禁用列表。语言切换由 `set_idioma` 配置控制。

### 3.9 AI 行为模式（stategraphs/brains/behaviours 168+129+9 个文件）

**Brain 组织纪律**：PriorityNode 顶层顺序 = 恐慌类（PanicHaunted/OnFire）→ 紧急战斗（AttackMomentarily/Dodge）→ 专属任务（工作/补货/送礼）→ 跟随（Follow/FaceEntity）→ 日常（day/night WhileNode）→ 兜底（Wander/Leash），`.25/.5` 为重评估秒数。

**WhileNode 条件互斥模拟状态机**（primeapebrain.lua 注释即优先级说明）：

```lua
WhileNode(function() return self.inst.components.combat.target and self.inst.components.combat.target:HasTag("player") and self.inst.HasAmmo(self.inst) end, "Attack Player",
    SequenceNode({
        ActionNode(function() EquipWeapon(self.inst, self.inst.weaponitems.thrower) end, "Equip thrower"),
        ChaseAndAttack(self.inst, MAX_CHASE_TIME, MAX_CHASE_DIST),
    })),
WhileNode(function() return self.inst.components.combat.target and self.inst.components.combat.target:HasTag("player") and not self.inst.HasAmmo(self.inst) end, "Pick Up Poop",
    DoAction(self.inst, GetPoop)),
```

**SG 三段式**：pre（蓄力）→ loop（onupdate/ontimeout 持续效果）→ pst（收尾），twister 的 vacuum/waves、pugalisk 的 gaze、shadowwaxwell 的 lunge 全部如此。计时器三件套：`sg:SetTimeout(x)+ontimeout`、`inst:DoTaskInTime`、`components.timer:StartTimer/TimerExists`（跨状态 CD）。

**自定义 BehaviourNode**：`Class(BehaviourNode, ...)` + Visit() 内 READY→RUNNING→SUCCESS/FAILED 状态机 + `self:Sleep(x)` 节流 + `__tostring()`；与 SG 交互靠 PushEvent（startcheer/victorypose/seekoblivion）和 `inst.__brain` 反向引用。

**双人 Boss 同步**（rhinodrill，bro 字段）：`bro_is_cheering = inst.bro and inst.bro.sg.currentstate.name == "cheer_loop"` + `wants_to_cheer` 队列 + `SetBuffLevel(inst.bro_stacks + 1)`。

### 3.10 传送/室内系统模式

- 室内房间：入口 → `TheWorld.components.contador:Increment(1)`（房间 ID 计数器）→ 墙体循环 → 4 部分 prefab 注册 → 双向 teleporter 配对（`inst.components.teleporter.targetTeleporter = "goddess_gate1"` 式）。
- `interactions` 组件：BoatJump/BoatDismount 8 槽位转移。
- 跨世界：`teleportato2`（1900 行，熔炉 Boss 传送门）、`gorge_portal`（DoTaskInTime(1) 遍历 Ents 互设 targetTeleporter）、`porkland_sw_entrance`（海难↔哈姆雷特碎片传送门，tropicalshards 配置）。

### 3.11 自定义 Action 模式

scripts/actions.lua（6761 行，原版 action 全量重写）：

- 字符串参数版：`AddAction("BOATMOUNT", ...)` 与对象版 `GLOBAL.Action({priority, rmb, distance, mount_valid})` 混用。
- BOATMOUNT：priority 10、distance 8、`EQUIPSLOTS.BARCO` 拷贝船装备。
- SHOP action：`stroverridefn` 显示 "Buy X for N oincs" + shopkeeper_speech。
- 同名覆盖原版 action（PICKUP 带 id="PICKUP" 完整重写 + shelfer 付费）。
- `AddComponentAction` SCENE 钩子：hackable/melter/workable/dislodgeable/shopped 等。

### 3.12 prefab 工厂模式

- **多 prefab 单文件**：`return Prefab(name, fn, assets, prefabs)` 返回多个（grass_tall 返回 9 个、goddess_flute 4 个、groundlifts 5 个、gnarwailunderwater 5 个、grotto_parsnip 4 个）。
- **参数化工厂**：`createbush(name, inspectname, berryname, master_postinit)`（coffeebush）、`MakeVegStats`（veggies）、`MakeHat`（new_hats 9 个帽子）、`MakeCritter`（goddess_hound）、`makestafflight`（goddess_star）。
- **TFWP 9 参数 CustomPrefab**：`CustomPrefab(name, fn, assets, prefabs, init, inventory_image, tuning_table, swap_build, arms_symbol)`。
- **物品三件套**：`inventoryitem.atlasname` + 自定义字段 `inst.caminho`（同值图集路径）+ `inst.Transform:SetScale`，图集集中在 volcanoinventory.xml / hamletinventory.xml / inventoryimages2.xml。

### 3.13 守卫仇恨插入模板（grass.lua/flower.lua 等反复出现）

```lua
local tiletype = TheWorld.Map:GetTile(TheWorld.Map:GetTileCoordsAtPoint(pt:Get()))
if tiletype == GROUND.SUBURB or tiletype == GROUND.FOUNDATION or tiletype == GROUND.COBBLEROAD or tiletype == GROUND.LAWN or tiletype == GROUND.FIELDS then
    if worker and worker:HasTag("player") and not worker:HasTag("sneaky") then
        local eles = TheSim:FindEntities(x,y,z, 40,{"guard"})
        for k,guardas in pairs(eles) do
            if guardas.components.combat and guardas.components.combat.target == nil then guardas.components.combat:SetTarget(worker) end
        end
    end
end
```

即：玩家在城镇地面采集 → 40 范围内 guard 标签守卫仇恨玩家。城镇保护语义。

### 3.14 潮汐判定/水下边界宏（10+ 处复用，lotus.lua 完整版）

```lua
local function IsWater(tile)
	return tile == GROUND.OCEAN_COASTAL or
		tile == GROUND.OCEAN_COASTAL_SHORE or
		tile == GROUND.OCEAN_SWELL or
		tile == GROUND.OCEAN_ROUGH or
		tile == GROUND.OCEAN_BRINEPOOL or
		tile == GROUND.OCEAN_BRINEPOOL_SHORE or
		tile == GROUND.OCEAN_WATERLOG or
		tile == GROUND.OCEAN_HAZARDOUS
end
```

8 种海洋 tile 判定；lotus 还做了 4 方向 4 格"四周必须全是水"的地形自检（groundtest，任一方向非水则 Remove）。

### 3.15 船与步行平台检测

- `walkableplatform` 标签：`TheSim:FindEntities(x, 0, z, TUNING.MAX_WALKABLE_PLATFORM_RADIUS, {"walkableplatform"})` 判定船。
- `tiletracker` 组件：`SetOnWaterChangeFn` 水陆切换回调（ox/hippo/otter 等两栖生物），`ClearCollidesWith(COLLISION.LIMITS)` 允许水下穿越。
- 船类：boatraft/boatlog_old/boatraft（PrefabFiles 条件插入）、rowboatwakespawner（尾迹）、driver/driver2（驾驶）、boatbadge（HUD 船血条 widget，`Badge._ctor` boat_health）。
- `MakeWaterObstaclePhysics` 水上建筑物理（lobsterhole/mangrovetrees/mermboat）。

### 3.16 存档/同步小字段模式

- `net_float/net_bool/net_tinybyte/net_event` + 客户端 ListenForEvent（goddess_star `_pulsetime` 脉动、green_forcefieldfx `_lightframe/_islighton`、goldobi `_ispathfinding`、gw_bonestaff_proj `_killtail`、camera mode `net_tinybyte`、hayfever_replica `net_byte sneezetime`）。
- OnSave/OnLoad/OnPreLoad 自定义存档（grabbing_vine 存 spawnpatch.GUID + LoadPostPass 恢复、gw_column_angel 存 runes GetSaveRecord、grassgekko 变形状态 WorldSettings_Timer_PreLoad/PreLoad_Fix）。

---

## 4. 亮点技术

1. **env 元表 GLOBAL 回落**（modmain 第一行）：一行代码让整个 mod 文件裸写全局，极大降低移植成本，是巨型移植 mod 的地基。
2. **upvalue 链 hook 工具箱**（utils.lua + upvaluehelper.lua）：FnDecorator / ChainFindUpvalue / HideFn / ListenForTableVal 四件套，覆盖"包装方法→改闭包局部→监听表变化"全部改造需求；DX_GetUpvalue/DX_SetUpvalue 来自 BBGoat。
3. **多世界碎片跨世界传送**（tropicalshards）：sw_exit/sw_entrance/hamlet_exit/hamlet_entrance/lobby_exit 5 组静态布局 + porkland_sw_entrance prefab + `ACTIONS.JUMPIN.strfn` 覆盖（hamletteleport 标签→"HAMLET" 动作文案）——把单机 DLC 结构搬进 DST 分片世界。
4. **分段 Boss**（multibody + 头尾同 SG 分流）：pugalisk 10000×bosslife 血、twister 9000×bosslife + vacuum 组件 500 伤害 + SpawnWavesSW 360 度海浪——海难系 Boss 招牌招数函数被 3 个 SG 复用。
5. **net 字段客户端驱动动画**：用 net_float+DoPeriodicTask 做服务器权威的视觉同步（goddess_star 脉动），用 net_event 做弹道尾迹清理（gw_bonestaff_proj 隐藏实体+客户端每帧 UpdateTail）——性能与同步的折中模板。
6. **水下世界完整实现**：UNDERWATER_SANDY/ROCKY 双 tile + 氧气组件群 + 水下刷怪 + 水下生物群系任务（SandyBiome/ReefBiome/KelpBiome/RockyBiome/MoonBiome/OpenWaterBiome）+ 分层渲染（setdivelayering ANIM_SORT_ORDER_BELOW_GROUND.UNDERWATER）。
7. **游戏内世界分支选择**：kindofworld 一个配置项切 4 套完全不同的世界（哈姆雷特大陆/海难群岛/火山群岛/纯海洋），配合 AddStartLocation 与 LevelPreInit 全量覆写 level 字段（`level.overrides.keep_disconnected_tiles = true`、`level.overrides.roads = "never"`）。

---

## 5. 可复用的模板代码

### 5.1 SpawnWavesSW（海浪扇形生成，kraken/twister/whale 复用）

```lua
function SpawnWavesSW(inst, numWaves, totalAngle, waveSpeed, wavePrefab, initialOffset, idleTime, instantActive, random_angle)
	wavePrefab = wavePrefab or "rogue_wave"
	totalAngle = math.clamp(totalAngle, 1, 360)
    local pos = inst:GetPosition()
    local startAngle = (random_angle and math.random(-180, 180)) or inst.Transform:GetRotation()
    local anglePerWave = totalAngle/(numWaves - 1)
	if totalAngle == 360 then
		anglePerWave = totalAngle/numWaves
	end
    for i = 0, numWaves - 1 do
        local wave = SpawnPrefab(wavePrefab)
        local angle = (startAngle - (totalAngle/2)) + (i * anglePerWave)
        local rad = initialOffset or (inst.Physics and inst.Physics:GetRadius()) or 0.0
        local total_rad = rad + wave.Physics:GetRadius() + 0.1
        local offset = Vector3(math.cos(angle*DEGREES),0, -math.sin(angle*DEGREES)):Normalize()
        local wavepos = pos + (offset * total_rad)
        wave.Transform:SetPosition(wavepos:Get())
        local speed = waveSpeed or 6
        wave.Transform:SetRotation(angle)
        wave.Physics:SetMotorVel(speed, 0, 0)
        wave.idle_time = idleTime or 5
        if instantActive then
        	wave.sg:GoToState("idle")
        end
    end
end
```

### 5.2 可落地传送（ancient_hulk 的 teleport 函数）

```lua
local function teleport(inst)
    inst.teleporttime = nil
    local pt = Vector3(inst.Transform:GetWorldPosition())
    if inst.components.combat.target then
        pt = Vector3(inst.components.combat.target.Transform:GetWorldPosition())
    end
    local tile = TheWorld.Map:GetTileAtPoint(pt.x, pt.y, pt.z)
    if tile == GROUND.IMPASSABLE or tile == GROUND.INVALID or tile == GROUND.OCEAN_COASTAL or ... then
        pt = Vector3(inst.Transform:GetWorldPosition())
    end
    local theta = math.random() * 2 * PI
    local offset = nil
    while not offset do
        offset = FindWalkableOffset(pt, theta, 12 + math.random()*5, 12, true)
    end
    pt.x = pt.x + offset.x
    pt.z = pt.z + offset.z
    inst.Physics:SetActive(true)
    inst.Transform:SetPosition(pt.x,0,pt.z)
    inst.sg:GoToState("telportin")
end
```

### 5.3 抛物线跳跃（beetletaur body_slam / JumpToPosition）

```lua
local function JumpToPosition(inst, target_pos, total_frames)
    ToggleOffCharacterCollisions(inst)
    inst.sg:AddStateTag("nointerrupt")
    if target_pos then
        local starting_pos = inst:GetPosition()
        inst:ForceFacePoint(target_pos:Get())
        inst.Physics:SetMotorVel(math.sqrt(distsq(starting_pos.x, starting_pos.z, target_pos.x, target_pos.z)) / (total_frames * FRAMES), 0, 0)
    end
end
```

### 5.4 动画百分比插值位移（AncientRobot leap_attack）

```lua
onupdate = function(inst)
    local percent = inst.AnimState:GetCurrentAnimationTime () / inst.AnimState:GetCurrentAnimationLength()
    local xdiff = inst.sg.statemem.targetpos.x - inst.sg.statemem.startpos.x
    local zdiff = inst.sg.statemem.targetpos.z - inst.sg.statemem.startpos.z
    inst.Transform:SetPosition(inst.sg.statemem.startpos.x+(xdiff*percent),0,inst.sg.statemem.startpos.z+(zdiff*percent))
end,
```

### 5.5 波次召唤随血量推进（wildboreking 行为）

```lua
local MinionsWaves = {
    [1] = { prefab = "pigman_minion", n = 5 },
    [2] = { prefab = "pigman_minion", leaderprefab = "pigguard_minion", n = 10 },
    ...
    [8] = { prefab = "pigman_minion", leaderprefab = "pigguard_minion", hat = "ruinshat", leadershat = "ruinshat", leaderwere = true, allwere = true, n = 15 },
}
local function MakeWave(players, wave, rei)
    local health = self.inst.components.health:GetPercent()
    local n = math.ceil( (1-health) * (#MinionsWaves+0.1))
    ...
    if wave.leaderwere then
        leader.components.werebeast:SetWere(10000000)
        leader.components.combat:EngageTarget(GetRandomItem(players))
    end
```

### 5.6 运行时创建武器（goldmonkey 双武器）

```lua
local function EquipWeapons(inst)
    if inst.components.inventory ~= nil then
        local weapon = CreateEntity()
        weapon.entity:AddTransform()
        MakeInventoryPhysics(weapon)
        weapon.persists = false
        weapon:AddComponent("weapon")
        weapon.components.weapon:SetDamage(TUNING.GOLDMONKEY_DAMAGE)
        weapon.components.weapon:SetRange(TUNING.GOLDMONKEY_ATTACK_RANGE, TUNING.GOLDMONKEY_ATTACK_RANGE + 4)
        weapon.components.weapon:SetProjectile("goldmonkey_thrower")
        weapon:AddComponent("inventoryitem")
        weapon.components.inventoryitem:SetOnDroppedFn(weapon.Remove)
        weapon:AddComponent("equippable")
        inst.weapon = weapon
        inst.components.inventory:Equip(inst.weapon)
        inst.components.inventory:Unequip(EQUIPSLOTS.HANDS)
    end
end
```

### 5.7 避墙避水逃跑角（BeaverWalkAway）

```lua
function BeaverWalkAway:GetRunAngle(pt, hp)
    if self.avoid_angle ~= nil then
        local avoid_time = GetTime() - self.avoid_time
        if avoid_time < 1 then return self.avoid_angle
        else self.avoid_time = nil; self.avoid_angle = nil end
    end
    local angle = self.inst:GetAngleToPoint(hp) + 180
    if angle > 360 then angle = angle - 360 end
    local radius = 6
    local result_offset, result_angle, deflected = FindWalkableOffset(pt, angle*DEGREES, radius, 8, true, false) -- 先避墙
    if result_angle == nil then
        result_offset, result_angle, deflected = FindWalkableOffset(pt, angle*DEGREES, radius, 8, true, true) -- 再不避墙也避水
        if result_angle == nil then return angle end
    end
    result_angle = result_angle / DEGREES
    if deflected then
        self.avoid_time = GetTime()
        self.avoid_angle = result_angle
    end
    return result_angle
end
```

### 5.8 客户端换 build（goddess_rabbit 疯狂观众）

```lua
inst:SetClientsideBuildOverride("insane", "rabbit", "beard_monster")
inst:SetClientsideBuildOverride("insane", "rabbit_winter_build", "beard_monster")
```

### 5.9 城市守卫仇恨/台词分流（royalpigguard）

```lua
local function shouldPanic(inst)
    local x,y,z = inst.Transform:GetWorldPosition()
    local ents = TheSim:FindEntities(x,y,z, 20, {"hostile"},{"city_pig"})
    if #ents > 0 then return true end
    if inst.components.combat.target then
        local threat = inst.components.combat.target
        local myPos = Vector3(inst.Transform:GetWorldPosition())
        local threatPos = Vector3(threat.Transform:GetWorldPosition())
        local dist = distsq(threatPos, myPos)
        if dist < FAR_ENOUGH*FAR_ENOUGH then
            if dist > STOP_RUN_AWAY_DIST*STOP_RUN_AWAY_DIST then return true end
        else
            inst.components.combat:GiveUp()
        end
    end
    return false
end
```

---

## 6. 特色岛屿/植物/地形专题

（用户点名专题：特色岛屿、特色植物、特色地形+域外海洋）

### 6.1 特色岛屿：海难风岛屿群生成

#### 6.1.1 世界分支总入口

modworldgenmain.lua 顶层按 `kindofworld` 分 4 支：

```lua
if GetModConfigData("kindofworld") == 5 then
    -- 哈姆雷特世界：AddTask("Edge_of_the_unknown", { locks = LOCKS.NONE,
    --   keys_given = KEYS.JUNGLE_DEPTH_1, room_choices = {["BG_plains_base"] = 1 + tamanho},
    --   room_bg = GROUND.PLAINS, background_room = "BG_plains_base", ...})
    --   AddStartLocation("porkland_start", { name = "Porkland", location = "forest",
    --     start_setpeice = "porkland_start", start_node = "PorklandPortalRoom" })
elseif GetModConfigData("kindofworld") == 20 then
    -- 域外海洋世界（详见 6.3.2）
else
    -- 火山世界（salasvolcano/salasbeach/salasjungle 房间池，TROPICAL* 系列任务）
    if GetModConfigData("kindofworld") == 10 then
        -- 海难世界（本专题核心，见下）
    end
end
```

#### 6.1.2 海难世界注册（kindofworld == 10）

起点：`AddStartLocation("tropicalexperience", { location = "forest", start_setpeice = "BeachStart", start_node = "MAINBeachPortalRoom" })`。

LevelPreInit（cave 分支插入洞穴任务，forest 分支强制起点）：

```lua
local function LevelPreInit(level)
    if level.location == "cave" then
        level.overrides.keep_disconnected_tiles = true
        -- 火山洞窟：separavulcao + vulcaonacaverna 0~4
        table.insert(level.tasks, "separavulcao")
        table.insert(level.tasks, "vulcaonacaverna")
        table.insert(level.tasks, "vulcaonacaverna1")
        ...（到 vulcaonacaverna4）
        -- 冰霜岛洞窟（frost_islandworld==10）：frostcavedivide/Frostcavetask/frostExitRoom
        -- 水下世界（underwater 配置）：
        table.insert(level.tasks, "underwaterdivide")
        table.insert(level.tasks, "UnderwaterStart")
        table.insert(level.tasks, "SandyBiome")
        table.insert(level.tasks, "ReefBiome")
        table.insert(level.tasks, "KelpBiome")
        table.insert(level.tasks, "RockyBiome")
        table.insert(level.tasks, "MoonBiome")
        table.insert(level.tasks, "OpenWaterBiome")
        table.insert(level.tasks, "task_underground_beach")
        table.insert(level.tasks, "task_underwaterothers")
        table.insert(level.tasks, "task_underwater_kraken_zone")
        table.insert(level.tasks, "secretcavedivisor")
        table.insert(level.tasks, "task_secretcave1")
        if GetModConfigData("togethercaves_shipwreckedworld") == 1 then
            table.insert(level.tasks, "atlantidaExitRoom")
        end
        table.insert(level.tasks, "task_underwaterlavarock")
        table.insert(level.tasks, "task_underwatermagmafield")
        table.insert(level.tasks, "task_underwaterwatercoral")
        table.insert(level.tasks, "UnderwaterExit1")
        -- 哈姆雷特洞窟（hamletcaves_shipwreckedworld==1）：
        table.insert(level.tasks, "separahamcave")
        table.insert(level.tasks, "HamMudWorld")
        table.insert(level.tasks, "HamMudCave")
        table.insert(level.tasks, "HamMudLights")
        table.insert(level.tasks, "HamMudPit")
        table.insert(level.tasks, "HamBigBatCave")
        table.insert(level.tasks, "HamRockyLand")
        table.insert(level.tasks, "HamRedForest")
        table.insert(level.tasks, "HamGreenForest")
        table.insert(level.tasks, "HamBlueForest")
        table.insert(level.tasks, "HamSpillagmiteCaverns")
        table.insert(level.tasks, "HamSpillagmiteCaverns1")
        table.insert(level.tasks, "caveruinsexit")
        table.insert(level.tasks, "caveruinsexit2")
        table.insert(level.tasks, "HamMoonCaveForest")
        table.insert(level.tasks, "HamArchiveMaze")
    end
    if level.location == "forest" then
        level.overrides.start_location = "tropicalexperience"
        level.required_prefabs = {}
    end
end
AddLevelPreInitAny(LevelPreInit)
```

TasksetPreInit（海难地表任务清单 + 岛屿可选任务）：

```lua
local function TasksetPreInit(taskset)
    if taskset.location ~= "forest" then return end
    taskset.tasks = {}
    table.insert(taskset.tasks, "inicioswsw")   -- 起始岛（locks=NONE，keys_given 工具链）
    table.insert(taskset.tasks, "inicioswsw2")
    table.insert(taskset.tasks, "TROPICAL39")   -- 沙滩赌场岛
    table.insert(taskset.tasks, "TROPICAL9")
    table.insert(taskset.tasks, "TROPICAL50")   -- DoyDoy 雨林
    table.insert(taskset.tasks, "TROPICAL51")
    table.insert(taskset.tasks, "TROPICAL28")   -- 鲨鱼巢
    table.insert(taskset.tasks, "PirateBounty")
    table.insert(taskset.tasks, "TROPICAL14")   -- 火山
    taskset.valid_start_tasks = { "iniciosw" }
    taskset.numoptionaltasks = GetModConfigData("howmanyislands")  -- 岛屿数量=配置项
    taskset.optionaltasks = {
        "HomeIslandSmall", "HomeIslandSmallBoon", "HomeIslandMed",
        "HomeIslandLarge", "HomeIslandLargeBoon", "DesertIsland",
        "JungleMarsh", "BeachJingleS", "BeachBothJungles", "BeachJungleD",
        "BeachSavanna", "GreentipA", "GreentipB", "HalfGreen", "BeachRockyland",
        "LotsaGrass", "AllBeige", "BeachMarsh", "Verdant", "VerdantMost",
        "Vert", "Florida Timeshare", "JungleSRockyland", "JungleSSavanna",
        "JungleBeige", "FullofBees", "JungleDense", "JungleDMarsh",
        "JungleDRockyland", "JungleDRockyMarsh", "JungleDSavanna",
        "JungleDSavRock", "HotNSticky", "Marshy", "NoGreen A", "NoGreen B",
        "Savanna", "Rockyland", "PalmTreeIsland", "IslandParadise",
        "PiggyParadise", "BeachPalmForest", "ThemeMarshCity", "Spiderland",
        "IslandJungleBamboozled", "IslandJungleMonkeyHell",
        "IslandJungleCritterCrunch", "IslandJungleShroomin",
        "IslandJungleRockyDrop", "IslandJungleEyePlant", "IslandJungleBerries",
        "IslandJungleNoBerry", "IslandJungleNoRock", "IslandJungleNoMushroom",
        "IslandJungleNoFlowers", "IslandJungleEvilFlowers",
        "IslandJungleSkeleton", "IslandBeachCrabTown", "IslandBeachDunes",
        "IslandBeachGrassy", "IslandBeachSappy", "IslandBeachRocky",
        "IslandBeachLimpety", "IslandBeachForest", "IslandBeachSpider",
        "IslandBeachNoFlowers", "IslandBeachNoLimpets", "IslandBeachNoCrabbits",
        "IslandMangroveOxBoon", "IslandMeadowBees", "IslandMeadowCarroty",
        "IslandRockyGold", "IslandRockyTallBeach", "IslandRockyTallJungle",
        "ShellingOut", "Cranium", "CrashZone",
    }
    -- Shipwreckedworld_plus：追加 4 个"相连大陆"任务
    if GetModConfigData("Shipwreckedworld_plus") == true then
        table.insert(taskset.tasks, "pandataskjunto")
        table.insert(taskset.tasks, "eldoradojunto")
        table.insert(taskset.tasks, "tikitribejunto")
        table.insert(taskset.tasks, "walrusvacationjunto")
    end
    -- frost_islandworld==10/15：追加 8 个冰霜岛任务
    -- Moonshipwrecked==1：追加 5 个月球岛任务（MoonIsland_IslandShards/Beach/Forest/Baths/Mine）
    -- underwater：追加 EntranceToReef
    -- 跨 mod：KnownModIndex:IsModEnabled("workshop-2039181790")（不妥协）→ GiantTrees
    --        workshop-1289779251（樱花林）→ cherry_mainland/cherry_island/cherry_grove/cherry_arquipelago，
    --        或 AddTaskPreInit 往 MoonIsland_* 里塞 Cherry* 房间
    -- set_pieces：
    --   Moonshipwrecked：MoonAltarRockGlass/Idol/Seed、BathbombedHotspring、MoonFissures
    --   togethercaves_shipwreckedworld==1：CaveEntrance count=10（列全部可选岛）
    --   tropicalshards ~= 0：sw_exit count=1（跨世界出口）
end
AddTaskSetPreInitAny(TasksetPreInit)
```

**岛屿 = 一个 Task**。典型岛屿任务（带 region_id 唯一编号）：

```lua
AddTask("HomeIslandVerySmall", {
    locks = {}, keys_given = {}, region_id = "ship1",
    crosslink_factor = math.random(0, 1),
    make_loop = math.random(0, 100) < 50,
    room_choices = {
        ["JungleDenseMedHome"] = 1,
        ["BeachSandHome"] = 2,
    },
    room_bg = GROUND.JUNGLE,
    background_room = { "BeachSandHome" },
    colour = { r = 1, g = 1, b = 0, a = 1 }
})

AddTask("DesertIsland", {
    locks = {}, keys_given = {}, region_id = "ship7",
    room_choices = { ["BeachSand"] = 2 },
    room_bg = GROUND.BEACH,
    background_room = { "BeachSand" },
    colour = { r = 1, g = 1, b = 0, a = 1 }
})

AddTask("TROPICAL39", {   -- 火山世界分支的"沙滩赌场岛"
    locks = {}, keys_given = {}, region_id = "tropical14",
    room_choices = {
        ["BeachPalmCasino"] = 1,
        [salasbeach[math.random(1, 24)]] = 1,
    },
    room_bg = GROUND.BEACH,
    background_room = salasbeach[math.random(1, 24)],
    colour = { 1, .5, .5, .2 },
})
```

要点：
- `region_id` 是故事生成的区域唯一标识（"ship1".."ship9"、"tropical1".."tropical26"），多个任务同一 region_id 则生成时连在一起（junto 系列任务用同一 region_id 拼大陆）。
- `room_choices` 混合丛林/沙滩/潮汐房间；`background_room` 决定任务边界房间（海难岛外围一圈 BeachSandHome 沙滩）。
- 房间池用 `math.random` 在生成时从 salasbeach/salasjungle 表里抽（每局随机化）。
- `crosslink_factor`（0/1）与 `make_loop`（50% 概率）控制岛屿之间的连桥密度。

#### 6.1.3 海陆交界处理（海洋填充）

taskset 尾部把"非陆地 tile"全部换成海难版海洋房间：

```lua
taskset.ocean_prefill_setpieces["coralpool1"] = { count = 3 * GetModConfigData("coralbiome") }
taskset.ocean_prefill_setpieces["coralpool2"] = { count = 3 * GetModConfigData("coralbiome") }
taskset.ocean_prefill_setpieces["coralpool3"] = { count = 2 * GetModConfigData("coralbiome") }
taskset.ocean_prefill_setpieces["octopuskinghome"] = { count = GetModConfigData("octopusking") }
taskset.ocean_prefill_setpieces["mangrove1"] = { count = 2 * GetModConfigData("mangrove") }
taskset.ocean_prefill_setpieces["mangrove2"] = { count = GetModConfigData("mangrove") }
taskset.ocean_prefill_setpieces["wreck"] = { count = GetModConfigData("shipgraveyard") }
taskset.ocean_prefill_setpieces["wreck2"] = { count = GetModConfigData("shipgraveyard") }
taskset.ocean_prefill_setpieces["kraken"] = { count = GetModConfigData("kraken") }

taskset.ocean_population = {
    "OceanCoastalShore_SW",
    "OceanCoastal_SW",
    "OceanSwell_SW",
    "OceanRough_SW",
    "OceanReef_SW",
    "OceanHazardous_SW",
}
taskset.location = "forest"
```

`ocean_prefill_setpieces` = 海洋区先铺的静态布局（珊瑚池/章鱼王巢/红树林/沉船/克拉肯区域），`ocean_population` = 海洋 tile 填充用的房间列表。海难版海洋房间（value = 对应 GROUND.OCEAN_*）：

```lua
AddRoom("OceanCoastal_SW", {
    colour = { r = .5, g = 0.6, b = .080, a = .10 },
    value = GROUND.OCEAN_COASTAL,
    contents = {
        countprefabs = {
            seaweed_planted = 200,
            mussel_farm = 300,
            messagebottle1 = 20,
        },
        distributepercent = 0.01,
        distributeprefabs = {},
    }
})

AddRoom("OceanRough_SW", {   -- 深海
    value = GROUND.OCEAN_ROUGH,
    contents = {
        countprefabs = {
            rawling = 1,
            tar_pool = 8,
            messagebottle1 = 20,
        },
        countstaticlayouts = {
            ["HermitcrabIsland"] = GetModConfigData("Moonshipwrecked"),
        },
    }
})

AddRoom("OceanHazardous_SW", {   -- 沉船区
    value = GROUND.OCEAN_HAZARDOUS,
    contents = {
        distributepercent = 0.15,
        distributeprefabs = {
            boatfragment03 = 1, boatfragment04 = 1, boatfragment05 = 1,
            seastack = 1,
        },
    }
})
```

海陆交界判定工具（scripts/tools/spawnutil.lua，仅世界生成期）：`IsShoreTile`（海滩/近岸判断）、`FindRandomWaterPoints`（素数步进找水面点：`{263,137,67,31,17,9,5,3,1}`）、`SpawnSunkenBoat`（沉船）、`AddWaterCommonSpawn/AddLandCommonSpawn`（水/陆公共生成注册）。

#### 6.1.4 哈姆雷特世界（kindofworld == 5）的岛式任务

同样用 Task 做"大陆块"：`Edge_of_the_unknown` 起点（locks=NONE、keys_given=KEYS.JUNGLE_DEPTH_1）、`Pigtopia/Pigtopia_capital/Edge_of_civilization/Lilypond_land/Deep_rainforest/Lost_Ruins_1/...` 全套，任务间靠 LOCKS/KEYS 解锁推进；`Land_Divide_1..4`、`separahamcave`（LOCKS.SACRED → KEYS.LAND_DIVIDE_5）实现"强制断开房间"（ForceDisconnectedRoom ×10）拼接大陆块。

### 6.2 特色植物

#### 6.2.1 椰子树（palmtrees.lua，752 行）

三阶段 growable（短/中/高），成长时间表、砍伐次数、掉落表、LEIF 树精：

```lua
local PALMTREE_GROW_TIME = {
    {base=1.5*day_time, random=0.5*day_time},   --tall to short
    {base=5*day_time, random=2*day_time},   --short to normal
    {base=5*day_time, random=2*day_time},   --normal to tall
}
local PALMTREE_CHOPS = "a"          -- 砍伐动画变体（按 build 生成 jile 字段）
local PALMTREE_CHOPS_SMALL = 5
local PALMTREE_CHOPS_NORMAL = 10
local PALMTREE_CHOPS_TALL = 15
local PALMTREE_COCONUT_CHANCE = 0.01  -- 椰子自然掉落概率
local LEIF_REAWAKEN_RADIUS = 20
local LEIF_MIN_DAY = 3
local LEIF_PERCENT_CHANCE = 1/50
local LEIF_MAXSPAWNDIST = 15

SetSharedLootTable('palmtree_short',  {{"log", 1.0}, {"palmleaf", 1.0}})
SetSharedLootTable('palmtree_normal', {{"log", 1.0},{"log", 1.0}, {"palmleaf", 1.0}, {"coconut", 1.0}})
SetSharedLootTable('palmtree_tall',  {{"log", 1.0}, {"log", 1.0}, {"coconut", 1.0}, {"coconut", 0.33},{"palmleaf", 1.0}})

local builds = {
    normal = {
        file="palmTree_build", prefab_name="palmtree",
        normal_loot = 'palmtree_normal', short_loot = 'palmtree_short', tall_loot = 'palmtree_tall',
        leif="leif",  -- 原版注释掉的 leif="treeguard" 改为 leif
        jile=""..DEF..""..PALMTREE_CHOPS.."_palmTree",
    },
}
```

动画按阶段生成（`makeanims(stage)`：idle/sway1/sway2/chop/fallleft/fallright/stump/burning/burnt/blown1/blown2/blown_pre/blown_pst 全套 + 阶段后缀），砍树用 `jile` 字段指定 build 内动画前缀；椰子相关 prefab：coconut.lua（可吃/可种）、palmleaf.lua（叶子）、clawpalmtrees.lua（爪椰树，掉 cave_banana）。

#### 6.2.2 竹子（bambootree.lua，377 行）

"砍+挖"双工作流：先 HACK 砍 6 刀（machetecut 标签），砍完变 DIG 挖 1 下得 bamboo + 定时器重生；直接挖则得 dug_bambootree。`oceanbambootree`/`oceanbambootreebig` 水上变体（跳过物理移除）：

```lua
local respawndays = 2  --tempo para renascer em dias（葡语：重生天数）

local function OnTimerDone(inst, data)
    if data.name == "spawndelay" then
        inst.AnimState:PlayAnimation("grow")
        inst.AnimState:PushAnimation("idle",true)
        inst:AddTag("machetecut")
        inst.components.workable:SetWorkLeft(6)
        inst.components.workable:SetWorkAction(ACTIONS.HACK)
        if inst.prefab ~= "oceanbambootree" and inst.prefab ~= "oceanbambootreebig" then
            MakeObstaclePhysics(inst, 0.35)
        end
    end
end

local function dig_up(inst, worker)
    if inst:HasTag("machetecut") then
        inst:RemoveTag("machetecut")
        inst.components.workable:SetWorkAction(ACTIONS.DIG)
        inst.components.workable:SetWorkLeft(1)
        inst.components.lootdropper:SpawnLootPrefab("bamboo")
        inst.components.timer:StartTimer("spawndelay", 60*8*respawndays)
        return
    end
    if not inst:HasTag("machetecut") then
        if inst.components.lootdropper ~= nil then
            inst.components.lootdropper:SpawnLootPrefab("dug_bambootree")
        end
        inst:Remove()
    end
end

local function onhackedfn(inst, hacker, hacksleft)
    if not inst:HasTag("machetecut") then return end
    local fx = SpawnPrefab("hacking_bamboo_fx")
    ...
    if(hacksleft <= 0) then
        inst.AnimState:PlayAnimation("picking")
        -- 砍完：播放采摘动画，物理碰撞体移除
        if inst.prefab ~= "oceanbambootree" and inst.prefab ~= "oceanbambootreebig" then
            RemovePhysicsColliders(inst)
        end
    else
        inst.AnimState:PlayAnimation("chop")
        inst.AnimState:PushAnimation("idle")
    end
end
```

标签 `bambootree`/`plant`/`machetecut`；OnSave 存 tag 状态（`data.tag = 1` 表示已砍），OnLoad 恢复为 picked 动画。

#### 6.2.3 香蕉（无独立 prefab，cave_banana 复用）

本 mod 没有 bananabush：香蕉直接用原版 `cave_banana` 物品，由丛林树和爪椰树掉落、金猴掉落：

```lua
-- jungletrees.lua（丛林树）
inst.components.lootdropper:AddChanceLoot("cave_banana", 1.0)
-- clawpalmtrees.lua（爪椰树）prefabs 列表含 "cave_banana"
-- primeape.lua（金猴）
local LOOT = { "smallmeat", "cave_banana" }
local function LOOT_FUNC(inst) return math.random() <= 0.5 and "cave_banana" or "smallmeat" end
-- primeape 行为里：banana 判定、喂香蕉加好感（"I eat bananas"）
if item.prefab == "cave_banana" then
    -- banana makes us friends (unless I'm a guard)
```

#### 6.2.4 咖啡（coffeebush.lua，250 行，createbush 工厂）

经典 berry bush 结构（pickable + barren 循环 + 挖掘移植）：

```lua
local function normal_postinit(inst)
    inst.components.pickable:SetUp("coffeebeans", TUNING.BERRY_REGROW_TIME)
    inst.components.pickable.getregentimefn = getregentimefn_normal
    inst.components.pickable.max_cycles = math.random(2)   -- 采 1~2 次后枯死
    inst.components.pickable.cycles_left = inst.components.pickable.max_cycles
    inst.components.workable:SetOnFinishCallback(dig_up_normal)
end
return createbush("coffeebush", "coffeebush", "coffeebeans", normal_postinit)
```

getregentimefn 按已采次数递增再生长（`BERRY_REGROW_INCREASE * num_cycles_passed`）；`ontransplantfn` 移栽即 MakeBarren；每采一次动画档位按 `cycles_left/max_cycles` 切换（berriesmost/berriesmore/berries）；`MakeNoGrowInWinter(inst)` 冬季不生长；YOTG 活动期间 spawnperd 火鸡偷吃。咖啡豆 → coffee.lua（饮品）+ coffeebeans.lua。

#### 6.2.5 藤蔓系

- `grabbing_vine.lua`：抓人藤（thief 组件偷窃 + playerprox 上下 + OnSave 存 spawnpatch.GUID + 死后 spawnNewVine 重生）；`grabbing_vinefixo` 同函数生成。
- `hanging_vine.lua`：垂挂藤（装饰）。
- `jungle_border_vine.lua`：雨林边缘藤。
- `bush_vine.lua`：灌木藤。
- `grabbing_vine` 的 mob 版 `snake`（水蛇 SGsnake2 有 emerge/submerge）。

#### 6.2.6 高草/草丛系（grass_tall.lua，9 个 Prefab）

- 三刀 HACK → fall + cutgrass；挖：machetecut → DIG 1 下 + 4 天重生（`timer:StartTimer("spawndelay", 60*8*4)` + grow 动画），否则 dug_grass 移除。
- **weevole 巢**：weevole_infested 标签 + isday 停/isdusk 启 + weevolenesttest 概率传染 + spawnweevole（用 `TheCamera:GetDownVec()` 定位）。
- **patch 系统**：`placeitemoffgrids` 随机圆内散点 + `checkIfValidGround` 排除 8 种 OCEAN tile（OCEAN_SWELL/OCEAN_BRINEPOOL/OCEAN_BRINEPOOL_SHORE/OCEAN_HAZARDOUS/OCEAN_ROUGH/IMPASSABLE/OCEAN_COASTAL/OCEAN_WATERLOG/OCEAN_COASTAL_SHORE）。
- 水版 grass_tallwater：`MakeWaterObstaclePhysics(0.35,2,1.25)` + ignorewalkableplatforms + `SetPrefabNameOverride("grass_tall")` + MakeInventoryFloatable(bob_percent 0) + OnLandedServer。
- 同一文件返回 9 个 Prefab：grass_tall/grass_tallwater/grass_tall_patch/deep_jungle_fern_noise/teatree_piko_nest_patch/asparagus_patch/vampirebatcave_potential(20%)/grass_patch。
- grass.lua：守卫仇恨插入 + **ontransplantfn 在平原/雨林/深雨林地皮上变高草**（`GROUND.PLAINS/RAINFOREST/DEEPRAINFOREST` → SpawnPrefab("grass_tall")）+ grassgekko 变形全套（worldsettingstimer morphdelay/morphing/morphrelay + triggernearbymorph 扩散 + GRASSGEKKO_MAX_DENSITY 密度上限）。
- grass_water.lua：水草（grassgekko 同构，dig_up 无守卫，`bank/build "grass_inwater"`）。
- greengrass.lua：绿色草（pickable cutgreengrass 180 + 烧毁 ash/charcoal + OnSave 存 no_banana）。
- grasswaterspawner.lua：一次性岸边草生成器（tentativas=10 重试、FindLandNextToWater 找岸、半径 48±4、12 次尝试、`IsNotNextToLand` 判定）。

#### 6.2.7 潮汐/海水植物机制（海难特色）

**莲花（lotus.lua）**——四周必须全是水的"岛心水塘植物"，八海洋 tile 自检 + 20% 概率引鹳：

```lua
local LOTUS_REGROW_TIME = 480*5
local BILL_SPAWN_CHANCE = 0.2

local function groundtest(inst)   -- 4 方向 4 格采样，任一方向非海洋则自毁
local map = TheWorld.Map
local ex, ey, ez = inst.Transform:GetWorldPosition()
local posicao1 = map:GetTile(map:GetTileCoordsAtPoint(ex, ey, ez+4))
local posicao2 = map:GetTile(map:GetTileCoordsAtPoint(ex, ey, ez-4))
local posicao3 = map:GetTile(map:GetTileCoordsAtPoint(ex+4, ey, ez))
local posicao4 = map:GetTile(map:GetTileCoordsAtPoint(ex-4, ey, ez))
if posicao1 ~= (GROUND.OCEAN_SWELL) and posicao1 ~= (GROUND.OCEAN_WATERLOG) and ... or
   posicao2 ~= (GROUND.OCEAN_SWELL) and ... or
   posicao3 ~= (GROUND.OCEAN_SWELL) and ... or
   posicao4 ~= (GROUND.OCEAN_SWELL) and ... then
    inst:Remove()
end
end

local function onpickedfn(inst)   -- 采莲花：20% 概率在 12 格外的水面生成鹳
    ...
    if not target and math.random() < BILL_SPAWN_CHANCE then
        local bill = SpawnPrefab("bill")
        local nearbyPositions = {{x, z + 12}, {x, z - 12}, {x + 12, z}, {x - 12, z}}
        for posIndex = 1, 4 do
            local nearbyPosition = nearbyPositions[posIndex]
            local tile = TheWorld.Map:GetTileAtPoint(nearbyPosition[1], y, nearbyPosition[2])
            if IsWater(tile) then
                bill.Transform:SetPosition(nearbyPosition[1], y, nearbyPosition[2])
                bill.sg:GoToState("surface")
                break
            end
        end
    end
end
```

**贻贝养殖场（mussel_farm.lua）**——6 阶段 growable（hidden→underwater→empty→small→medium→large），`SetDeployMode(DEPLOYMODE.WATER)` + `OCEAN_SHALLOW` 限定浅水部署，trader 收 mussel_stick 杆；配套 mussel.lua（贝肉）、mussel_bed.lua、mussel_stick.lua。

**海带/水草**：kelp.lua、seaweed_planted（OceanCoastal 房间 countprefabs 200 个）、bullkelp_plant（distributeprefabs 权重 2）、waterplant（OceanRough 房间 waterplant_spawner_rough 0.04 + countprefabs waterplant 1）、grass_water、kelpy（海带怪）。

**红树林（mangrovetrees.lua）**：3 阶段树 + `MakeWaterObstaclePhysics` + `OverrideSymbol("droplet"/"water_ripple", ..., " ")` 隐藏水上特效；mangrovespawner.lua 岸边生成；mangrovetreesbee.lua 蜜蜂版；mangrove1/mangrove2 ocean_prefill_setpieces。

**浮萍（lilypad）**：lilypadnovo/lilypadnovograss 静态布局（数量由 `GetModConfigData("lilypad")` 配置）；`lilypad` 本体（SG 空壳）。

**其他树/果**：palmconetree（松果椰）、peach_trees（桃子，windy.lua 里 Crop.Harvest 覆盖 15/60/25% 桃子）、crabapple_tree（蟹苹果）、pandatree（竹林）、q_sugarwoodtree 系列（盛宴糖木）、jungletrees（丛林树，cave_banana 掉落）、jungletreeseed、livingjungletree、jungletreeguard（丛林树守卫，扔果实）、dug_cofeecactus/elephantcactus（仙人掌咖啡）。

### 6.3 特色地形

#### 6.3.1 新地皮 tile 全清单（tileadder.lua + tiledescription.lua，29 个）

| tile（GROUND.XXX） | 纹理映射 | layer | isfloor | terraformer 掉落地皮 |
|---|---|---|---|---|
| MAGMAFIELD | cave | 35 | | turf_magmafield |
| JUNGLE | jungle | 25 | | turf_jungle |
| ASH | cave | 25 | | turf_ash |
| VOLCANO | cave | 25 | | turf_volcano |
| TIDALMARSH（潮汐沼泽） | beach | 25 | | turf_tidalmarsh |
| MEADOW（草地） | jungle | 25 | | turf_meadow |
| SNAKESKINFLOOR（蛇皮地板） | carpet | 30 | true | turf_snakeskinfloor |
| BEACH（沙滩） | beach | 30 | | turf_beach |
| WATER_MANGROVE（水红树林） | water_mangrove | 40 | true | （无 turf，frost 湖用） |
| PLAINS（平原） | jungle | 25 | | turf_plains |
| DEEPRAINFOREST（深雨林） | deeprainforest | 25 | | turf_deeprainforest |
| RAINFOREST（雨林） | rainforest | 25 | | turf_rainforest |
| PAINTED（涂彩） | deeprainforest | 25 | | turf_painted |
| BATTLEGROUND（战场） | deeprainforest | 25 | | turf_battleground |
| GASJUNGLE（瓦斯雨林） | deeprainforest | 25 | | turf_gasjungle |
| FIELDS（农田） | jungle | 25 | | turf_fields |
| CHECKEREDLAWN（棋盘草坪） | cobbleroad | 30 | true | turf_checkeredlawn |
| SUBURB（郊区） | deciduous | 14 | | turf_suburb |
| BEARDRUG（胡须地毯） | rocky | 30 | true | turf_beardrug |
| FOUNDATION（地基） | blocky | 20 | | turf_foundation |
| COBBLEROAD（鹅卵石路） | cobbleroad | 38 | true | turf_cobbleroad |
| ANTFLOOR（蚁地板） | antfloor | 25 | | turf_antfloor |
| BATFLOOR（蝙蝠地板） | batfloor | 25 | | （无 turf，熔岩地板） |
| PIGRUINS（猪遗迹） | carpet | 30 | | （无 turf，熔岩边饰） |
| UNDERWATER_SANDY（水下沙地） | cave | 5 | | （水下，无 turf） |
| UNDERWATER_ROCKY（水下岩地） | marsh | 5 | | （水下，无 turf） |
| WINDY（风地） | windy | 25 | | turf_windy |
| MARSH_SW（海难沼泽） | marsh_sw | 25 | | turf_marsh_sw |
| HAMARCHIVE（档案库） | deeprainforest | 25 | | turf_hamarchive |

注释里还有被禁用的 `water_coral/water_deep/water_medium/water_shallow`（tile 编号被预留）。描述表结构（tiledescription.lua SetInfo）：

```lua
--0 [STRING] name - 小写 tile 名（须匹配 levels/tiles/ 的纹理与图集）
--1 [TABLE] specs - tile 边缘纹理、跑/走/雪/泥声音
--2 [TABLE] turf - terraformer 掉落（prefab, min, max），不设置则无
--3 [INTEGER] layer - 渲染顺序
--4 [BOOL] isfloor - true 则视为地板（不能种植物）
magmafield = { specs = {name = "cave"}, turf = {{"turf_magmafield"}}, layer = 35 },
```

#### 6.3.2 域外海洋世界（OceanWorld，kindofworld == 20）

**全海图世界**：起点在海洋中（`oceanworldstart` 静态布局 + Blank 房间），level 全量覆写：

```lua
AddStartLocation("OceanWorld", {
    name = "OceanWorld",
    location = "forest",
    start_setpeice = "oceanworldstart",
    start_node = "Blank",
})

AddTask("OceanWorldstart", {
    locks = {}, keys_given = {},
    room_choices = { ["Blank"] = 1 },
    room_bg = GROUND.GRASS,
    background_room = "Blank",
    colour = { r = 0, g = 1, b = 0, a = 1 }
})

AddLevelPreInitAny(function(level)
    if level.location ~= "forest" then return end
    level.tasks = { "OceanWorldstart" }
    level.numoptionaltasks = 0
    level.optionaltasks = {}
    level.valid_start_tasks = nil
    level.set_pieces = {}
    if level.ocean_population == nil then level.ocean_population = {} end
    level.ocean_population = {
        "OceanCoastalShore_SEA",
        "OceanCoastal_SEA",
        "OceanSwell_SEA",
        "OceanRough_SEA",
        "OceanReef_SEA",
        "OceanHazardous_SEA",
    }
    level.random_set_pieces = {}
    level.ordered_story_setpieces = {}
    level.numrandom_set_pieces = 0
    level.overrides.start_location = "OceanWorld"
    level.overrides.keep_disconnected_tiles = true
    level.overrides.roads = "never"
    level.ocean_prefill_setpieces["coralpool1"] = { count = 3 * GetModConfigData("coralbiome") }
    level.ocean_prefill_setpieces["coralpool2"] = { count = 3 * GetModConfigData("coralbiome") }
    level.ocean_prefill_setpieces["coralpool3"] = { count = 2 * GetModConfigData("coralbiome") }
    level.ocean_prefill_setpieces["octopuskinghome"] = { count = GetModConfigData("octopusking") }
    level.ocean_prefill_setpieces["mangrove1"] = { count = 2 * GetModConfigData("mangrove") }
    level.ocean_prefill_setpieces["mangrove2"] = { count = GetModConfigData("mangrove") }
    level.ocean_prefill_setpieces["wreck"] = { count = GetModConfigData("shipgraveyard") }
    level.ocean_prefill_setpieces["wreck2"] = { count = GetModConfigData("shipgraveyard") }
    level.ocean_prefill_setpieces["kraken"] = { count = GetModConfigData("kraken") }
    level.required_prefabs = {}
end)
```

关键点：`keep_disconnected_tiles = true`（保留分离 tile，海洋世界必需）+ `roads = "never"`（无路）+ `start_setpeice = "oceanworldstart"`（海上出生点）。

域外海洋版房间（_SEA 后缀，与 _SW 版区别在于内容更"DST 海洋"）：

```lua
AddRoom("OceanCoastal_SEA", {
    value = GROUND.OCEAN_COASTAL,
    contents = {
        countprefabs = {
            seaweed_planted = 200,
            mussel_farm = 300,
            messagebottle1 = 20,
            mermboat = 4,
            boat_otterden = 15,
        },
        distributepercent = 0.01,
        distributeprefabs = {
            driftwood_log = 1,
            bullkelp_plant = 2,
            messagebottle = 0.08,
        },
    }
})

AddRoom("OceanSwell_SEA", {
    value = GROUND.OCEAN_SWELL,
    required_prefabs = { "crabking_spawner" },
    contents = {
        distributepercent = 0.005,
        distributeprefabs = {
            seastack = 1,
            seastack_spawner_swell = 0.1,
            undersearock1 = 0.5,
            undersearock2 = 0.25,
            undersearock_flintless = 0.1,
            undersearock_moon = 0.1,
            oceanfish_shoalspawner = 0.07,
        },
        countstaticlayouts = {
            ["CrabKing"] = 1,
            ["BullkelpFarmSmall"] = 6,
            ["BullkelpFarmMedium"] = 3,
            ["lilypadnovo"] = 2 * GetModConfigData("lilypad"),
            ["lilypadnovograss"] = GetModConfigData("lilypad"),
            ["icebergs"] = 8,
            ["oceangrotolunar"] = 1,
            ["oceanrocks"] = 4,
        },
    }
})

AddRoom("OceanRough_SEA", {
    value = GROUND.OCEAN_ROUGH,
    required_prefabs = { "hermithouse_construction1", "waterplant" },
    countstaticlayouts = {
        ["HermitcrabIsland"] = 1,
        ["MonkeyIsland"] = 1,
        ["BullkelpFarmSmall"] = 6,
        ["BullkelpFarmMedium"] = 3,
        ["oceanforest"] = 5,        -- 海上森林（红树）
        ["oceanbamboforest"] = 5,   -- 海上竹林
    },
})
```

`oceanforest`/`oceanbamboforest` 即"海面铺地皮的树岛"——通过 countstaticlayouts 把带 BEACH/JUNGLE tile 的静态布局直接放进海洋房间，实现海中的岛型地皮。这也是"海面铺地皮"的世界生成侧实现：**静态布局的 BG_TILES 层直接覆盖海洋 tile**（布局带 `fill_mask = IGNORE_IMPASSABLE_BARREN_RESERVED` 不要求陆地）。

#### 6.3.3 跨世界传送（tropicalshards 碎片系统）

- 传送门布局成对：`sw_exit` ↔ `sw_entrance`、`hamlet_exit` ↔ `hamlet_entrance`、`lobby_exit`（lobby 大厅），全部 16×16 Tiled 格式（BG_TILES tilelayer + FG_OBJECTS objectgroup）。
- 注册：`Layouts["sw_exit"] = StaticLayout.Get("map/static_layouts/sw_exit", { start_mask = GLOBAL.PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED, fill_mask = ... })`。
- 放置：taskset.set_pieces["sw_exit"] = { count = 1, tasks = { 全部可选岛 } }（海难世界）/ ["hamlet_exit"]（哈姆雷特世界）/ ["sw_exit"]（火山世界 TROPICAL 系列任务列表）。
- 传送门 prefab：`porkland_sw_entrance`（tropicalshards ~= 0 时插入 PrefabFiles）、`pigbanditexit`、`teleportato_sw`/`teleportato_sw_parts`（SW 机械传送）、`maxwellportal`。
- 交互文案：`ACTIONS.JUMPIN.strfn` 覆盖，`hamletteleport` 标签 → "HAMLET" 动作名：

```lua
GLOBAL.ACTIONS.JUMPIN.strfn = function(act)
    if act.target ~= nil and act.target:HasTag("hamletteleport") then
        return "HAMLET"
    end
    return Oldstrfnjumpin(act)
end
```

- startlocation 配置：`tropicalshards == 30` 时出生点用 `lobby`（start_setpeice="lobby", start_node="Clearing"），否则 `BeachStart`/`DefaultStart`。

#### 6.3.4 船与海上行动

- 船 prefab：boatraft（竹筏，含 raft 标签）、boatraft_old/boatlog_old（kindofworld==10 或 raftlog 配置时加载）。
- 船体组件链：driver/driver2（驾驶）、rowboatwakespawner（尾迹）、boatbadge（HUD 船血条，`Badge._ctor` boat_health + sanity_arrow）。
- 船装备槽：`EQUIPSLOTS.BARCO`（自定义槽位，actions.lua 的 BOATMOUNT 在 mount_valid 检查时拷贝 BARCO 槽）。
- 船相关生物/建筑：mermboat（鱼人船）、boat_otterden（水獭船巢）、knightboat（骑士船）、boatfragment03/04/05（船骸，OceanHazardous 分布）。
- 船探测（两栖生物/拾取判定）：`TheSim:FindEntities(x, 0, z, TUNING.MAX_WALKABLE_PLATFORM_RADIUS, {"walkableplatform"})`。
- 自动上下船（modmain L5246-5332）：`automatic_disembarkation` 配置，自动下船逻辑。
- 海面铺地皮（terraformer 系组件，scripts/components/）：
  - `terraformer`：13 种 tile 禁止铺地（OCEAN 系 8 种 + IMPASSABLE 等）。
  - `autoterraformer`：30 种 tile 挖出地皮（掉 turf_X）。
  - `deployable` 的 `CanDeploy`：9 种水下/海洋 tile 判定（允许水上部署）。
  - `tiletracker`：`ClearCollidesWith(COLLISION.LIMITS)` + SetOnWaterChangeFn 水陆切换。
  - 船上的地皮判定：`amphibiouscreature` 的 OnEnterOcean/OnExitOcean + `SetAllowPlatformHopping(true)`（goldbishop/otter_old/squid 等）。

---

## 附：可作反面教材的笔误清单（技能文档可收录）

1. `gorge_crabtrap.lua`：`inst.caminho = "images/images/inventoryimages2.xml"` 多一层 images/（fish_med.lua 同病）。
2. `gw_column_angel.lua`：`math.cos(angle + 2,0944)` 用逗号写小数（等于 cos(angle+2)），120° 定位失效。
3. `goddess_statue.lua` 等 OnGetItem：先 SetPercent 再判断旧值，逻辑混乱。
4. `goldmonkey.lua`：夜间形态触发源全部注释，`SetNightmareMonkey` 实际永不触发。
5. `gw_rune.lua`：监听 "builditem" 事件但 RemoveEventCallback 用 "damaged"，事件名不一致。
6. `goddess_gate1.lua`：MakeObstaclePhysics(.25) 后被 MakeInventoryPhysics 覆盖。
7. `goddess_tori.lua`：ondeploy 生成 goddess_gate2 但目录里只有 gate1。
8. `elephantcactus.lua`：active 未定义；`empty_bottle_green.lua`：`inst.componwatersource` 拼写错误；`dungball.lua`：startmoving 未定义；`deco_util.lua`：bckground 拼写；`glass.lua`：DES_GLASS_SWORD_THRONS 模块加载时求值。

---

（完）本笔记基于全部 9 份精读报告 + 世界生成/地皮/植物/海洋世界第一手源码阅读整理，作为技能文档的原始材料。
