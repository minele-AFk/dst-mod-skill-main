# 纹理模式

当任务涉及图集 `tex+xml`、库存图标、PNG 调整大小或从 `images.zip` 提取官方纹理时使用此文件。

本页介绍纹理工作流程，而非 `AnimState` 库/构建逻辑。
如果任务还涉及预制件资源注册，请阅读 `references/patterns/asset/asset-patterns.md`。
如果任务涉及动画资源编译，请继续使用游戏的官方 `autocompiler` 流程，而非扩展这些纹理脚本。

## 常见案例

- 从 `images.zip` 解包官方图集
- 从 `my_atlas.tex + my_atlas.xml` 解包本地图集
- 将多个 PNG 打包成一个图集 `tex+xml`
- 将一个图标或整个图标目录调整大小以更好地适应 DST UI 或图集使用
- 检查已知的官方图标图集，如 `images/inventoryimages1.tex`

## 默认官方源

当用户请求官方图集但未提供路径时，使用 `images.zip`。

常见归档路径：

- `...\Don't Starve Together\data\databundles\images.zip`

有用的官方条目：

- `images/inventoryimages1.tex`
- `images/inventoryimages1.xml`

默认解包输出：

- `.tmp/.output/images/`

## 辅助脚本

### `references/tools/general/tex_atlas_tool.py`

当任务涉及图集打包或解包时使用此脚本。

当前支持的工作流程：

- 从 `images.zip` 解包官方 `dxt5` 图集
- 从 `.tex + .xml` 对解包本地 `argb` 或 `dxt5` 图集，包括官方风格的 KTEX 头（mip 计数编码在格式代码中）
- 将图集条目拆分为单独的 PNG 文件
- 将多个 PNG 打包成一个图集 PNG + XML + TEX，最好在安装了模组工具时通过 Klei `TextureConverter.exe` 进行
- 官方模组工具确实支持通过与 `image_build.py` 使用的相同 `atlas.Atlas(...)` 加上 `TextureConverter.exe` 流程将多个 PNG 文件打包成一个图集

常见命令：

```bash
python references/tools/general/tex_atlas_tool.py unpack inventoryimages1
```

```bash
python references/tools/general/tex_atlas_tool.py unpack --tex path/to/my_atlas.tex --xml path/to/my_atlas.xml
```

```bash
python references/tools/general/tex_atlas_tool.py pack path/to/png_dir my_atlas
```

规则：

- 官方图集名称通常从 `images/<name>.tex` 和 `images/<name>.xml` 读取
- 如果用户省略输出路径，解包默认为 `.tmp/.output/images/`
- 打包应优先使用本地模组工具 `TextureConverter.exe` 进行 TEX 输出，因为它比后备写入器更接近 Klei 的预乘和平台打包路径
- 安装模组工具时，优先使用源自 `klei/atlas.py` 的官方风格图集布局和 XML 生成路径，而非手动编写的打包布局
- 后备纯 Python 写入器在模组工具不可用时仍然有用，但应视为兼容性后备
- 解包支持官方 `dxt5` 图标图集和其他常见官方 UI 图集头，如 `0xFFFD4220`
- 将脚本打包的 UI 图集视为"需要游戏内验证"，而非官方模组工具输出的自动替代品
- 如果打包的 UI 图集渲染为黑色，请在指责 XML 坐标或部件代码之前将其 KTEX 格式代码与已知良好的官方输出进行比较
- 如果模组工具缺失，请在回退之前询问用户是否在 Steam 默认 `common` 路径之外安装了它
- 如果用户未安装它，请推荐 Steam 应用 ID `245850` 和 Windows 安装命令 `start steam://install/245850`

### `references/tools/general/resize_png.py`

当任务涉及在图集打包或图标替换之前调整一个 PNG 或多个 PNG 的大小时使用此脚本。

常见命令：

```bash
python references/tools/general/resize_png.py path/to/icon.png 64x64
```

```bash
python references/tools/general/resize_png.py path/to/icon_dir 64x64 --mode contain --output .tmp/.output/resized_icons
```

支持的调整大小模式：

- `contain`
  - 保持宽高比，填充到精确目标尺寸
- `cover`
  - 保持宽高比，通过裁剪填充目标尺寸
- `stretch`
  - 强制精确目标尺寸
- `fit-width`
  - 设置宽度，保持宽高比
- `fit-height`
  - 设置高度，保持宽高比

规则：

- 对大多数库存图标适配使用 `contain`
- 仅当变形可接受或明确需要时使用 `stretch`
- 当目标槽位形状比保留完整源边界更重要时使用 `cover`

## 意图索引

- "解包官方图集"
  - 使用 `python references/tools/general/tex_atlas_tool.py unpack <atlas_name>`
- "解包本地 tex+xml 对"
  - 使用 `python references/tools/general/tex_atlas_tool.py unpack --tex ... --xml ...`
- "将多个 PNG 打包成一个图集"
  - 使用 `python references/tools/general/tex_atlas_tool.py pack <input_dir> <atlas_name>`
- "将图像调整为 64x64 或 128x128"
  - 使用 `python references/tools/general/resize_png.py ... <size>`
- "调整多个图像大小，然后打包"
  - 首先使用 `resize_png.py` 调整大小，然后使用 `tex_atlas_tool.py` 打包
- "检查官方库存纹理"
  - 解包 `inventoryimages1`

## 经验法则

- 如果任务涉及资源声明，请阅读 `references/patterns/asset/asset-patterns.md`。
- 如果任务涉及纹理文件生成或提取，请先阅读本页。
- 对于官方图集检查，优先使用 `images.zip` 而非临时提取的副本。