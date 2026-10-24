# DST Mod 深度分析笔记：万物书 The Book of All Things

> 分析对象：`C:\Users\22308\Desktop\new\3544387985`（约 249MB，3326 文件）
> 版本：3.5.13（modinfo.lua:11）｜作者：童瑶，悉茗茗（modinfo.lua:1）
> 官方介绍页：https://www.alan.plus:9091/mod?type=WWS ｜ 交流群 1049427294
> 关联工坊号：workshop-3573215226（modinfo.lua:105 调试 flag 判定，证据等级 A——明文写死）
> 混淆评估：**全部 Lua 明文无混淆**。作者采用"开源式开发 + 版本防盗"策略（见 modmain.lua:53-69 多版本重复加载检测）。任务描述中的"混淆推断"无需启用。

---

## 1. Mod 全貌

### 1.1 一句话定位

**万物书 = "幻想世界"内容包 + 内置百科全书（图鉴）UI + 自研 TBAT 框架**。不是纯图鉴类 mod，而是以"图鉴/收集"为叙事包装的大型内容 mod：幻想岛屿、万物之树、翠羽鸟 NPC、冒险家笔记收集线、十余种幻想生物/宠物、农场变异作物、药水锅、皮肤系统、自动收集宠物。mod 名"万物书"即游戏内可打开的那本书（图鉴 UI）。

### 1.2 双子 Mod（submod）架构——最值得学的结构

```
3544387985/
├── modmain.lua              # 根加载器：依次加载 atbooks1 + atbooks2 两个子 mod
├── scripts/                 # 共享层：prefab 汇总 wrapper
│   ├── atbooks_all_prefab_loader.lua
│   └── prefabs/atbooks_all_atbooks{1,2}_prefabs.lua   # 转发注册
├── atbooks1/                # 主体"幻想世界"（720 个 Prefab 定义，24 个分类目录）
├── atbooks2/                # 第二章节（93 个 Prefab，作者 Gyde，AI Codex 参与开发）
├── mod.manifest             # MNFS 二进制清单
└── modicon.tex/.xml
```

根 `modmain.lua`（共 131 行）核心机制：

```lua
-- modmain.lua:38-51 每个子 mod 注入独立的 package 搜索路径和资产路径
local function EnsureSubModSearchPath(submod)
    local scripts_path = string.gsub(root .. submod .. "/scripts/?.lua;", "/", "\\")
    if not string.find(package_ref.path, scripts_path, 1, true) then
        package_ref.path = scripts_path .. package_ref.path
    end
    local asset_path = string.gsub(root .. submod .. "/", "/", "\\")
    for _, pathdata in ipairs(package_ref.assetpath) do
        if pathdata.path == asset_path then return end
    end
    table.insert(package_ref.assetpath, { path = asset_path, manifest = nil })
end
```

- 每个子 mod 用 `CopyEnv(env)` 拷贝独立环境，`kleiloadlua` + `setfenv` 隔离运行（modmain.lua:72-124）。
- `modimport` 被重写为子 mod 私有版本（modmain.lua:85-99）。
- 子 mod 的 `Assets/PreloadAssets/FrontEndAssets/PrefabFiles` 最后合并回父环境（modmain.lua:113-121），prefab 注册走 `atbooks_all_atbooks1_prefabs` 中转。
- **`AddComponentAction` 合并器**（modmain.lua:53-71）：子 mod 里 AddComponentAction 互不覆盖——第一次注册时把原函数包装成遍历调用器，之后所有子 mod 的 action 都塞进同一个表。这是多人协作/多模块叠加 action 的标准解法。

### 1.3 内容规模统计（实测）

| 资产 | 数量 | 说明 |
|---|---|---|
| tex | 1005 | DXT5 1001 张 / DXT1 2 张 / RGBA8 2 张（见 §2.1） |
| xml | 923 | atlas 定义（373 inventoryimages + 281 map_icons + 43 图鉴页等） |
| lua | 723 | 全部明文，含 30+ components、9 brains、5 stategraphs、8 widgets |
| zip（anim） | 661 | atbooks1 585 + atbooks2 76，每 zip = anim.bin + build.bin + atlas-*.tex |
| Prefab 定义 | 813 | atbooks1 720 + atbooks2 93（`Prefab(` 计数） |
| 声效 | 2 fev + 2 fsb | FMod 格式（atbooks1/sound/） |
| 地皮纹理 | 23 张非 mini 图 | levels/textures/ |

atbooks1 的 prefab 分类目录（`scripts/prefabs/tbat__all_prefabs.lua:10-33`）按数字前缀分 24 类：00_others、01_items、02_materials、03_equipments、04_foods、05_foods_cooked、06_containers、07_buildings、08_resources、09_plants、10_minerals、11_animals、12_boss、13_pets、14_turfs、15_debuffs、16_spells、17_sfx、18_projectiles、19_characters、20_events、21_rooms、22_npc、_debugging。每类目录内 `__prefabs_list.lua` 声明文件列表。

### 1.4 命名规范

- 全局框架命名空间：`TBAT`（挂 TUNING.TBAT_BASE_NODE，modmain.lua:47-50），是类 Class() 实例。
- prefab 前缀：`tbat_`（内容）+ `atbook_`（UI/机器，如 atbook_wiki、atbook_ordermachine、atbook_chefwolf）+ `tbat_farm_plant_`（农场作物）。
- 组件命名：`tbat_com_xxx`（通用组件，如 tbat_com_rpc_event）+ `atbook_xxx`（业务组件）。
- 事件命名：`tbat_event.xxx`（mod 内部）、`__tbat_event.xxx`（主客机 RPC 事件）。
- 存档键：`gift.xxx`（新玩家礼物防重复）、`wild_xxx_spawned.num`（野生生成计数）。

### 1.5 版本与兼容

- `api_version = 10`，`all_clients_require_mod = true`，`priority = -100`（modinfo.lua:116-123）。
- 中文/英文双语：`TBAT.LANGUAGE` 自动检测（atbooks1/modmain.lua:113-136），字符串统一走 `TBAT:GetString2(prefab, key)` 查语言表（imports_of_tbat/02_01_strings_ch.lua 等）。
- 官方 API 破坏兼容修复：`imports_of_tbat/08_fix_for_klei.lua`、"给科雷修 bug"（atbooks2/modmain.lua:107）。

---

## 2. 美术风格专题

### 2.1 KTEX 格式实测（已解码验证）

实测 `modicon.tex` 与全量 1005 张 tex，确认格式：

```
offset 0    : magic "KTEX" (4B)
offset 4    : format u32（高位是标志位：0xFFF0_2240 RGBA8 / 0xFFFD_8220 DXT5 / 0xFFF1_6220 DXT5 等，低 16 位区分族）
offset 8    : mip 头列表，每 10B：w u16, h u16, pitch u16(常为0), size u32
数据区      : 8 + 10*N 起（N=mip 数），按 mip0..mipN 顺序排列
```

判断压缩方式不看 format 数字，看 **mip0 块大小**：`size == w*h*4` → RGBA8；`per_block == 16` → DXT5/BC3（每像素 1B）；`per_block == 8` → DXT1/BC1（0.5B）。mip 链最后一级 1x1 的 size 固定为 16（DXT5 块）或 8（DXT1 块）。

**全量格式分布**：DXT5 1001 张（绝对主流）、DXT1 2 张、RGBA8 2 张（modicon 及另一个 128x128 图标）。最大图集 2048x2048（UI 图集、生物动画画布）。动画 zip 内 atlas 为 2048x2048 大画布，实际内容只占小部分（桂花猫图集仅 27% 不透明像素，内容区集中）。

### 2.2 XML Atlas 组织规律

**atbooks1 模式——"一物一图集"**：`images/inventoryimages/` 下 373 组 `xxx.tex + xxx.xml`，每 atlas 单一元素，element 名 = tex 名：

```xml
<Atlas><Texture filename="tbat_material_emerald_feather.tex" />
<Elements><Element name="tbat_material_emerald_feather.tex" u1="0" u2="1" v1="0" v2="1" /></Elements></Atlas>
```

配套 `_single_xml_creater.py`（atbooks1/images/inventoryimages/）自动批量生成这类 xml。注册时 `RegisterInventoryItemAtlas("images/inventoryimages/xxx.xml", "xxx.tex")`。

**atbooks2 模式——"合并大图集"**：`images/tbat_inventoryimages.xml` 一个 1024x512 图集塞 81 个 element，每个 element 是 64x64 网格单元（u1/u2 步长 0.0625 = 1/16），命名 `物品名.tex`（如 `tbat_windchime_cat_backpack_skin6.tex`），皮肤变体用 `_skinN` 后缀同列排布。UI 图集 tbat_ui.xml 仅 3 个元素（note_background.tex 等）。

**图鉴内容图集**：`images/ui/atbook_wiki/content/{creature,food,plant,structure,inventory,decor}/` 每条目一对 tex+xml（立绘大图），`food/img/` 存小图。

### 2.3 像素统计与画面内容（ASCII 解码预览实测）

以下全部为实际解码 mip0 + 像素统计结果（含画面内容人工判读）：

**Mod 图标（modicon.tex，128x128 RGBA8）**：红色书封——主色 #b03010 深红、#f0d0b0 米白、#f0f070 金黄、#101010 黑。顶部一条金黄装饰带，中央偏右深色主体物（K 暗部 + 金边）。饱和 141、亮度 110，全不透明。**红底金边书 = 万物书视觉锚点。**

**地皮纹理（levels/textures/，23 张）**：平均饱和 84、亮度 128，色相饱和度差异极大（低饱和路面 11 → 高饱和幻木地板 180）：

| 纹理 | avg RGB | 饱和 | 画面 |
|---|---|---|---|
| tbat_milkyway_cloud | (233,180,187) 粉白 | 60 | 粉彩云朵，W 亮部 + m 粉阴影 |
| tbat_turf_lavender_dusk | (174,139,154) 紫 | 62 | 薰衣草紫 + 白色花簇亮块 |
| tbat_turf_fallen_cherry_blossoms | (157,112,109) 暗红 | 78 | 满地樱花瓣，红底黄点 |
| tbat_turf_emerald_feather_leaves | (114,119,95) 灰绿 | 55 | 绿叶 + 红色羽毛点缀（翠羽鸟主题） |
| tbat_turf_clover_butterfly | (182,177,125) 黄绿 | 79 | 三叶草草地 + 红花 + 右上角蝴蝶 |
| tbat_turf_fake_ocean_shallow/middle/deep | 浅(180,208,213)→深(77,135,171) | 39-139 | 三阶渐变海洋（岛屿造海） |
| tbat_turf_water_sparkles | (174,204,208) | 41 | 水面 + 白色波光 |
| tbat_turf_checkerfloor_pink | (161,120,141) | 68 | 粉白棋盘格，图案规则清晰 |
| tbat_redautumn_maplepath | (169,100,89) | 122 | 红枫落叶路 |
| tbat_terracotta_road | (189,152,124) | 92 | 陶土黄橙路 |
| tbat_herringbone_road / checkerboard_road | 灰 (142-158) | 11-26 | 人字形/棋盘石板路（低饱和灰） |
| tbat_miragewood_floor_{purple,yellow,blue,orange} | 深 (76,27,41) 等 | 145-180 | **高饱和深色**幻木地板（紫/黄/蓝/橙四色） |

配色逻辑：低饱和中性色（石板/陶土路）+ 主题高饱和色（樱花红、薰衣草紫、幻木四色）混用，保证"幻想感"又不刺眼。

**物品图标（373 张）**：平均饱和 41、亮度 50、alpha 117（半透明描边系）。典型如翠羽羽毛——绿色羽毛斜放、黑色粗描边（K 轮廓清晰）、高光 G；与官方 DST 图标风格一致，黑描边 + 高光。

**生物动画图集**：
- 桂花猫：橙黄猫多帧贴图，黑色描边，画布 2048 利用率低。
- 枫叶松鼠：红棕松鼠 + 白腮/白肚（W 亮部），主色 #f0b090/#f07050，对比度高。
- 玫瑰双生鹅：白色鹅身 + 红冠（atbooks2）。
- 枫叶狐狸：红橙狐狸 + 白尾尖 + 黑描边。
- 樱花兔兔秋千（建筑）：白兔剪影 + 深红木框。

**UI 图集（ui/ 目录 200+ 张）**：平均饱和 44、亮度 50（**深色 UI 风**）。实测：
- `atbook_wiki/icon_k.tex`（图鉴背景）：中央白纸书页（W 大块）+ 红棕木质书脊镶边 + 绿/金花纹，**"打开的书"构图**。
- `icon_yxy.tex`：金色横幅标题带。
- `icon_an_hxdy` 等 6 个 tab 按钮：深木牌 + 金字 + 红边，统一设计语言。
- `icon_gb`（关闭钮）：绿环 + 红叉。
- atbooks2 `tbat_ui.tex` 的 note_background：**米黄羊皮纸**（#f0f0b0 19%）+ 深棕木框 + 左上绿饰——冒险家笔记页风格。
- atbooks2 HUD 图集：主色 #f0f0f0 白 + #d0f0f0 浅青（小地图图标为蓝色水滴 + 粉色心形 + 金色建筑标）。

**一句话风格总结**：红金书卷纹样 + 白纸羊皮纸 UI + 黑描边高饱和生物立绘 + 低饱和中性地皮混搭高饱和主题色地皮（樱花粉/薰衣草紫/幻木四色），整体是"童话幻想绘本"画风，UI 深底浅字偏暗金配色。

---

## 3. 特色岛屿 / 植物 / 地形

### 3.1 幻想岛屿生成（本 mod 最精华的地图创作系统）

全链路：**岛位搜索 → 分块瓷砖铺设 → 锚点装修**，全部在主世界 OnPostInit 后异步执行。

**入口**：`12_fantasy_island_creater/01_base_api.lua:351-375`
```lua
TBAT:AddTheWorldRealOnPostInitFn(function()
    TBAT:AddOnPostInitFn(function(self)
        if not TBAT.MAP:HasIslandCreateTask() then self:ClearAllBlocks(); return end
        self:RunIslandTaskFns()   -- 逐个执行岛屿任务（含搜索）
        self:ClearAllBlocks()
    end, TBAT.MAP)
end)
```

**步骤一：候选位置搜索**（`02_avalable_location_searcher.lua:42-`，豆包 AI 优化，约 7 秒搜出 1500+ 候选）：
- 全图 tile 缓存在 `ocean_tiles`/`quick_ocean` 二维数组（行 57-66）。
- 黑名单实体（epic/建筑/海洋植物等，行 11-17）影响半径 30 记录进 `BLACKLIST_ENTS`，用**矩形 AABB 碰撞检测**预判（行 79-82）。
- 候选区域校验："角落 4 点 + 中心 1 点"抽查 + 三行三列全量检查（行 104-155），全部须为海洋且避开黑名单。
- **动态步长**：遍历时用 `os.clock()` 卡 4 秒预算，超时就 `step+1` 加大步长（行 168-179）。这是"限时搜索"的教科书写法。
- 随机取一个候选 → `TBAT.MAP:CreateBlock("fantasy_island_blocks", x, y)`。

**步骤二：36x30 岛块瓷砖铺设**（`03_fantasy_island_block_main.lua:13-71`）：
- 主块把 36x30 区域内的实体全删（`GetEntitiesOnTileAtPoint` 循环 Remove，行 22-32）。
- 划分 6 个子块（main + a-e），每个子块用 `tbat_com_special_timer_for_theworld:AddTimer` **错帧创建**，避免一次性卡死（行 61-68）。
- 每个子块是一张硬编码的 ASCII 瓷砖图：`data` 数组逐格 `TheWorld.Map:SetTile(x, y, tile)`（行 88-108）。tile 用 `WORLD_TILES[string.upper("tbat_turf_emerald_feather_leaves")]` 这种方式取自定义地皮索引。
- 码头：`dockmanager:CreateDockAtTile(tile_x, tile_y, WORLD_TILES.MONKEY_DOCK)`（行 110-118）。
- 创建**唯一锚点** `CreateUniqueAnchor`（TheSim:FindEntities 查重，行 123-134）。

**步骤三：JSON 数据驱动的锚点装修**（`03_fantasy_island_block_main.lua:142-147` + `01_base_api.lua:234-298`）：
```lua
TBAT.MAP:AddAnchorDecorateTask("tbat_room_anchor_fantasy_island_main", "level_1", function(x, y, z)
    local str = '{"grass":{"prefab":"grass","points":[{"z":8.6,"x":-11.3},...]}, "tbat_the_tree_of_all_things":{"prefab":"tbat_the_tree_of_all_things","points":[{"z":0,"x":0}]}, ...}'
    TBAT.MAP:DecorateIslandByAnchor(str, x, y, z)
end)
```
`DecorateIslandByAnchor` 支持 per-prefab 参数：points（坐标数组或 JSON）、rotation、tbat_skin 皮肤、mirror、scale、health_percent、fn 回调（`01_base_api.lua:234-298`）。**皮肤系统直接嵌入世界装修数据**（`has_tbat_skin = true` 时以 key 为皮肤名，行 277-279）。

**开发工作流亮点**：`00_island_decorate_fns.lua` 是配套"扫描器"——在游戏里圈选装修区域，自动把实体转成 JSON 数据（prefab、相对坐标、缩放、生命值、皮肤），打印/存盘，再粘回代码（行 58-141，注释掉的扫描逻辑 + 打印模板 `'["'..prefab..'"]=true,#'..name..'@'`）。**这就是"编辑器 → 数据 → 代码"资产管线。**

### 3.2 特色地形与 tile

- 自定义 tile 走官方 turf 注册（`10_turfs/`），纹理在 `levels/textures/`，mini 版本给地图用。tile 索引通过 `WORLD_TILES[string.upper("turf_名")]` 取（03 文件行 86）。
- `TBAT.MAP:GetTileIndexByItemPrefab`（01_base_api.lua:209-215）：`"turf_savanna"` → 反查 WORLD_TILES，写地图脚本不用记数字。
- **伪海洋**：`turf_fake_ocean_{shallow,middle,deep}` 三级渐变——岛屿周围用 SetTile 铺"假海"地皮，视觉上是海但仍是陆地逻辑（可用于岛屿边缘过渡）。水百合猫等水面生物点：`tbat_turf_water_lily_cat` 是全黑图（特殊 alpha 材质）。
- 野生生成器（`02_the_world_upgrade/` 目录 15 个 spawner）：清甜椰子树、血红枫树、蒲公英猫、雪梅、桂花猫石屋、枫叶松鼠树屋、水晶矿、蘑埚蜗牛屋、三叶草鹤、薰衣草花房、礁石灯塔……统一模式 = 世界数据计数 + 锚点/地形 tag 匹配 + `GetSurroundPoints` 找可生成点（见 §4.7）。

### 3.3 特色植物

**农场作物**（`17_farm_plant_defs/`）：3 种作物 + 3 种变异（幻想苹果/蜜桃/土豆），直接填官方 `PLANT_DEFS` 表（`01_fantasy_apple.lua:32-140`）——bank/build 动画、生长时间、潮湿度、肥料需求/产出、季节、重量数据、8 阶段 plantregistryinfo、巨型合影动画。关键 hook（`01_fantasy_apple.lua:154-169`）：
```lua
AddPrefabPostInit("tbat_farm_plant_fantasy_apple", function(inst)
    local old_UpdateResearchStage = inst.UpdateResearchStage
    inst.UpdateResearchStage = function(self, stage)
        self:PushEvent("tbat_event.onupdate_researchstage", stage)
        if stage == 5 and self.is_oversized then
            if math.random() <= .3 or self.force_mutated then
                SpawnPrefab("tbat_farm_plant_fantasy_apple_mutated"):PushEvent("normal_switched", self)
            end
        end
        return old_UpdateResearchStage(self, stage)
    end
end)
```
30% 概率巨型果实切换为变异作物实体——"变异作物"实现方式 = 实体替换 + normal_switched 事件。

**图鉴植物书 hook**（`00_01_plantregistryupdater_hooker.lua:21-117`）：`AddGlobalClassPostConstruct("plantregistrydata", "PlantRegistryData", ...)` 把官方植物记录器 11 个 API 全部包装，做**果实名 → 植物名 → 变异名映射**（名字修复，行 24-51）。官方系统扩展的通用姿势：先找 `GetKnownPlantStages`/`KnowsPlantStage` 这类入口，批量包一层名字转换。

其他植物：风铃水母（水生植物，带兑换店 `07_06_jellyfish_shop_list.lua`）、蒲公英猫、幻木、血红枫树、清甜椰子树、三叶草鹤草箱、月光记忆晶泉等。

---

## 4. 核心设计模式

### 4.1 TBAT 全局框架：Class 实例当命名空间

`atbooks1/modmain.lua:44-50`：
```lua
TBAT = TBAT or TUNING.TBAT_BASE_NODE or Class()
rawset(_G,"TBAT",TBAT); rawset(GLOBAL,"TBAT",TBAT)
TUNING.TBAT_BASE_NODE = TBAT
```
用 Class() 实例承载全局 API：`TBAT.MAP`、`TBAT.SKIN`、`TBAT.FNS`（常用函数）、`TBAT.ClientSideData`、`TBAT.PARAM`（调参表）。好处：多 mod 协作时其他 mod 可以 `TBAT.LANGUAGE` 直接覆盖语言（modmain.lua:92-136 注释明确写了第三方语言 mod 接入协议）。**版本防重复加载**：`TBAT.__loaded_flag` + 每 300 秒播报"发现多个版本加载行为"（modmain.lua:52-70）。

### 4.2 通用 KV 存档组件 tbat_data（+ 玩家数据桥 tbat_data_to_world）

`components/tbat_data.lua`（129 行）：
- `DataTable` KV 表，`Get/Set/Add(index,num,min,max)`（行 53-78，Add 带 clamp）。
- `OnSave/OnLoad` 直存整个表（行 92-119）。
- `AddOnLoadFn/AddOnSaveFn` 挂回调（行 31-50）。
- **PostInit 队列**：`AddOnPostInitFn` 收集的 fn 在 OnPostInit 时执行（行 80-90）——世界加载后、任务开始前的初始化钩子。
- `tbat_data_to_world`：玩家组件数据**写入世界存档**（防跨存档重复发礼物的依据，见 03_new_enter_gifts.lua:15-31）。

### 4.3 RPC 框架：多信道锁 + 超时重发 + 回调（最成熟的封装）

`components/tbat_com_rpc_event.lua`（207 行）：
- `PushEvent(event_name, data, target_inst, succeed_callback, timeout_callback)`（行 38-67）：序列化 JSON → RPC 发送 → 注册回调。
- **5 个 RPC 信道轮转**（RPC_LOCK_1..5，行 89-133）：SendModRPCToClient 单信道 1 帧内只能发一次（官方限制），多信道轮流发绕开限制；全忙则 2 帧后重试（行 130-132）。
- **超时重发**：DoTaskInTime(2s) 超时任务，客户端回执 `Send_Event_Finished` 取消（行 76-87, 136-146, 149-176）。
- `BroadcastEvent` 给所有玩家（行 190-198）。
- 单机直通：ThePlayer==self.inst 且 ismastersim 时直接 PushEvent 不走 RPC（行 43-52）。
- 服务端事件去重：`actived_events[task_id]` 防重复触发（行 183-184）。

### 4.4 客户端数据桥：服务端读写客户端存档（任务中心数据层）

`components/tbat_com_client_side_data.lua`（87 行）：
- `GetByCallback(index, cb)` / `Set(index, value)`：服务端通过 RPC 事件让客户端读写 `TheSim:GetPersistentString("tbat_client_side_data")`（01_client_data_api.lua:13-37），JSON 往返。
- **Sheet API**：`SheetGetByCallback(sheet, index, cb)` 自由表 + `PlayerGet/PlayerSet` 按 userid 分区（01_client_data_api.lua:47-58）。
- **nil 处理**：`value or "nil"` 字符串占位，解码后还原（client_side_data.lua:25, 37）。
- 数据压缩：`14_zip_json_data.lua` 用**常用字符串密码表**替换（"tbat_"、"tbat_eq_"、全部图标文件名进表），压缩后再传输，传输 payload 大幅缩小（含 `generate_common_strings` 自动生成建议表的工具函数）。

### 4.5 图鉴（万物书本体）：数据驱动 + 分类 UI

- 组件 `atbook_wiki.lua` 只有 6 行（Class 壳），**核心是客户端 widget**：`widgets/atbook_wikiwidget.lua`（1350 行）+ `atbook_wikiwidget_defs.lua`（2935 行，纯数据）。
- 6 大分类 `BTNINDEX = {"ISLAND","CREATURE","PLANT","STRUCTURE","INVENTORY","FOOD"}`（wikiwidget.lua:17-24），每条目数据含 prefab/name/type/ys(野生)/jy(家养) 双语描述（defs.lua:2-94）。
- 资源路径约定：`images/ui/atbook_wiki/content/{分类}/{prefab}.xml` + `page/`/`img/` 子目录（wikiwidget.lua:138-148）。
- 打开/关闭推事件：`tbat_event.wiki_open/close/created`（wikiwidget.lua:116-134），HUD 悬浮按钮由 `06_widgets/01_wiki_button.lua` 提供（位置存客户端存档）。
- **皮肤标签页**：CDK 验证输入框（InputDialogScreen 弹层）→ `SendModRPCToServer(MOD_RPC["ATBOOK"]["atbook_brcverify"], ...)` → `ThePlayer.replica.tbat_com_skins_controller:HasSkin(skincode)` 显示已拥有皮肤（wikiwidget.lua:262-283, 305-325）。皮肤列表数据同样在 defs.lua。
- 解锁收集链（叙事线）：**BOSS 掉落冒险家笔记 → 玩家读笔记（tbat_note 组件，atbooks2 复制官方 simplebook）→ 交给翠羽鸟 NPC → 图鉴/兑换解锁**。笔记正文在 `languages/tbat_note_text_chinese.lua`，阅读屏幕 `screens/tbat_adventurers_notes_screen.lua`（米黄羊皮纸 UI）。

### 4.6 皮肤系统：自建 PREFAB_SKINS 转置

`11_prefab_skin_sys/01_item_prefab_skins_api.lua`（1340 行模块群）：
- 双向索引：`SKINS_DATA_SKINS[skin_name]` + `SKINS_DATA_PREFABS[prefab_name]`（行 61-63）。
- 两个 replica 组件：`tbat_com_skins_controller`（玩家）+ `tbat_com_skin_data`（物品/建筑）（行 50-53）。
- 官方接入点注释（行 1-45）：`PREFAB_SKINS/PREFAB_SKINS_IDS` 只列已拥有皮肤；`RecipePopup:GetSkinOptions()` 改制作栏贴图；放置时 hook `PlayerController:StartBuildPlacementMode`；服务端监听 `buildstructure/builditem` 事件。
- 配套组件：`tbat_com_skin_data`（实例状态）、`tbat_com_skin_tool`（改皮工具）、`09_default_skin_name_replacer`（默认皮肤名替换）、`07_reskin_tool_action`（改皮动作）、`101_cdkey_input_debug`（CDK 解析，`tbat_com_cdkey_analyzer`）。
- 免费皮肤/权限皮肤分开注册（atbooks2 tbat_free_skins / tbat_permissions_skins）。

### 4.7 野生生成器模式（世界内容投放标准写法）

以椰子树为例（`02_the_world_upgrade/03_wild_coconut_tree_spawner.lua:20-63`）：
```lua
if TheWorld.components.tbat_data:Add("wild_coconut_tree_spawned.num",0) >= MIN_TREE_NUM then return end
-- 半径 40 逐圈缩小，收集 CanPlantAtPoint 可种植点
while true do
    local points = TBAT.FNS:GetSurroundPoints({ target = Vector3(x,y,z), range = radius, num = radius*5 })
    for i,pt in ipairs(points) do
        if TheWorld.Map:CanPlantAtPoint(pt.x,0,pt.z) then table.insert(ret_avalable_points,pt) end
    end
    radius = radius - 3; if radius <= min_radius then break end
end
local avalable_points = TBAT.FNS:GetRandomDiffrenceValuesFromTable(ret_avalable_points, max_num)
for i,pt in ipairs(avalable_points) do
    local tree = SpawnPrefab("tbat_plant_coconut_tree")
    TheWorld.components.tbat_data:Add("wild_coconut_tree_spawned.num",1)
    tree.Transform:SetPosition(pt.x,0,pt.z)
    tree.components.growable:SetStage(4)   -- 直接拔苗到成年
end
```
模式：世界数据计数防重复 + 环形采样 + 地形过滤 + 去重随机 + 出生即设定成长阶段。atbooks2 的枫叶美食屋投放（tbat_world_init.lua:15-70）走 pigking 附近落叶林地皮查找 + 最小间距约束（8 格），风格更工程化。

### 4.8 世界级自适应定时器（加载范围外逻辑）

`components/tbat_com_special_timer_for_theworld.lua`（197 行）：
- 挂 TheWorld 的 0.1s 周期任务，**专门跑加载范围外 inst 的定时逻辑**（岛屿分块创建用它错帧）。
- **性能自适应**：`os.clock()` 实测每轮耗时，超过预期就 `update_interval += 0.01`（上限 1s）并重建 DoPeriodicTask（行 43-58）；`serverpauseddirty` 后重置（行 63-76）。
- 挂载时机：等 `ms_registermigrationportal`（世界就绪）后 3 秒启动（行 80-89）。
- 一次性任务队列 `AddOneTimeTimer/DoAllOneTimeTimers`（行 94-116），注释明确"加载范围外搞事太容易闪退"。

### 4.9 生物/宠物/NPC 模式

- **翠羽鸟 NPC**（`prefabs/22_tbat_npc/01_01_emerald_feather_bird.lua`）：复用官方 `carnival_host` 动画 bank + 自定义 build（行 10-12, 110-111），`playerprox` 靠近对话（行 139-144）、`knownlocations:RememberLocation("home", ...)` 锚点绑定（行 76-80）、随机台词走 TBAT 语言表（行 83-87）、`inst.persists = false` 每次开档重建（行 130）。talker 染色（行 117）。
- **万物之树**（`07_tbat_buildings/00_03_tbat_the_tree_of_all_things.lua`）："活建筑"——12 云 + 12 星 + 29 宠物 = 53 个 `SpawnChild` 特效实体用 `Follower:FollowSymbol(parent.GUID, layer, ...)` 钉在动画符号层上，各自循环动画 + 随机相位 `SetTime(4*math.random())`（行 23-61）；每日刷新星尘掉落（行 108-119）；庇护半径参数化（modinfo MAIN_TREE_PROTECT_RADIUS）。
- **宠物等级**：玫瑰双生鹅 `tbat_twin_goose_level.lua`——`net_smallbyte` 网络变量 + dirty 事件推世界广播，`level:set(0)` 本地默认值保证确定性（atbooks2）。
- **幻灵水池** `tbat_pool.lua`：按 `TheWorld.state.cycles`（游戏日）做"每日一次"限制表，key 用 `doer.userid`（atbooks2）。

### 4.10 烹饪/配方系统

- atbooks1 烹饪模块（`15_cooking/`）兼容**棱镜（fwd_in_pdt）**的食谱注册格式：`test` 函数（names/tags 计数）+ hunger/sanity/health + cookbook_tex + overridebuild 图层替换（`01_01_phase2_cooked_foods_data.lua:5-37`）。
- 蘑埚蜗牛锅（`16_mushroom_snal_cauldron_sys/`）：自定义 4 格合成锅，配方按**增序索引 id 注册、找第一个匹配**、满 4 格才做、同种类物品按总数计、多余材料返还（`_all_cauldron_modules_init.lua:2-15` 注释即规格文档）。配套"悄悄话"API（03_whisper_of_snail.lua）。
- 自助点菜机 atbook_ordermachine + 厨狼 atbook_chefwolf：容器 + 机器 UI（widgets/atbook_chefwolfwidget.lua）。

---

## 5. 亮点技巧

1. **官方系统名字修复 hook**：植物名/果实名/变异名三套名字互相纠缠导致图鉴解锁失效，用 `AddGlobalClassPostConstruct("plantregistrydata", ...)` 批量包装 11 个 API + "取最短名字"启发式修复（`17_farm_plant_defs/00_01_plantregistryupdater_hooker.lua:24-51`）。**解决"官方系统扩展"型 bug 的通用手法：先列全入口 API，再统一包一层。**
2. **AddComponentAction 合并器**：子模块各自注册 action 不覆盖（根 modmain.lua:53-71）。多人协作多模块场景直接抄。
3. **动态步长限时搜索**：世界生成搜索候选位时用 `os.clock()` 预算控制 step（`02_avalable_location_searcher.lua:168-179`）。4 秒/7 秒/5 秒/9000 候选的参数注释是调优记录，非常有参考价值。
4. **JSON 密码表压缩**：客户端数据传输前把高频字符串（prefab 名前缀 + 全部图标名）替换成短 id（`_0_common_func/14_zip_json_data.lua`），还提供自动生成建议表的工具函数——**RPC payload 瘦身的现成方案**。
5. **全局变量访问统计调试**：modname 为内测名时给 env 套 `__index` 元表，统计每个全局变量访问次数，>99 次打印警告 + StackTrace（atbooks1/modmain.lua:1-32）。**死循环/热全局排查神器。**
6. **"编辑器→JSON→代码"装修管线**：游戏内扫描实体自动生成 JSON 装修数据（`00_island_decorate_fns.lua`），数据再灌回 `DecorateIslandByAnchor`。**手动摆岛+复现的成熟工作流。**
7. **Follower:FollowSymbol 挂特效**：53 个动态特效实体钉在建筑动画符号层（万物之树），每个独立循环 + 随机相位，实现"活建筑"而不卡 AnimState（`00_03_tbat_the_tree_of_all_things.lua:23-61`）。
8. **声音 hook 模块**（`22_tbat_npc/01_04_sound_hook.lua`）：NPC 音效单独成文件，prefab 里 require 注入——声音与逻辑解耦。
9. **加载范围外定时器 + 错帧创建**：大块地图分块创建用世界级定时器排队（`03_fantasy_island_block_main.lua:61-68`），避免单帧卡死。
10. **存档键规范**：`gift.xxx` 防重复送礼 / `wild_xxx.num` 生成计数 / 按 userid 分区客户端存档——命名即文档。
11. **皮肤数据直嵌装修数据**：`has_tbat_skin=true` 时以 JSON key 为皮肤名（`01_base_api.lua:277-279`），装修系统与皮肤系统零耦合打通。
12. **性能自适应定时器**（见 §4.8）——卡顿自动降频、暂停后复位，长稳服务器必备。
13. **多语言接入协议**：第三方语言 mod 可通过 `TBAT.LANGUAGE` + `TBAT.STRINGS` 覆盖（atbooks1/modmain.lua:92-136 注释完整协议），语言包与代码彻底解耦。

---

## 6. 可复用模板

### 模板 A：双子/多子 mod 加载器（根 modmain.lua）
```lua
-- 复制根 modmain.lua:38-124 骨架
local SUBMOD_PREFAB_WRAPPERS = { ["atbooks1"] = "atbooks_all_atbooks1_prefabs" }
local function EnsureSubModSearchPath(submod)   -- 注入 package.path + assetpath
    local scripts_path = string.gsub(root .. submod .. "/scripts/?.lua;", "/", "\\")
    if not string.find(package_ref.path, scripts_path, 1, true) then
        package_ref.path = scripts_path .. package_ref.path
    end
    local asset_path = string.gsub(root .. submod .. "/", "/", "\\")
    table.insert(package_ref.assetpath, { path = asset_path, manifest = nil })
end
local function RunSubMod(submod)
    EnsureSubModSearchPath(submod)
    local subenv = CopyEnv(env); subenv.GLOBAL = GLOBAL
    subenv.MODROOT = root .. submod .. "/"
    subenv.modimport = function(name)  -- 私有 modimport
        local result = kleiloadlua(subenv.MODROOT .. name)
        setfenv(result, subenv.env); return result()
    end
    local fn = kleiloadlua(subenv.MODROOT .. "modmain.lua")
    RunInEnvironmentSafe(fn, subenv)
    MergeArrayField(env, subenv, "Assets")          -- 资源合并回父环境
    MergeArrayField(env, subenv, "PreloadAssets")
end
```
用途：多章节/多作者拆分大 mod，独立 env 防污染，统一资产合并。

### 模板 B：RPC 封装（服务端→客户端事件 + 回调）
```lua
-- 复制 tbat_com_rpc_event.lua:38-67 骨架，简化版
function Com:PushEvent(event_name, data, succeed_cb, timeout_cb)
    if ThePlayer == self.inst and TheWorld.ismastersim and not TheNet:IsDedicated() then
        self.inst:DoTaskInTime(0.1, function()
            target_inst:PushEvent(event_name, data); succeed_cb and succeed_cb()
        end)
        return
    end
    local task_id = "task_" .. tostring(self.task_id); self.task_id = self.task_id + 1
    self.tasks[task_id] = { ok = succeed_cb, timeout = timeout_cb }
    SendModRPCToClient(CLIENT_MOD_RPC["my_namespace"]["pushevent"], self.inst.userid,
        self.inst, json.encode({ task_id = task_id, event = event_name, data = json.encode(data) }))
    -- 超时重发: self.inst:DoTaskInTime(2, function() ... 重新 Send ... end)
end
-- 客户端收包: data.task_id 去重 -> target:PushEvent(data.event, decoded) -> 回执 Send_Event_Finished
```
要点：task_id 去重、超时重发、成功/超时回调、单机直通。

### 模板 C：服务端↔客户端存档桥（KV + 按玩家分区）
```lua
-- 复制 components/tbat_com_client_side_data.lua 骨架
function TBAT.ClientSideData:Set(index, value)
    local data = {}
    TheSim:GetPersistentString("my_mod_data", function(ok, str)
        if ok and str then local f, t = pcall(json.decode, str); if f then data = t end end
    end)
    data[index] = value
    TheSim:SetPersistentString("my_mod_data", json.encode(data), false, function() end)
end
function TBAT.ClientSideData:PlayerSet(index, value)
    local uid = ThePlayer and ThePlayer.userid or "no_player"
    local t = self:Get(uid, {}); t[index] = value; self:Set(uid, t)
end
```
用途：UI 布局记忆、本地进度、皮肤持有表——一切"放服务器会漂、放客户端没人管"的数据。

### 模板 D：数据驱动图鉴/百科 UI
```lua
-- 结构: defs(数据) + resource(资源名表) + widget(渲染)
local CONTENT = {
    CREATURE = { A = { { prefab = "my_creature", name = "名字",
        ys = { sc = "野生生成方式", sd = "属性数值", tx = "习性" } } } }
}
-- widget 骨架（复制 atbook_wikiwidget.lua:35-136 的构造 + 138-148 的资源路径约定）:
local function GetContentResources(category, index)
    local prefab = CONTENT[BTNINDEX[category]][type][index].prefab
    local path = string.lower(BTNINDEX[category])
    return "images/ui/mywiki/content/" .. path .. "/" .. prefab .. ".xml", prefab .. ".tex"
end
-- 打开/关闭推事件 tbat_event.wiki_open/close，HUD 悬浮按钮位置存客户端存档
```
要点：内容 = 纯数据表（可被语言包/策划替换），渲染 = 通用网格 + 详情页，资源路径按约定生成。

### 模板 E：世界生成"搜索+铺块+装修"三件套
```lua
-- 1) 注册岛屿任务
TBAT.MAP:SetIslandTaskFn("my_island", function()
    -- 2) 限时搜索: ocean_tiles 缓存 + 黑名单 AABB + 动态步长 (复制 02_avalable_location_searcher.lua)
    -- 3) 铺块: 硬编码 tile 数组 + SetTile (复制 03_fantasy_island_block_main.lua:88-108)
    -- 4) 锚点: CreateUniqueAnchor(x, y, z) 查重生成
    -- 5) 装修: DecorateIslandByAnchor(json_str, x, y, z) -- points/rotation/skin/scale/health_percent 全支持
    return true  -- 成功标记, 世界数据存档防重
end)
-- 执行时机: AddTheWorldRealOnPostInitFn -> RunIslandTaskFns (01_base_api.lua:351-375)
```
要点：世界数据记 `island_id=true` 防重复；装修数据支持 JSON 字符串直接灌。

---

## 附：任务要求的回报数据

- **笔记行数**：本文约 400 行。
- **文件覆盖统计**：浏览根目录 5 文件 + scripts/ 3 文件；atbooks1 下 modmain/modinfo、scripts 全目录结构（prefabs 24 分类、components 30+、brains 9、stategraphs 5、widgets 8、_key_modules_of_tbat 18 个模块、imports_of_tbat 12 文件、levels 纹理目录、images 全部分类）、atbooks2 下 modmain/scripts/screens/anim 目录。逐行精读约 30 个文件（合计约 6000 行），grep 扫描全部 723 个 lua；实际解码 tex 30+ 张（含全量格式统计 1005 张 + 23 张地皮像素统计 + 12 张 ASCII 画面预览 + 9 张 UI 元素 + 5 张生物动画图集），解析 XML atlas 20+ 个（含 81 元素合并图集），拆包 anim zip 8+ 个确认 anim.bin/build.bin/atlas-*.tex 结构。
- **美术风格一句话总结**：红金书卷纹样 + 羊皮纸 UI 的"幻想童话绘本"风——深色木框白纸图鉴、米黄笔记页、黑描边高饱和生物立绘，地皮以低饱和中性路面打底、配樱花粉/薰衣草紫/幻木四色等高饱和主题色块，整体偏暗金暖色调。
