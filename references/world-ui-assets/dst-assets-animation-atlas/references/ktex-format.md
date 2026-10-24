# KTEX 纹理容器格式（只读诊断参考）

> **定位**：只读诊断/理解格式，便于排查"贴图丢失、解码失败、尺寸不符"。**不是**用来手工伪造 tex 的配方。
> 出处标注为版本敏感：KTEX 布局属于引擎级内部格式，无官方 Lua 源码可锚定，请以当前客户端实际读取能力为准。
> 与本地源码核对：tile/turf 纹理走 `tiledefs.lua`/`tilemanager.lua`（`D:\mods\scripts`）。
> 配套解码脚本见 `../tools/`（KTEX 解码族，暂未验证运行，仅作格式理解底本）：
> - `ktex_decode.py` — 单文件 tex → PNG
> - `ktex_batch.py` — 目录批量解码 + 像素统计
> - `ktex_ascii.py` — 小纹理 ASCII 预览（无需 Pillow）
> - `dst_tex_analyze.py` — 全量研究解码 + 格式/尺寸统计
> 文件间 `from ktex_decode import ...`，须同目录使用。

## 1. 布局总览

```
offset 0  : "KTEX" magic (4 bytes)
offset 4  : format u32
offset 8  : N 个 mip 头，每个 10 字节
           (w u16, h u16, pitch u16, size u32)
           所有 mip 头连续排列在头部，mip 数 = floor(log2(min(w,h))) + 1
数据区     : 紧跟所有 mip 头之后 (offset = 8 + 10*N)
           按 mip 从大到小连续存放
```

**关键坑**：mip 头不是"头+数据+头+数据"交错，而是「所有头在前、所有数据在后」。

## 2. format 字段判定（低 16 位）

| 值 | 压缩 | 数据区长 | 说明 |
| --- | --- | --- | --- |
| `0x2220` 族 | DXT5 | `w*h` | 主流（3153/3295 = 95.7%，带 alpha 的 UI/图标/图集） |
| `0x2200` 族 | DXT1 | `w*h/2` | 少数（62 个，无 alpha） |
| 数据区 `== w*h*4` | **8-bit RGBA 无压缩** | `w*h*4` | **不要假设 DXT**；官方人物 build 图集与 names 类大图走此格式 |

- `format` 高 16 位是标志位（`0xfff0/0xfffc/0xfffd` 前缀），不影响解码。
- DXT1 每 4x4 块 8 字节；DXT5 每 4x4 块 16 字节。
- **size 判定经验**：`DXT5 = w*h`、`DXT1 = w*h/2`、`RGBA8 = w*h*4`；对方 3295 个样本中 3293 个与此完全吻合。

## 3. mip 链与尺寸规范

- 全部带完整 mip 链（`2^n → 1x1`，最小级 2x2/1x1 各 16 字节块）。
- 尺寸几乎全部为 2 的幂。已知例外：`500x500`（Uncompromising UI）、`63x63`（telebase_active）、`1024x32`（横向 strip 纹理）。
- 常见规格：图标 `64x64`、图鉴/大图 `256x256`、UI 面板 `512x512/1024x1024`、地皮纹理 `1024x1024`、tile 集 `2048x1024`。

## 4. 常见目录尺寸速查

| 用途 | 常见尺寸 |
| --- | --- |
| inventory 图标 | 64x64 |
| 图鉴/largeimage | 256x256 |
| UI 面板 | 512x512 / 1024x1024 |
| 地皮纹理 | 1024x1024 |
| tile 集 | 2048x1024（16x8 格，每格 128x128） |

## 5. XML Atlas 两种形态

1. **单纹理图集（占绝大多数）**：`<Atlas><Texture filename="xxx.tex"/><Elements><Element name="xxx.tex" u1 v1 u2 v2/></Elements></Atlas>`。inventoryimages 类图片都这样。
2. **多元素网格图集（少数）**：多个 Element 共享一个 Texture，UV 归一化 0-1。典型 2x2/4x4 网格（uv 幅度 0.25/0.5），如 tabs.xml、UI 面板九宫格。

**tile 图集特例**（`levels/tiles/*.xml`）：`<Element name="48" u1 v1 u2 v2 variant="">`——`name` 是 tile ID（如 48、04、33），`variant` 是子变体（"a"/"b"）。tile 纹理格 128x128，排列在 2 的幂 atlas 上（如 2048x1024 = 16x8 格）。

## 6. anim zip 内部结构与命名

- zip 内部：`build.bin` / `anim.bin` / `atlas-0.tex`（+ 可选 `atlas-1.tex` 大图拆分）+ `atlas.xml`。
- 人物 build 用**双图集**拆分大图：`esctemplate.zip = anim.bin + build.bin + atlas-0.tex + atlas-1.tex`。
- 幽灵皮肤 zip 命名 `ghost_<build>.zip`（如 `ghost_esctemplate_build.zip`）。
- 命名分类（对方各 mod 汇总）：`ghost_*`（幽灵/透明变体）、`swap_*`（手持）、`*_actions`（动作扩展）、`player_*`（玩家）、`status_*`（状态图标）、`ui_*`（UI）。

## 7. 零美术成本修改技巧（低风险参考）

- 直接引用游戏本体纹理：`<Texture filename="data/DLC0002/levels/tiles/jungle.tex"/>`——只重排 UV/content 就能造出新地皮素材（对方多个 mod 采用，tiles XML 完全相同、字节数一致）。**仍须验证目标路径在你当前客户端确实存在**，不应想当然。
- 复用原版 anim zip：anim/ 目录直接放原版动画 zip。

## 8. 边界与不变量

- **不手工伪造**：本文件仅用于读懂现有资源；不用于 `Write` 生成二进制 tex/zip。
- 判定 RGBA8 必须用"数据区大小 == w*h*4"，不要看到 `KTEX` 就默认 DXT。
- 遇到解码失败时，先核对是 DXT5/DXT1/RGBA8 哪种，再确认 mip 头与数据区是否「全部头在前」布局。
- 涉及人物 build 的双图集与部件尺寸，交叉参考 `dst-character-parts` 的官方 esctemplate 标准。