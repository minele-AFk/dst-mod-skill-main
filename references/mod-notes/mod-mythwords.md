# [DST] 神话书说 Myth Words — 大型中国神话主题 MOD 逆向笔记

> 来源目录：`E:\神秘复苏\饥荒大型mod\1991746508\`（约 2040 个文件）
> 版本：9.10.27.4（`modinfo.lua`）；2026 年仍在更新的活跃项目
> 重要前提：**全部 286 个 .lua 文件均被自定义混淆器（DaxSg 工具链）加密**，无法直接精读源码。
> 本笔记 = 从文件结构、命名规律、可读 XML/文本片段、混淆机制分析中还原的架构全貌。
> 所有"设计模式"均标注证据等级：`[源码]`=直接读到代码，`[XML]`=读XML得到，`[命名]`=从文件名/目录结构推断（DST 标准 API 语境下可信度高）。

---

## 1. MOD 全貌

| 项 | 值 |
|---|---|
| 名称 | [DST] 神话书说（Myth Words），主题包："年跃青竹·篇" |
| 作者 | 羽中、幼儿园小班花、lw老王、杨柳、ti_Tout、逸尘、八戒Godfrey、小明（8人团队） |
| 版本 | 9.10.27.4 |
| 兼容 | `api_version=6`，`api_version_dst=10`，`dst_compatible=true`，`all_clients_require_mod=true` |
| 规模 | 2040 文件：286 个 .lua、305 个 anim zip、约 200 个 atlas xml、17 个 fmod 音效 |
| 多语言 | 中/英/日/越 5 套字符串表（`scripts/languages/strings_myth_theme_{chs,en,ja,vi,rwms}.lua`） |
| 配置项 | 语言（自动/中/英/日/越）、Buff图标显示开关 |
| 群宣 | QQ 群 959381112 / 1023311816 |
| 代码保护 | 全 Lua 混淆 + 静态资源白名单 + mod.manifest 签名 |

### 特色系统清单（从 prefab/组件命名还原）
- **神仙角色**：老子 laozi、八戒 pandaman_myth、土地 myth_tudi、嫦娥 myth_chang_e、判官/鬼差 commissioner、黑熊精 blackbear、阎君 myth_yjp
- **Boss**：年兽 myth_nian、金蟾 myth_goldfrog、犀牛 myth_rhino_boss、石灵 boss myth_siving_boss、广寒宫 myth_ghg（冰雪场景+天气）
- **坐骑**：老子的青牛 laozi_qingniu、年兽坐骑 nian_mount、牛鞍 saddle_qingniu
- **功法/修仙等级系统**：laozisp_pack（技能点包）、myth_saveinfo（跨存档存档）、myth_playernwd（玩家内力）、myth_jzfz、myth_hassoul（魂魄）、laozitimer
- **法宝**：金箍棒 myth_ruyi/mk_jgb、白骨精三件套 bone_blade/bone_wand/bone_whip、哪吒火尖枪/乾坤圈/混天绫 nz_lance/nz_ring/nz_damask、杨戬三尖两刃枪 yj_spear、紫金铃 myth_weapon_gtt、三尖两刃刀 myth_weapon_syd/syf、玉兔琴 guitar_jadehare、金丝袍 golden_armor_mk
- **丹药**：20+ 种 *pill（armor_pill 护甲丹、bloodthirsty_pill 嗜血丹、fly_pill 飞行丹、movemountain_pill 移山丹、condensed_pill 凝气丹、冷热抗性丹、还魂丹 myth_huanhundan）+ 丹葫芦 pill_bottle_gourd
- **法术**：拂尘 fuchen_spell、范围法术 myth_aoespell、笔法术 myth_penspell、飞行术 myth_flyskill（9 种角色变体）、读法宝书 read_fly_book、阴阳鱼 myth_yylp、九星珠 myth_qxj
- **建筑**：竹屋 myth_house_bamboo、粮仓 myth_granary、集市 myth_store（12 商铺）、井 myth_well、聚宝盆 myth_treasure_bowl、方寸山 fangcunhill、竹/木围栏 fence_bamboo、红灯笼 redlantern_myth_a~i、室内装修系统 myth_interiors_*（床/灯/墙纸/地板 10 人份 groundlight）
- **植物/农耕**：竹子 myth_plant_bamboo、莲花 myth_plant_lotus、人参果树 infantree（4 阶段）、蟠桃树 myth_peachtree、香蕉树 myth_banana_tree、摇钱树 myth_cash_tree、葫芦 gourd（巨型作物）
- **食物**：40+ 种中式菜肴 myth_food_*（缩写命名）+ 月饼/粽子/桃酒/蟠桃宴 + 专属锅具 myth_food_table
- **货币经济**：铜钱 myth_coin、钱箱 myth_coin_box、金锭 myth_goldnugget_ingot
- **法宝商城**：bambooshop_myth 组件 + bambooshopdialog 全屏 UI + bbshop 美术
- **图鉴/典籍系统**：myth_bookinfo（145KB 主模块）+ bookinfo 图鉴 + mythbookwidget + 7 个图鉴页（道具/地形/公告/怪物/丹药/玩家/神仙）
- **Buff 系统**：myth_buffs + mythbuffbar/mythbuffslot 控件 + 60 个 buff 图标 + myth_buff_ly_api
- **节日活动**：年兽（鞭炮 firecrackers_myth、红包 redpouch、年兽帽）、中秋（月饼）、端午（粽子）、生肖 myth_zodiac
- **物品皮肤系统**：myth_itemskin / myth_itemskin_theme / myth_skinsapi / registerinventoryitematlas
- **世界生成**：鲲鹏 kunpeng、广寒宫 layout_ghg、蟠桃园 layout_peach、160KB 通用布局库 layout_xml、自定义地皮 atlas（复用 SW 丛林纹理）
- **音效**：Laozi.fev、Myth_nian.fev、rhino、编钟 bianzhong、快板 bamboo_clappers、鹤 crane、按钮音 —— 全套中式配乐 fmod 工程

---

## 2. 框架架构

### 2.1 目录树（完整）

```
1991746508/
├── modinfo.lua                  # 元数据+配置项（唯一未混淆的顶层文件）
├── modmain.lua                  # 入口：混淆 loader（51KB，单行压缩）
├── modmain0.lua                 # 主逻辑（111KB，base64变体编码混淆）
├── modmain1.lua                 # 追加逻辑（17KB，二进制字节码加密）
├── modworldgenmain.lua          # 世界生成入口 loader（51KB）
├── modworldgenmain0.lua         # 世界生成主逻辑（110KB）
├── modworldgenmain1.lua         # 世界生成追加（17KB）
├── mod.manifest                 # 文件签名清单（MNFS 格式，防篡改）
├── modicon_theme.tex/.xml       # MOD 图标
├── anim/                        # 305 个 Spriter 动画 zip
│   ├── *.zip                    # build.bin + anim.bin + atlas-0.tex
│   └── dynamic/*.dyn            # 动态加载动画（DLCDynamicAnim）
├── images/                      # 纹理 atlas（xml+tex 成对）
│   ├── inventoryimages/         # 200+ 物品图标 atlas（一物一atlas）
│   ├── bookinfo/                # 图鉴大图（约 300 张法宝/物品插画）
│   ├── bbshop/                  # 商城 UI（ui_bs_*，8 大页签）
│   ├── bufficons/               # 60 个 buff 状态图标
│   ├── cookbook/                # 34 个烹饪图鉴图标
│   ├── hud/                     # 神话书标签页 UI（myth_tab、myth_tab_skill）
│   ├── map_icons/               # 25 个地图图标
│   └── *.xml                    # 根级：图鉴背景、云特效、加载条
├── levels/
│   ├── tiles/jungle.xml+.tex    # 自定义地皮 tile atlas（复用 SW 纹理）
│   └── textures/                # Ground_noise_savannah_detail、mini_savannah_noise（大陆噪声）
├── main/                        # 34 个主逻辑模块（等价于一个巨型 main.lua 的拆分）
│   ├── actions.lua  components.lua  containers.lua  equips.lua
│   ├── foods.lua  recipes.lua  tech.lua  tuning.lua  sg.lua
│   ├── laozi.lua  blackbear.lua  rhino.lua  peach.lua  pills.lua
│   ├── mythhouse.lua  myth_bambooshop.lua  myth_bookinfo.lua
│   ├── myth_newturf.lua  myth_pill_recipes.lua  myth_skins.lua  myth_skinsapi.lua
│   ├── myth_buff_ly_api.lua  myth_lotus.lua
│   ├── prefabpostInit.lua  plantable.lua  registerinventoryitematlas.lua
│   ├── hotupdate.lua  mod_rpc.lua  logupload.lua  flag.lua
│   ├── mk_flyer.lua  myth_bbn.lua
│   └── widgets.lua
├── scripts/                     # 镜像 DST 原版目录结构
│   ├── behaviours/   (nian_eat)
│   ├── brains/       (9 个：黑熊、判官书、年兽、土地、年兽坐骑、八戒、青牛、犀牛)
│   ├── components/   (68 个神话组件)
│   ├── languages/    (5 套字符串表)
│   ├── map/          (static_layouts: layout_xml 160KB、kunpeng、layout_ghg、layout_peach、rhino_desk_retrofitting)
│   ├── prefabs/      (130 个神话 prefab)
│   ├── screens/      (bambooshopdialog 商城、mythbookpopupscreen 图鉴弹窗)
│   ├── stategraphs/  (SGmyth_* 11 个：土地、年兽、金蟾、嫦娥、犀牛、黑熊、八戒、石灵boss、判官书、香蕉龙卷)
│   ├── widgets/      (mythbuffbar/slot、mythfoodui、仙气特效overlay)
│   └── widgets/redux/ (mythbookwidget + 7 图鉴页：道局/地形/公告/怪物/丹药/玩家/神仙)
└── sound/                      # fmod：Laozi/Myth_nian/rhino/编钟/快板/鹤/按钮 (fev+fsb)
```

### 2.2 加载架构（三级 loader）

`modinfo.lua` 无 modmain 字段 → DST 默认加载根目录 `modmain.lua`。证据链：
1. `modmain.lua` 是**入口 loader**（51KB 单行压缩，开头有少量明文：`local e=_G or GLOBAL; e.setmetatable(env,...)` 包装全局环境，`e.daxsg_tn=e.tonumber` 定义解码工具）；
2. 其主体是数据表 `local t={...}`（607 个大整数 + 201 个 base64 转义字符串），运行时解码重组字节码后 `load()` 执行；
3. `modmain0.lua` / `modmain1.lua` 分别被 loader 顺序加载（0=主逻辑 111KB，1=追加 17KB），文件名成对出现 `modmain0/modmain1`、`modworldgenmain0/modworldgenmain1` —— 经典"主文件+更新补丁"分层，便于小包热更新；
4. `main/hotupdate.lua` 模块存在，佐证热更新机制；
5. `main/mod_rpc.lua`：自研 RPC 通信框架（多客户端 mod 必备）；
6. `main/logupload.lua`：日志上报（遥测/排障）；
7. `StaticAssetsReg = {'gourd'}`（modinfo 底部）：**禁用动态加载的静态资源白名单**，与 `anim/dynamic/*.dyn` 配套。

### 2.3 混淆机制分析（DaxSg 工具链）

modmain.lua 明文片段（原样）：

```lua
local e=_G or GLOBAL;
e.setmetatable(env,{__index=function(a,t)return e.rawget(e,t)end})
e.daxsg_tn=e.tonumber;
e.daxsg_nilstr=""
do local t={18919908328660,11418461,11936108,5606177150053;
1182244,"\090\076\067\057\107\115\061\061";
"\065\115\061\061", ... }
```

实测解码（Python 验证）：`"\090\076\067\057\107\115\061\061"` → `"ZLC9ks=="` → base64 解码 → 二进制片段 `d\xb0\xbd\x92`。机制：
- 代码先编译为 luac 字节码；
- 字节码按块切分：小块 → base64 字符串（再转义成 `\ddd` 十进制转义）；大块 → 十进制大整数（含 `-a+b` 恒等表达式做算术后混淆）；
- 运行时：`daxsg_tn`（tonumber）转换整数 → 拼接 → `load()` 执行。
- `modmain0.lua` 用另一套：base64 变体字母表（`4g3LMgtX02ZL0D...` 无 `+` `/`，字符集被替换），解码后为二进制；`modmain1.lua` 是纯二进制加密字节码。
- 三份 loader 首部均有 `e.setmetatable(env,{__index=function(a,t)return e.rawget(e,t)end})` —— **沙箱全局包装**，既保证 mod 环境隔离又防外部注入。

结论：**源码不可直接复用**，但架构/资产/模式可完全学习。

---

## 3. 关键设计模式

### 3.1 新角色实现（神仙/妖王）`[命名+资产证据]`

9 个可玩/可交互角色，每个的标准资产包：
- prefab：`scripts/prefabs/laozi.lua`、`pandaman_myth.lua`、`myth_tudi.lua`、`myth_chang_e.lua`、`blackbear.lua`、`commissioner_book.lua`
- 状态机：`scripts/stategraphs/SGmyth_tudi.lua`（54KB）、`SGmyth_chang_e.lua`、`SGpandaman_myth.lua`、`SGblackbear.lua`
- AI：`scripts/brains/myth_tudibrain.lua`、`pandaman_mythbrain.lua`、`blackbearbrain.lua`、`qingniubrain.lua`、`commissioner_bookbrain.lua`
- 动画：`laozi.zip`（3.2MB 大包）、`myth_tudi.zip`、`pandaman_myth_*.zip`（按装备/食物/植物/武器/稀有物/数字学拆 7 包）、`myth_chang_e.zip` + `myth_chang_e_furniture.zip`
- 专属组件：`laozisp_pack.lua`（老子技能包）、`laozitimer.lua`（计时）、`laozo_qingniu_buff.lua`（青牛 buff）

**角色专属技能/等级系统**（功法体系）`[命名]`：
- `laozisp_pack`：技能点（SP）包 —— 按"境界/功法"成长
- `myth_saveinfo`：跨存档角色数据（等级、境界、已学功法）
- `myth_playernwd`：玩家"内力/灵能"（player noobs? 实际为内力值）
- `myth_jzfz`：九转飞升类境界
- `myth_hassoul`：魂魄/灵魂值
- `myth_favorability`：NPC 好感度（与神仙互动提升）
- `myth_upvaluehelper`：upvalue 注入工具（修改原版函数闭包实现深度魔改）
- 等级成长 UI：`hud/myth_tab_skill.xml`（技能页签）、`mythbuffbar`（属性栏）

### 3.2 地皮/地形/世界生成 `[XML+命名]`

**(a) 自定义 tile atlas —— 复用原版纹理零成本造新地皮** `[XML 源码]`

`levels/tiles/jungle.xml`（原样节选）：
```xml
<Atlas><Texture filename="data/DLC0002/levels/tiles/jungle.tex" />
<Elements>
<Element name="48" u1="0.134765625" u2="0.197265625" v1="0.47265625" v2="0.59765625" variant="" />
<Element name="08" u1="0.732421875" u2="0.794921875" v1="0.33984375" v2="0.46484375" variant="b" />
...
<Element name="01" u1="0.267578125" u2="0.330078125" v1="0.33984375" v2="0.46484375" variant="b" />
</Elements></Atlas>
```
要点：`Texture` 直接引用**游戏本体** `data/DLC0002/levels/tiles/jungle.tex`，Elements 用归一化 UV 重新定义 48 个 tile 变体（a/b 变体，对应 SW 丛林地皮 tile 图集），即"新地皮=原纹理的新 UV 重排"。地皮 prefab 由 `main/myth_newturf.lua` 注册（turf_myth_zhu 竹地皮、turf_quagmire_parkfield 均见于 inventoryimages）。

**(b) 大陆噪声纹理** `[文件]`：`levels/textures/Ground_noise_savannah_detail.tex` + `mini_savannah_noise.tex` —— 世界生成用的噪声层（对应"竹林/桃园"大陆的外观纹理）。

**(c) 静态布局库** `[命名]`：
- `scripts/map/static_layouts/layout_xml.lua`（160KB！）：把 XML 静态布局序列化为 Lua 表的**集中式布局库**，一个文件承载上百个房间/布局定义（竹林、桃园、药园等）
- 专属布局：`kunpeng.lua`（鲲鹏地图 32KB）、`layout_ghg.lua`（广寒宫 39KB）、`layout_peach.lua`（蟠桃园 69KB）
- `scripts/map/myth_rhino_desk_retrofitting.lua`：犀牛书桌的"改造"布局（房间内装饰重排）
- `modworldgenmain*.lua` 三件套：世界生成钩子（`AddRoomPreInit`/`AddTaskSetPreInit` 级操作，配合 layout 库）

### 3.3 建筑/物品/配方/法宝 `[命名]`

- **建筑 prefab 标准资产**：`myth_house_bamboo.zip` + `myth_house_bamboo` prefab + `mythhouse.lua`(44KB) + `mythhouse` 组件（建房管理器）+ `myth_interiors_*.zip`（床/灯/隔断/地面光）+ `myth_oldinteriors` 组件（旧内饰兼容）+ `myth_interiors` prefab（10 人份 groundlight 配色：bgz/blz/crh/gxy/llt/qzh/ryx/std/yhy/zsz —— 10 个好友共享广寒宫）
- **多部件建筑**：`myth_door_enter/exit`（传送门）+ `myth_stonedoor`、`myth_walls` + `wall_dwelling`、`myth_floor/myth_floor1` + `myth_wallpaper`（墙纸/地板皮肤：`myth_floorskin_*`、`myth_wallskin_*`、`myth_wall_decals_*` 装饰贴花）
- **配方体系**：`main/recipes.lua` + `main/tech.lua`（科技等级）+ `main/plantable.lua`（种植）+ `myth_pill_recipes.lua`（丹药专属配方）+ `main/foods.lua`（烹饪配方）
- **法宝/武器批量 prefab**：`myth_ironitems.lua`（铁甲/铁剑/铁盔）、`mk_items.lua`（金丝袍系列）、`myth_weapon_gtt/syd/syf.lua`、`myth_ruyi.lua`、`myth_gold_staff.lua`
- **容器**：`myth_bbn_container`（百宝囊）、`krampussack_sealed`（封印袋）、`myth_coin_box`、`myth_bundle/myth_wrap_bundle`（捆扎物）
- **可充能物品**：`myth_rechargeable` 组件（法宝灵力充能）

### 3.4 法术/技能系统 `[命名]`

- **AoE 法术框架**：`myth_aoespell.lua` 组件（范围法术基类）+ `myth_aoeweapon_leap/lunge`（武器附带位移技）
- **投射法术**：`fuchen_spell`（拂尘）、`myth_qxj_biu`（九星珠弹幕）、`peach_complexprojectile`（桃瓣复合弹道）
- **书法术**：`book_myth.lua`（神话书）、`commissioner_book.lua`（判官书）+ `SGcommissioner_book.lua` + `commissioner_bookbrain.lua` + `book_leash`（牵引）、`book_fly_myth.lua` + `read_fly_book` 组件（读飞行书）
- **飞行系统**：`myth_flyskill.lua`（飞行术，9 角色变体 myth_flyskill_mk/nz/pg/wb/ya/yj/yt/yt_apricot/yt_laurel）、`mk_flyer.lua` + `mk_flyer` 组件 + `mk_cloudfxspawner`（筋斗云特效生成器）、`myth_flyer_fx`
- **Buff 引擎**：`myth_buffs.lua`（38KB 全 buff 定义）+ `myth_buff_ly_api.lua`（buff 插件 API）+ `mythbuffbar`/`mythbuffslot`（HUD）+ `bufficons/`（60 图标：免疫火/冰/水、攻防增益、失眠、饥渴、swift、thorns、undead、mountain_shaking 等）
- **状态叠加类**：`myth_show_hotmeter` + `_replica`（温度计显示）、`myth_hotmeter` prefab

### 3.5 商店/经济/交互 `[命名]`

- `bambooshop_myth` 组件（52KB 商城逻辑）+ `myth_bambooshop.lua`（106KB 主模块）+ `screens/bambooshopdialog.lua`（95KB 全屏对话框 UI）+ `images/bbshop/ui_bs_*`（8 页签 × 每页 5-6 商品位 + 价格/买入/卖出/修理标签）
- 商铺主题：黑店/铁匠/建造/工匠/算命/花鸟/珍珠/种子/茶具/蔬菜 —— `myth_store*.zip` 12 种
- 货币：`myth_coin` + `myth_coin_box` + `myth_goldnugget_ingot`（金锭）+ `myth_essense`（灵气精华/冰火精华）

### 3.6 图鉴/典籍系统 `[命名]`

- `main/myth_bookinfo.lua`（145KB，全 mod 第二大 Lua）：典籍数据+逻辑
- `mythbookinfodata` 组件：图鉴存档数据（解锁记录）
- `images/bookinfo/*`：约 300 张法宝/物品插画 atlas（一物一图）
- `widgets/redux/mythbookwidget.lua` + 7 页面：`mythbookpage_{daoju,dixing,gonggao,guaiwu,pill,player,shenxian}`（道具/地形/公告/怪物/丹药/玩家/神仙）
- `myth_bookinfo.xml` + `myth_bookinfo_bg.xml`（书页背景）+ `screens/mythbookpopupscreen.lua`（弹窗）

### 3.7 物品皮肤系统 `[命名]`

- `myth_itemskin` 组件 + `myth_itemskin_theme`（主题皮肤）+ `myth_itemskin_prefabs` + `main/myth_skins.lua` + `main/myth_skinsapi.lua` + `main/registerinventoryitematlas.lua`（atlas 动态注册）—— 物品皮肤 = 换 atlas + 换 anim 的完整管线

### 3.8 美术资产组织

**(a) anim zip 标准结构**（Spriter 编译产物，`unzip -l laozi.zip` 实测）：
```
anim/laozi.zip:
  anim.bin      (125KB)  动画数据（Spriter 编译）
  atlas-0.tex   (5.6MB)  纹理图集
  build.bin     (73KB)   骨骼/部件构建数据
```
**(b) 命名规律**（可复用的资产命名约定）：
- 角色主包：`角色名.zip`；动作扩展包：`角色名_actions.zip`、`_basic.zip`、`_idle.zip`、`_attacks.zip`
- 手持替换动画：`swap_物品名.zip`（玩家手持时的皮肤动画）
- 动态加载：`anim/dynamic/同名.dyn`（对应 DLCDynamicAnim 动态加载；modinfo 白名单 `StaticAssetsReg={'gourd'}` 例外）
- 建筑多形态：`myth_plant_infantree_{small,medium,trunk,vine}.zip` 阶段拆分
- 特效包：`myth_rhino_fx.zip`、`mk_firefx.zip`、`myth_tornadofx.zip`、`myth_smalllight.zip`
- 座位动画：`player_myth_stool_sit.zip`（玩家坐姿替换）、`sit_on_myth` 组件
- 城镇猪改造：`townspig_{actions,attacks,basic,idle,sneaky}.zip`（复用原版猪人骨骼改行为）

**(c) images atlas 组织**：
- 一律 `xml+tex` 成对；物品图标**一物一 atlas**（inventoryimages/xxx.xml 通常单元素，UV 满幅 0.0078~0.9922）
- 大 UI（商城/图鉴）一屏一 atlas（ui_bs_1_1 等分页切图）
- atlas XML 模板（原样）：
```xml
<Atlas><Texture filename="gourd.tex" /><Elements><Element name="gourd.tex" u1="0.0078125" u2="0.9921875" v1="0.0078125" v2="0.9921875" /></Elements></Atlas>
```

### 3.9 世界生成模块清单 `[命名]`
`modworldgenmain.lua`（loader）→ `modworldgenmain0/1.lua` → `map/static_layouts/*` + `levels/tiles/jungle.xml` + `levels/textures/*` + `myth_newturf` + 布局专属 prefab（fangcunhill、myth_tudi_shrines 土地庙、myth_goldfrog_spawner、myth_rhino_desk_spawner、myth_farm_spawn 农场刷怪）。

---

## 4. 亮点技术（最有价值的 5 个）

1. **全量 Lua 混淆 + 三级 loader 架构**（DaxSg 工具链）：luac 字节码 → 分块 base64/大整数编码 → 运行时 `load()`；`modmain/modmain0/modmain1` 三层（主逻辑/补丁）支撑热更新；`main/hotupdate.lua` 专门模块。防抄程度业界顶级，证明大 mod 完全可以在混淆下运营 8 年（首个版本 2018 年）。

2. **复用原版纹理的自定义 tile atlas**：`levels/tiles/jungle.xml` 的 `Texture filename="data/DLC0002/levels/tiles/jungle.tex"` 直接引用游戏本体纹理，只重排 UV 就获得全新地皮 —— 新地形零新增美术成本的最优解（配合 `levels/textures/` 噪声纹理定义大陆外观）。

3. **160KB 集中式静态布局库** `layout_xml.lua`：把成百个房间布局以 Lua 表形式集中管理，配合 `kunpeng/ghg/peach` 专属布局，实现 3 个新世界区域 —— "布局库 + 专属布局"分层的世界生成组织范式。

4. **动态加载动画体系**：`anim/dynamic/*.dyn` 动态加载 + `StaticAssetsReg={'gourd'}` 白名单（葫芦因高频使用禁止动态加载），平衡了 305 个动画包的加载时长与内存；配合 `swap_*` 手持替换动画和 `*_actions` 动作扩展包的命名约定，形成完整的角色动画资产规范。

5. **模块化镜像目录 + 系统化 API 拆分**：`main/` 34 模块按 DST 原版命名（actions/equips/foods/recipes/tech/tuning/sg）平行扩展；自定义基建齐全 —— `mod_rpc.lua`（RPC 框架）、`myth_buff_ly_api.lua`（buff 插件 API）、`myth_skinsapi.lua`（皮肤 API）、`myth_saveinfo`（跨存档数据）、`myth_upvaluehelper`（upvalue 注入）。大团队多系统并行开发的工程范式。

---

## 5. 可复用的模板代码

### 5.1 多语言 modinfo 模板（原样，来自 modinfo.lua）
```lua
local L = locale ~= "zh" and locale ~= "zhr" --true-英文; false-中文

name = L and "[DST] Myth Words" or "[DST] 神话书说"
api_version = 6
api_version_dst = 10
dst_compatible = true
dont_starve_compatible = false
reign_of_giants_compatible = false
shipwrecked_compatible = false
all_clients_require_mod = true
icon_atlas = "modicon_theme.xml"
icon = "modicon_theme.tex"
server_filter_tags = L and { "MYTH WORDS: theme" } or { "神话书说：主题" }

configuration_options =
{
    L and {
        name = "Language", label = "Language", hover = "Set Language",
        options = { {description = "English", data = "ENGLISH"}, {description = "中文", data = "CHINESE"}, {description = "日本語", data = "JAPAN"}, {description = "Tiếng Việt", data = "VI"}, {description = "Auto", data = 'A'} },
        default = 'A',
    } or { -- 中文版同样式
        name = "Language", label = "语言", hover = "设置语言",
        options = { {description = "中文", data = "CHINESE"}, {description = "英文", data = "ENGLISH"}, {description = "日本語", data = "JAPAN"}, {description = "越南语", data = "VI"}, {description = "自动", data = 'A'} },
        default = 'A',
    },
}
--禁用动态加载
StaticAssetsReg = {'gourd'}
```
要点：`L` 布尔切换整段配置；语言配置含 "Auto" 让游戏内再切换（配合 scripts/languages 多套字符串表）。

### 5.2 自定义 tile atlas（新地皮零美术模板）
```xml
<Atlas><Texture filename="data/DLC0002/levels/tiles/jungle.tex" /><Elements>
<Element name="48" u1="0.134765625" u2="0.197265625" v1="0.47265625" v2="0.59765625" variant="" />
<Element name="01" u1="0.267578125" u2="0.330078125" v1="0.33984375" v2="0.46484375" variant="b" />
</Elements></Atlas>
```
放 `levels/tiles/`；配套 `levels/textures/*_noise.tex` 定义大陆噪声；`main/myth_newturf.lua` 模式注册 turf prefab。

### 5.3 单元素物品图标 atlas 模板
```xml
<Atlas><Texture filename="gourd.tex" /><Elements><Element name="gourd.tex" u1="0.0078125" u2="0.9921875" v1="0.0078125" v2="0.9921875" /></Elements></Atlas>
```

### 5.4 动画资产包组织模板（Spriter）
```
anim/物品.zip        = build.bin + anim.bin + atlas-0.tex
anim/dynamic/物品.dyn = 同名动态加载（低频/大体积动画）
anim/swap_物品.zip   = 手持替换动画
anim/角色_basic.zip + 角色_actions.zip + 角色_attacks.zip = 角色动作拆分
```

### 5.5 大 mod 目录骨架模板（镜像 DST 结构）
```
modmain.lua            → 主入口（可混淆）
modworldgenmain.lua    → 世界生成入口（独立加载）
main/                  → 逻辑模块拆分（recipes/tech/foods/equips/actions/tuning）
scripts/prefabs/       → 全部 prefab（一物一文件）
scripts/components/    → 自定义组件（myth_ 前缀）
scripts/stategraphs/   → SGmyth_* 状态机
scripts/brains/        → *brain 逻辑
scripts/widgets/redux/ → 复杂 UI 页
scripts/languages/     → strings_<主题>_<语言>.lua 多语言表
scripts/map/static_layouts/ → 布局库
images/inventoryimages/ + images/bookinfo/ + images/bufficons/ + images/hud/
sound/                 → fmod 工程（fev+fsb）
levels/tiles/ + levels/textures/ → 地皮与噪声
```

---

## 附录：资产速查表

- **prefab 数**：约 130 个（scripts/prefabs/*.lua），覆盖角色 9、boss 5、建筑 20+、植物 8、法宝武器 30+、食物 40+、特效 15
- **组件数**：68 个（myth_ 前缀统一命名空间）
- **buff 数**：60 图标 / 约 40 种效果
- **图鉴插图**：约 300 张（bookinfo）
- **动画包**：305 个 zip + 60 个 dyn
- **音效工程**：8 套 fmod（fev+fsb）
- **多语言**：中/英/日/越 4 语言内容（字符串文件 5 个，含 rwms 一版）
- **商铺**：12 类
- **年份活动**：年（兽+鞭炮+红包）、中秋（月饼 4 味）、端午（粽子 2 形）、生肖

---

## 6. 特色专题补充：岛屿/植物/地形

> 本专题基于 **anim.bin/build.bin 可读字符串**（Spriter 编译产物保留动画名/部件名，`[anim]` 级硬证据）、
> prefab/inventoryimages/map_icons 命名（`[命名]`）、布局文件与 tile XML（`[XML]`）交叉推断。
> 字符串表（strings_myth_theme_chs.lua 等 5 文件）经实测为 DaxSg 自定义字节混淆（无 LF/标准编码，频率分析 XOR/线性偏移均无法还原），**中文文案不可读**，全部名称以资产拼音命名为准。

### 6.1 特色植物全清单（10 系 26 项）`[anim]+[命名]`

| # | 植物系 | 资产 | 推断功能 | 证据 |
|---|---|---|---|---|
| 1 | 蟠桃树 | myth_peachtree | 仙桃树，2 级生长，花果期，冬季雪变体，可烧焦；产出蟠桃/大蟠桃/桃酒/蟠桃宴 | [anim] lv1_idle/lv2_idle；build 部件 sapling/short_trunk/tall_trunk/flower/fruit/burnt_trunk/snow/emptysnow |
| 2 | 人参果树 | myth_plant_infantree(+_small/_medium/_trunk/_vine) | 五包分阶段树，小→中→高连续过渡动画，6 层叶/7 层枝，冬季雪变体，带"unique"变异株；树上结人参果 | [anim] smalltomedium/mediumtotall/mediumtotall1/tall/idle_snow/leaves_1~6/sticks_1~7 |
| 3 | 人参果 | myth_plant_infant_fruit + mythinfant_fruitfx | 挂在藤上（vine/vine_2/vine_3j），spawn 出生动画+特效；图标 myth_infant_fruit | [anim] idle/spawn/fruit/vine |
| 4 | 葫芦（巨型作物） | gourd / myth_new_gourd / farm_plant_gourd | **DST 农场作物系统**：seed→sprout→small→med→full→oversized 六阶段+腐烂+巨型变体；gourd 进 StaticAssetsReg 白名单（高频静态加载） | [anim] crop_seed/crop_sprout/crop_small/crop_med/crop_full/crop_oversized/crop_rot + grow_* 序列 + soil01/vine/stem/leaves |
| 5 | 紫葫芦 | purple_gourd | 葫芦法宝变体：可手持（swap_1/swap_2）+ 皮毛外观（swap_fur），配 purplegourd_action 组件 | [anim] swap_1/swap_2/swap_fur |
| 6 | 丹/酒葫芦 | pill_bottle_gourd / wine_bottle_gourd(_wine) | 丹药容器（20+ pill 配方体系）/ 酒葫芦（含"换酒"swap_wine 动画） | [anim] pill5/swap_wine |
| 7 | 莲花（农场作物） | myth_plant_lotus | **莲花也能进农场**：lotus_seed→sprout→small→med→full→rot 六阶段+腐烂 | [anim] lotus_sprout/lotus_small/lotus_med/lotus_full/lotus_rot + grow_* |
| 8 | 池塘莲 | lotus | 池塘生长的莲，**昼开夜合**（open/close），水陆两态（idle/idle_water），可摘（picking/picked） | [anim] close/open/idle_water/picking/picked |
| 9 | 莲产物 | myth_lotus_items / lotusleaf_hat / lotusleaf_umbrella | 荷叶/莲藕/莲子（各含 cooked 变体）+ 荷叶帽/荷叶伞 | [anim] lotus_leaves/lotus_root/lotus_seeds |
| 10 | 竹子 | myth_plant_bamboo | **3 级生长**（short_0/1/2）+ 砍伐（chop）+ 烧焦（burnt）；产竹材/竹笋（可食） | [anim] short_0/short_1/short_2/chop/burnt |
| 11 | 青竹 | myth_greenbamboo | 竹材的另一形态/装饰竹 | [命名] inventoryimages |
| 12 | 香蕉树 | myth_banana_tree（dynamic） | **标准树逻辑 4 级**：tree→tree_2/3/4，grow 生长、pick 摘果、fall/chop/burnt/burnt_stump 完整砍伐燃烧链；配香蕉叶 myth_banana_leaf | [anim] tree/tree_2/tree_3/tree_4/grow/pick/fall/burnt_stump |
| 13 | 摇钱树 | myth_cash_tree | 挂钱树：idle/crash（钱币掉落碰撞）/ground（倒地）；产出铜钱 myth_coin/金锭；配 yqs_record 记录组件 | [anim] idle/crash/ground |
| 14 | 仙草药粉系 | powder_m_hypnoticherb / lifeelixir / improvehealth / charged / coldeye / becomestar / takeiteasy | **7 种药粉**：催眠药草粉、生命灵药、恢复健康、充能、冷眼等——"仙草入药"路径；有 bookinfo 插画 | [命名] inventoryimages+bookinfo |
| 15 | 炼丹材料 | mk_hualing（花灵）/ mk_huoyuan（火源） | 仅图标无动画包，推断为丹药配方材料（八戒线 mk_ 前缀） | [命名] inventoryimages |
| 16 | 岩石草/灵岩 | myth_rocktips | rock1~rock6 六形态岩块（石灵 siving 线相关：siving_rocks/siving_stone 图标） | [anim] rock1~rock6 |
| 17 | 树荫地毯 | infantree_carpet + infantree_leaves_canopy | 人参果树下的树冠投影/地毯层（canopy 单独 1024 图集，高饱和深绿） | [anim] idle |
| 18 | 井 | myth_well（dynamic） | 舀水（fill/splash）+ **vortex 漩涡形态**（vortex_fill/vortex_idle_full/vortex_empty/vortex_splash）——疑似连接秘境的水道 | [anim] vortex_* |
| 19 | 粮仓 | myth_granary（dynamic） | 储粮建筑，动画带 **pepper（胡椒）/garlic（大蒜）** 香料件——中式调料库 | [anim] pepper/garlic |
| 20 | 蜜罐 | myth_honeypot | 蜂蜜容器，开/关/满三态 | [anim] open/close/full_open |

### 6.2 生长机制汇总（证据等级：`[anim]`=动画名直读）

| 植物 | 生长阶段 | 机制推断 | 证据 |
|---|---|---|---|
| 蟠桃树 | **2 级**（lv1/lv2）+ 苗→矮干→高干 | 树形按阶段替换（DST tree growable 变体模式），结果期树冠挂果（fruit 部件），冬季整树换雪冠（snow/emptytop/emptysnow） | [anim] lv1_idle/lv2_idle + build 部件表 |
| 人参果树 | **3 大阶段**（small→medium→tall）含**过渡动画** | smalltomedium / mediumtotall 是明确的"升级生长"动画 → 非静态换皮，有持续生长过程；tall1/idle1 多 idle 变体 | [anim] 过渡动画名 |
| 竹子 | **3 级**（short_0→short_1→short_2→idle） | 与 DST 原版 grass/竹类 growable 一致：三档高度+可砍（chop）+烧焦 | [anim] short_0/1/2 |
| 葫芦 | **6 级 + 巨型**（seed/sprout/small/med/full/oversized） | 直接挂接 DST 1.0 农场作物管线（farm_plant 前缀+crop_* 动画命名=农场注册作物），rot 腐烂态说明会过期；oversized=巨型葫芦（gourd_oversized 图标） | [anim] 全套 crop_* |
| 莲花（农场版） | **6 级 + 腐烂**（同葫芦） | 同上，莲花被做成可农场种植作物；另存池塘生态版（lotus.zip 昼开夜合）——一物两系统 | [anim] lotus_small/med/full |
| 香蕉树 | **4 级**（tree~tree_4） | 标准 DST 树逻辑：生长/摘果/砍伐/燃烧/残桩全套动画，树型 4 档 | [anim] tree/tree_2/3/4 + chop/burnt_stump |
| 摇钱树 | 常绿单态（idle）+ 掉落（crash） | 非生长型：成熟后摇动掉落钱币（crash=碰撞帧），不砍伐 | [anim] 仅 idle/crash/ground |

### 6.3 特色岛屿/秘境（世界生成区域）`[命名+anim+布局]`

| 区域 | 资产 | 内容推断 | 证据 |
|---|---|---|---|
| 蟠桃园 | layout_peach.lua（69KB 专属布局） | 固定布局的蟠桃种植区：N 棵蟠桃树阵 + 桃产物，地图标 peachtree | [布局文件] layout_peach + map_icons/peachtree |
| 广寒宫 | layout_ghg.lua（39KB）+ myth_ghg | 冰雪宫殿场景：白蓝冰晶中式飞檐建筑、冰岩 myth_rock_ghgice、专属天气 myth_ghg_weather、降雪 myth_ghg_snow；嫦娥居住+室内装修 myth_interiors_ghg_*（10 人份 groundlight） | [布局文件] layout_ghg + [anim] myth_ghg + map_icons/myth_ghg |
| 方寸山 | fangcunhill | 山体地标：灰青岩石山+顶部平台，冬季雪山变体（snow/emptysnow）；老子（菩提祖师）讲道场景 | [anim] fangcunhill（hill/emptysnow/snow）+ map_icons/fangcunhill |
| 土地庙 | myth_tudi_shrines | 世界散布的小型"秘境枢纽"：建造动画、香炉（thurible）、供品（food/food_3）、灯光、雪变体；配 tudi_shrines_trader 交易组件（庙祝兑换） | [anim] build/thurible/food/light + map_icons |
| 金蟾道场 | myth_goldfrog_base + myth_goldfrog_spawner | 金蟾 boss 的台座/刷新点（世界生成刷怪器），金色台座 | [anim] myth_goldfrog_base + map_icons + prefab spawner |
| 犀牛书桌 | myth_rhino_desk + myth_rhino_desk_spawner | 献祭型地标：3 级火焰（fire2/3/4）+空/点燃态；配 myth_rhino_tribute（献祭）/myth_rhino_team（组队） | [anim] fire2/fire3/fire4/empty/swap1 + map_icons |
| 鲲鹏地图 | kunpeng.lua（32KB 专属布局） | 鲲鹏背上/体内特殊地图布局（无独立 anim，推断复用原版动物骨骼） | [布局文件] kunpeng.lua |
| 跨界通道 | myth_door_enter/exit + myth_door_exit**1/2/3** + myth_stonedoor | **3 个传送门出口变体 + 石门**——多秘境/多区域传送体系；井的 vortex 漩涡态疑似水上传送通道；myth_passcard_jie（通行证"界"）为进入凭证 | [anim] door + [命名] 出口编号 1/2/3 |
| 通用布局库 | layout_xml.lua（160KB） | 集中式 XML 布局序列化库：竹林/桃园/药园等上百房间定义（"布局库+专属布局"分层，见 3.2c） | [命名] 3.2c 已述 |

### 6.4 特色地形补充（3.2 遗漏项）

- **turf 清单扩充**：`myth_turfs.zip` 动画包内两 turf 部件名直读——`turf_myth_zhu`（竹地皮）+ `turf_quagmire_parkfield`（**猪镇公园草坪地皮**，复用 SW quagmire 系），均配 inventoryimages 图标，由 main/myth_newturf.lua 注册 `[anim+命名]`。
- **噪声纹理**：levels/textures/ 仅 `Ground_noise_savannah_detail` + `mini_savannah_noise` 两张 —— 大陆外观=稀树草原系噪声（竹林/桃园大陆）`[文件]`。
- **tile atlas**：`levels/tiles/jungle.xml` 48 格 UV 重排复用本体 `data/DLC0002/levels/tiles/jungle.tex`；mod 目录自带同名 jungle.tex（2.8MB，2048x1024，实测为 DXT5）作兜底 `[XML+实测]`。
- 未发现"仙境/天庭/瑶池"专属 tile 或地表纹理 —— 新地皮只有竹地皮+公园草坪两类，其余区域沿用原版地皮 `[命名]`。

### 6.5 美术分析（KTEX 实测解码 + PIL 统计）

方法：mod 内 305 个 anim zip 中挑 20 个代表性 tex，用 dst_tex_analyze.py 的 KTEX 解码器（DXT5/DXT1）还原 RGBA，PIL 统计覆盖像素的饱和度/明度/硬 alpha（alpha>200 占比），并保存 PNG 目检。全部为 **DXT5 + 2 的幂尺寸**（2048/1024/512/256）。

**① 特色植物画风**
| 资产 | 尺寸 | 饱和/明度 | 视觉特征 |
|---|---|---|---|
| 蟠桃树 | 2048² | 26%/27% | **粉白花树冠**（视觉确认大片粉色），白描边，暗部压深；树/花/果/雪四态部件同图集 |
| 人参果树 | 2048²+1024 | 47%/41%（a1 达 55%/35%） | 深绿圆润树冠+黑描边，多层叶堆叠，比原版 evergreen 鲜艳（神话树"发光感"） |
| 树冠层 canopy | 1024² | **71%/18%** | 全 mod 最高饱和深绿（点睛色） |
| 竹子 | 2048x1024 | 38%/23% | 墨绿细长柳叶+节状竹竿，三行高度递进（short_0/1/2） |
| 池塘莲 | 512x256 | 25%/46% | 淡雅低饱和，粉白花瓣+碧绿荷叶盘 |
| 葫芦 | 512² | 25%/36% | 翠绿上小下大葫芦带斑点；紫葫芦 35% 饱和（紫色调） |
| 大蟠桃 | 256² | 31%/52% | 亮粉果，高亮部多（仙桃"发亮"处理） |
| 摇钱树 | 2048x1024 | 43%/34% | 深绿圆冠**挂满金色圆钱**（视觉确认金点密布），金+绿强对比 |
| 巨型葫芦 | 2048x1024 | 28%/44% | 藤蔓卷须+心形大叶+绿黄葫芦果，农场作物标准布局 |
| 共性 | - | 饱和 25~55%，明度 18~52% | **软边 alpha（硬 alpha 16~39%）**=边缘渐变过渡，无硬切；植物整体中低明度深色底 |

**② 岛屿/地形画风**
| 资产 | 尺寸 | 饱和/明度 | 视觉特征 |
|---|---|---|---|
| 方寸山 | 2048² | 21%/42% | **灰青写实岩石**，低饱和块状山体，顶部平台，左下雪盖变体（全 mod 最低饱和建筑） |
| 广寒宫 | 2048² | 41%/46% | **蓝白冰晶琉璃宫**：飞檐翘角中式屋脊+冰晶六角装饰，白亮冰面（视觉确认） |
| 土地庙 | 1024² | 27%/37% | 青灰石庙+香炉小件，朴素 |
| 金蟾台座 | 1024² | **61%/59%** | **全 mod 最高饱和/明度（金色）**——"金"主题一眼可辨 |
| 竹屋 | 2048² | 33%/33% | 青瓦白墙竹编席纹，硬 alpha 46%（建筑件硬切边） |
| 地皮 tile | 2048x1024 | **4%/95%** | 米白底（图集留白格）+彩格（SW 丛林地皮绿/米黄/棕），复用原版纹理验证（3.2a） |
| 地图图标 | 64~128² | 14~49%/20~43% | **硬 alpha 49~66%**：硬边描边小图标（地图缩放下可辨轮廓），统一双色块风 |

**③ XML atlas 组织（已实测样例）**
- 一物一 atlas：`map_icons/peachtree.xml`、`bookinfo/gourd.xml` 均为单 Element 全幅 UV（u1/v1≈0.0078~0.0234，u2/v2≈0.99）`[XML]`；
- anim 包内 build.bin 引用 atlas-0.tex（部分双纹理 atlas-1.tex：人参果树 medium、大蟠桃、香蕉树）`[anim]`；
- dynamic 包（香蕉树/井/粮仓/广寒宫装修）zip 内**只有 anim.bin+build.bin**，纹理内嵌于同名 .dyn（头部加密字节，非 KTEX 明文）——DLCDynamicAnim 的独立纹理通道 `[实测]`。

**结论**：植物美术走"原版 DST 生态系 + 中国题材配色"：形制完全复用 DST 的树/作物/草逻辑与描边风格，仅换配色主题（粉蟠桃、金摇钱树、墨绿竹、淡粉莲）；岛屿建筑则是"中式飞檐 + 写实岩体/冰晶"的 Spriter 部件化图集（2048² 大包），金色（金蟾）与蓝白（广寒宫）两个高辨识度主题色。全部为 DXT5 软边 alpha，图标类硬边。
