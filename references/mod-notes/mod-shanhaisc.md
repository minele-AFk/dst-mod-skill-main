# 山海秘藏（DST Mod 3046680574）深度学习笔记

> 分析对象：`C:\Users\22308\Desktop\new\3046680574`（229MB，中文修仙/山海经题材大型 mod）
> 版本：`102 2.8.237`，api_version 10，制作团队：动画师 素冥真仙 / 代码师 金曦沐晨 玉萍经纬
> 核心：全部 lua 为明文（未混淆），`mod_key_modules_for_mountain_and_sea/` 目录是官方"源码版"模块，直接可读

---

## 1. Mod 全貌

### 1.1 规模统计

| 类型 | 数量 | 说明 |
|---|---|---|
| lua | 357 | prefabs 约 200+ 个实体定义 + components/brains/map/fsmdata |
| tex | 244 | 全部 DXT5 压缩，无 mip 链（单 mip 大图） |
| xml | 239 | 图集描述（222 个为"单图单 Element 同名"模式） |
| anim zip | 362 | 每个 zip = anim.bin + build.bin + atlas-N.tex |
| 模块源码 | 40 | `mod_key_modules_for_mountain_and_sea/` 8 大功能模块 |
| 音频 | 若干 | `sound/`（.fev/.fsb FMOD）+ `exported_sound/`（.fdp FMOD Designer 工程，狐王 BGM/朱雀叫等自制音乐） |

### 1.2 目录结构（加载关系）

```
modmain.lua (105行, 入口)
├── modimport("scripts/fsm_skin_system.lua")         -- 物品皮肤系统(1203行, token激活)
├── modimport("mod_key_modules_for_mountain_and_sea/00_mod_key_modules_for_mountain_and_sea.lua")
│   ├── 01_basic_modifications/   -- 基础修改: 图集注册/小地图/turf注册/移植/食物排序/配方过滤/养殖/房屋/弓箭/动作/状态机/容器/RPC/秃鹫
│   ├── 02_fsm_Island_generation/ -- 世界升级 + 太虚岛 + 招摇岛
│   ├── 03_fsm_main_modules/      -- 丹药主模块/UI组件/初始物品/山海绘卷(图鉴书)
│   ├── 04_fsm_resource_refresh/  -- 资源刷新(甘木/生物/树/桂兔/火龙果等, 多数已ban)
│   ├── 05_fsm_liandan/           -- 炼丹系统(配方配表 + 丹炉框架)
│   ├── 06_fsm_love/              -- 情缘系统(连理树6阶段/红绸/新郎帽/大羿/恒娥NPC)
│   ├── 07_fsm_book/              -- 山海绘卷图鉴(9标签: 地形/仙宗/角色/丹药/异兽/灵植/材宝/佳肴/公告)
│   └── 08_fsm_fox/               -- 狐王系统
├── PrefabFiles = { "fsm_skin_prefabs", "fountains_and_sea_are_mysterious__all_prefabs" } -- 总入口加载全部prefab
├── modimport("scripts/fsm_prism_dressup_compat.lua") -- 棱镜(Prism)模组幻化兼容
└── AddClassPostConstruct 补丁: container/container_replica(无效opener清理), widgets/controls(屏蔽智能锅对炼丹炉的干扰)
```

`scripts/prefabs/` 分 20 类：00_other / 01_items / 02_materials / 03_equipments / 04_foods / 05_cooked / 06_buildings / 07_resources / 08_plants / 09_minerals / 10_animals / 11_boss / 12_turfs / 13_debuffs / 14_special_effects / 15_characters / 16_events / 17_rooms / 18_npc / 19_scrapped_bill（废案）

`scripts/fsmdata/`：配方与公式数据（pellet_recipes.lua / ruyi_pellet_formula.lua / buffs_nya.lua / gsg_shop_nya.lua）

### 1.3 世界设定（modinfo.lua:7-19）

昆仑之墟降临永恒大陆、裂隙招来"祂们"、兕兽裂天、血池涌现、月圆太极化镜、灵气风暴、月下心魔——这是 2 张特色岛屿 + 炼丹修仙 + 山海经异兽的背景框架。注意：**裂隙/血池/心魔等只出现在 lore 文本中**（证据等级 B：无对应 prefab 文件，属设定文案）。

---

## 2. 美术风格专题（重点）

### 2.1 纹理技术规格（全量扫描 244 个 tex）

- **压缩格式：100% DXT5**（格式字节 = byte5 & 0x1F = 2）。无 DXT1/RGBA32。
- **尺寸分布**：64x64 图集 206 个（物品/图标级）、128x128 14 个、512x512 13 个（地皮/UI）、1024x1024 5 个、2048x1024/2048x2048 若干（生物/建筑 atlas）、**4096x2048~8192x8192 巨型 atlas**（fsm_hundun 混沌 8192x8192/87MB、fsm_foxking 狐王 4096x4096/21MB、扶桑/甘木/草缠枝 4096x2048）。
- **关键发现：所有 tex 均为单 mip**（无 mip 链），大图集全尺寸加载——这是 DST 少见的做法，内存开销大但省去 mip 生成。
- KTEX 头实际结构：`"KTEX"(4) + version u8(0x20) + format u8(低5位) + reserved u16(0xFFFD) + N×mip头(10B) + 数据区`。

### 2.2 XML Atlas 组织方式（239 个 xml）

- **单图单 Element（222/239）**：`<Atlas><Texture filename="xxx.tex"/><Elements><Element name="xxx.tex" u1 v1 u2 v2/></Elements></Atlas>`——每个物品/建筑一个独立小图集，Element 名 = 文件名。这是 DST mod 的标准做法，利于 AddRecipe2 的 atlas/image 默认约定（`images/inventoryimages/<name>.xml`）。
- **多 Element 图集仅 3 个**：
  - `images/icons/fsm_gsg.xml`：商城 UI，Element 名 = `a.tex/back.tex/invbg.tex/last.tex/next.tex/quest.tex`（按钮语义化命名）
  - `images/inventoryimages/fsm_zg_pf.xml`：地皮图集，含 `fsm_zg_pf.tex` + `fsm_zg_pf_item.tex`
  - `levels/tiles/stoneroad.xml`：**引用原版** `data/DLC0002/levels/tiles/deciduous.tex`，48 个 Element 名 = 纯数字地皮变体 `00~48`
- **turf 引用模式**：新地皮 tex 直接放 `levels/textures/`（fsm_decorate_taixulslandground 512x512 / fsm_ymfloor_0 等），tile 数字由 WORLD_TILES 注册（见 3.3）。

### 2.3 像素统计结论（40 张代表样本实测，工具 scripts/analyze_art_batch.py，该脚本未随本仓库发布）

| 资产 | 尺寸 | 不透明% | 亮度 | 饱和 | 主色板（量化） | 描边 |
|---|---|---|---|---|---|---|
| 太虚岛地面 fsm_decorate_taixulslandground | 512 | 86.7 | 0.36 | **0.67** | #308010 #008010 #30B010 #208010 | 无 |
| modicon（mod图标） | 128 | 12.2 | 1.00 | 0.00 | 纯白 #F0F0F0（**白色兽面剪影**） | — |
| fsm_yuemen（玉冕） | 64 | 41.2 | 0.41 | 0.52 | #00A060 翡翠绿 #50A0A0 青 #A05050 赭 #000000 | 弱 |
| fsm_zgfence（机关栅栏） | 64 | 13.3 | 0.47 | 0.49 | #D0B0A0 木色 #700080 紫 #704090 蓝紫 | 弱 |
| 巴蛇 fsm_bashe_snake | 2048 | 32.2 | 0.39 | 0.24 | #000000 #A0A0A0 #307050 墨绿 | **强** |
| 金乌 fsm_jinwu | 2048 | 10.9 | **0.29** | **0.64** | #C04000 #B03000 暗红橙 #50A0A0 | **强** |
| 狐王 fsm_foxking | 4096 | 20.9 | 0.76 | 0.49 | #A0E0A0 #C030E0 紫 #F0F0D0 #00A000 | 弱 |
| 混沌 fsm_hundun | 8192 | 24.2 | 0.88 | 0.60 | #F0F0F0 #F0D0E0 粉白 #B09060 棕 | 弱 |
| 扶桑树 fsm_fusang | 4096 | 6.2 | 0.75 | 0.50 | #A0E0A0 #00A000 绿 #0010F0 蓝 #904040 | 弱 |
| 长藤树 fsm_changten_tree | 2048 | 14.2 | 0.31 | 0.32 | #000000 #101010 #50A0A0 | **强** |
| 月桂 fsm_bay_laurel_tree | 2048 | 13.8 | 0.25 | 0.34 | #101010 #A0C0B0 #004020 墨绿 | **强** |
| 祝余桃 fsm_zhuyu_peach_tree | 2048 | 9.8 | 0.24 | 0.35 | #101010 #50A0A0 #307070 | **强** |
| 沙棠松 fsm_shatang_pine_tree | 2048 | 11.2 | 0.24 | 0.38 | #705040 #50A0A0 #100000 | **强** |
| 挽歌枫 fsm_elegiac_maple | 2048 | 28.1 | 0.53 | 0.37 | #F0F0E0 #E0E0B0 米白金 | **强** |
| 大殿 fsm_smxz_dadian | 2048 | 13.6 | 0.27 | 0.37 | #101010 #100000 #E0E0D0 金 | **强** |
| 功善阁 fsm_smxz_gongshange | 2048 | 18.8 | 0.28 | 0.33 | #E0E0D0 金 #B0A080 #101010 | **强** |
| 太极门 fam_taichi_door | 2048 | 24.3 | 0.24 | 0.29 | #604030 木 #101010 #50A0A0 | **强** |
| 日晷 fsm_universal_dial | 2048 | 10.4 | 0.43 | 0.47 | #E0C010 金黄 #F0A0A0 粉 | **强** |
| 会稽山 fsm_mountain_stone | 2048 | 19.5 | 0.35 | 0.33 | #808070 #909080 灰岩 | **强** |
| 公告 UI fsm_announcement_ui | 2048 | 2.7 | 0.13 | 0.18 | #000000 #50A0A0 暗青 | 弱 |
| 碧海伞 fsm_bihai_umbrella | 1024 | 4.9 | 0.83 | 0.17 | #F0F0F0 #B0D0D0 淡蓝白 | 弱 |
| 伪木 fsm_weimu | 256 | 5.0 | 0.36 | **0.68** | #10A030 #006000 翠绿 | 弱 |
| 石路 stoneroad（复用原版 deciduous 图集） | 1024 | 10.2 | **0.88** | 0.10 | #F0F0F0 灰白 #206060 青灰 #B0D0D0 | 强 |
| 玉冕地板 fsm_ymfloor_0 | 512 | 86.7 | 0.36 | 0.67 | 与太虚地面同贴图（#308010 系） | 无 |
| 玉冕地板 fsm_ymfloor_1 | 1024 | 48.4 | **1.00** | 0.00 | 纯白 #F0F0F0（白玉层） | 无 |
| 太虚地面小地图 mini_fsm_decorate_taixulslandground | 256 | **99.9** | 0.32 | 0.46 | #507020 橄榄绿 #607030 | 中 |
| 大羿头像 fsm_avatar_dayi_npc | 128 | 7.6 | 0.92 | 0.06 | #F0F0F0 #603020 棕 #703080 紫袍 | 无 |
| 商城 UI fsm_gsg | 1024 | 14.9 | **0.96** | 0.04 | #F0F0F0 白 #1060A0 蓝 #3020A0 深蓝 | 无 |
| 避火 buff 图标 buff_bihuo | 128 | 2.2 | 0.97 | 0.04 | #F0F0F0 #701040 暗红 #F0D070 金 | 无 |

### 2.4 画风总结（一句话）

> **手绘卡通线条 + 浓暗描边（DST 正统）为骨，青绿山水（#308010 系）+ 朱砂暗红（金乌 #C04000）+ 金色描金（建筑 #E0E0D0 / 日晷 #E0C010）+ 墨色暗底（#101010）为魂的中国古风山海经异兽美术。**

展开证据链：

1. **配色习惯**：植物/树木统一墨绿暗色系（亮度 0.24~0.31，饱和 0.3~0.4），主色集中在 `#00A060/#004020/#307070/#101010` 区间——符合"仙山灵植"想象；建筑统一"暗底 + 金/米白描边"（#101010 底 + #E0E0D0 亮部）；神兽/异兽走"高饱和单色强调"（金乌暗红橙、狐王亮紫、混沌白粉）。无荧光色，无高饱和红绿对比滥用，整体是"沉稳仙气"。
2. **画风**：所有生物/建筑/植物图集检测到显著暗描边（edge darken 0.2~0.4），配合 DXT5 柔和 alpha——DST 手绘描线风格；无写实贴图、无水墨晕染（alpha 边缘干净，无渐变墨迹特征，证据等级 A：直接像素统计）。
3. **元素设计**：生物命名直接取自《山海经》——巴蛇（bashe_snake）、金乌（jinwu）、混沌（hundun）、饕餮（glutton）、当康（dangkang）、祝余（zhuyu）、沙棠（shatang）、迷榖（migu）、蓟柏（jibai）、朱厌（zhuyan 猴）、三尾狐（friendly_fox）、大羿/恒娥（NPC）——美术与题材严格对应。
4. **UI 风格**：图标 64x64 单图集、白/金描边为主；公告 UI 暗底青字（亮度 0.13）；商城 UI（fsm_gsg 1024 底图）则是**明亮浅色系**（亮度 0.96、白底蓝描边 #1060A0），与游戏内暗色 UI 刻意区分；按钮语义化命名（back/next/quest/invbg）。
5. **地皮**：太虚岛地面是唯一大面积"实体地皮"——高饱和深绿（0.67），带黑砖变体（taixulslandblackbrick_ground）和 256x256 专用小地图橄榄绿变体（#507020，99.9% 不透明）；石路 stoneroad 复用原版 deciduous 图集（1024x1024，**浅色石板**：亮度 0.88、青灰 #206060、强描边）；玉冕地板 fsm_ymfloor_0 与太虚地面同贴图、fsm_ymfloor_1 为纯白玉层（亮度 1.00）——地板采用"深绿 + 白玉"双层贴图拼贴，呼应玉冕青玉设定。
6. **动画帧命名**：anim.bin 可读串仅 show/atk 等（其余为二进制浮点）；帧名规律需从 prefab 代码的 `PlayAnimation` 调用推断（idle/grow/picked/dead_to_empty/full_to_dead 等，见草缠枝），证据等级 B。

### 2.5 解码工具与产物

- 解码器：`E:\神秘复苏\dist\dst-mod-creater\scripts\decode_ktex.py`（KTEX 解析 + numpy 向量化 DXT1/3/5 解码，8192x8192 仅 6 秒）
- 批量统计：`scripts/analyze_art_batch.py`（色板/饱和度/明暗/alpha/暗描边）
- 产物：`decode_out/` 下 55 张 PNG + `art_stats.json` + `small_preview.jpg`（缩略墙）+ `ui_preview.jpg`

---

## 3. 特色岛屿/植物/地形

### 3.1 太虚岛（昆仑之墟主题岛）

`mod_key_modules_for_mountain_and_sea/02_fsm_Island_generation/02_taixundao.lua`（281 行）

- 机制：`AddPrefabPostInit("world")` → `fwd_in_pdt_func:Map__Add_Terrain_Modifier("02_taixundao", fn)` 注册地形任务；任务用 `fwd_in_pdt_data:Get(ISLAND_CREATED_FLAG)` 判重（一次性）。
- 选址：遍历 `map_data.OceanTileMap`，`Map_Quick_Area_Check_In_Tiles(x, y, 15, 15, target_tile_check_fn, inst_check_fn, cache)` 找 15x15 海洋区域（四角+中心十字快速检测），排除 epic/charactor/structure/plant 等实体（L12-15）。
- 生成：`SpawnPrefab("fsm_island_creater"):PushEvent("Set", cmd_table)`，cmd_table 含 pt 中心点、35x35 地皮数组（202=海洋/临岸海，a=黑砖地皮，b=太虚地面）、`edge.data` 装饰数组（数字索引）+ `edge.fns` 生成函数表（L196-266）：
  - 1=太极门(fam_taichi_door 传送门)、2=草、3=树枝、4=功善阁、5=丹阁、6=大殿、9=长藤树、10=月桂、11=芭蕉、12=祝余桃、13=沙棠松、14=朱果丛、15=草缠枝、16=恋蝶花、17=蜘蛛巢、18=当康、19=兽苑阁、20/21/23=会稽山/昆仑山/招摇山、22=空
- 标记：岛屿中心存 `fwd_in_pdt_data:Set(ISLAND_POSITION_FLAG, {x, z})`，`os.clock()` 计时。

### 3.2 招摇岛

`03_zhaoyaodao.lua`（223 行）同构：25x25 地皮数组（含 COTL_GOLD 官方金砖地皮）、edge 装饰 1=荒草、2=迷榖树、3=月桂、4=金矿、5=祝余、6=浆果丛、7=草缠枝、9=电羊群、25=狐狸祭坛、26=三尾狐。

### 3.3 特色地形/tile

- 新地皮：`levels/textures/fsm_decorate_taixulslandground.tex`（太虚地面，512x512）、`fsm_decorate_taixulslandblackbrick.tex`（黑砖）、`fsm_ymfloor_0/1.tex`（玉冕地板 512x512）
- 注册：`mod_key_modules/01_basic_modifications/03_fsm_turfs_register.lua`（WORLD_TILES[string.upper("taixulsland_ground")]）
- `modworldgenmain.lua:46-76`：`AddTaskSetPreInit("default")` 注册传送门 set_piece `trash_tjm`（count=1，挂所有任务），并 require 4 个房间文件，`AddTaskPreInit` 把房间塞进指定任务（月桂房间→"Forest hunters"、云咩→"Great Plains"、日晷→"Lightning Bluff"、甘木→"Squeltch" 已 ban）
- 房间定义（`scripts/map/rooms/forest/`，纯配表）：
  - `00_rooms_ganmu.lua`：沼泽地皮，9 骷髅 + 1 甘木 + 9 玩家骷髅
  - `03_rooms_bay_laurel_tree.lua`：草地皮，countprefabs（月桂树 2+rand(3)、桂兔洞 9）+ distributepercent 0.1 散布（月桂/恋蝶花/当康/草/树枝）
  - `04_rooms_yunmie_Patch.lua`：热带草原，云咩 2+rand(4)
  - `01_rooms_universal_dial.lua`：荒漠地皮，1 日晷
- 静态布局：`scripts/map/static_layouts/taixudao.lua`（1233 行 Tiled 导出 60x60）、`trash_tjm.lua`（传送门）

### 3.4 特色植物（`scripts/prefabs/08_plants/` 25 个）

| 植物 | 定位 | 要点 |
|---|---|---|
| 扶桑 fsm_fusang.lua (220行) | 神树 | **树冠 canopy 系统**：OnNear/OnFar 统计玩家 `under_fusangtreeleaves_num`，PushEvent `onchangecanopyzone`；叶子从 35 高度飘落（`onspawnchild`：idle_loop + `startfalling` + 阴影随高度缩放 `Lerp(.5,1.5,height/35)`）；引用《山海经》文案"汤谷上有扶桑，十日所浴"（L8） |
| 连理巨树 fsm_lianli.lua | 情缘核心 | 6 阶段：树芽→连理树→连理巨树→红丝缠连理→祭祀供桌；GIANT_TREE_SCALE 1.75；被雷劈按概率掉 1-3 树枝/橡果/真心/复活器 |
| 蓟柏 fsm_jibai.lua | 四季草药 | 3 阶段生长（v1芽/v2苗/v3成株），timer"grow"驱动，种子→芽→苗→株 |
| 墨影梅 fsm_moyingmei.lua | 四季草药 | 同 3 阶段 + 种子 anim |
| 草缠枝 fsm_caochanzhi.lua | 基础草药 | 标准可采摘植物模板：pickable/witherable/burnable/deployable 全套，随机帧+随机色 |
| 朱果丛 fsm_zhuguocong.lua (165行) | 灵果 | 太虚岛特产 |
| 长藤树/月桂/芭蕉/祝余桃/沙棠松 | 岛屿树 | 同构"生长树"：v3/v4/v5 命名代表不同生长状态版本 |
| 挽歌枫 fsm_elegiac_maple | 装饰树 | 米白金配色（挽歌=丧，美术故意做旧） |
| 龙血珊瑚 fsm_longxueshanhu / 魂莲 fsm_soul_lotus / 鸡白草 fsm_jibai | 炼丹材料 | 与丹药配方表对应 |

### 3.5 三座仙山（`scripts/prefabs/07_resources/03_fsm_hills_nya.lua`）

- 会稽山：金镐可开采（tag `fsm_goldworkable`），敲 10 次掉 2 石头（L92-119）
- 昆仑山：纯水源（watersource 组件 + 水声 fsm_hill.fev，L122-152）
- 招摇山：水源 + 金镐 + 每 10 天可"搜山"（-40 饥饿、15 秒动作，得 10 祝余桃 10 草 10 树枝）（L153-199）

---

## 4. 核心设计模式

### 4.1 FWD 框架三件套（价值最高）

`scripts/components/fwd_in_pdt_data.lua`（92 行）：**通用 KV 存档组件**
```lua
fwd_in_pdt_data:Get/Set/Add(DataName_Str, data)  -- 世界级键值存储
-- OnSave/OnLoad 自动存档 DataTable（L49-62）
```

`scripts/components/fwd_in_pdt_func.lua`（307 行）：**模块化功能加载器**
- `:Init(cmd_table, ...)` 按名字 require 模块（module_fns 表，L187-210），防重复加载（`__func_init_loaded_module_names`）
- replica 数据下发：`Replica_Set_Simple_Data` 用 json 批量 + `DoTaskInTime(0)` 合并发送防阻塞（L65-99）
- 生命周期钩子：`Add_TheWorld_OnPostInit_Fn`（L138-161）、`Add_OnLoad_Fn`（L272）
- 对其他 mod 的扩展点：`inst:PushEvent("fwd_in_pdt.event.main_func_inited")`

`scripts/components/fsm_theworld_map_modifier.lua`（507 行）：**动态地图修改器**
- 全图扫描建 `map_data.TileMap[y][x] = {tile, ents, tile_x, tile_y, mid_pt}`（L345-386），分类 LandTileMap/OceanTileMap/VoidTileMap（洞穴虚空）
- 坐标换算 `Map_GetWorldPointByTileXY`（TileXY→世界坐标，每格 TILE_SCALE）
- 快速区域检测 `Map_Quick_Area_Check_In_Tiles`：四角 + 中心十字 + 缓存表（L185-302）
- 任务注册 `Map__Add_Terrain_Modifier(task_name, fn)` + `Map_Time_0_Task_Start` 统一执行
- **协程防掉线**：`inst:StartThread(function() ... end)`（L484-489）

### 4.2 岛屿生成配表（cmd_table 三件套）

tile 数组（数字/变量） + edge 装饰数组（数字索引） + fns 函数表（数字→SpawnPrefab），见 3.1。模式：**数据与行为分离**——地图形状是纯数据，装饰是 fns 查表。

### 4.3 炼丹系统（纯配表驱动）

`scripts/fsmdata/ruyi_pellet_formula.lua`（569 行）每丹药一个表：
```lua
fsm_bishui_x = {
    test = function(cooker, names, tags)  -- 材料校验函数
        return Item(names, "fsm_shatang_pine") and Item(names, "honey")
           and not (names["spice_garlic"] or ...)
    end,
    dylv = 2,                             -- 等级: 黄玄地天
    fsm_pill_level = FSM_PILL_LEVEL.X,
    strName = "玄级避水丹", renwuStr = "玄级避水丹",
    overridesymbolname = "h_bishuidan",   -- 切换玩家身上丹药符号动画
}
```
`scripts/fsmdata/pellet_recipes.lua`（85 行）：AddRecipe2 全字段注释文档（L1-45 是极好的配方字段参考）
`05_fsm_liandan/02_pellet_modframework.lua`（144 行）：配表 → `AddRecipe2` 批量注册，自动图集推断 `images/inventoryimages/<name>.xml`，科技降级处理（SCIENCE_ONE 等→TECH.NONE），兼容排队论 mod（ActionQueuer）
`05_fsm_liandan/01_main.lua`（437 行）：丹炉/炼丹炉组件 `fsm_pellet_cookpot`、`fsm_smalldanlu_pot`，modmain 里屏蔽智能锅干扰

### 4.4 Boss 魔改模板（饕餮 = 克劳斯框架）

`scripts/prefabs/11_boss/01_fsm_glutton.lua`（605 行）：
- 直接复用 `TUNING.KLAUS_*`（hit_recovery/attack_range/chomp_range），`SetStatScale` 按体型缩放数值（L49-63）
- **"饕餮"特性用 `thief` 组件实现**：OnHitOther_StealItems 每次攻击偷 1-3 件物品（L107-120）
- 战斗饥饿机制：OnAttacked/OnAttackOther 挂 `DoPeriodicTask(3)` 扣饥饿（L88-105）
- 战利品：10 肉 + 9 通天珠 + 4 蓝图（L11-25）
- 其他 Boss：混沌 fsm_hundun、狐王 fsm_foxking（fsm_foxking_brain 等专用 brain）

### 4.5 皮肤系统（token 激活）

`scripts/fsm_skin_system.lua`（1203 行）：自制"mod 内付费皮肤"——皮肤数据文件放 `unsafedata/fsm_skin_data.data`，hex 密钥 `FSM2` + 校验和 mod 1000000007 + 每皮肤 token（`FSM_XUELIN_6B5D2F`），配表字段：base_prefab/skin_name/bank/build/anim/swap_build/swap_symbol/assets。`free=true` 白嫖，缺省为付费。另有 `build/generate_fsm_skin_data/` 生成器（exe + pyc）。

### 4.6 其他值得抄的

- `scripts/fsmdata/buffs_nya.lua`（1224 行）：全套 buff 组件定义（避水/避火/避死/雷阳丹/明蝶丹等）
- `scripts/components/fsm_zhaoyao_nya.lua`：搜山 10 天冷却 timer 实现
- `scripts/components/fsm_takecare.lua` + replica：照料组件（情缘用）
- `scripts/brains/` 23 个 brain：`fsm_gluttonbrain`、`fsm_hundunbrain`、`fsm_foxking_brain` 等
- `01_basic_modifications/14_fsm_containers_nya.lua`：自定义容器；`15_fsm_rpc_nya.lua`：自定义 RPC

---

## 5. 亮点技巧

1. **协程跑地图扫描**（fsm_theworld_map_modifier.lua:484-489）：`inst:StartThread` 包住全图扫描，避免存档创建/加人时连接超时——大型世界修改 mod 的必修课。
2. **replica 数据合并下发**（fwd_in_pdt_func.lua:71-85）：批量 Set 时用 `DoTaskInTime(0)` 合并为一次 json 传输，防粘包。
3. **"四角+中心十字"快速区域检查**（fsm_theworld_map_modifier.lua:185-302）：检查 15x15 区域是否全是海，不用扫 225 格，只查 4 角 + 中轴 + 缓存表，O(n) 变 O(1) 级别。
4. **地皮数组 + fns 装饰表**：岛屿美术布局写成 ASCII 风格 tile 数组（202/47/a/b 数字代表地皮），装饰物用数字索引查 fns 表——改布局不动代码。
5. **one-liner 植物随机化**：`SetRandomColor`（亮度 0.7~1.0 抖动）+ `SetRandomAnimFrame`（随机帧/随机时间）——几十行让全地图植被不重样。
6. **兼容层写法**：`pcall(require, "components/actionqueuer")` 检测第三方 mod 存在才接入（pellet_modframework.lua:96）；`AddClassPostConstruct("widgets/controls")` 里保存原方法再覆盖（modmain.lua:60-104）——不破坏原 mod 的 patch 模式。
7. **AddString 收敛函数**：每个 prefab 顶部 `local function AddString(prefab, name, desc)` 批量写 STRINGS.NAMES + DESCRIBE。
8. **动画状态机注释文档**：`fsm_fusang.lua` 每个函数前有逐行中文注释（OnFar/OnNear/UpdateShadowSize），代码即文档。

---

## 6. 可复用模板

### 模板 1：海面随机生成岛屿（世界生成核心，可直接抄）
来源：`mod_key_modules_for_mountain_and_sea/02_fsm_Island_generation/02_taixundao.lua`

```lua
-- 前置：01_theworld_upgrade.lua 已挂 fwd_in_pdt_data + fwd_in_pdt_func(Init{"fsm_map_modifier"})
AddPrefabPostInit("world", function(inst)
    if not TheWorld.ismastersim or TheWorld:HasTag("cave") then return end
    inst.components.fwd_in_pdt_func:Map__Add_Terrain_Modifier("my_island", function()
        if TheWorld.components.fwd_in_pdt_data:Get("my.island.created") == true then return end
        TheWorld.components.fwd_in_pdt_data:Set("my.island.created", true)
        -- 1) 找一片 15x15 海洋
        local tiles = TheWorld.components.fwd_in_pdt_func.map_data.OceanTileMap
        local ok_tiles = {}
        local cache = {}
        for _, t in pairs(tiles) do
            if TheWorld.components.fwd_in_pdt_func:Map_Quick_Area_Check_In_Tiles(
                t.tile_x, t.tile_y, 15, 15,
                function(num) return TileGroupManager:IsOceanTile(num) end,
                function(i) return not i:HasOneOfTags({"epic","structure","plant"}) end,
                cache) then
                table.insert(ok_tiles, t)
            end
        end
        if #ok_tiles > 0 then
            local start = ok_tiles[math.random(#ok_tiles)]
            local a = WORLD_TILES[string.upper("my_ground")]  -- 需先在 turf 注册
            local b = WORLD_TILES[string.upper("my_blackbrick")]
            local cmd = {
                pt = start.mid_pt, remove_entities_flag = true,
                width = 21, height = 21,
                data = {  -- 21x21 tile 数组, 202=海
                    202,202,202,202,b,b,b,b,b,b,b,b,b,b,b,b,202,202,202,202,202,
                    -- ... 省略
                },
                edge = { [1] = {
                    data = { 0,0,b,1,2,0,... },  -- 数字索引装饰
                    fns = { [1] = function(pt) SpawnPrefab("my_tree").Transform:SetPosition(pt.x,0,pt.z) end,
                            [2] = function(pt) SpawnPrefab("my_rock").Transform:SetPosition(pt.x,0,pt.z) end }
                } }
            }
            SpawnPrefab("fsm_island_creater"):PushEvent("Set", cmd)  -- 或你自己的岛屿创建器
        end
    end)
end)
```

### 模板 2：配表驱动配方注册（带全字段文档）
来源：`mod_key_modules_for_mountain_and_sea/05_fsm_liandan/02_pellet_modframework.lua` + `scripts/fsmdata/pellet_recipes.lua`

```lua
-- 配方表（fsmdata/my_recipes.lua）
local Recipes = {
    { name = "my_pill", ingredients = { Ingredient("marble", 2), Ingredient("nitre", 2) },
      level = TECH.MAGIC_TWO, nounlock = true, filters = {"MY_FILTER"},
      product = "my_pill", numtogive = 1,
      description = "自定义配方描述", canbuild = function() return true end },
}
-- 注册器
local ok, data = pcall(require, "fsmdata/my_recipes")
if ok and data.Recipes then
    for _, r in pairs(data.Recipes) do
        local atlas = r.atlas or ("images/inventoryimages/" .. (r.product or r.name) .. ".xml")
        local image = r.image or ((r.product or r.name) .. ".tex")
        AddRecipe2(r.name, r.ingredients, r.level, {
            nounlock = r.nounlock, numtogive = r.numtogive, atlas = atlas, image = image,
            product = r.product, builder_tag = r.builder_tag, testfn = r.testfn,
            placer = r.placer, filter = r.filter, canbuild = r.canbuild,
            min_spacing = r.min_spacing, no_deconstruction = r.no_deconstruction,
        }, r.filters)
    end
end
```

### 模板 3：三阶段生长草药（种子→芽→苗→成株）
来源：`scripts/prefabs/08_plants/15_fsm_jibai.lua`（v1/v2/v3 命名 + timer 驱动）

```lua
-- 芽 inst（种子播种产物）
local function OnTimerDone_sprout(inst, data)
    if data.name == "grow" then
        local tree = SpawnPrefab(inst.growprefab)
        if tree then
            tree.Transform:SetPosition(inst.Transform:GetWorldPosition())
            if tree.StartGrowing ~= nil then tree:StartGrowing() end
            if tree.SoundEmitter ~= nil then tree.SoundEmitter:PlaySound("dontstarve/forest/treeGrow") end
        end
        inst:Remove()
    end
end
-- 成株（v3）
local function fn_v3()
    local inst = CreateEntity()
    inst.entity:AddTransform(); inst.entity:AddAnimState(); inst.entity:AddNetwork()
    inst.AnimState:SetBank("fsm_jibai"); inst.AnimState:SetBuild("fsm_jibai")
    inst.AnimState:PlayAnimation("idle", true)
    -- 随机化: 每个个体颜色/动画相位不同
    inst.AnimState:SetMultColour(.7 + math.random()*.3, .7 + math.random()*.3, .7 + math.random()*.3, 1)
    inst.AnimState:SetTime(math.random() * inst.AnimState:GetCurrentAnimationLength())
    inst.entity:SetPristine()
    if not TheWorld.ismastersim then return inst end
    inst:AddComponent("workable")  -- 采摘
    inst.components.workable:SetWorkAction(ACTIONS.PICK)
    -- 采摘掉落 + 变回 v2
    return inst
end
```

### 模板 4：KV 存档组件（世界级数据，5 分钟抄完）
来源：`scripts/components/fwd_in_pdt_data.lua`（全文 64 行核心）

```lua
local mydata = Class(function(self, inst)
    self.inst = inst
    self.DataTable = {}
end)
function mydata:Get(k) return self.DataTable[k] end
function mydata:Set(k, v) self.DataTable[k] = v end
function mydata:Add(k, n)
    if self:Get(k) == nil then self:Set(k, 0) end
    self:Set(k, self:Get(k) + n)
    return self:Get(k)
end
function mydata:OnSave() return next(self.DataTable) ~= nil and { DataTable = self.DataTable } or nil end
function mydata:OnLoad(d) if d.DataTable then self.DataTable = d.DataTable end end
return mydata
-- 挂载: TheWorld:AddComponent("mydata") 即自动随存档保存
```

### 模板 5：世界组件挂载 + 补丁（theworld_upgrade + modmain 风格）

```lua
-- 01_theworld_upgrade.lua 风格: 世界级功能挂载
TUNING["MyMod.World_Com_Func"] = { "my_map_modifier" }
AddReplicableComponent("my_func")
AddPrefabPostInit("world", function(inst)
    if not TheWorld.ismastersim then return end
    if inst.components.my_data == nil then inst:AddComponent("my_data") end
    if inst.components.my_func == nil then inst:AddComponent("my_func"):Init(TUNING["MyMod.World_Com_Func"]) end
end)

-- modmain.lua 风格: 保存原方法的安全覆盖（不破坏原 mod）
AddClassPostConstruct("components/container", function(self)
    local old = self.OnUpdate
    function self:OnUpdate(dt)
        -- 前置修复逻辑
        return old(self, dt)
    end
end)
```

---

## 附：分析覆盖统计

- lua 浏览：357 个（重点精读 ~40 个：入口/模块 init/岛屿生成/地图修改器/FWD 组件/炼丹/皮肤/植物/山/Boss/房间）
- tex 解码：55 张（全量 244 扫描规格 + 40 张像素统计，覆盖地皮/建筑/生物/角色/植物/UI/图标/公告）
- xml 浏览：239 个（全量命名模式统计）
- anim zip：362 个（结构解析 + atlas 解码 + build.bin/anim.bin 字符串分析）
- 美术风格一句话总结：**手绘卡通描线 + 青绿山水/朱砂/金色古风配色的山海经异兽风，深绿仙山地皮 + 墨色暗底金描建筑 + 高饱和单色神兽**
