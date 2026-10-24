# DST Mod 深度分析笔记：地府（3774422345）

> 分析对象：`C:\Users\22308\Desktop\new\3774422345`（约 122MB，426 文件：168 lua / 254 tex / 1 xml / 2 fev+fsb / 2 manifest）
> 主题：十殿阎罗 / 生死簿 / 范无忌 / 黑白无常 / 孟婆 / 秦广王 boss——东方地府恐怖题材大型 DST mod
> 版本：1.0.18（作者：范无忌，代码：Chilla）

---

## 1. Mod 全貌

### 1.1 基本信息（modinfo.lua，明文）

- **名字**：地府（`name = "地府"`）
- **版本**：1.0.18，`api_version = 10`，DLC 全兼容（dont_starve / reign_of_giants / dst）
- **强制全端加载**：`all_clients_require_mod = true`、`client_only_mod = false`（有 RPC 主从逻辑）
- **更新日志透露的玩法**（modinfo.lua 描述）：
  - 范无忌 boss（5 万血，脱战清飞剑数量）
  - 生死簿（带铃铛音效）、七魂刀（普攻给范无忌加消失时间）
  - 秦广王（去重死亡动画）、陆之道（新增动画）
  - 石压地狱行刑者（击杀给玩家回血）
  - 丹炉升级（可堆叠武器）
- **配置**：`configuration_options = {}` 为空；但定义了一整套键位枚举（KEY_A 到 PAGEUP/1-9，`AddorGetConfig` 辅助函数）——**预留给法宝/技能快捷键，当前未启用**

### 1.2 文件结构

```
3774422345/
├── modmain.lua          141,313B  chilla 加密（VM 字节码）
├── modworldgenmain.lua  141,906B  chilla 加密（世界生成入口）
├── modmain0.lua          636B     chilla 加密（二进制）
├── modworldgenmain0.lua 7,511B    chilla 加密（二进制）
├── modicon.tex          1.4MB     1024x1024 DXT5 图集（mod 图标）
├── modicon.xml           176B     标准 DST atlas（1 element）
├── chilla/_s_/art/      254 个混淆路径 .tex —— 全部美术资源
├── key_modules_for_thigh_bone/  大腿骨动画模块（加密）
├── main/                15 个 .lua（明文只有 difu_gotodifu_ritual.lua 18B 是真尺寸，其余加密）
├── scripts/             168 个 .lua（prefabs/brains/stategraphs/static_layouts，全加密）
└── yr_fn/               作者原始开发目录（main.lua / test.lua / recipe / world_fn/cave / world_fn/difu_teleport_targets，全加密）
```

### 1.3 加密体系（Chilla 商业保护，证据等级：A——已实际逆向）

**证据等级标注**：A = 已实际逆向验证；B = 从二进制结构推断；C = 从命名/行为推断。

| 层次 | 内容 | 证据 |
|---|---|---|
| modmain/modworldgenmain | 明文 loader（0-30794B）+ 混淆段（30794B 起） | A |
| 混淆段 | 流密码解密循环 + 水印假代码 + `return({[1160626]=...})` VM 解释器 | A |
| scripts/*.lua | 全部为 `00` 开头高熵二进制（独立文件加密，密钥在 VM 内） | A |
| chilla/_s_/art/*.tex | KTEX 头 + ZIP 条目容器（raw deflate，**未加密**，已完整提取） | A |

**chilla 流密码（modmain 头部解密器，已完全逆向）**：
- 48 位 LCG：`v=(v*25+14021572225547)%35184372088832`
- 流生成：`x=(x*220)%257` + `T()`，U 表 = `{O,e,u,A}`，`table.remove(U)` 取末位
- 解密循环：`O=((byte+T()+O)%256)`（异或语义由 256 取模等价）
- m 表恒等（`m[k]=char(k-1)`，`math.random` 乱序是诱饵）
- 自定义 base64：`u=u+A*64^(3-U)`，浮点除法 floor 语义（`b0=int(u/65536)` 等）

**chilla VM**（决定放弃逆）：真实逻辑编译为字节码，由 25 参数匿名函数解释执行：
`function(V,R,z,X,P,O,e,A,m,g,v,N,u,a,x,G,W,M,q,T,n,p,U)`。水印：`"quest to decrypt, deobfuscate..."`、`"(c) Chilla - All Rights Reserved. 未经授权请勿反编译/篡改"`。假代码 `if(X*X)%X~=0 then ... end` 永不执行。

### 1.4 scripts/ 加密文件清单（文件名即信息，证据等级：B/C）

- **prefabs**（80+，命名规则 `difu_` 前缀）：difu_danlu（丹炉）、difu_boss_fwj（范无忌）、difu_boss_qgw（秦广王）、difu_worm_boss（虫boss）、difu_mengpo（孟婆）、difu_hehua（荷花）、difu_shanshi（山石）、difu_yujian（御剑）、difu_fabao（法宝）、difu_dundi（遁地）、difu_dici（地刺）、difu_futou（斧头）、difu_jianzhi（剪纸）、difu_qizi（旗子）、difu_scj、difu_caw、difu_csm、difu_xiao、difu_ld、difu_lzd_wind（雷泽殿·风）等
- **brains**（16）、**stategraphs**（15）：boss 行为树/状态机
- **static_layouts**（9）：difu_yd（阎罗殿）、difu_sydy（十阎罗殿）、difu_dsdy、difu_yls、difu_ccs、difu_dazz、difu_fes、difu_kd、difu_sss —— 9 个地府建筑布局

### 1.5 世界生成入口（证据等级：B）

- `modworldgenmain.lua` 与 `modworldgenmain0.lua` 均加密（`00` 开头）
- `yr_fn/world_fn/cave.lua`（加密，11489B）：**洞穴世界逻辑**
- `yr_fn/world_fn/difu_teleport_targets.lua`（加密，1011B）：**地府传送目标表**——小文件即一张传送点列表，说明地府通过传送点连接主世界/洞穴
- `main/difu_gotodifu_ritual.lua`：18B 明文——**前往地府的仪式**（短文件=简单仪式触发）
- `main/difu_migration.lua`（加密）：玩家迁移逻辑

---

## 2. 地府特色专题（世界 / 空间 / 地图设计）★核心

### 2.1 地府世界架构（证据等级：B/C，从文件结构与命名推断）

```
主世界 (Overworld)
  └─ 仪式入口 (difu_gotodifu_ritual) → 地府世界
洞穴 (Cave, yr_fn/world_fn/cave.lua)
  └─ 通过 difu_teleport_targets 与地府互通
地府世界
  ├─ 九大建筑布局 static_layouts:
  │    difu_yd      阎罗殿（核心主殿）
  │    difu_sydy    十阎罗殿（十殿体系）
  │    difu_dsdy    大石压狱？
  │    difu_yls     阎罗/夜叉?
  │    difu_ccs     城池/城隍?
  │    difu_dazz    大案牍?
  │    difu_fes     佛殿?
  │    difu_kd      苦殿?
  │    difu_sss     三生石?
  └─ 传送点系统 (difu_teleport_targets)
```

### 2.2 地府建筑体系（美术资产实证，证据等级：A——build 符号已提取）

从 131 个 `build.bin`（BILD v6）符号名提取，地府建筑资产完整：

| 建筑 | build 符号 | 纹理 | 实测特征 |
|---|---|---|---|
| 鬼门关（牌坊） | guimenguan | 8j0tg1ic.tex (4096²) + owsoid.tex (4096x2048) | 5 部件：2016x1344 横梁 + 1032x2384 门柱 + **2×1144x1464 对称门扇**，全黑+灰 |
| 城墙 | chengqiang | 50iny8l.tex (**8192²**) | 12 部件：8160x5952 城体（黑 68%+红 17%）+ 2688x1728 城门（浅灰 46%+红 32%）——**红黑中式城墙** |
| 丹炉 | danlu | fmyw6q7iy.tex (2048²) | 2×944x1012 对称炉体（黑 67%）+ 132x132 **红焰**（红 40%） |
| 三生石 | sanshengshi | 0oeeyizhlu.tex (1024²) | 618x870 灰石（灰 71%+黑） |
| 奈何桥碑 | naiheqiaobei | vrctgi5.tex (512²) | 81x94 浅色碑（lum 120 偏亮） |
| 孽镜台 | niejingtai | （无 tex 引用） | — |
| 迷魂殿 | mihundian | （无 tex 引用） | — |
| 雕像 | diaoxiang | 4z4tvuo.tex (4096²) | 2312x2824 大像（黑 52%+青/紫 22%）+ 4 个 112x88 红块（供品/烛台） |
| 枯树 | kushu | 9xnkv9fi.tex (4096x2048) | 8 部件，**100% 纯黑剪影树**（1288x688/1032x1376/1248x1120） |
| 石灯 | shideng | 1biqo3kv9.tex (512²) | 72x92 |
| 灯笼/灯 | deng | 7up6zohgo5.tex (512²) | 48x109 竖长（灯柱），warm 69% |
| 八角楼 | bajiaolou | （无 tex 引用） | 楼阁建筑 |
| 房子 | fangzi | 0nnytg3i.tex (1024²) | 96x77 |
| 亭子 | pavilion | 9rjln95.tex + 8wu7p0.tex | 76x55 + 125x74，warm 59-62% |
| 大山 | dashan/dashan_2 | 8vjv96.tex + z8gwc342.tex | 87x107 / 93x102，warm 88-89%（土山暖色） |
| 第一殿/第一使 | diyidian / diyushi | 8ho7zflhs.tex (4096²) / bxdynoyf47.tex | 4 部件 79x121 / 54x66 |

### 2.3 地府角色体系（美术资产实证）

| 角色 | build 符号 | 纹理 | 结构实测 |
|---|---|---|---|
| **秦广王（boss）** | difu_boss_qgw | 5bcfla.tex (**8192²**) | 157 部件，**LUM=5 近全黑**；部件 512-640² 为主；#01 640x1008 含白 22%（面/面具）；散落蓝/青细节。**黑色剪影系 boss** |
| 白无常 | baiwuchang + swap_bai | dce11os61.tex (2048x1024) | 165 部件：**10 帧白袍摆**（164x344，白 45%+黑 32%）+ 156x220 黄/褐高帽 + 80x152 橙/棕手 |
| 黑无常 | heiwuchang + swap_hei | ofqmlk2r.tex (2048x1024) | 同构：10 帧**黑/灰袍摆**（184x336）+ 黄/褐帽 + 橙/棕手 |
| 孟婆 | difu_mengpo + swap_mengpo | 95zaqzahqi.tex (2048x1024) | 170 部件：10 帧袍摆（黑 59%/白 31% 混合）+ 156x220 黄/褐头 + 60x204 橙/棕手臂 |
| 马面 | mamian | 5hor68x.tex (2048x1024) | 88 部件：袍帧黑 96% + 224x224 白/黑头 + 104x192 黑长条（马蹄/兵器） |
| 崔玨（判官） | cuijue + swap_cuijue + images_cuijue | d9w70zqu.tex (2048²) | 44 部件，LUM 48 |
| 魏征（判官） | images_weizheng + swap_weizheng | lwefobl90b.tex (256x512) | 人像立绘 48x133，warm 69% |
| 钟馗 | images_zhongkui + swap_zhongkui | fehi2knul.tex (256x512) | 人像立绘 52x136，warm 70% |
| 陆之道 | luzhidao + images_luzhidao + swap_luzhidao | v09p6p.tex (2048²) | 46 部件，LUM 66 |
| 白无常/黑无常/孟婆/崔玨立绘 | images_bai / images_hei / images_mengpo / images_cuijue | 256x512 竖版 | **立绘 = 竖长 1:2 构图**（人像全身像） |
| 骷髅大兵 | kuloudabing | 0g11xvmwh.tex (4096²) | 142 部件全黑+浅灰（骨白） |
| 烈风马/马 | horse_build + horse_action + horse_liefeng | fc5qcavk.tex (2048²) + sqtcarxzv.tex (4096²) | 60 部件/57 部件 |
| 鬼（动作） | difu_ghost_action / ghost_expand_build | yweevhv0.tex (2048²) | 20 部件，青灰（冷色鬼魂） |
| 龙/虫 boss | difu_worm_boss（prefab 名） | — | — |

### 2.4 法宝 / 武器体系

| 武器 | build 符号 | 纹理 | 特征 |
|---|---|---|---|
| 七魂刀 | （fwj_sword 系列） | zs0j7c8.tex (128x512) | **1:4 竖长刀身**（71x320） |
| 驱魔剑 | exorcist_sword | bzxsyca.tex (128x512) | 69x386，warm 63% |
| 判官笔 | cj_bi（崔玨笔）+ swap_cj_bi | 1heooc82.tex (256x128) | 88x32 横长 |
| 黑无常枪 | hwc_gun + swap_hwc_gun | 0hyfqj.tex (128x512) | 57x284 |
| 白无常旗 | bwc_qi + swap_bwc_qi | gh22l01jf.tex (256x512) | 59x136 |
| 地府斧头 | difu_futou + swap_futou | 0a1txt4.tex (256x512) | 108x194 |
| 御剑 | difu_yujian | zowbea.tex (512x128) | 96x17 横长（剑身横置） |
| 锁链/索 | suo | jnvkwx19qa.tex (512x**4096**) | **67x604 竖长锁链** |
| 飞剑（法宝） | difu_fb_lxj + difu_fb_lxj_attack | gtqmla.tex + ik42al8mz.tex | 64x231 竖长 |
| 法宝·伞 | difu_fb_san | gx3yrv2u.tex (2048²) | **红伞：RED 50%** |
| 法宝·扇 | difu_fb_ssb | aakhgvglz.tex | 13x27 |
| 法宝·宝剑/棍 | difu_fb_bgj / difu_fb_san 系列 | — | — |
| 地府锤 | swap_difu_hammer | z3tj0e6.tex (1024x512) | 7 部件 |
| 大剑 | dajian | （无 tex） | — |
| 标枪 | speargun + swap_speargun | zd1c1kat.tex (1024²) | 17 部件 |
| 影子武器 | shadow_weapon_thigh_bone（大腿骨阴影武器） | bz014d.tex | 66x23 横长 |

### 2.5 Boss 技能动画体系（ANIM v4 符号，证据等级：A）

40 个 anim 集，可读符号拼出 **boss 技能树**：

- **陨石**：`meteor_charge`（陨石蓄力）+ `meteorground_loop`（陨石落地循环）——范无忌/秦广王召唤陨石
- **地刺**：`dici_loop`（地刺循环）+ `dici_pre`（前摇）+ `dici_pst`（后摇）
- **遁地**：`dundi` + `dundi_action`
- **飞剑**：`fz_loop`（飞剑循环）+ `fz_pre` + `jian_pst`（剑后摇）+ `yujian`（御剑 line+idle）
- **连击**：`lj_atk1`（连击攻击1）+ `lianzi2`（链子/连招2）
- **烈风**：`lefeng_pre`（烈风马前摇）——雷泽殿·风（difu_lzd_wind）
- **通用**：`idle` / `idle_loop` / `day_idle` / `attack` / `death` / `dead_fx` / `broken` / `spawn_pre` / `hou_pre` / `charge_loop` / `fly` / `follow` / `customanim` / `swap` / `BUILD_PLAYER_swap`（玩家手持）
- **奇怪命名**：`CEObS`、`fff`、`XY1` 等 3 字符随机串——**anim 符号本身被混淆**（证据等级：A，ANIM v4 内符号名就是随机串）

### 2.6 氛围营造手法（实测总结）

1. **全黑剪影**：boss（秦广王 LUM=5）与枯树（100% 黑）——DST 恐怖系常用"纯黑剪影+彩色点缀"
2. **红黑双色**：城墙（黑 68%+红 17%）、枫树（红 40%+黑 31%）——地府标志性配色
3. **青色冷光**：鬼（青灰）、雕像（青/紫 22%）、秦广王蓝/青细节——鬼火冷色
4. **巨型图集**：8192² 图集（秦广王、城墙、sm_wx_boss）——高分辨率细节
5. **多帧袍摆**：角色 10 帧行走袍摆（160-200px 宽）——衣袂飘飘的东方仙侠感

---

## 3. 美术风格（KTEX 解码实测）★核心交付

### 3.1 格式破解（证据等级：A）

**纯纹理**（115 个文件，chilla/_s_/art/）：
```
"KTEX"(4B) + format u32 LE + mip 头 ×N (各 10B: w u16 LE, h u16 LE, pitch u16 LE, size u32 LE) + 连续 DXT 数据
format 低字节: 0x20 = DXT5 (1B/像素), 0x00 = DXT1 (0.5B/像素)
mip0 尺寸 = 4096² (巨型 atlas) / 2048² / 1024² / 512² / 64² (图标) / 小文件 (<200B = 空纹理)
```
- 注意：**与标准 DST tex 的差异**——w/h 为 LE u16（解码工具 `dst_tex_analyze.py` 的假设需调整为 LE；实际 Klei 原版 tex 相同布局，只是 chilla 打包了大图集）
- 例证：1024² 全 mip 链（1024→1，11 级）文件大小精确 = 8 + 110 + 1398120 = 1398238 ≈ 实际 1398246 ✓

**容器纹理**（138 个文件）：
```
KTEX 头（伪 mip 链，声明数据量是实际 10 倍，用于校验）
+ ZIP 条目流:
  "PK\x03\x04" + ver u16 + flags u16 + method u16(8=deflate) + 4B + crc u32
  + csize u32 + usize u32 + namelen u16 + extralen u16 + 文件名 + RAW DEFLATE 数据
条目: anim.bin (ANIM v4) / build.bin (BILD v6) / *.tex (混淆名, 标准 KTEX 纹理)
```
- **重要**：raw deflate（无 zlib 头），`zlib.decompress(data, -15)` 直接解
- 421 个条目：138 anim.bin + 135 build.bin + 148 tex
- **zip 头时间字段为固定魔数** `af 0c d1 5c`（处处相同，非真实时间戳）

### 3.2 整体色板统计（批量 32+ 图集实测）

| 指标 | 数值 | 解读 |
|---|---|---|
| 全图集平均亮度 | LUM 30-60（暗） | 恐怖地府基调 |
| 最低亮度 | 秦广王 LUM=5 / 枯树 LUM=5 / 孟婆立绘 LUM=6 | 纯黑剪影 |
| 饱和度高区 | 枫树 0.75 / 荷花 0.52 / 法宝伞 0.43-0.53 | 红色点缀物 |
| 暖色占比高 | 枫树 93% / 丹炉 73% / 大山 88-89% / 立绘 69-72% | 红/橙/棕暖色系 |
| 冷色占比高 | 秦广王蓝青 / 鬼魂青灰 / 雕像青紫 22% | 鬼火冷光 |
| 主色板 | `#101010`(黑) `#103030`(暗青) `#700000`(暗红) `#503030`(暗红棕) `#305050`(青灰) | 黑+暗红+青三系 |

**modicon 图标**：1024² 图集，element uv (0.0005, 0.3687)-(0.6265, 0.9995) = 641x646px；色板 `#000000` 15.4% + `#700000` 暗红 4.9% + `#407080` 青灰 3.6%——**黑底暗红青灰的地府场景图**（含建筑+人形+装饰多元素）

### 3.3 角色美术结构（部件级实测）

以白无常（dce11os61.tex 2048x1024）为例——**DST 角色标准组件化 + 东方元素**：

```
10 帧袍摆（164x344 竖条, 白 45%+黑 32%）——行走动画循环
   │
   ├─ 2 帧暗袍（黑 62%+白 34%）—— 侧面/背面帧
   ├─ 黄/褐高帽（156x220, 43% 黄褐）—— 无常标志性高帽
   ├─ 浅灰帽饰（196x92 长条 + 116x112）
   ├─ 橙/棕手臂（60-80x152-204 竖条）
   ├─ 手（88x108 ×4）
   └─ 头部（64x84 白）
```

**角色配色规律**：
- 白无常 = 白袍+黄帽；黑无常 = 黑/灰袍+黄帽；孟婆 = 黑白混合袍+黄褐头；马面 = 黑袍+白面
- 所有角色 **黄/褐(43%)+浅灰(39%)** 的帽/头配色一致——**共享美术模板**（同一作者手笔）
- 皮肤/手统一 **橙/棕（40% 左右）**

### 3.4 建筑美术结构（部件级实测）

**鬼门关**（8j0tg1ic.tex 4096²，5 部件）：
- 2016x1344 顶部横梁（黑 55%）+ 1032x2384 左右门柱 + 2×1144x1464 对称门扇 + 1200x1280 基座
- **完全对称的中式牌坊结构**

**城墙**（50iny8l.tex 8192²，12 部件）：
- 8160x5952 主体城体（黑 68%+红 17%）+ 2688x1728 城门（浅灰 46%+红 32%）+ 多个 400-600² 塔楼/箭楼小块
- **红黑城墙 = 阴曹地府城墙的经典配色**

**丹炉**（fmyw6q7iy.tex 2048²，3 部件）：2×944x1012 对称炉身（黑）+ 132x132 红焰——**单火苗点缀**

### 3.5 画风总结

1. **配色**：黑（50-70%）+ 暗红（17-32%）+ 青灰（10-22%）三系；点缀亮红（枫叶/火焰/红伞）与白（无常袍/骨白）
2. **明暗**：整体低亮（LUM<60），boss 与剪影物近纯黑（LUM≤5）
3. **描边**：alpha 边缘跳变比 0.004-0.138（低）——**实心色块+硬边，非细描边风**；靠剪影和色块对比，非线条
4. **构图**：角色 10 帧竖条动画帧；武器 1:4-1:8 竖长；立绘 1:2 竖版；建筑完全对称
5. **恐怖手法**：纯黑剪影（秦广王/枯树/鬼门关）+ 冷色鬼火（青蓝）+ 红点缀（血/火/枫）

---

## 4. 特色地形 / 植物

| 资产 | build | 纹理 | 实测 |
|---|---|---|---|
| 枫树（红枫） | fengshu | l0c2vfke.tex (2048²) + sdylyy.tex | 14 部件全红（RED 40-49%）+黑树干——**地府红叶树**，8 棵树冠 124-732² 多尺寸变体 |
| 枯树（黑剪影） | kushu | 9xnkv9fi.tex (4096x2048) | 8 部件 100% 纯黑——**剪影枯树**，大中小 3 档（1288x688 / 1032x1376 / 432x376） |
| 荷花 | hehua | 5hugfwht.tex (2048x1024) | 4 部件，LUM 70 / SAT 0.52（粉红荷花） |
| 地刺 | difu_dici | 4pa34udv.tex (4096²) | 11 部件，竖长 84x**1344**（尖刺），配合 `dici_loop/dici_pre/dici_pst` 技能动画 |
| 大山 | dashan / dashan_2 | 8vjv96.tex / z8gwc342.tex (1024²) | warm 88-89%（土色山体），两个变体 |
| 城墙 | chengqiang | 50iny8l.tex (8192²) | 红黑中式城墙（见 3.4） |
| 强化石 | qianghuashi | awm12ek.tex (1024x512) | 5 部件 19x27（小石堆） |
| 石头 | shanshi / difu_shanshi | hldi7z2z.tex (2048x1024) | 2 部件 41x51 |
| 尘土/遁地 | difu_dundi + dundi_action | u0dvdy.tex (2048²) | 18 部件，与 dundi 技能联动 |

---

## 5. 核心设计模式（lua 侧为推断，美术侧为实证）

> 由于 lua 全加密（VM），以下模式从**文件名 + 美术资产 + 更新日志**交叉推断（证据等级：B/C），但结构本身有强证据。

### 5.1 Boss 设计模式（difu_boss_fwj 范无忌 / difu_boss_qgw 秦广王）

- **技能动画独立 prefab**：`meteor_charge`（陨石）、`dici_*`（地刺）、`dundi`（遁地）、`fz_*`（飞剑）——技能作为独立 anim + 独立 prefab（difu_dici、difu_dundi、difu_yujian）
- **多阶段/脱战重置**：更新日志"范无忌血量下调 5w，脱战后清空飞剑数量"
- **连击联动**：`lj_atk1`、`lianzi2`——普通攻击累加（"七魂刀每普攻一下增加范无忌消失时间 1 秒"）
- **玩家增益**："石压地狱行刑者参与击杀的玩家也会给予血量"

### 5.2 世界观系统（生死簿 / 法宝 / 七魂刀）

- **生死簿**：独立音效（铃铛）——modinfo 更新日志
- **法宝系统**（difu_fabao + difu_fb_* 5 件套）：伞（红）、扇、剑、棍、攻击形态（difu_fb_lxj_attack）
- **武器 swap 系统**：`swap_*` 17 个 build（swap_bai / swap_hei / swap_mengpo / swap_cuijue / swap_zhongkui / swap_weizheng / swap_futou / swap_speargun / swap_wuqi 等）——**DST 经典手持武器替换模式**，配合 `BUILD_PLAYER_swap` 动画
- **判官阵营**：崔玨（判官笔 cj_bi）、魏征、钟馗、陆之道、黑白无常、马面、孟婆——角色+立绘+swap 三件套

### 5.3 世界生成模式

- `modworldgenmain` + `yr_fn/world_fn/cave.lua`：地府作为**独立世界层**（洞穴文件单独存在）
- `difu_teleport_targets`：传送点表驱动（小文件）
- 9 个 `static_layouts`：**每殿一个静态布局**（阎罗殿 difu_yd、十阎罗殿 difu_sydy 等）——建筑群用 static_layout 摆放大场景
- `main/difu_migration`：跨世界迁移玩家数据（加密）

### 5.4 RPC 模式（main/rpc_client.lua + rpc_server.lua）

- 客户端/服务端分离的 RPC 文件——多人同步（法宝、boss 血量、生死簿）

---

## 6. 亮点技巧

1. **KTEX 容器化资源打包**（chilla 手法）：把 anim.bin/build.bin/tex 全部塞进"伪 tex"文件，扩展名伪装 + 路径混淆（4 层随机目录 `4/z/y/3/w/b/l/.../0.tex`），文件名混淆（`50iny8l.tex`）——**但数据本身 raw deflate 未加密**，PK 头完整可提取
2. **伪 mip 链**：容器头部声明 14 级 mip（声称数据量 2 亿字节）——**防分析者读 mip 链**（数据区实际是 ZIP）
3. **格式魔数伪装**：ZIP local header 的 time/date 字段固定 `af 0c d1 5c`——不是真时间戳
4. **VM 级混淆**（chilla 商业保护）：Lua 源码 → 字节码 → 25 参数 VM 解释器，附水印字符串和永不执行的假代码块——**目前最难破解的 DST mod 保护**（证据等级：A，完整逆向了 loader 和流密码）
5. **美术规模**：单 boss 图集 8192²（6700 万像素），全套 148 纹理 + 138 动画 + 135 build——**约等于一个小型商业游戏的美术量**
6. **动画符号混淆**：ANIM v4 里符号名混入 `CEObS/fff/XY1` 随机串——即使解出 anim.bin 也难以直接对号入座
7. **开发目录残留**：`yr_fn/`（阎罗 之 fn？）保留作者原始工程结构（main/test/recipe/world_fn）——**加密工具只处理了发布目录，`yr_fn` 目录名泄露了开发组织方式**

---

## 7. 可复用模板（可直接抄）

### 7.1 KTEX 纹理解码（Python，已验证）

```python
import struct, zlib

def parse_tex(d):
    """KTEX: magic + fmt u32 + mip头(10B)*N + 数据"""
    if len(d) < 18 or d[:4] != b'KTEX':
        return None
    fmt = struct.unpack_from('<I', d, 4)[0]
    mips, off = [], 8
    while off + 10 <= len(d):
        w, h = struct.unpack_from('<HH', d, off)      # LE u16!
        size = struct.unpack_from('<I', d, off + 6)[0]
        if not w or not h:
            break
        mips.append((w, h, size))
        off += 10
    return fmt, mips, 8 + 10 * len(mips)              # 数据起点

def dxt5_block(b):
    a0, a1 = b[0], b[1]
    al = [a0, a1]
    if a0 > a1:
        al += [(6*a0+a1)//7, (5*a0+2*a1)//7, (4*a0+3*a1)//7,
               (3*a0+4*a1)//7, (2*a0+5*a1)//7, (a0+6*a1)//7]
    else:
        al += [(4*a0+a1)//5, (3*a0+2*a1)//5, (2*a0+3*a1)//5,
               (a0+4*a1)//5, 0, 255]
    ai = int.from_bytes(b[2:8], "little")
    c0, c1 = struct.unpack_from('<HH', b, 8)
    r0, g0, b0 = ((c0 >> 11) & 31) << 3, ((c0 >> 5) & 63) << 2, (c0 & 31) << 3
    r1, g1, b1 = ((c1 >> 11) & 31) << 3, ((c1 >> 5) & 63) << 2, (c1 & 31) << 3
    rgb = [(r0, g0, b0), (r1, g1, b1),
           ((2*r0+r1)//3, (2*g0+g1)//3, (2*b0+b1)//3),
           ((r0+2*r1)//3, (g0+2*g1)//3, (b0+2*b1)//3)]
    idx = int.from_bytes(b[12:16], "little")
    return [(rgb[(idx >> (2*i)) & 3][0], rgb[(idx >> (2*i)) & 3][1],
             rgb[(idx >> (2*i)) & 3][2], al[(ai >> (3*i)) & 7]) for i in range(16)]

def decode_mip(data, w, h):
    """DXT5 解码 mip, 返回 RGBA 字节串"""
    bw, bh = (w + 3) // 4, (h + 3) // 4
    out = bytearray(w * h * 4)
    for by in range(bh):
        for bx in range(bw):
            px = dxt5_block(data[(by*bw+bx)*16:(by*bw+bx+1)*16])
            for j in range(4):
                for i in range(4):
                    x, y = bx*4+i, by*4+j
                    if x < w and y < h:
                        out[(y*w+x)*4:(y*w+x)*4+4] = bytes(px[j*4+i])
    return bytes(out)
```

### 7.2 容器 tex 提取（Python，已验证——地府 mod 全部美术资源即由此提取）

```python
import zlib, struct
from pathlib import Path

def extract_entries(tex_path, start=128):
    """chilla 容器: KTEX 头后嵌入 ZIP-like 条目 (raw deflate)"""
    d = Path(tex_path).read_bytes()
    entries, pos = [], start
    while pos + 30 <= len(d):
        if d[pos:pos+4] != b'PK\x03\x04':
            break
        namelen  = struct.unpack_from('<H', d, pos + 26)[0]
        extralen = struct.unpack_from('<H', d, pos + 28)[0]
        csize    = struct.unpack_from('<I', d, pos + 18)[0]
        usize    = struct.unpack_from('<I', d, pos + 22)[0]
        name = d[pos+30:pos+30+namelen].decode('utf-8', 'replace')
        data_start = pos + 30 + namelen + extralen
        raw = d[data_start:data_start + csize]
        dec = zlib.decompressobj(-15)               # raw deflate!
        out = dec.decompress(raw, usize)
        consumed = csize - len(dec.unconsumed_tail)
        entries.append((name, out))
        pos = data_start + consumed                  # 精确推进
    return entries   # [('anim.bin', bytes), ('build.bin', bytes), ('xxx.tex', bytes)]
```

### 7.3 BILD v6 / ANIM v4 符号提取

```python
import re
# build.bin: 正则扫 ASCII 符号名 + .tex 引用
syms = re.findall(rb'[A-Za-z_][A-Za-z0-9_.]{2,59}', build_bin)
build_name = next(s for s in syms if not s.startswith(b'BILD') and b'.tex' not in s and not s.isdigit())
tex_refs  = [s for s in syms if s.endswith(b'.tex')]
# anim.bin: 同样正则扫动画符号 (ANIM v4)
```

### 7.4 图集部件级分析（连通域 + 色板，判断角色/建筑结构）

```python
def connected_components(px, w, h, min_size=20):
    """px: [(r,g,b,a)] 列表; 返回 [(minx,miny,maxx,maxy,cells)] 按面积降序"""
    visited = [False] * (w * h)
    comps = []
    for sy in range(h):
        for sx in range(w):
            i = sy * w + sx
            if visited[i] or px[i][3] < 40:
                continue
            stack, cells = [i], 0
            visited[i] = True
            minx = miny = 10**9; maxx = maxy = -1
            while stack:
                ci = stack.pop(); cells += 1
                cx, cy = ci % w, ci // w
                minx, maxx = min(minx, cx), max(maxx, cx)
                miny, maxy = min(miny, cy), max(maxy, cy)
                for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
                    nx, ny = cx+dx, cy+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        ni = ny*w+nx
                        if not visited[ni] and px[ni][3] >= 40:
                            visited[ni] = True; stack.append(ni)
            if cells >= min_size:
                comps.append((minx, miny, maxx+1, maxy+1, cells))
    return sorted(comps, key=lambda c: -c[4])
# 用法: 白无常图集 → 10帧白袍(164x344) + 黄帽(156x220) + 橙棕手(80x152) ...
```

### 7.5 一键统计图集画风（批量对比）

```python
import collections
def atlas_stats(dec, w, h):
    px = [dec[i*4:(i+1)*4] for i in range(w*h)]
    vis = [p for p in px if p[3] > 8]
    lum = sum(0.299*p[0]+0.587*p[1]+0.114*p[2] for p in vis) / len(vis)
    sat = [ (max(p)-min(p))/max(p) for p in vis]  # 简化: 通道差/最大
    warm = sum(1 for p in vis if p[0] > p[2]) / len(vis)
    quant = collections.Counter((p[0]>>5, p[1]>>5, p[2]>>5) for p in vis)
    return {'LUM': lum, 'SAT': sum(sat)/len(sat), 'WARM': warm, 'PALETTE': quant.most_common(6)}
# 判读: LUM<10 = 纯黑剪影; SAT>0.5 = 高饱和点缀; WARM>0.6 = 暖色系
```

---

## 附：分析成果统计

- **文件覆盖**：426 文件全部浏览；254 tex 全部解析（115 纯纹理 + 138 容器 + 1 modicon）；421 个容器条目全部提取；131 build / 40 anim 符号全部识别；modinfo/manifest/xml 明文读取
- **解码量**：30+ 图集解码并做像素统计（mip0 全尺寸 + 缩略层），覆盖：角色（白无常/黑无常/孟婆/马面/秦广王/骷髅大兵）、建筑（鬼门关/城墙/丹炉/三生石/雕像）、植物（枫树/枯树/荷花/地刺）、UI（modicon 图标）、武器（刀/剑/伞/锁链/枪/旗）
- **关键结论**：地府 mod = 独立地府世界（9 殿 static_layouts + 传送点 + 仪式入口）＋判官阵营角色体系＋法宝武器体系＋黑红青三色恐怖画风＋Chilla 全套商业加密（VM 级）

**一句话总结**：地府 mod 通过 `modworldgenmain` + 9 个 static_layout 静态布局 + 传送点/仪式构建独立地府世界层，用 131 个 build 资产（判官/无常/孟婆/秦广王/鬼门关/三生石等）铺陈红黑青三色恐怖画风，全部逻辑经 Chilla VM 字节码混淆保护，美术资源以 KTEX 容器（ZIP+raw deflate）打包。
