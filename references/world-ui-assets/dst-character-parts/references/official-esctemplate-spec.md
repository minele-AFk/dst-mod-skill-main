# DST 官方人物模板 esctemplate 开发标准

> **定位**：本文件是「**从零新建一个 DST 人物**」时采用的官方硬标准（底图/部位/尺寸/pivot/编译）。若已有目标人物的 SCML（用户指定或最近可编译工程），仍以 `dst-parts-spec.md` 的模板优先级为准（目标 SCML > 本官方标准）。
> 版本锚定：api_version 10 / dst_compatible，版本敏感；数值以你手上模板为准。
>
> **本标准的客观依据（同目录内，均来自官方工程）：**
> - 官方 SCML 工程与 20 部位 PNG：`../../../assets/dst-character-parts/official-template/exported/esctemplate/`
> - 动画 zip / build：`../../../assets/dst-character-parts/official-template/anim/`（esctemplate.zip、ghost_esctemplate_build.zip）
> - 部位硬标准图样与贴图模板：`../../../assets/dst-character-parts/official-template/`（animsheet_char_blank 等 *_RGBA.png）
> - 部位数据导出：`../tools/scml_analyze.py`（stdlib）、`../tools/esc_parts.json`
> - 贴图模板生成/校验：`../tools/char_sheet_gen.py`（需 Pillow）
>   （上述脚本暂未在本环境验证运行，仅作标准理解与后续迁移底本。）

## 1. 目录与加载链

```
modinfo.lua
modmain.lua  ── PrefabFiles = { "esctemplate", "esctemplate_none" }
├── scripts/prefabs/esctemplate.lua      (MakePlayerCharacter 人物定义)
├── scripts/prefabs/esctemplate_none.lua (CreatePrefabSkin 皮肤/幽灵注册)
├── scripts/speech_esctemplate.lua       (Wilson 基准语音表)
├── anim/esctemplate.zip                 (anim.bin + build.bin + atlas-0/1.tex)
├── anim/ghost_esctemplate_build.zip     (幽灵 build)
├── bigportraits/  images/(avatars|map_icons|saveslot_portraits|selectscreen_portraits|names)
├── modicon.png/.tex/.xml
└── exported/  esctemplate/ | esctemplate_cleared/ | ghost_esctemplate_build/   (Spriter 源工程)
```

## 2. modinfo / modmain 关键点

- `dst_compatible=true`、`dont_starve_compatible=false`、rogs/shipwrecked=false。
- **`all_clients_require_mod=true`（人物 mod 必须全员加载）**。
- `server_filter_tags={"character"}`；`icon_atlas` / `icon`。
- modmain：**18 项 IMAGE(.tex)+ATLAS(.xml) 资产**逐项声明；`AddMinimapAtlas("images/map_icons/esctemplate.xml")`。
- 选人界面 STRINGS：`CHARACTER_TITLES / CHARACTER_NAMES / CHARACTER_DESCRIPTIONS / CHARACTER_QUOTES / CHARACTER_SURVIVABILITY`；`NAMES.ESCTEMPLATE`；`SKIN_NAMES`。
- **皮肤模式**（选人循环视图，官方写法）：
  ```lua
  local skin_modes = {
      { type = "ghost_skin", anim_bank = "ghost", idle_anim = "idle",
        scale = 0.75, offset = { 0, -25 } },
  }
  AddModCharacter("esctemplate", "FEMALE", skin_modes)
  ```
  ghost_skin 的 anim_bank 指向游戏本体 "ghost" bank。

## 3. prefab：MakePlayerCharacter 标准写法

```lua
return MakePlayerCharacter("esctemplate", prefabs, assets, common_postinit, master_postinit, prefabs)
```

- 属性全走 TUNING 常量；初始物品 `TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT.ESCTEMPLATE = {...}`。
- common_postinit（客户端+服务端）：`inst.MiniMapEntity:SetIcon("esctemplate.tex")`。
- master_postinit（仅服务端）：`inst.soundsname = "willow"`（复用语音）；`health/hunger/sanity:SetMax(...)`；`OnLoad = onload; OnNewSpawn = onload`。
- 技能演示用 `locomotor:SetExternalSpeedMultiplier(inst, "..._speed_mod", x)`，按 `HasTag("playerghost")` 切换；监听 `ms_respawnedfromghost / ms_becameghost`。

## 4. 皮肤/幽灵注册（esctemplate_none.lua）

```lua
local skins = { normal_skin = "esctemplate", ghost_skin = "ghost_esctemplate_build" }
return CreatePrefabSkin("esctemplate_none", {
    base_prefab = "esctemplate", type = "base", assets = assets, skins = skins,
    skin_tags = {"ESCTEMPLATE", "CHARACTER", "BASE"},
    build_name_override = "esctemplate", rarity = "Character",
})
```

- `type="base"` 基础皮肤；`normal_skin` 指主 build；`ghost_skin` 指幽灵 build zip。

## 5. 图片资产规格（18 项）

| # | 路径 | 尺寸 | 内容 |
|---|---|---|---|
| 1 | `images/saveslot_portraits/<c>.png` | 120x104 | 存档槽头像 |
| 2 | `images/selectscreen_portraits/<c>.png` | 188x284 | 选人头像（头+肩） |
| 3 | `images/selectscreen_portraits/<c>_silho.png` | 188x284 | 剪影（未解锁态） |
| 4 | `bigportraits/<c>.png` | 491x654 | 大肖像源图（灰度胸像） |
| 5 | `images/map_icons/<c>.png` | 64x64 | 小地图图标 |
| 6 | `images/avatars/avatar_<c>.png` | 64x64 | 头像 |
| 7 | `images/avatars/avatar_ghost_<c>.png` | 64x64 | 幽灵头像 |
| 8 | `images/avatars/self_inspect_<c>.png` | 64x64 | 自我检查剪影 |
| 9 | `images/names_<c>.png` | 876x434（tex 后 1024x512 = 2 的幂 padding） | 名称横幅 |
| 10 | `images/names_gold_<c>.png` | 876x434 | 金色名称横幅 |
| 11 | `modicon.png` | 128x128 | mod 图标 |

> ⚠️ **完整性**：这 18 项资产 modmain 逐项声明，缺一项选人界面就报错或显示空白。

## 6. names_[char].png 编译陷阱（重要）

编译后**必须手动把 `names_[char].png` 和 `names_gold_[char].png` 的 XML 里 Element name 改成 `[character].tex`**（Texture filename 不能改），否则选人界面角色名不显示：

```xml
<Atlas><Texture filename="names_esctemplate.png" .../>
<Elements><Element name="esctemplate.tex" .../></Elements></Atlas>
<!-- Element name 必须是角色名.tex，不是 names_esctemplate.tex -->
```

## 7. anim zip 逆向（ANIM v4 / BILD v6）

- `anim/esctemplate.zip`：anim.bin（158KB）、build.bin（81KB）、atlas-0.tex（5.5MB）、atlas-1.tex（2.7MB）；ghost 包同构（anim.bin 仅 867B）。
- anim.bin（"ANIM" v4）：头=magic+ver+关键帧总数+帧数+动画名；动画记录=实体哈希+帧率40+帧数；每帧=包围盒+元素数+每元素 40 字节。
- 40 字节元素布局：`u32 部位哈希 | u32 文件帧号 | u32 名称哈希 | 2×2矩阵(4×f32) | x | y | z`。
- sdbm 小写哈希：`h = (h*65599 + c) & 0xFFFFFFFF`。
- **主包 40 帧 × 98 元素全部相同（静态构建姿态，无运行时动画）**；坐标 y 向下（SCML y 取反）。
- build.bin（"BILD" v6）：字符串表含 build 名 + 2 图集名 + 20 folder 名；155 符号 = 全部 PNG 帧。
- atlas tex = KTEX + 8-bit RGBA 无压缩（`size == w*h*4`，见 assets `ktex-format.md`）。
- **运行时动画（idle/walk/run...）由游戏本体玩家系统提供**；做自定义动画需在 SCML 加 timeline 重新编译。

## 8. 部位规范表（20 部位 / 155 帧）

> 生成人物时**保持官方帧数与 pivot，只换像素**。

| folder | 部位 | 帧数 | 尺寸 | pivot（代表值） |
|---|---|---|---|---|
| 0 | face | 33 | 200x200 | (0.543,0.571) |
| 1 | headbase | 4 | 300x300 | (0.521,0.187) |
| 2 | hair | 4 | 400x400 | (0.506,0.381) |
| 3 | torso | 11 | 160x120 | (0.500,0.212) |
| 4 | foot | 8 | 100x100 | (0.500,0.650) |
| 5 | hand | 20 | 100x100 / 150x200 | (0.477,0.636) |
| 6 | leg | 11 | 60x60 / 60x80 | (0.511,0.762) |
| 7 | arm_lower | 7 | 50x50 / 50x80 / 60x60 / 80x50 | (0.516,0.833) |
| 8 | arm_upper | 7 | 80x80 | (0.504,0.711) |
| 9 | cheeks | 2 | 64x60 | (0.509,0.500) |
| 10 | hair_hat | 4 | 400x400 | (0.506,0.381) |
| 11 | headbase_hat | 4 | 300x300 | (0.521,0.187) |
| 12 | hairpigtails | 5 | 250x300 | (0.713,0.539)/(0.329,0.491) |
| 13 | skirt | 5 | 160x120 | (0.502,0.562) |
| 14 | tail | 12 | 250x100 | (0.628,0.500) |
| 15 | hairfront | 2 | 400x400 | (0.506,0.381) |
| 16 | arm_upper_skin | 3 | 80x80 | (0.503,0.609) |
| 17 | torso_pelvis | 11 | 160x120 | (0.500,0.212) |
| 18 | SWAP_ICON | 1 | 268x244 | (0.500,0.500) |
| 19 | face_sail | 1 | 200x200 | (0.623,0.570) |

**风格**：灰度铅笔线稿为主（face/hand/leg/arm/tail/headbase 等）；着色件：torso/torso_pelvis（黄）、skirt（深黄绿）、hairpigtails（深棕）。SWAP_ICON 未被 mainline 引用（仅 build 符号）。

## 9. SCML 结构要点

- BrashMonkey Spriter；唯一动画 `BUILD_PLAYER`（40 帧 @40fps）。
- **无 `<bone>` 元素**，纯 sprite-object 构建（98 条 timeline，z_index 0-97 每 timeline 独占一层）。
- 编译符号名 = `<folder>_<file>_<timelineID>`；同 (部位,帧) 重复组合用 timeline 名消歧。
- tail 分三组：左/右（scale_x=-1 镜像）/前。关键 z：tail 底部 → 身体服装中部 → headbase/hair → face → hairfront 顶部。

## 10. 幽灵 build（5 部位 64 帧）

| 部位 | 帧数 | 尺寸（代表） | 内容 |
|---|---|---|---|
| ghost_FX | 41 | 32x28 ~ 484x284 | 幽灵雾/云特效 |
| ghost_body | 1 | 360x352 | 白色身体 |
| ghost_eyes | 4 | 250x250 | 双眼 |
| ghost_tail | 16 | 224x404 ~ 236x412 | 幽灵尾卷 |
| ghost_hairpigtails | 2 | 200x250 | 幽灵双马尾 |

动画 4 帧 @40fps；mainline 只引用 eyes/tail/hairpigtails；body 与 FX 是 build 符号供运行时换肤。

## 11. 新角色生成工作流（8 步）

1. 复制官方模板为你的 mod 目录。
2. 全局替换 `esctemplate→mychar`（含文件名）、`ESC→MYCHAR`（STRINGS 键）。
3. 改 modinfo.lua（name/description/author/version）。
4. **按 §8 部位表重绘贴图**：保持 20 部位、官方帧数与 pivot，只换像素；风格=灰度线稿+局部着色。
5. Spriter 装配（无骨 98 timeline）→ autocompiler 编译 anim zip。
6. png→tex 编译全部图片资产（KTEX 8-bit RGBA），**names_[char].xml 的 Element name 改 [char].tex**。
7. 改 speech / 选人界面 STRINGS / 属性与技能 / 幽灵 build。
8. 游戏内验证：选人界面完整（18 项）、小地图图标、幽灵形态、初始物品。

## 12. 与现有拆件 skill 的边界

- 本文件：**官方硬标准**与**从零新建**流程。
- `dst-parts-spec.md`：**已有 SCML 的拆件**原则（模板优先级 / 部件族 / 镜像 / 透明边缘 / 验收）。
- 决策：已有目标 SCML → 按 dst-parts-spec（目标 SCML 为准）；从零新建 → 先按本文件官方标准起步。