# 原版参考图（精简入库）

只收录**风格对照**与**运行套件模板**；同族皮肤变体不入库。

提炼纪律：表中「对照点」是**画法**不是题材说明；套到新物体时只复用线/面/材质/色规则。

用途分流：
- 本目录 → 只服务 **原版 DST 画风**（`../../references/texture-style.md`）
- 用户提供的 Mod 例图 → 按 [参考驱动流程](../../references/reference-led-prompts.md) 单独选型，不强制套统一 Mod 画风

## 目录

| 路径 | 内容 |
|------|------|
| `style/` | 风格样本（材质/线稿/构图） |
| `kits/` | 完整运行套件（icon + world + swap/阴影） |
| `DISPLAY_SIZE_BOARD.png` | 展示实际大小对照（默认 zoom 1:1） |
| `DISPLAY_SIZE.md` | 展示大小怎么调 |
| `STYLE_CONTACT.png` | style 拼板 |

## style/ 清单

| 文件 | 尺寸 | 对照点 |
|------|------|--------|
| `style/icon-tool-weapon/axe.png` | 64×64 | 木柄+石/铁头，斜置工具构图 |
| `style/icon-tool-weapon/spear.png` | 64×64 | 长柄武器，尖端焦点 |
| `style/icon-tool-weapon/nightsword.png` | 64×64 | 暗色魔法武器，高对比轮廓 |
| `style/icon-tool-weapon/goldenaxe.png` | 64×64 | 金属高光+木柄，金色焦点 |
| `style/icon-armor-hat/armorwood.png` | 64×64 | 木甲分面与钉扣 |
| `style/icon-armor-hat/footballhat.png` | 64×64 | 皮革头盔，硬边明暗 |
| `style/icon-armor-hat/tophat.png` | 64×64 | 布料/毡帽，柔和分面 |
| `style/icon-food-material/carrot.png` | 64×64 | 有机物条状笔触 |
| `style/icon-food-material/meat.png` | 64×64 | 生肉脏旧质感 |
| `style/icon-food-material/log.png` | 64×64 | 木纹与截面 |
| `style/icon-food-material/goldnugget.png` | 64×64 | 矿物/金属块面 |
| `style/icon-item-container/backpack.png` | 64×64 | 容器+背带结构 |
| `style/icon-item-container/treasurechest.png` | 64×64 | 箱体木板+锁扣 |
| `style/icon-item-container/cookpot.png` | 64×64 | 金属锅+盖，器皿 |
| `style/icon-magic-misc/purplegem.png` | 64×64 | 宝石高光与透光 |
| `style/icon-magic-misc/firestaff.png` | 64×64 | 法杖+宝石焦点 |
| `style/icon-magic-misc/amulet.png` | 64×64 | 小件挂饰 |
| `style/world-world-tool/axe__axe01.png` | 151×156 | 世界工具 sprite（透明边） |
| `style/world-world-tool/swap_hammer__swap_hammer.png` | 126×190 | 手持 swap 拆件 |
| `style/world-world-building/treasure_chest__chest01.png` | 240×171 | 建筑主件 |
| `style/world-world-building/campfire__campfire_log.png` | 125×80 | 设施木堆 |
| `style/world-world-equip/armor_wood__swap_body.png` | 89×124 | 装备穿戴件 |
| `style/world-world-equip/hat_football__swap_hat.png` | 248×212 | 帽子穿戴件 |
| `style/world-world-food/carrot__carrot01.png` | 273×116 | 地面食物 |
| `style/world-world-fx/fire__flames.png` | 276×659 | FX 软边/叠层 |
| `style/world-world-fx/splash__droplet.png` | 41×92 | 半透明液滴 |

## kits/ 完整运行套件

每个 kit 对应「一件资源如何配齐」；工具/装备 build 可能无独立 shadow symbol。

### `kit-building-campfire`

- `icon_campfire_64.png` — 64×64
- `world_campfire_log-1.png` — 125×80
- `world_campfire_shadow-0.png` — 311×111
- `world_fire_dead-2.png` — 331×123
- `world_Logs-3.png` — 311×147
- `world_preview-4.png` — 266×416

### `kit-building-chest`

- `icon_treasurechest_64.png` — 64×64
- `world_chest01-1.png` — 240×171
- `world_chest_shadow-0.png` — 245×30
- `world_keyhole-2.png` — 137×124
- `world_sparkle-3.png` — 213×182

### `kit-equip-armorwood`

- `icon_armorwood_64.png` — 64×64
- `world_swap_body-0.png` — 89×124

### `kit-equip-footballhat`

- `icon_footballhat_64.png` — 64×64
- `world_swap_hat-0.png` — 248×212

### `kit-tool-axe`

- `icon_axe_64.png` — 64×64
- `swap_swap_axe-0.png` — 125×194
- `world_axe01-0.png` — 151×156

## 重新提取（需要更多原版样本时）

```powershell
python references/tools/general/tex_atlas_tool.py unpack inventoryimages1 --output <tmp>
python references/tools/general/anim_scml_tool.py <game>/data/anim/axe.zip --output <tmp>/axe
python references/tools/general/anim_scml_tool.py <game>/data/anim/swap_axe.zip --output <tmp>/swap_axe
```

分析：

```powershell
python tools/analyze_textures.py assets/vanilla/style --max-files 200 --summary-only
```
