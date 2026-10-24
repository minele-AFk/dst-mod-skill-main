# Mod 资产图集样本索引（资产参考，未入库）

> 资产参考，仅索引不拷贝。以下图集样本来自资料包，本机可直接访问，未复制进 skill 库（避免二进制入库）。
> 用途：查看官方/大型 mod 的 tex 图集组织规律与动画 atlas 结构。

## 一、官方 tex 图集样本（60 张 DXT5，约 7.4MB）

**路径**：`d:\mods\资料包\dst-mod-creater\assets\`（文件命名 `*_DXT5_*.png`，取自 6 大 mod 提取的官方图集）

| 类别（文件名前缀） | 示例 | 说明 |
|---|---|---|
| ui 大图集 | `1392778117_ui_256x256_DXT5_0.png` 等 6 张 | 各 mod 的 UI 主图集 |
| avatars | `avatars_other_64x64_DXT5_53.png` | 头像 64×64 |
| bigportrait | `bigportrai_other_1024x1024_DXT5_48.png` | 大立绘 1024×1024 |
| foodimages | `foodimages_*_256x256_DXT5_*.png` | 食物图标 256×256 |
| fx | `fx_*_*.png` | 特效图集 |
| icons | `icons_ui_*.png` | 通用图标 |
| images | `images_*_*.png` | 通用大图 |
| inventoryimages | `inventoryi_*_64x64_DXT5_*.png` | 背包图标 64×64（building/creature/other/plant/turf/ui） |
| largeimages | `largeimage_*_256x256_DXT5_*.png` | 大地图图标 |
| mapicons / map_icons | `mapicons_*`、`map_icons_*`（64/128） | 地图图标（building/plant/ui/creature） |
| slotimages | `slotimages_ui_128x128_DXT5_*.png` | 装备槽位图标 |
| textures | `textures_*_*.png`（512~1024） | 地表贴图（other/plant/turf） |
| tiles | `tiles_turf_*.png`（1024/2048×1024） | 地皮图块 |
| widgetimages | `widgetimag_*_*.png` | Widget 控件图 |

## 二、山海秘藏 fsm 动画图集（7 张，约 10.5MB）

**路径**：`d:\mods\资料包\dst-mod-creater\assets\shanhaisc\`

`art_atlas_fsm_*.png`（announcement_ui / banana_tree / caochanzhi / elegiac_maple / fusang / henhouse / jinwu）—— 山海秘藏 mod 的角色/建筑/公告 UI 动画图集。

## 关联

- 解码/分析这些 DXT5 图集用 `tools/` 下 KTEX 解码族（见 [ktex-format.md](ktex-format.md)）。
- 图集与动画打包流程见 [asset-pipelines.md](asset-pipelines.md)。
