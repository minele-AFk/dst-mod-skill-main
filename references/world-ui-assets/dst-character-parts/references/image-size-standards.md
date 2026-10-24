# 人物贴图尺寸硬标准

> 人物美术标准唯一出处。出处以本地 `D:\mods\scripts` 源码与官方人物模板为准。

## 尺寸表（唯一出处）

| 用途 | 尺寸 | 备注 |
|---|---|---|
| 角色动画贴图（Spriter 导入原图） | **1024x512 RGBA** | Wilson 骨架风格，动画贴图硬标准 |
| 存档槽头像 saveslot | **120x104 RGBA** | `images/saveslot_portraits/` |
| 选人界面头像 selectscreen | **188x284 RGBA** | `images/selectscreen_portraits/` |
| 选人大肖像 bigportrait | **1024x1024 RGB** | `bigportraits/` |
| 小地图图标 map_icons | 64x64 | `images/map_icons/` |
| 头像 avatars（含 ghost/self_inspect） | 64x64 | `images/avatars/` |
| 名称横幅 names / names_gold | 876x434（png 源，编译后 tex 1024x512） | `images/names_<char>.png` |
| mod 图标 modicon | 128x128 | `modicon.png` |
| bigportrait 源图（灰度胸像） | 491x654 | esctemplate 出品 |

## 使用要点

- 三张基础图为**人物贴图尺寸硬标准**：动画贴图 1024x512 + saveslot 120x104 + selectscreen 188x284。
- 大肖像仅有 png 源（无 tex/xml），需用 tex 工具编译出三件套——见 `references/world-ui-assets/dst-assets-animation-atlas/references/ktex-format.md`。
- PHP 尺寸偏离硬标准会导致动画错位 / 部位穿模。