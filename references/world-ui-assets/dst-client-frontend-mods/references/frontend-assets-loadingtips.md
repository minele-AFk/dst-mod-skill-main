# 前端资源与加载提示

本页说明建服前端资源、预加载资源和加载提示的注册边界。依据当前安装版 `modutil.lua`、`mainfunctions.lua`、`mods.lua`、`loadingtipsdata.lua` 与 `constants.lua`；游戏更新后重新核对。

## 1. `FrontEndAssets`

`FrontEndAssets` 只用于 `modservercreationmain.lua` 所服务的建服前端阶段。典型用途是建服界面新增的自定义世界选项图集、图标和 XML。

```lua
-- modservercreationmain.lua
FrontEndAssets = {
    Asset("ATLAS", "images/mymod_customization.xml"),
    Asset("IMAGE", "images/mymod_customization.tex"),
}
ReloadFrontEndAssets()
```

- 先声明资源，再调用 `ReloadFrontEndAssets()`；该函数会使用当前环境的 `FrontEndAssets` 和模组名重建前端资源。
- 不要在普通游戏内 `modmain.lua` 中用 `ReloadFrontEndAssets` 代替 `Assets` 或 `PreloadAssets`。
- 前端阶段通常没有 `TheWorld`、`ThePlayer` 或游戏内 HUD；资源加载成功不等于客户端运行时可用。

## 2. `PreloadAssets`

`PreloadAssets` 用于提前加载客户端运行时需要的资源，尤其适合在玩家进入世界前减少首次显示等待。声明后调用 `ReloadPreloadAssets()`；资源路径和依赖仍要在实际消费者处核对。

不要把前端资源、普通运行时资源和加载提示图标混成一套。前端资源只在建服界面阶段加载，预加载资源面向客户端运行时，世界内 `Assets` 则按 Prefab/模块依赖声明。

## 3. `AddLoadingTip`

```lua
AddLoadingTip(
    STRINGS.UI.LOADING_SCREEN_TIPS,
    "mymod_tip_unique_id",
    "这是模组加载提示。"
)
```

- 第一参是实际字符串表，第二参是唯一 ID，第三参是提示文本。
- ID 必须唯一；用模组前缀避免覆盖原版或其他模组提示。
- `controltipdata` 非空时还会写入 `LOADING_SCREEN_CONTROL_TIP_KEYS`，供控制提示使用。
- 移除时用 `RemoveLoadingTip(stringtable, id)`，同时清理控制提示键。

`AddLoadingTip` 不负责把提示自动加入某个分类。当前加载提示数据从 `STRINGS.UI.LOADING_SCREEN_TIPS` 等表生成权重；自定义分类需要同时核对 `LOADING_SCREEN_TIP_CATEGORIES`、`SetLoadingTipCategoryWeights` 和 `SetLoadingTipCategoryIcon`。

## 4. 分类与权重

当前 `OTHER` 分类的默认权重为 0；仅把文本放进 OTHER 表通常不会让它在正常流程中出现。需要显示时显式设置开始/结束权重，或使用已有分类。

`SetLoadingTipCategoryWeights(weighttable, weightdata)` 会逐键覆盖权重表；`SetLoadingTipCategoryIcon(category, atlas, icon)` 设置分类图标。分类和图标资源仍要按前端/运行时阶段声明。

## 5. 验证清单

- 建服界面新增图标能加载，返回主菜单和再次进入不残留旧资源。
- `FrontEndAssets` 没有混入只在游戏内使用的资源。
- 加载提示 ID 唯一，禁用模组后不残留文本或控制提示键。
- OTHER 分类的提示按预期权重出现，而不是永久为零。
- 服务器未安装纯客户端模组时，客户端仍能启动和进入。

本页于 2026-10-22 对照安装版 `modutil.lua:187-206,975-1009`、`mainfunctions.lua:184-234` 与 `constants.lua:2803-2847`；未执行真实建服界面或加载提示实机测试。
