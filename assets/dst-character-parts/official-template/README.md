# assets/official/ — 官方人物美术标准样本

从 `templates/official/`（Klei 官方模板 verbatim 副本）提炼的 PNG 参考样本，命名沿用项目约定"用途_尺寸_格式"。**全量部位库在 `templates/official/extended sample character-DST/exported/`**，这里只放快速目检样本。

## 硬标准图（来自 samplecharacter_templates1/2，生成人物贴图的强制尺寸）

| 文件 | 来源 | 尺寸 | 用途 |
|---|---|---|---|
| `animsheet_char_1024x512_RGBA.png` | templates1\anim\template_player_character.png | 1024x512 | 角色动画贴图（Spriter 导入原图） |
| `saveslot_char_120x104_RGBA.png` | templates1\images\saveslot_portraits\template_save.png | 120x104 | 存档槽头像 |
| `selectscreen_char_188x284_RGBA.png` | templates1\images\selectscreen_portraits\template_selectscreen_portraits.png | 188x284 | 选人界面头像 |
| `bigportrait_char_1024x1024_RGB.png` | templates2\bigportraits\template_bigportrait.png | 1024x1024 | DST 选人大肖像 |
| `animsheet_char_blank_1024x512_RGBA.png` | 工具生成（char_sheet_gen.py） | 1024x512 | 空白分区模板（部位名标注，绘制管线填色用） |

## esctemplate 部位代表帧（exported\esctemplate\，全部 -0 帧）

| 文件 | 尺寸 | 部位 |
|---|---|---|
| `esc_face_200x200_RGBA.png` | 200x200 | 脸（33 帧，眼/嘴特征） |
| `esc_headbase_300x300_RGBA.png` | 300x300 | 头骨底座（4 帧） |
| `esc_hair_400x400_RGBA.png` | 400x400 | 发型（4 帧） |
| `esc_torso_160x120_RGBA.png` | 160x120 | 躯干（11 帧，**黄色着色件**） |
| `esc_skirt_160x120_RGBA.png` | 160x120 | 裙（5 帧，**深黄绿着色件**） |
| `esc_hairpigtails_250x300_RGBA.png` | 250x300 | 双马尾（5 帧，**深棕着色件**） |
| `esc_tail_250x100_RGBA.png` | 250x100 | 尾巴（12 帧，左/右/前三组） |
| `esc_hand_100x100_RGBA.png` | 100x100 | 手（20 帧，多姿态） |
| `esc_leg_60x80_RGBA.png` / `esc_leg_alt_60x80_RGBA.png` | 60x80 | 腿（11 帧，-1 帧为另一姿态） |
| `esc_foot_100x100_RGBA.png` | 100x100 | 脚（8 帧） |
| `esc_arm_upper_80x80_RGBA.png` | 80x80 | 上臂（7 帧） |
| `esc_arm_upper_skin_80x80_RGBA.png` | 80x80 | 上臂皮肤条（3 帧） |
| `esc_cheeks_64x60_RGBA.png` | 64x60 | 腮红（2 帧） |
| `esc_torso_pelvis_160x120_RGBA.png` | 160x120 | 骨盆（11 帧，**黄色着色件**） |

## 幽灵 build 代表帧（exported\ghost_esctemplate_build\）

| 文件 | 尺寸 | 部位 |
|---|---|---|
| `esc_ghost_body_360x352_RGBA.png` | 360x352 | 幽灵身体（1 帧，白色） |
| `esc_ghost_eyes_250x250_RGBA.png` | 250x250 | 幽灵双眼（4 帧） |
| `esc_ghost_tail_232x392_RGBA.png` | 232x392 | 幽灵尾卷（16 帧，尺寸逐帧变化） |
| `esc_ghost_fx_184x136_RGBA.png` | 184x136 | 幽灵雾特效（41 帧，尺寸逐帧变化，-0 帧为 184x136） |

## 风格速记

- 部位贴图以**灰度铅笔线稿**为主（face/hand/leg/arm/tail 等），个别部件上色（torso/torso_pelvis 黄、skirt 深黄绿、hairpigtails 深棕）
- 幽灵 build 整体白色（RGB ~213,212,185）+ 雾特效
- 生成新人物时：保持官方帧数与 pivot（见 `references/character-esc.md` §10-11，可用 `tools/scml_analyze.py` 重新导出）
