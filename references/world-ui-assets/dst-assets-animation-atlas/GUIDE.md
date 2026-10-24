---
name: dst-assets-animation-atlas
description: Manage Don't Starve Together animations, builds, atlases, and textures. Use when creating AnimState, build files, texture atlases, frame timing, and asset pipeline workflows.
---

# DST 动画、Build 与图集

先识别资源使用者和要改的层，再选择已有可用工具编译；动画播放、图片替换与网络状态分别处理。

## 工作流

1. 从同类原版调用核对 ZIP 路径、bank、build、animation、symbol 和 layer；这些名字可以不同。
2. 用 SetBank/SetBuild/PlayAnimation/PushAnimation 选择资源；单符号替换用 OverrideSymbol。不要套用未确认的 SetVisual/AddEnum 接口。
3. 库存与 UI 图片沿 PNG → TEX → XML Texture/Element → 调用者 image 名检查；图集 XML 是资源映射，build.bin 是动画图像数据，两者不同。
4. 按用途选择 build-only、animation-only 或两者都有的 ZIP，不为凑“三件套”伪造缺失文件。
5. 发现当前工具路径、版本和 help，再在独立输出目录编译。SCML、Spine JSON、编译 BIN 不是可直接互换的输入；不依赖未确认存在的 tex_atlas_tool.py/scml_build_tool.py。
6. 核对产物内部名称、依赖图集、pivot、朝向和透明边缘，再在真实客户端检查地面、装备、库存与目标动作。

## 名称合同

| 内容 | 使用者 |
|---|---|
| anim/xxx.zip | Asset("ANIM", ...) |
| bank / animation | anim.bin；SetBank 与 PlayAnimation |
| build / symbol / symbol frame | build.bin；SetBuild 与 OverrideSymbol |
| XML Element 名 | Image、配方、库存图集查询，通常包含 .tex |
| XML Texture filename | 实际 TEX 路径；不必等于每个 Element 名 |

Assets 在 modmain 或相关 Prefab 按依赖声明；modinfo 只配置如 modicon 等元信息，不是通用动画资源清单。自定义动作名不要求与原版完全相同，只需与目标 bank 一致。

## 验证与资源

- 检查输入、编译日志、真实产物和调用链；离线预览不能证明游戏加载或远端表现。
- 原图、源工程与已批准设计保留，处理输出不覆盖母版；实际 64/256 等交付尺寸按任务验收。
- [资源管线](references/asset-pipelines.md)：缺图/缺动作与 build-only 判断。
- [KTEX 格式](references/ktex-format.md)：只读解析与诊断，不用于伪造容器。
- [UI 图集注册](references/ui-atlas-registration.md)：库存图、小地图、剪贴簿、技能树图标和角色技能树背景的注册键、`.tex` 与缓存边界。
- [工具与资源补充](../../engineering/dst-mod-engineering/assets-animation.md)：编译工具发现、库存图集和装备符号。
- 已有只读工具见 references/tools/general/anim_scml_tool.py 及本专题 tools/；先看各自 help/文件头，不猜路径。
- 外部资产参考 [asset-sample-archive.md](references/asset-sample-archive.md) 的访问仍受项目授权限制。
