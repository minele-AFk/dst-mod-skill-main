# 资源管线对照

> 需要读懂 tex/bin 字节布局（排查贴图丢失、解码失败、判别 DXT5/DXT1/RGBA8）时，读取 [ktex-format.md](ktex-format.md)。
> 注意：ktex-format 仅用于**只读理解/诊断**现有资源，不是手工伪造二进制容器的配方。

| 目标 | 资源 | Lua 消费 |
| --- | --- | --- |
| 世界动画 | 编译后的 anim zip | Asset ANIM、AnimState |
| UI 动画 | anim zip | UIAnim 的 AnimState |
| UI 图片 | atlas xml 与 tex | Asset ATLAS、Asset IMAGE、Image |
| 库存图标 | inventory atlas | inventoryitem、Recipe、注册 Atlas |
| Minimap 图标 | minimap atlas | MiniMapEntity |
| Shader | ksh | dst-shader-authoring |

## 名称层级

bank、build、animation 与 symbol 是不同名称。SetBank 选择动画银行，SetBuild 选择图像资源，PlayAnimation 选择时间线，OverrideSymbol 替换单个 symbol。

## 检查顺序

1. 源文件存在。
2. Mod Tools 实际编译成功。
3. 编译产物位于模组相对路径。
4. Asset 类型与路径正确。
5. XML 与 TEX 名称匹配。
6. Lua 中 bank、build、animation、symbol 存在。
7. 干净客户端能加载资源。

不要手工制造 anim zip、tex 或其他二进制容器，也不要把未运行的编译步骤写成已通过。

## 只读诊断与预览

- 已编译 anim 或已解包三件套：`anim_scml_tool.py` 反编译为 SCML + 符号 PNG；可选离线合成 GIF/胶片条。
- 弹幕类「动画是代码生成的」：分清烘焙 `attack` 循环与 Lua 的染色/拖尾/飞行，见 `references/patterns/asset/animation-build-patterns.md`。
- 预览失败时先确认用途：新动作通常需要 anim.bin，纯换皮可以只有 build.bin 和引用图集，复用已有 build 的动作包也可以只有 anim.bin。再查内部名称、图集引用和 KTEX 解码；不要把合法 build-only 包误报为缺文件。

## 静态图集与库存查询

XML 的 Texture filename 指实际纹理，Element name 指其中区域，二者不必同名。inventoryitem.imagename 通常不带 .tex；RegisterInventoryItemAtlas 的查询键通常带 .tex。Recipe.image、UI Image 的入参分别沿消费者核对，不统一删后缀。

source PNG 尺寸、编译图集尺寸、symbol 几何范围、pivot 和实体缩放是不同层。先查握持点/落点与实际原尺寸，不能以 ZIP 名或图像像素直接推算世界米数。来源见 [图像与动画参考](../../../engineering/dst-mod-engineering/assets-animation.md)。
