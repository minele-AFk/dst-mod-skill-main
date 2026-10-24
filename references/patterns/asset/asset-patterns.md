# 资源模式

当任务添加动画压缩包、物品栏图标、小地图图像、前端资源或图集引用时，使用此文件。
如果任务特别涉及灯光、特效 prefab、粒子特效或声音播放逻辑，也请阅读 `references/patterns/asset/effects-patterns.md`。
如果任务特别涉及图集打包、TEX/XML 解包或 PNG 调整大小工作流，也请阅读 `references/patterns/asset/texture-patterns.md`。
如果任务主要涉及字符串或本地化，阅读 `references/patterns/runtime-i18n-patterns.md` 而不是用文本逻辑膨胀资源注册。

## Prefab 资源

Prefab 文件通常在顶部附近声明 `assets` 表：

```lua
local assets =
{
    Asset("ANIM", "anim/my_item.zip"),
    Asset("MINIMAP_IMAGE", "my_item"),
}
```

在官方 prefab 中观察到的常见资源类型：

- `Asset("ANIM", "anim/<name>.zip")`
- `Asset("MINIMAP_IMAGE", "<name>")`
- `Asset("SOUND", "sound/<name>.fsb")`

实用规则：

- 保持 prefab 资源路径相对于 mod 根目录
- 只注册 prefab 实际需要的资源

常见拆分：

- 视觉或声音资源声明
  - 属于这里
- 运行时播放逻辑、符号覆盖或特效生成流程
  - 属于 prefab、SG 或 `references/patterns/asset/effects-patterns.md`

## Mod 级别 `Assets`

`modmain.lua` 也可以定义顶级 `Assets = { ... }`。

观察到的加载器流程：

- mod 加载器创建默认的 `Prefab("MOD_"..modname, nil, mod.Assets, prefabnames, true)`
- 这为 mod 包收集 mod 级资源

实际用途：

- 全局 mod 资源
- 不绑定到单个 prefab 文件的共享图集或图像
- 被多个 prefab 文件引用的共享美术

## 物品栏图像和图集

对于物品图标，mod 通常依赖图集/xml 加上纹理对。

典型的资源声明可能包括：

```lua
Asset("ATLAS", "images/inventoryimages/my_item.xml")
Asset("IMAGE", "images/inventoryimages/my_item.tex")
```

当配方或 UI 元素需要图标图集时，保持图集路径显式。

实际结果：

- 仅纹理文件不够
- 配方、物品栏或 UI 代码通常还需要显式图集路径

纹理工作流规则：

- 资源注册属于这里
- 图集生成、图集提取和 PNG 调整大小属于 `references/patterns/asset/texture-patterns.md`

## 小地图图像

对于小地图图标，prefab 文件通常声明：

```lua
Asset("MINIMAP_IMAGE", "my_prefab")
```

资源名称应该与 prefab 期望的小地图图像资源匹配。

`modutil.lua` 还公开：

```lua
AddMinimapAtlas(atlaspath)
```

当小地图图集必须显式注册时使用。

## 前端和预加载资源

从 `scripts/modutil.lua` 观察到的 mod 环境助手：

```lua
FrontEndAssets = { ... }
PreloadAssets = { ... }
ReloadFrontEndAssets()
ReloadPreloadAssets()
```

仅当任务特别需要前端仅或预加载资源行为时使用这些。

对于大多数游戏玩法 prefab，普通 `assets` 或 mod 级别 `Assets` 就足够了。

## 加载器现实

在 `scripts/mods.lua` 中观察到：

```lua
Prefab("MOD_"..modname, nil, mod.Assets, prefabnames, true)
```

实际结果：

- 顶级 `Assets` 成为 mod 默认加载器 prefab 的一部分
- 这就是为什么共享 mod 资源可以放在 `modmain.lua` 中，即使没有单个游戏玩法 prefab 拥有它们

## 资源和字符串交叉检查

当功能"看起来缺失"时，检查资源和字符串两侧：

- 配方可见但图标缺失
  - 可能是资源或图集连接问题
- 图标存在但制作物品文本为空
  - 可能是 `STRINGS` 侧问题
- 运行时语言环境加载器工作正常但某些图标路径损坏
  - 语言环境和资源注册是分开的问题

## 常见失败点

- 资源文件存在但从未声明
  - 加载器永远看不到它
- 图集和图像路径与引用它们的代码不一致
  - 制作或 UI 图标查找中断
- 共享资源被保存在一个 prefab 本地的 `assets` 表中，即使多个系统需要它
  - 将其移到顶级 `Assets`
- 尝试通过编辑字符串或语言环境文件来解决资源问题
  - 错误的子系统

## 经验法则

- 将 prefab 本地资源放在该 prefab 文件的 `assets` 表中。
- 将共享 mod 资源放在顶级 `Assets` 中。
- 对 UI 或物品栏图标资源使用图集/图像对。
- 仅当小地图注册需要时使用 `AddMinimapAtlas`。
- 如果用户要求打包、解包或调整纹理文件大小，切换到 `references/patterns/asset/texture-patterns.md`。