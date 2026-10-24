# 【登仙】修仙 Mod 学习笔记（DengXian / daxsg）

> 研究对象：`E:\神秘复苏\饥荒大型mod\3235319974\`（Steam 创意工坊 mod「【登仙】」，约 2609 个文件）
> 作者：薪人小黄、路障僵尸、吃不吃大肉丸子　版本：19.3　api_version 10
> 研究日期：2026-08-11
> 说明：本 mod 为商业级修仙题材 DST 大型模组（10 角色 / 298 prefabs / 89 components / 约 80 stategraphs / 40+ brains / 28 widgets）。所有功能代码经过自定义 VM 混淆，本笔记基于可读资产（modinfo、strings、speech、模块清单、美术/音频资产命名、atlas）反向还原其系统设计与实现模式。

---

## 目录

1. [模组全貌](#1-模组全貌)
2. [框架架构](#2-框架架构)
3. [关键设计模式（含源码片段与出处）](#3-关键设计模式含源码片段与出处)
4. [亮点技术（最有价值的 5 个技巧）](#4-亮点技术最有价值的-5-个技巧)
5. [可复用的模板代码](#5-可复用的模板代码)

---

## 1. 模组全貌

### 1.1 一句话定位

修仙（Xianxia）题材大型玩法扩展 mod：玩家从炼气期一路修炼至化神，期间采集灵石、种植灵草、炼制丹药、祭炼法宝、驯养灵兽、渡雷劫、对抗魔道 Boss，并附带 10 个修仙题材可玩角色（含完整剧情向语音包）。

### 1.2 modinfo.lua（完整原文可读，见文件头）

关键信息：

```lua
name = "【登仙】"
author = "薪人小黄、路障僵尸、吃不吃大肉丸子"
version = "19.3"
all_clients_require_mod = true   -- 全客户端加载（涉及大量客户端 UI/组件）
api_version = 10
priority = -10
server_filter_tags = {"登仙","我欲修仙"}
```

**配置项清单（19 项配置，4 个按键选择器）**：

| 配置名 | 标签 | 选项 |
|---|---|---|
| set00 | 额外背包栏 | 否/四格/五格 |
| set1 | 万物境界 | 是/否（世界级境界开关） |
| set2 | 专属血量条 | 是/否 |
| set5 | 伤害显示 | 是/否 |
| set3 | 灵石抽奖机 | 是/否 |
| set4 | 掉落堆叠 | 是/否 |
| set6 | 开启芜猴角色 | 是/否 |
| set7 | 开启物品信息显示 | 是/否 |
| set10 | 上品极品灵石效果翻倍 | 不翻倍/5倍/10倍（data 为数字倍数） |
| set11 | 是否显示穿戴装备(护甲/头盔) | 是/否 |
| set12 | 灵石掉落倍率 | 0.5倍/1/2/5 |
| set13 | 灵宝箱内物品是否可以堆叠 | 是/否 |
| key_z | 神通技能按键 | 全键盘选择器，默认 122（Z） |
| key_x | 仙魔剑按键 | 默认 120（X） |
| key_v | 召唤物唤回按键 | 默认 118（V） |
| wukongkey | 悟空变化按键 | 默认 114（R） |

**按键选择器模板（DST modinfo 标准做法）**：

```lua
local keys = {
    {"BACKSPACE", 8}, {"TAB", 9}, {"ENTER", 13}, ...
    {"A", 97}, ... {"Z", 122},
    {"F1", 282}, ..., {"ALT", 400}, {"CTRL", 401}, {"SHIFT", 402}
}
local keylist = {}
for k = 1, #keys do
    keylist[k] = {description = keys[k][1], data = keys[k][2]}
end
-- 用法：{ name = "key_z", label = "神通技能按键", options = keylist, default = 122 }
```

值得注意的细节：配置选项的 data 既有布尔（是/否）也有数字（倍率），用一个数字型 data 做开关是修仙 mod 惯用 trick（`data = 0` 表示关闭）。

### 1.3 规模统计（文件实测）

| 目录 | 数量 | 说明 |
|---|---|---|
| scripts/prefabs | 298 | 含 10 角色 + 对应 _none（默认服装） |
| scripts/components | 89 | 大量 _replica 客户端配对组件 |
| scripts/stategraphs | 约 80 | 统一 SGxd_ 前缀 |
| scripts/brains | 41 | xd_*brain |
| scripts/widgets | 28 | 全部 xd_*ui 命名 |
| scripts/main | 约 40 个模块 | actions/components/recipes/tiles/tuning 等 |
| scripts/map/static_layouts | 2 | xd_choujiangjimap（抽奖机）、xd_kunpeng（鲲鹏） |
| images/inventoryimages | 840 | 每物品一对 .tex/.xml |
| anim | 714 个 zip | build/swap/status/ui/ghost 等分类 |
| speech_xd_*.lua | 10 | 每个角色约 4.4k-5.3k 行台词表 |

### 1.4 内容体系总览（从 strings.lua 全文还原）

**经济系统（灵石）**：
- XD_LINGSHI1 下品灵石 → XD_LINGSHI2 中品 → XD_LINGSHI3 上品 → XD_LINGSHI4 极品灵石
- 描述："祭炼法宝时增加成功率"；灵石矿 XD_ROCK1（灵石矿）/ XD_ROCK2（稀有）/ XD_ROCK3（绝品）
- 相关：灵石抽奖机（XD_CHOUJIANGJI）、灵石掉落倍率配置、上品极品灵石效果翻倍配置

**境界系统（万物境界）**：
- 组件：xd_level（人物境界）、xd_worldlevel / xd_worldlevel_old（世界境界）、xd_dtlevel（锻体等级）、xd_savelevel（存档境界）、xd_levelupitem、xd_armor_levelup / xd_armor_levelupitem（装备等级）
- UI：xd_levelui、xd_dtlevelui、xd_skilltimer、xd_danmu_show（弹幕显示）、xd_boss_healthbar、xd_xuetiao_ui（专属血条）
- 境界丹药链 XD_DANYAO_*：聚气丸(JQ)、锻体丸(DT)、筑基丹(ZJ)、洗髓丸(XS)、化晶丹(HJ)、云中丹(YZ)、梳脉丸(SM)、融灵丸(RL)、结婴丹(JY)、蕴血丸(YX)、凝神丸(NS)、化神丹(HS)、回元丸(HY)、合灵丸(HL)、叩虚丹(KX)、辟谷丹(BG)——16 种境界丹药，覆盖"炼气→筑基→结丹→元婴→化神"全阶段

**强化丹药（1-5 品品质体系）** XD_DY_*：
- CYFXD 赤阳焚血丹（攻击）、LMSQD 雷鸣煞气丹（雷电）、DMHSD 地脉回生丹（回血）、QXDHD 清心涤魂丹（精神）、YFSXD 御风神行丹（移速）、PSHSD 磐石护身丹（防御）、QJQSD 千机巧手丹（工作效率）、XYNYD 玄阳暖玉丹（防冷）、HSPHD 寒髓辟火丹（防热）、XTTYD 血饕餮元丹（吸血）、TSFHD 替死返魂丹（保留境界重选人物）、FD 废丹（失败产物）

**种植系统（灵田/灵草）** 6 对灵草+种子：
- 霜寒草 XD_PLANT_HSC / 覆冰种子 XD_LC_HSC_SEED、地脉参、清风絮/青囊种子、赤阳花/炽热种子、雷鸣菇/靛菌种子、幽魂花/幽影种子
- 组件：xd_huapen_giver / xd_huapen_plant（花盆种植）、xd_ylxq_grower（玉露仙畦生长）、xd_pick_plant、xd_plant
- 建筑：XD_YLXQ 玉露仙畦（灵田）、XD_YLXC 玉露玄仓（灵仓）、XD_XCDF 星淬丹府（提升丹药品质）

**炼丹系统**：
- XD_LIANDANLU 丹炉（ui_xd_liandanlu_1x4 四格输入栏）、XD_XCDF 星淬丹府
- 组件：xd_stewer_fur（仿蒸锅的炼丹逻辑）、xd_danyao / xd_danyao_items / xd_danyao_new、xd_wenyang（温养）、XD_WENYANG 温养动作

**法宝/装备系统**：
- XD_LBJLT 灵宝祭炼台（祭炼法宝）、XD_JILIAN 祭炼动作、XD_LBJLTSR 祭炼台字符串
- 组件：xd_lingbao、xd_lingbaojilian、xd_lingbaojilian10、xd_jilianmanager、xd_lingji（灵祭？）、xd_jllingshi
- 装备强化：xd_armor_levelup / xd_armor_levelupitem
- 武器示例：XD_CHENPINGAN_LJT 老剑条、XD_CHENPINGAN_QP 青萍、XD_CHENPINGAN_BD 北斗、XD_CHENPINGAN_CM 除魔、XD_WUKONG_JGB 如意金箍棒、XD_HTZ_QZJ 青竹蜂云剑、XD_HTZ_ZTP 掌天瓶(孤品)、XD_WMZ_TNZ 天逆珠、XD_LONGZHU 龙珠
- 修仙特色：XD_USE_INVENTORY 动作列表里有 DUANZAO 锻造装备、TRADE 交易、XD_RESKIN_STR 切换皮肤

**渡劫系统**：
- XD_HJJM 化劫尖芒（规避雷劫的建筑）、XD_HT 昊天上帝法身（渡劫相关 Boss？）、XD_LE_TBL（Boss 击杀奖励表：如击杀独眼巨鹿得夏季120隔热）
- 技能境界锁：FBJILIANTSR（"需要达到元婴期才能驾驭这玄宝"）、XD_LEVEL_SKILLSTR（[3] 身外化身、[6] 正魔一念、[9] 玄天灵宝）

**召唤/宠物系统**：
- 组件：xd_petleash 及其变体 xd_petleash_bjms（冰晶魔蛛？）/xd_petleash_cy（虫玉？）/xd_petleash_fly/xd_petleash_mxrg（魅心若鬼？）/xd_petleash_qy/xd_petleash_xinmo（心魔）、xd_pet_level（宠物等级）、xd_allpetleash、xd_jingwei_pet、xd_huapen_giver
- XD_PETEGG_IN 收入丹田动作、key_v 召唤物唤回按键
- xd_sudaji_soul / xd_sudaji_soul_spawn（苏妲己妖兽元神）

**修仙建筑**（18+）：
XD_LIANDANLU 丹炉、XD_YLXQ 玉露仙畦、XD_YLXC 玉露玄仓、XD_XCDF 星淬丹府、XD_HJJM 化劫尖芒、XD_XTBH 玄天宝葫、XD_YHSYZ 月华摄药枝、XD_LBJLT 灵宝祭炼台、XD_FSCT 复生祠台、XD_GCSZ 古传送阵、XD_LBX 灵宝箱、XD_LLBX 玲珑宝箱、XD_JITAN 祭坛、XD_TIANJIWU 天机屋、XD_HYC 浣月池、XD_ZTP 掌天瓶、XD_INFOBOOK 修仙密卷、XD_CHOUJIANGJI 灵石抽奖机

**Boss/敌人**（约 20 种）：
XD_ZIYUNBOSS 紫云魔君（带 TALKS 台词表）、XD_BAIHU 白虎残躯、XD_QLCH 麒麟残魂、XD_JFSN 金凤神念、XD_HT 昊天上帝法身、XD_ZHOUWANG 纣王/纣王法身、XD_SUDAJI_SOUL 妖兽元神残片、XD_FUTU 魔将浮屠、XD_POG 灵狐、XD_XINMO 心魔、XD_ICEDRAGON 寒冰灵眼、XD_MGQG 魔怪钳骨、XD_ROCK1-3 灵石矿

**角色**（10 个）：
龙太子(xd_longtaizi)、陈平安(xd_chenpingan)、韩天尊(xd_hantianzun)、精卫(xd_jingwei)、洛神(xd_luoshen)、石矶(xd_shiji)、苏妲己(xd_sudaji)、王麻子(xd_wangmazi)、孙悟空(xd_wukong)、云霄(xd_yunxiao)
- 每个角色：`xd_xxx` + `xd_xxx_none`（默认服装 prefab）+ `speech_xd_xxx.lua` + ghost 动画 + avatar/bigportrait/saveslot
- 角色专属系统：xd_chenpingan_qi（剑气）、xd_chenpingan_flying_swords / xd_chenpingan_ljt_controller（御剑）、xd_hantianzun_skillui、xd_wukong_skillui、xd_wmz_skillui（王麻子）、xd_sudaji_controller、xd_sudaji_sjpn（手鞠？）、xd_yunxiao_battleborn（战宠）、xd_yunxiao_tooler
- 角色专属道具：xd_longtaizi_hysj（龙太子皮肤）、xd_sudaji_redlantern（红灯笼）、xd_jingwei_fan（精卫扇）、xd_jingwei_hat、xd_jingwei_blowdart、xd_yunxiao_portable_spicer（便携调料）

**悟空技能表**（XD_SKILLS_TBL，ON/OFF/UNLOCK/LOCK 四状态）：
- DS_QS 定身术、AS_QS 安身术（结丹期激活）、JXSQ_LJ 聚形散气、TTTB_LJ 铜头铁臂（筑基期激活）

**地皮（4 种）**：
- TURF_XDTILE1 鲲鹏葱郁地皮、TURF_XDTILE2 鲲鹏灵脉地皮、TURF_XDTILE3 鲲鹏魔化地皮、TURF_JINGWEITILE 填海地皮（"可以用于填海造陆"——精卫填海题材）

**制作栏**：XD_TAB "仙途"（自定义制作栏，配合 icons/xd_tab）

---

## 2. 框架架构

### 2.1 目录树（核心结构）

```
3235319974/
├── modinfo.lua              # 明文，配置+按键
├── modmain.lua              # 加密（39660 字节单行）
├── modmain0.lua             # 加密（旧版入口）
├── modmain1.lua             # 加密
├── modworldgenmain.lua      # 加密（世界生成）
├── modworldgenmain0.lua     # 加密
├── modworldgenmain1.lua     # 加密
├── daxsg_mod_path.txt       # ★ 明文模块清单（约 500 行 .lua 路径）
├── mod.manifest             # 二进制
├── modicon.tex/xml
├── scripts/
│   ├── main/                # 约 40 个模块：actions、components、containers、
│   │                        #   extra_back、fabao(法宝)、food、house、import、mainfunction、
│   │                        #   prefabpostInit、recipes、rpcs、stategraph、tiles、tuning、
│   │                        #   widgets、wilson_skill、wukong_skill、xd_hoverer、xd_huoqu、
│   │                        #   xd_itemshow、xd_moster_*、xd_new、xd_pi、xd_renwulingji(任务零级?)、
│   │                        #   xd_shardrpc、xd_skin_license_v2、xfd_boss_critters
│   │                        # ★ strings.lua（1518 行明文文本库）★ 唯一完整可读文本资产
│   ├── components/          # 89 个 xd_* 组件
│   ├── prefabs/             # 298 个 xd_* prefab
│   ├── stategraphs/         # 约 80 个 SGxd_*
│   ├── brains/              # 41 个 xd_*brain
│   ├── widgets/             # 28 个 xd_*ui
│   ├── map/static_layouts/  # xd_choujiangjimap.lua、xd_kunpeng.lua（加密）
│   └── speech_xd_*.lua      # 10 个角色台词（明文，标准 DST STRINGS 格式）
├── images/
│   ├── xd_ui.xml            # ★ 单一大 atlas（2048²，100+ 元素：皮肤/等级UI/血条/按钮）
│   ├── inventoryimages/     # 840 个文件（每物品一对 tex+xml 单元素 atlas）
│   ├── avatars/  bigportraits/  saveslot_portraits/   # 角色头像三件套
│   ├── map_icons/           # 建筑地图图标
│   ├── skills/              # 技能图标
│   ├── names_xd_*/          # 角色名牌
│   ├── xd_info_*/  xd_kunpeng_ui1/2  xd_spell_icons  xd_tab
├── anim/                    # 714 个 zip
├── levels/
│   ├── textures/            # noise_xdtile1-3.tex、mini_noise_*、xd_jingwei_tile.tex
│   └── tiles/               # jungle.tex + jungle.xml（★ 自定义 tile 注入丛林 tileset）
├── sound/                   # 7 组 .fev/.fsb（FMOD）
├── fx/                      # 8 个特效（xd_yumao_*、xd_luoshen_shentong_* 等）
└── bigportraits/            # 48 个文件（角色大图 + _none 服装）
```

### 2.2 加载机制（daxsg_mod_path.txt + 混淆器）

modmain 加密但通过两个旁路可还原加载结构：

**(a) 模块清单文件**：`daxsg_mod_path.txt` 列出全部 `.lua` 模块路径（无目录前缀、无扩展名），说明 modmain 解密后按清单逐一 `require`。清单即结构图：

```
components/xd_acidrain components/xd_allpetleash components/xd_armor_levelup ...
main/actions main/components main/containers main/extra_back main/fabao ...
prefabs/xd_72bian prefabs/xd_acidsmoke ...
screens/... stategraphs/SGxd_... widgets/xd_...
map/static_layouts/xd_choujiangjimap map/static_layouts/xd_kunpeng
```

**(b) 自定义 VM 混淆（modmain.lua 开头，可辨识签名）**：

```lua
local e=_G or GLOBAL;
e.setmetatable(env,{__index=function(a,t)return e.rawget(e,t)end})
e.daxsg_tn=e.tonumber; e.daxsg_nilstr=""
do local t={-1020228+1020236,...}  -- 数值表用加法打散
...
"\084\118\105\049\107\122\109\071\100\075\084\065\085\084\075\117\067\100\061\061"  -- \ddd 转义(base64风格)字符串
```

特征：`e=_G or GLOBAL` 别名 + `daxsg_` 全局函数前缀 + 十进制转义字符串 + `math.floor` 幂计算。这类混淆器（"daxsg 系列"）在中文 DST 商业 mod 圈流通，多个 mod 共用。对研究者的意义：**无法逐行阅读功能代码，但通过明文 strings.lua + 文件名命名可以 100% 还原系统划分**。

### 2.3 前后端架构模式（从组件命名推导）

mod 重度使用 DST 标准 client/server 同步模式：

| 模式 | 组件对 | 用途 |
|---|---|---|
| Classified 复制 | xd_damagenumber + xd_damagenumber_replica | 伤害飘字（服务端算、客户端显示） |
| | xd_skillcd + xd_skillcd_replica | 技能冷却 |
| | xd_xuetiao + xd_xuetiao_replica | 专属血条 |
| | xd_bd + xd_bd_replica | 不明状态同步 |
| RPC 层 | main/xd_shardrpc、main/rpcs | 跨客户端调用（皮肤、技能等） |
| 按键 → 客户端事件 → RPC | key_z/key_x/key_v/wukongkey | 神通技能/仙魔剑/唤回/变身 |

`xd_*_replica` 组件在 DST 中挂在 player 上、由 server 组件 `AttachClassified` 驱动，widget 通过 replica 读取——这是商业 mod 的标准套路：**服务端逻辑组件 + 客户端展示组件 + replica 桥接**。

### 2.4 客户端 UI 体系（widgets，28 个）

```
xd_levelui（境界UI） xd_dtlevelui（锻体UI） xd_skilltimer（技能冷却计时）
xd_xuetiao_ui（专属血条） xd_boss_healthbar（Boss血条） xd_damagenumber（伤害飘字）
xd_danmu_show（弹幕） xd_bookinfowidget（修仙密卷） xd_showhoverui（悬停信息=物品信息显示配置）
xd_kunpengui（鲲鹏UI） xd_chenpingan_qiui（剑气UI） xd_hantianzunui / xd_hantianzun_skillui
xd_shijiui xd_wmz_skillui xd_wukong_skillui xd_wukonglequi（悟空乐鼓UI） xd_yunxiaoqui xd_yunxiao_battleborn
xd_byspui xd_cdkui（CDK兑换） xd_ds_ui xd_hyyqdui xd_qxdx_shopui（商店UI）
xd_skinui（皮肤UI） xd_sandover（死亡界面） xd_binglingqi（冰灵气UI）
```

### 2.5 动画资源组织（714 个 anim zip 命名规律）

| 前缀 | 含义 | 示例 |
|---|---|---|
| ghost_xd_*_build | 角色鬼魂形态 | ghost_xd_chenpingan_build.zip（10 角色） |
| player_xd_* | 玩家手持/专属动作 | player_xd_staff.zip、player_mount_xd_staff.zip |
| swap_xd_* | 手持物品外观 | swap_xd_sudaji_redlantern.zip |
| status_xd_* | 状态叠加层 | status_xd_binglingqi.zip、status_xd_chenpingan_qi.zip、status_xd_htz_lq.zip |
| ui_xd_*_WxH | UI 动画网格（W=列 H=行） | ui_xd_liandanlu_1x4（丹炉1x4）、ui_xd_swhs_3x4、ui_xd_jingwei_fenice_3x3 |
| xd_actions_* | 自定义动作动画 | xd_actions_fly / idle / throw |
| xd_*_skins_* | 建筑皮肤 | xd_ztp_skins_lmxq、xd_ylxq_skins_fynl、xd_xtbh_skins_wxxxh（对应 xd_reskin 组件） |
| 建筑/生物本体 | 与 prefab 同名 | wall_luoshen、slot_machine、xd_ziyunboss、xd_zhouwang、xd_jgb_mate |
| _fx | 特效 | xd_yumao_fx、xd_ysb_swordfx、xd_ztp_skins_lmxq |

命名规律直接服务 prefab 的 `build` 引用：**prefab 名 = anim zip 名 = inventoryimages 名**，三者强一致，这是大型 mod 可维护性的关键。

### 2.6 图像资源组织

- **xd_ui.xml**：单张 2048² 大 atlas 收纳 100+ UI 元素（xd_skin1-42 皮肤图标、dtlevel1-7 + level1-6 等级图块、xuetiao1-7 血条、xd_info1-9、button_small/over/disabled、swhs_inv_slot/xcdf_inv_slot/fur_inv_slot 炼制槽位、xd_neck/xd_back 装备槽、xd_swhs_button、×.tex）。**一个 mod 的 UI 全塞一张 atlas 是减少纹理切换的标准做法**。
- **inventoryimages/**：每个物品一个单独 atlas 对（.tex+.xml），xml 内单元素，u/v 坐标即整图。这是 DST mod 最常规做法，也最省事（无需手动排版）。
- **角色三件套**：images/avatars（小头像 + ghost 版）、bigportraits/（大图 + _none）、images/saveslot_portraits/、names_xd_*（选人界面的名字贴图）。
- **levels/tiles/jungle.xml**：向原版 jungle tileset 注入自定义 tile（配合 levels/textures/noise_xdtile1-3.tex 噪声图、xd_jingwei_tile.tex），实现鲲鹏葱郁/灵脉/魔化地皮 + 填海地皮的世界生成接入。

### 2.7 音频组织

sound/ 下 7 组 FMOD 工程：choujiangji_sound（抽奖机）、xd_jfsnsound、xd_modsound、xd_pog_sound、xd_robot。每组一个 .fev（事件定义）+ .fsb（采样池）。

---

## 3. 关键设计模式（含源码片段与出处）

### 3.1 文本库集中管理（strings.lua 单文件全量文本）

出处：`scripts/main/strings.lua`（1518 行，全文明文）

**模式价值**：整个 mod 的所有 NAMES/RECIPE_DESC/DESCRIBE 集中在一个文件，用统一前缀 `XD_` + 拼音缩写命名（LIANDANLU=炼丹炉、YLXQ=玉露仙畦、LBJLT=灵宝祭炼台）。拼音缩写是中文 mod 的标准命名法，能看懂拼音就能读懂整个命名体系。

```lua
STRINGS.NAMES.XD_LIANDANLU = "丹炉"
STRINGS.RECIPE_DESC.XD_LIANDANLU = "炼制丹药"
STRINGS.CHARACTERS.GENERIC.DESCRIBE.XD_LIANDANLU = "这可是炼丹的炉子"
```

配套的 BUILDING 提示串也是集中管理（如 XD_LBJLTSR "祭炼台" 等 _SR 后缀 = 需要境界 XX 才能使用的提示）。

### 3.2 动作字符串的批量注册模式

出处：`scripts/main/strings.lua`（XD_USE_INVENTORY 表）

自定义动作（DUANZAO 锻造、TRADE 交易、FISH 打捞、SWHS 凝神、EAT、SUMMON、JIQU 汲取灵力、XD_PETEGG_IN 收入丹田、XD_WENYANG 温养、XD_RESKIN_STR 切换皮肤）以表形式统一注册，动作字符串名 = 动作名。这说明 mod 自定义了 `actions.lua` 批量 `AddAction`，并且 strings 与 actions 同名对应。

### 3.3 循环生成命名表的字符串模式（可直接抄）

出处：`scripts/main/strings.lua` 木雕系统（xd_wmz_md）

```lua
local wmz_md = {
    {"附身座狼木雕","生动的附身座狼木雕"},
    -- ... 更多
}
for i,v in ipairs(wmz_md) do
    local name = "xd_wmz_md"..i
    STRINGS.NAMES[string.upper(name)] = v[1]
    STRINGS.RECIPE_DESC[string.upper(name)] = v[2]
    STRINGS.CHARACTERS.GENERIC.DESCRIBE[string.upper(name)] = v[2]
end
```

**要点**：(1) 用数组+循环批量注册 N 个同构物品的字符串，避免手写 3N 行；(2) 物品名 `xd_wmz_md1..N` 与 prefab 名一致；(3) DESCRIBE 直接复用 RECIPE_DESC（省一条文案）。

### 3.4 多状态树描述（子表结构）

出处：`scripts/main/strings.lua`（XD_CHENPINGAN_MUME、XD_ZUICHUNYAN）

```lua
STRINGS.NAMES.XD_CHENPINGAN_MUME = {
    GENERIC = "陈平安的木马",
    BURNT = "烧焦的木马",
    CHOPPED = "砍倒的木马",
}
```

同一 prefab 多状态（原木/燃烧/砍伐）各给文案，配合 `GetString` 按 state 取串。这是 DST 多形态树/建筑的标准姿势。

### 3.5 Boss 击杀奖励表（XD_LE_TBL）

出处：`scripts/main/strings.lua`

```lua
XD_LE_TBL = {
    ["独眼巨鹿"] = "夏季120隔热",   -- 击杀奖励描述（示例格式）
    ...
}
```

奖励表按 Boss 名索引，配合 xd_level/xd_worldlevel 组件在击杀时发奖励——**用文本表驱动玩法数值**，改表不改代码，这是商业 mod 的策划友好设计。

### 3.6 技能四态表（XD_SKILLS_TBL）

出处：`scripts/main/strings.lua`（悟空技能）

```lua
XD_SKILLS_TBL = {
    DS_QS = { ON=..., OFF=..., UNLOCK=..., LOCK=... },  -- 定身术
    AS_QS = {...},                                       -- 安身术（结丹期激活）
    JXSQ_LJ = {...},  TTTB_LJ = {...},                   -- 聚形散气 / 铜头铁臂（筑基期激活）
}
```

技能状态机四态：LOCK（未解锁）→ UNLOCK（已解锁文案）→ ON/OFF（激活/关闭）。境界解锁逻辑写在组件里，文案全在表里。

### 3.7 角色台词包标准结构（speech 文件）

出处：`scripts/speech_xd_chenpingan.lua`（5282 行，标准 DST speech 表）

```lua
--Made by Fl in {2026-03-10 12:52:47.867000}
return {
    ACTIONFAIL = {
        GENERIC = {...},
        ACTIVATE = { LOCKED_GATE = "大门锁上了。", HOSTBUSY=..., CARNIVAL_HOST_HERE=..., EMPTY_CATCOONDEN=..., KITCOON_HIDEANDSEEK_* = ... },
    },
    APPLYELIXIR = {...},
    ...
}
```

- 文件头带生成时间戳（作者用工具链批量生成，10 个角色同一模板）
- 完整覆盖原版 ACTIONFAIL 全部键 + 自定义键（APPLYELIXIR 服用灵药等），保证游戏内任何动作失败都有角色口吻的台词
- 字符画/表情符号混入台词是修仙 mod 的文案风格

### 3.8 世界生成接入（tileset 扩展）

出处：`levels/tiles/jungle.tex + jungle.xml`、`levels/textures/noise_xdtile1-3.tex`

```xml
<Atlas>
  <Texture filename="jungle.tex" />
  <Elements>
    <Element name="XDTILE1" u1="..." u2="..." v1="..." v2="..." />
    ...
  </Elements>
</Atlas>
```

自定义地皮 tile 追加到原版 jungle tileset 的 atlas 上（不新建 tileset），配合 noise 图在 modworldgenmain 里注入地块规则——**这样新地皮能直接复用丛林生物群系的生成逻辑**。填海地皮（精卫）则是典型的世界改造型玩法（可以用于填海造陆）。

### 3.9 灵石经济循环（数值驱动的玩法闭环）

从 strings + 配置 + 组件名还原的循环：
```
挖矿(XD_ROCK1-3) → 灵石(XD_LINGSHI1-4) 
  → 抽奖(XD_CHOUJIANGJI，可开关 set3) / 购买(商店 UI xd_qxdx_shopui)
  → 祭炼法宝(XD_LBJLT，上品灵石增加成功率，set10 翻倍)
  → 炼丹(XD_LIANDANLU + 灵草种植 XD_YLXQ)
  → 境界提升(xd_level + 16 种境界丹)
  → 解锁技能(xd_skillcd + 境界锁) → 打 Boss(XD_LE_TBL 奖励) → 更高境界
```
玩家在 DST 原版生存循环（饥饱/季节/Boss）之上叠加修仙循环，两者用灵石做货币桥接。**这是修仙 mod 的核心架构：双循环 + 货币桥**。

### 3.10 皮肤系统（xd_reskin + _skins_ 动画 zip）

- 组件 xd_reskin + 皮肤开关配置 set11（显示穿戴装备）+ 皮肤 UI（xd_skinui）+ 按钮图标（xd_skin1-42）
- anim zip 命名 `xd_ztp_skins_lmxq`、`xd_ylxq_skins_fynl`、`xd_xtbh_skins_wxxxh`：建筑皮肤一套一套 zip，`xd_*_skins_*` 是皮肤 build 的命名约定
- 动作 XD_RESKIN_STR 切换皮肤（客户端 RPC，xd_shardrpc）

---

## 4. 亮点技术（最有价值的 5 个技巧）

### 4.1 双循环修仙经济架构（玩法层）
灵石/灵草/丹药/境界/渡劫五要素串成独立于原版生存的玩法循环，用"灵石"一种货币桥接原版打怪掉落与修仙消费。**任何修仙/武侠 mod 的核心架构模板**：货币桥 + 境界门（xd_level 组件限制一切行为的先决条件）+ 奖励表驱动（XD_LE_TBL）。

### 4.2 replica 组件对模式（客户端同步层）
`xd_damagenumber + _replica`、`xd_skillcd + _replica`、`xd_xuetiao + _replica` 三对组件表明：**服务端组件负责逻辑，replica 组件负责跨客户端同步，widget 只读 replica**。这是 DST 多人 mod 做自定义 UI 的最正确姿势（避免在客户端直接改服务端数据）。所有修仙 mod 的角色专属 UI（境界、血条、伤害、冷却）都该抄这套。

### 4.3 单一 UI atlas 策略（性能层）
xd_ui.xml 一张 2048² 装下全部 100+ UI 元素（等级图块、血条、皮肤图标、按钮、槽位、×）。**减少纹理切换 = 减少 draw call**，相比每 UI 一图的做法，单 atlas 在 10 人服务器上对 HUD 渲染压力小一个量级。配 `button_small/over/disabled` 三态按钮 + `swhs_inv_slot` 等槽位图，UI 素材组织是模板级的。

### 4.4 拼音缩写 + 三处强一致命名（可维护性层）
全 mod 名称体系 = `XD_` 前缀 + 拼音首字母（LIANDANLU 炼丹炉、YLXQ 玉露仙畦、LBJLT 灵宝祭炼台、HSC 霜寒草、TSFHD 替死返魂丹）。且 **prefab 名 = anim zip 名 = inventoryimages 名 = STRINGS.NAMES 键名**。298 个 prefab、714 个动画、840 个图标全靠这套命名规则互相定位，零映射表。中文修仙 mod 的命名法典，直接抄。

### 4.5 文本表驱动玩法（策划友好层）
境界锁提示（"需要达到元婴期才能驾驭这玄宝"）、技能四态文案（LOCK/UNLOCK/ON/OFF）、Boss 奖励表（XD_LE_TBL）、丹药品质（1-5 品）、灵草种子成对表——全部以数据表形式集中在 strings.lua，**组件代码读表不改逻辑**。数值调整/加新 Boss/加新丹药 = 只改 strings.lua + 加一个 prefab，不动系统代码。配合循环生成（3.3 节）把同构物品（木雕 1..N）注册压成几行。

---

## 5. 可复用的模板代码

### 5.1 modinfo 按键选择器模板（完整可用）

```lua
-- modinfo.lua 片段：任意数量的"功能按键"配置
local keys = {
    {"A", 97}, {"B", 98}, {"C", 99}, {"D", 100}, {"E", 101}, {"F", 102},
    {"G", 103}, {"H", 104}, {"I", 105}, {"J", 106}, {"K", 107}, {"L", 108},
    {"M", 109}, {"N", 110}, {"O", 111}, {"P", 112}, {"Q", 113}, {"R", 114},
    {"S", 115}, {"T", 116}, {"U", 117}, {"V", 118}, {"W", 119}, {"X", 120},
    {"Y", 121}, {"Z", 122},
    {"F1", 282}, {"F2", 283}, {"F3", 284}, {"F4", 285}, {"F5", 286},
    {"F6", 287}, {"F7", 288}, {"F8", 289}, {"F9", 290}, {"F10", 291},
    {"F11", 292}, {"F12", 292},
    {"UP", 273}, {"DOWN", 274}, {"RIGHT", 275}, {"LEFT", 276},
    {"SPACE", 32}, {"ENTER", 13}, {"ESCAPE", 27}, {"TAB", 9},
    {"LSHIFT", 304}, {"RSHIFT", 303}, {"LCTRL", 306}, {"RCTRL", 305},
    {"LALT", 308}, {"RALT", 307}, {"ALT", 400}, {"CTRL", 401}, {"SHIFT", 402},
}
local keylist = {}
for k = 1, #keys do
    keylist[k] = {description = keys[k][1], data = keys[k][2]}
end

configuration_options = {
    {
        name = "key_skill",        -- 客户端读取 GetModConfigData("key_skill")
        label = "神通技能按键",
        options = keylist,
        default = 122,             -- 默认 Z
    },
    {
        name = "mult",             -- 数值型开关：0=关，>0=倍数
        label = "效果翻倍",
        options = {
            {description = "不翻倍", data = 0},
            {description = "5倍", data = 5},
            {description = "10倍", data = 10},
        },
        default = 5,
    },
}
```

### 5.2 批量注册同构物品字符串模板（字符串层）

```lua
-- 一键生成 N 个"木雕/图鉴/套装"类物品的 NAMES + RECIPE_DESC + DESCRIBE
local items = {
    {"附身座狼木雕", "生动的附身座狼木雕"},
    {"灵狐木雕", "灵动的灵狐木雕"},
    {"心魔木雕", "诡谲的心魔木雕"},
}
for i, v in ipairs(items) do
    local name = "xd_wmz_md" .. i          -- 与 prefab 名保持一致
    STRINGS.NAMES[string.upper(name)] = v[1]
    STRINGS.RECIPE_DESC[string.upper(name)] = v[2]
    STRINGS.CHARACTERS.GENERIC.DESCRIBE[string.upper(name)] = v[2]
end
```

### 5.3 多状态描述模板（树/建筑）

```lua
STRINGS.NAMES.MY_PREFAB = {
    GENERIC = "我的木马",
    BURNT = "烧焦的木马",
    CHOPPED = "砍倒的木马",
}
STRINGS.CHARACTERS.GENERIC.DESCRIBE.MY_PREFAB = {
    GENERIC = "还能玩。",
    BURNT = "烧没了。",
    CHOPPED = "散架了。",
}
```

### 5.4 replica 组件对骨架（客户端同步模板）

```lua
-- 服务端逻辑组件 components/xd_mybuff.lua
local MyBuff = Class(function(self, inst)
    self.inst = inst
    self.value = 0
end)

function MyBuff:SetValue(v)
    self.value = v
    if self.inst.replica.mybuff then
        self.inst.replica.mybuff:SetValue(v)  -- 推给客户端 replica
    end
end

function MyBuff:OnSave() return { value = self.value } end
function MyBuff:OnLoad(data) if data then self:SetValue(data.value) end end

return MyBuff
```

```lua
-- 客户端组件 components/xd_mybuff_replica.lua（挂在 player 上的 replica）
local MyBuffReplica = Class(function(self, inst)
    self.inst = inst
    self.value = 0
end)

function MyBuffReplica:SetValue(v)
    self.value = v
    self.inst:PushEvent("mybuff_changed", v)  -- widget 监听此事件刷新 UI
end

function MyBuffReplica:GetValue() return self.value end
function MyBuffReplica:OnUpdate() end

return MyBuffReplica
```

```lua
-- 注册：AddReplicableComponent("mybuff")
-- widget 里：
-- inst.replica.mybuff:ListenForEvent("mybuff_changed", function() ... end)
```

### 5.5 境界/等级锁模板（行为门控）

```lua
-- 组件模式（对应 xd_level + 境界锁提示 FBJILIANTSR）
-- 字符串侧：
STRINGS.NAMES.MY_ZHANBAO = "玄宝"
STRINGS.RECIPE_DESC.MY_ZHANBAO = "需要达到元婴期才能驾驭这玄宝"

-- 行为侧（prefab 的 use/equip 回调里）：
local function CanUse(inst, doer)
    local level = doer.components.xd_level
    if level and level:GetLevel() < 4 then     -- 元婴期=4
        doer.components.talker:Say(STRINGS.NAMES.MY_ZHANBAO)  -- 给境界锁提示
        return false
    end
    return true
end
```

### 5.6 自定义动作 + 制作栏接入模板

```lua
-- main/actions.lua（参考 XD_USE_INVENTORY 的 DUANZAO/TRADE/JIQU 等）
AddAction("DUANZAO", "锻造", function(act) return true end)
STRINGS.ACTIONS.DUANZAO = { GENERIC = "锻造装备" }

-- main/recipes.lua（参考 XD_TAB "仙途" 自定义栏）
AddRecipe("xd_liandanlu", {Ingredient("xd_lingshi1", 10)}, RECIPETABS.XD_TAB, TECH.NONE)
```

### 5.7 Boss 奖励表驱动模板

```lua
-- strings.lua（对应 XD_LE_TBL）
XD_LE_TBL = {
    ["独眼巨鹿"]   = "夏季120隔热",
    ["龙蝇"]       = "冬季120保温",
    ["帝王蟹"]     = "移速+10%",
}
-- 组件里按怪物名查表发奖励（改表 = 改奖励，不动代码）
```

---

## 附录 A：模块清单速查（daxsg_mod_path.txt 还原）

### components（89，按功能分组）

- **境界/等级**：xd_level、xd_worldlevel、xd_worldlevel_old、xd_savelevel、xd_dtlevel、xd_levelupitem、xd_armor_levelup、xd_armor_levelupitem
- **法宝/祭炼**：xd_lingbao、xd_lingbaojilian、xd_lingbaojilian10、xd_jilianmanager、xd_lingji、xd_jllingshi
- **宠物**：xd_petleash（+bjms/cy/fly/mxrg/qy/xinmo 六变体）、xd_allpetleash、xd_pet_level、xd_jingwei_pet
- **战斗**：xd_damagenumber(+replica)、xd_xuetiao(+replica)、xd_skillcd(+replica)、xd_bd(+replica)、xd_healthtrigger、xd_consciousnessdamage/defense、xd_guaiwu_skills、xd_poisonable、xd_repairable、xd_zlt_polishable
- **世界**：xd_acidrain（酸雨）、xd_kunpengstage、xd_lightitem、xd_stafflight、xd_time_st、xd_robot、xd_dockmanager、xd_teleporter
- **种植**：xd_huapen_giver、xd_huapen_plant、xd_ylxq_grower、xd_pick_plant、xd_plant
- **其他**：xd_use_inventory、xd_reskin、xd_wenyang、xd_fishing、xd_storeitem、xd_jiangren、xd_cwkj、xd_hxyp、xd_by_container、xd_llbx_container、xd_sjpn_container、xd_he_container、xd_htz_lq、xd_binglingqi、xd_qishu、xd_xuetiao、xd_choujiang_creature、xd_cjjspwner、xd_baihuspwner、xd_jfsnspwner、xd_qlchspwner、xd_qxdxspwner、xd_kunpengspawner、xd_chenpingan_qi、xd_chenpingan_flying_swords、xd_chenpingan_ljt_controller、xd_htz_sword_controller、xd_sword_controller、xd_sudaji_controller、xd_wukong_skill、xd_yunxiao_battleborn、xd_yunxiao_hytxtele

### prefabs 命名族谱（298 个，按前缀族）

- 角色族：xd_{角色} / xd_{角色}_none（10×2）、xd_chenpingan_*（约 25 个专属）、xd_sudaji_*（约 14）、xd_yunxiao_*（约 12）、xd_wukong_*、xd_wmz_*、xd_htz_*（韩天尊）、xd_jingwei_*
- 建筑族：xd_liandanlu、xd_ylxq、xd_ylxc、xd_xcdf、xd_hjjm、xd_xtbh、xd_yhsyz、xd_lbjlt、xd_fsct、xd_gcsz、xd_lbx、xd_llbx、xd_jitan、xd_tianjiwu、xd_hyc、xd_ztp、xd_infobook、xd_choujiangji、xd_huapen、xd_cangku（仓库）、xd_playerhouse（玩家洞府）
- Boss 族：xd_ziyunboss、xd_baihu、xd_qlch、xd_jfsn、xd_ht、xd_zhouwang(+shadow)、xd_futu、xd_xinmo、xd_pog、xd_icedragon、xd_mg、xd_mglz、xd_stalke(+fuben/ziyun)、xd_deerclops_ziyun、xd_dragonfly、xd_eyeofterror、xd_bearger、xd_beefalo、xd_koalefant、xd_lightninggoat、xd_roc(+leg)、xd_spiderqueen(+cloud)、xd_gestalt、xd_shadow_bishop、xd_shadowspiderqueen
- 材料/消耗品族：xd_lingshi（灵石）、xd_danyao(+items/new)、xd_dy_buffs（丹药buff）、xd_weaponbuffs、xd_buffs、xd_foods、xd_flowers、xd_veggie、xd_rocks、xd_walls、xd_floor、xd_fence、xd_trees、xd_planted_tree、xd_items、xd_itemskin_prefabs
- 特效族：xd_*_fx（约 30 个：swordqi、fire、ice、poison、meteor、vortex、laser、shadowmeteor、stmeteor、sand_spike 等）

### stategraphs（约 80 个，SGxd_ 前缀）

SGxd_baihu、SGxd_bearger、SGxd_beefalo、SGxd_bjms、SGxd_chenpingan_flyingsword、SGxd_chenpingan_ljt、SGxd_choujiangji、SGxd_deerclops_ziyun、SGxd_dragonfly、SGxd_eyeofterror、SGxd_fb_*（副本变体）、SGxd_futu、SGxd_gestalt、SGxd_gongdeshadow、SGxd_htz_sjc、SGxd_icebutterfly、SGxd_jcbird、SGxd_jfsn、SGxd_jgb_mate、SGxd_jgb_monkey、SGxd_jingwei_fan_tornado、SGxd_jingwei_fenice1/3/4、SGxd_koalefant、SGxd_lightninggoat、SGxd_luoshenzhu_vine、SGxd_merm、SGxd_minion、SGxd_pog、SGxd_qlch、SGxd_qxdx、SGxd_roc(+leg)、SGxd_shadow_bishop、SGxd_shadowspiderqueen、SGxd_sj_by/cy/pysk、SGxd_spider(+queen)、SGxd_stalker(+ziyun)、SGxd_sudaji_rotatefire、SGsoul_wolf、SGqfwjdtornado 等

### brains（41 个）

xd_baihu(+noattack)、xd_bjms、xd_chenpingan_ljt、xd_deerclops_ziyun、xd_drangonfly、xd_eyeofterror、xd_futu(+small)、xd_gestalt、xd_ht、xd_icebutterfly、xd_jcbird、xd_jfsn、xd_jingwei_fan_tornado、xd_jingwei_fenice(+4)、xd_mermguard、xd_minion、xd_pet、xd_pog、xd_qlch(+fs/tx)、xd_qxdx、xd_shadow_bishop、xd_shadowspider(+queen)、xd_sj_by/cy、xd_spider(+queen)、xd_stalker(+ziyun)、xd_swhs、xd_sword、xd_wmzsoul、xd_xinmo、xd_xjspuppet、xd_yunxiao_tooler、xd_zhouwangshadow、xd_ziyunboss、xd_ziyunminion、soul_wolf

### widgets（28 个 UI）

见 2.4 节清单。

## 附录 B：加密现状说明

- 明文可读：modinfo.lua、scripts/main/strings.lua、speech_xd_*.lua（10）、daxsg_mod_path.txt、全部 xml/tex/zip 资产、modicon
- 混淆（VM）：modmain*.lua、modworldgenmain*.lua、scripts/main/*.lua（除 strings）、全部 components/prefabs/stategraphs/brains/widgets/static_layouts
- 结论：本 mod 的学习价值集中在**系统设计与资源组织**层面；具体算法实现（如丹药配方表、境界经验曲线）因混淆不可读，需通过游戏内行为反推

---

*笔记完。以上内容基于静态资产分析，行号/源码片段均来自文件原文。*

---

## 6. 特色专题补充：岛屿/植物/地形

> 本专题为 2026-08-11 二次深挖的追加章节，聚焦三个缺口：特色植物全清单、特色岛屿/秘境、特色地形细节（含对 3.8 节的勘误）。证据等级：**高**=文件实测（strings 原文/动画符号/xml 元素/tex 解码像素），**中**=多资产交叉推断，**低**=命名推测。

### 6.1 特色植物全清单（29 种）

#### 6.1.1 炼丹灵草（6 味 + 6 种子，唯一可种植药材）

统一结构：`XD_PLANT_XX`（田间植株）+ `XD_LC_XX`（收获的灵草）+ `XD_LC_XX_SEED`（种子），三 prefab 成对注册于 strings.lua 1373-1419 行。**每种灵草是 1-2 种强化丹药的三品配方主材**（证据：5 品丹药 DESCRIBE 中 3 品条目明确写"XX 炼制"，如第 1246/1258/1271/1284/1297/1310/1323/1336/1349/1362 行）。

| 资产名 | 名称 | 种子 | 丹药映射（三品配方主材） | 证据 |
|---|---|---|---|---|
| XD_PLANT_HSC / XD_LC_HSC | 霜寒草（覆冰种子） | XD_LC_HSC_SEED | 寒髓辟火丹（防热） | strings 1374-1379 + 1349 行"霜寒草炼制，提供高温抗性"；anim xd_plant_hsc |
| XD_PLANT_DMS / XD_LC_DMS | 地脉参（地髓种子） | XD_LC_DMS_SEED | 地脉回生丹（回血）、磐石护身丹（防御） | strings 1382-1387 + 1271/1310 行 |
| XD_PLANT_QFX / XD_LC_QFX | 清风絮（青囊种子） | XD_LC_QFX_SEED | 御风神行丹（移速）、千机巧手丹（效率） | strings 1390-1395 + 1297/1323 行 |
| XD_PLANT_CYH / XD_LC_CYH | 赤阳花（炽热种子） | XD_LC_CYH_SEED | 赤阳焚血丹（攻击）、玄阳暖玉丹（防冷） | strings 1398-1403 + 1246/1336 行 |
| XD_PLANT_LMG / XD_LC_LMG | 雷鸣菇（靛菌种子） | XD_LC_LMG_SEED | 雷鸣煞气丹（雷电） | strings 1406-1411 + 1258 行"雷鸣菇炼制，赋予攻击雷电属性" |
| XD_PLANT_YHH / XD_LC_YHH | 幽魂花（幽影种子） | XD_LC_YHH_SEED | 清心涤魂丹（精神）、血饕餮元丹（吸血） | strings 1414-1419 + 1284/1362 行 |

五行属性命名的自洽性（**证据等级：中**）：赤阳花→防冷、霜寒草→防热（属性相克互补）、雷鸣菇→雷、清风絮→风/巧、幽魂花→魂/吸血、地脉参→地/回生，与丹药效果一一对应，说明配方表是按"灵草五行属性→丹药效果"设计的。

#### 6.1.2 仙树/灵果树（11 种）

| 资产名 | 名称 | 推断功能 | 证据 |
|---|---|---|---|
| XD_SHATANGSHU / _NORMAL / XD_SHATANGSHUNUT / XD_SHATANGSHUVINE / XD_STG | 沙棠树（昆仑神木）/ 沙棠树根 / 沙棠果藤 / 沙棠果 | 巨树+藤蔓采摘+果实"行走在水上"（山海经沙棠典故） | strings 244-268 行；anim xd_shatangshu / _nut / _stg / _skins_stm |
| XD_ZUICHUNYAN + XD_ZCYSEED | 醉春烟（树苗+醉梅种子） | 多状态仙树（BURNT/CHOPPED 三态描述），**绿/紫双形态变种** | strings 943-955 行（三态描述）；anim xd_zuichunyan_green / _purple（+leaves_chop 砍伐帧） |
| XD_FANHUNSHU / XD_FANHUNSHUVINE / XD_FHG / XD_FANHUNGUOPU | 返魂树 / 返魂果藤 / 返魂果 / 返魂果脯 | 复活功能树："只要神魂仍在，此处皆可重塑肉身"；果藤两天垂一支 | strings 865-872 行；anim xd_fanhunshu |
| XD_CHENPINGAN_MUME / _SAPLING / XD_CHENPINGAN_MUMEFRUIT | 青梅树（树苗）/ 青梅 | 陈平安角色树：青梅→青梅酒/青梅排骨（食物链） | strings 450-463 行；anim xd_chenpingan_mume / mumefruit / mumeleaf（树/果/叶三 zip 拆分） |
| XD_NPXSZ | 涅槃血髓竹 | 灵竹（焚尽留玉骨，涅槃化血髓） | strings 1460-1461 行（无独立 prefab 名，推断并入批量 prefab 注册，**证据等级：低**） |
| XD_TREE_DF / _YXS / _XHS / _YLS / _YHS / _LS | 丹枫 / 银杏 / 杏花树 / 烟柳树 / 樱花树 / 蓝杉 | 6 种观赏灵树（樱花树明确"灵石蕴养"），装饰+木材来源 | strings 566-588 行；anim xd_trees（单 zip 含 6 树帧）+ 6 个 _skins_* 皮肤 zip |

#### 6.1.3 灵花（12 种）

| 资产名 | 名称 | 推断功能 | 证据 |
|---|---|---|---|
| XD_FLOWER_SFR/ZYH/BMG/LL/YL/MD/BH/PGY/MLH | 水芙蓉/朝阳花/白玫瑰/铃兰/幽兰/牡丹/百合/蒲公英/木梨花 | 9 种观赏花（纯美术+蜜蜂相关），各有皮肤 | strings 527-562 行；anim xd_flowers（单 zip 9 花）+ 5 个 skins zip（bh_ya/bmg_srlg/md_rjfg/sfr_fr/sfr_xy） |
| XD_LUOSHEN_HUA + XD_LUOSHEN_HUAZHONG | 洛神花（洛神花种） | 洛神核心植物：种下后**需以掌天瓶催开**；洛神引/归蕊动作=传送回花旁 | strings 1506-1511 行（"种下后需以掌天瓶催开花灵"）；anim xd_luoshen_hua / huazhong / yin / huayin |
| XD_LUOSHEN_LIFEFLOWER_BUILDER / _DEATHFLOWER_BUILDER | 生之花 / 灭之花 | 洛神双形态转化花 | strings 110-115 行 |
| XD_AYMG | 暗影玫瑰花 | 织影者元神寄宿的暗影花（掉落物） | strings 68-69 行 |

### 6.2 生长机制（动画阶段 + 组件）

**动画阶段证据（证据等级：高，anim/build 二进制内嵌符号实测）**：

1. **灵草种子→成株两阶段**：`xd_lingcao.zip` 的 anim.bin 含 12 个动画：`cyh / cyh_seed / dms / dms_seed / hsc / hsc_seed / lmg / lmg_seed / qfx / qfx_seed / yhh / yhh_seed` —— **6 味灵草共用一份动画文件，seed 与成株分帧**，种子与植株是明确的 2 阶段生长。
2. **田间植株的完整状态机**：`xd_plant_hsc.zip` 的 build.bin 符号：`soil01`（土块）、`plant`（成株）、`veggie_seed`（埋土种子）、`swap_body`（手持收获物）、`swap_body_rottenk`（**腐烂形态**）、`fx_wax_comp3`（蜡封/保鲜特效）、`fx_star_part`（**收获星光特效**）——对应"播种→生长→收获→腐烂→保鲜"完整生命周期。
3. **灵田/花盆双种植载体**：`xd_ylxq.zip` anim：`idle / idle_full / plant / shu8 / qipao / shuiliuk(水流) / snow`；`xd_huapen.zip` anim：`idle / idle1`。玉露仙畦有专门的 `plant`（种植）与水流动画，花盆只有两个 idle——花盆更简单，仙畦是主种植设施。
4. **果藤类**：返魂果藤（"两天会垂落一支"）、沙棠果藤（摘果）——藤蔓挂果模型。

**组件链推断（证据等级：中，daxsg_mod_path.txt 组件名）**：`xd_ylxq_grower`（玉露仙畦生长驱动）→ `xd_plant`（通用植物组件，服务端生长逻辑）→ `xd_pick_plant`（采摘动作）→ `xd_huapen_giver / xd_huapen_plant`（花盆种植）。配套建筑：XD_YLXC 玉露玄仓（灵草保鲜）、XD_YHSYZ 月华摄药枝（"可以直接收获灵草"，远程/自动收获）、XD_XCDF 星淬丹府（丹药品质提升）。

**未发现"年份灵草"系统**：strings 全文无"百年/千年/年份"字眼，动画也只有 seed/成株两态。年份成长大概率不存在，或被混淆代码内的时间倍率隐藏（**证据等级：低**，负向证据：文本与动画均无年份痕迹）。

### 6.3 特色岛屿/秘境（区域名 | 内容 | 证据）

#### 6.3.1 鲲鹏岛（核心世界级秘境：北冥鲲鹏之背）

- **内容**：一张 static_layout（`map/static_layouts/xd_kunpeng.lua`，加密）+ 3 种专属地皮（鲲鹏葱郁/灵脉/魔化）+ 组件 xd_kunpengstage（鲲鹏阶段）/ xd_kunpengspawner（鲲鹏生成）+ 2 张 UI（xd_kunpeng_ui1/2，2048x1024）+ xd_kunpeng_shadow 动画 + 紫云阁 NPC 驻留
- **证据**：TURF_XDTILE2 描述"**在鲲鹏脊背时**能凝实这一界中的灵力"（strings 842-843 行）；XD_ZYG_NPC"神魂似乎和鲲鹏有一些融和"（977 行）；紫云魔君 NPC 台词"以本君的手段也镇压不了这**遮天之鲲鹏**"（932 行）。三处文本互证 + noise_xdtile1-3 三张地块噪声图——鲲鹏背上生成的三地形大陆（**证据等级：中**，static_layout 加密，靠文本+噪声图交叉）

#### 6.3.2 紫云秘境（魔君主线副本链）

- **内容**：紫云阁（清修寒舍，xd_ziyunge）+ 紫云魔君 NPC（xd_zyg_npc）+ Boss 紫云魔君（xd_ziyunboss，4 段台词）+ 魔心（channeler）+ 异化的天机屋（xd_ziyun_house）+ 专属怪群（ziyunwarg/ziyunminions/ziyunjfsn/stalke_ziyun/deerclops_ziyun）+ 独立出口门（xd_door_exit_zyg）
- **证据**：strings 915-933 行 NPC 对话链（斩心魔→击败失控化身→重谢，5 段任务式流程）；916-924 行 Boss 台词表；door_exit 变体 zip 名（**证据等级：中**）

#### 6.3.3 返魂秘境（复活空间）

- **内容**：返魂树 + 返魂果藤 + 青玉案（石案）+ 明灯 + 独立出口门（xd_door_exit_fhs / _fhs_heng 横版）+ 配套道具链：返魂果→返魂果脯（食用）→返生香（"将彼岸的魂魄拉回肉体"）+ 复生祠台（重塑肉身）+ 替死返魂丹（死亡保境界重选人物）
- **证据**：strings 865-872 行（"只要神魂仍在，此处皆可重塑肉身"）、994-998 行；door_exit_fhs 动画 zip（**证据等级：中**）

#### 6.3.4 洞天类独立空间（门变体揭示至少 6 个秘境）

`xd_door_exit*` 系列 8 个动画 zip = **独立空间入口的强证据**（**证据等级：中**，zip 命名+对应 prefab/字符串）：

| 门 zip | 对应空间 | 关联资产 |
|---|---|---|
| xd_door_exit_fhs(_heng) | 返魂秘境 | 返魂树/复生祠台 |
| xd_door_exit_zyg | 紫云阁 | 紫云魔君 NPC 清修地 |
| xd_door_exit_tjw(_heng/_byj) | 天机屋（碧云居皮肤变体） | xd_tianjiwu 天机屋+令牌+卷轴（"云舒霞卷，内有乾坤"） |
| xd_door_exithyjd(_heng) | 混元金斗空间（云霄） | 混元金斗（空间法器）+ 9 个跃迁点 + 混元太虚跃迁台 |
| xd_door_exittnz(_heng) | 伏龙台/天逆珠空间（王麻子） | 天逆珠 + 伏龙台（巨龙盘踞成台） |
| xd_door_exit_stm | 未知秘境（STM） | 沙棠树皮肤 xd_shatangshu_skins_stm 同名缩写（**证据等级：低**） |

#### 6.3.5 角色专属秘境

- **洛神花境**：洛神花种→掌天瓶催开→洛神花；洛神引（回到洛神花附近）/归蕊动作（GUIRUI）= **以花为锚点的个人空间传送**；洛神诛（攻击性植株）+ 枯荣双生（KRSS）+ 花瓣建筑（绣墙/芳菲栅栏/锦门）——洛神角色的花系据点（**证据等级：中**，strings 101-131/1469-1504 行 + anim xd_luoshen_plant_front/back/vine 三件套藤蔓）
- **骷髅山白骨洞（石矶）**：XD_SJ_KLS"骷髅山白骨洞"（封神石矶道场）+ KLS 动作"法体遁入"——石矶的洞府型空间（**证据等级：中**）
- **青丘坊（灵狐村）**：XD_POG_HOUSE 青丘坊——灵狐栖身之所（青丘山典故），anim xd_pog_house（**证据等级：中**）
- **玩家洞府**：xd_playerhouse prefab + XD_ENTER_HOUSE 进入/离开动作 + xd_interiors 室内模块（**证据等级：中**）
- **抽奖机布局**：static_layouts/xd_choujiangjimap（灵石抽奖机的固定布局，地图上独立摆放区）（**证据等级：中**）

### 6.4 特色地形（tileset 细节 + 对 3.8 节的勘误）

#### 6.4.1 勘误：jungle.xml 实测无 XDTILE 元素（原 3.8 节推断不成立）

文件实测（**证据等级：高**）：
- `levels/tiles/jungle.xml`：元素名为 **01-48 数字编号**（带 variant a/b），**全文无 XDTILE 字样**（grep 全 mod xml 零命中）
- `levels/tiles/jungle.tex`：mod 自带 2048x1024 DXT5，解码 73% 为近白（#F8FCF8）——与原版 jungle tileset 一致（白色地皮图块）
- XML 内 Texture 引用 `data/DLC0002/levels/tiles/jungle.tex`（游戏原版相对路径）

**修正结论**：mod 的 jungle.tex 是原版副本（覆盖式加载），XDTILE 地皮**不是**在 jungle atlas 上追加元素，而是**换皮复用**：worldgen 用 3 张噪声图把 XDTILE 区域画成现有 tile 编号，地皮的特色视觉靠 `images/inventoryimages/turf_xdtile*.tex` 图标 + 地表装饰 + 小地图 mini 噪声图实现。地皮注册模块为 `scripts/main/tiles.lua`（加密）。

#### 6.4.2 地皮与噪声图完整映射（**证据等级：高**，文件实测）

| 地皮 | 名称 | turf 图标 | 世界生成噪声图 | mini 小地图噪声 |
|---|---|---|---|---|
| TURF_XDTILE1 | 鲲鹏葱郁地皮 | inventoryimages/turf_xdtile1.tex（128 方） | noise_xdtile1.tex（512 方灰度，avg 64） | mini_noise_xdtile1.tex（256 方） |
| TURF_XDTILE2 | 鲲鹏灵脉地皮 | turf_xdtile2.tex（128 方） | noise_xdtile2.tex（512 方，avg 75） | mini_noise_xdtile2.tex（256 方） |
| TURF_XDTILE3 | 鲲鹏魔化地皮 | turf_xdtile3.tex（128 方） | noise_xdtile3.tex（512 方，avg 36，最稀疏） | mini_noise_xdtile3.tex（256 方） |
| TURF_JINGWEITILE | 填海地皮 | turf_jingweitile.tex（64 方） | xd_jingwei_tile.tex（1024 方，avg 84，最密） | mini_xd_jingwei_tile.tex（256 方） |

噪声图数值差异（avg 36-84）控制各鲲鹏地块在地图上的覆盖率；填海地皮噪声 1024 方是普通地块噪声的两倍分辨率，配合"填海造陆"玩法（精卫角色改造海洋）。tileset 元素 01-48 即原版 jungle 全 tile 编号，XDTILE 运行时映射到其中若干编号（具体映射在混淆的 tiles.lua 内，**证据等级：低**）。

### 6.5 美术小节（tex 解码画风分析）

> 方法：KTEX 解码（DXT5/DXT1 转 RGBA）为 PNG 后按不透明像素统计色板/亮度/饱和度。解码样本存于 `references/mod-notes/art_samples/`（PNG 目录）。全 mod 植物/地形/建筑美术统一特征：**黑色硬描边 + 高饱和国风设色 + 暗底衬托亮部**。

#### 6.5.1 特色植物画风

- **灵草**（xd_lingcao.zip atlas 1024x512）：黑描边为主色（13%），主体高饱和蓝/青（23%）+ 红/橙（11%），亮白高光 #F8FCF8 点缀，整体亮度 0.22 的暗底衬托荧光感灵草；seed 帧与成株帧同图集。灵草=「暗底+黑描边+冷色荧光」，与丹药五行色（赤阳花偏红、雷鸣菇偏靛、霜寒草偏青）一一对应（**证据等级：中**）
- **仙树**（xd_trees.zip atlas **4096x4096 单张 4K**）：6 种树全塞一张 4K 图集（大型 mod 的图集集中策略）；红/橙 25%（丹枫/杏花）+ 绿/黄绿 12% + 赭红树干 #A03828/#C86848——工笔设色、明度 0.36
- **醉春烟双形态**：green/purple 两个 4K zip 分色打包，绿紫双色是修仙 mod 的"灵性/魔性"二元表达（**证据等级：中**）
- **灵花**（xd_flowers.zip 2048x1024）：9 花一图集，绿/黄绿 28% + 红/橙 21%，饱和 0.45（全植物最高）——花瓣用高饱和色+黑描边
- **洛神系**：洛神花/花种/花裀/藤蔓（front/back/vine 三张 1024x512）+ 花瓣建筑（绣墙/栅栏/锦门）——花系专属图集族

#### 6.5.2 岛屿/秘境/地形画风

- **鲲鹏地皮三色**（turf 图标 128 方，**证据等级：高**）：
  - 葱郁 XDTILE1：青绿湖蓝 (72,204,208) + 棕土 (96,76,56)，明亮像素 32%——生机感
  - 灵脉 XDTILE2：灰白岩脉 (112,124,128)，**饱和度 0.17 全 mod 最低**——石脉质感
  - 魔化 XDTILE3：深蓝紫 (48,56,88)/(40,52,80)，亮度 0.13 全 mod 最暗——阴森感
- **填海地皮**（64 方）：新绿草地 (104,172,96) + 土棕 (72,64,40)——新生成陆地的嫩绿感
- **鲲鹏 UI**（xd_kunpeng_ui1/2 各 2048x1024）：墨色底 (8,8,8) + 青绿 (176,204,168)/(136,204,200) + 米白 (248,248,216)——**水墨青绿山水画配色**，与鲲鹏（北冥巨鸟/海）题材吻合
- **秘境建筑**：天机屋青白 (173,205,216)、青丘坊暖棕金 (165,129,90)（狐村温暖感）、浣月池青白月光 (178,188,168)+(53,202,208)、祭坛**黑金朱红** (213,154,40)+(154,40,37) 饱和 0.58（全 mod 最高饱和——"劫难/机缘"的仪式感）
- **tileset 本体**（jungle.tex 2048x1024）：73% 近白，饱和 0.04——原版地皮图块，非 mod 定制

#### 6.5.3 美术结论

1. 植物：暗底 + 黑描边 + 高饱和荧光色，五行色系编码到植物配色（灵草辨识靠颜色，不需要看名字——游戏内快速采药的设计）
2. 岛屿/秘境：地皮用"青绿（生机）/灰白（灵脉）/暗紫（魔化）"三元色系区分鲲鹏三域；秘境建筑按角色主题配色（狐=暖金、祭坛=黑金朱红、天机=青白）
3. 图集组织：植物按族合并大图集（树 4K、花 2K、灵草 1K 三档），皮肤用独立 zip（_skins_*）；turf 图标单独 128 方小图集；UI 双 2K 图集
4. 对比原版 DST 植物（绿植高亮度 0.5+）：本 mod 植物亮度普遍 0.2-0.36、饱和 0.4-0.5——**暗色国风**，与修仙题材的"秘境幽光"气质一致

---

*章节 6 完（2026-08-11 二次深挖）。植物清单 29 种（灵草 6 + 仙树 11 + 灵花 12）；秘境 8+ 处；地皮 4 种；对 3.8 节 tileset 推断已勘误。*
