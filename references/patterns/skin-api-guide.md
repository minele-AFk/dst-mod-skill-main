# SkinAPI 指南

当任务涉及 **[FL] SkinAPI** 模组时使用本文件，这是一个用于在饥荒联机版中创建和管理自定义人物及物品皮肤的第三方库。

官方模组：
- Steam: MySora (workshop-1638724235)
- WeGame: 穹の空 (workshop-2199027653598519351)
- 版本: v1.19

## 快速上手

```lua
-- 在 modmain.lua 中，设置 GLOBAL.SoraAPI = env 之后
SoraAPI.MakeCharacterSkin(base, skinname, data)
SoraAPI.MakeItemSkin(base, skinname, data)
SoraAPI.MakeItemSkinDefaultData(base, itemimg, itemanim, data)
```

## 核心 API 参考

### MakeCharacterSkin

创建人物皮肤：

```lua
MakeCharacterSkin(base, skinname, data)
```

| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| `base` | string | 是 | 基础人物预制物名称 |
| `skinname` | string | 是 | 唯一的皮肤标识符 |
| `data.name` | string | 是 | 显示名称 |
| `data.des` | string | 否 | 描述文本 |
| `data.quotes` | string | 否 | 选人界面引用语 |
| `data.rarity` | string | 否 | 稀有度（默认为"Loyal"） |
| `data.raritycorlor` | table | 否 | 稀有度颜色 {R,G,B,A} |
| `data.skins` | table | 是 | 皮肤 build 映射 |
| `data.init_fn` | function | 否 | 皮肤应用时调用 |
| `data.clear_fn` | function | 否 | 皮肤移除时调用 |
| `data.skin_tags` | table | 否 | 用于过滤的标签 |
| `data.assets` | table | 否 | 额外资源 |

```lua
MakeCharacterSkin("sora", "sora_dress", {
    name = "连衣长裙",
    des = "悠!快出來...\n你在哪儿?",
    quotes = "悠......",
    rarity = "总之就是非常可爱",
    raritycorlor = {255/255, 215/255, 0/255, 1},
    skins = {
        normal_skin = "sora_dress",
        ghost_skin = "ghost_sora_build",
    },
    skin_tags = {"BASE", "sora", "CHARACTER"},
    init_fn = function(inst) print("dress_init") end,
    clear_fn = function(inst) print("dress_clear") end,
})
```

### MakeItemSkin

创建物品皮肤：

```lua
MakeItemSkin(base, skinname, data)
```

| 参数 | 类型 | 必填 | 说明 |
|-----------|------|----------|-------------|
| `base` | string | 是 | 基础物品预制物名称 |
| `skinname` | string | 是 | 唯一的皮肤标识符 |
| `data.name` | string | 是 | 显示名称 |
| `data.atlas` | string | 否 | 背包图标 atlas 路径 |
| `data.image` | string | 否 | 背包图标名称 |
| `data.build` | string | 否 | 动画 build 名称 |
| `data.bank` | string | 否 | 动画 bank 名称 |
| `data.anim` | string | 否 | 动画名称 |
| `data.animloop` | boolean | 否 | 是否循环播放动画 |

```lua
MakeItemSkin("cookpot", "cookpot_portable", {
    name = "便携锅",
    atlas = "images/inventoryimages1.xml",
    image = "portablecookpot_item",
    build = "portable_cook_pot",
    bank = "portable_cook_pot",
})
```

### MakeItemSkinDefaultData

设置物品无皮肤时的默认外观：

```lua
MakeItemSkinDefaultData(base, itemimg, itemanim, data)
```

```lua
-- 完整参数
MakeItemSkinDefaultData("cookpot",
    {atlas="images/inventoryimages/sora2sword.xml", image="sora2sword"},
    {bank="cookpot", build="cookpot", anim="idle", animloop=false},
    {temp="111"})

-- 默认图标: "images/inventoryimages/"..name..".xml", image=name
-- 默认动画: bank=name, build=name, anim='idle', 循环播放
MakeItemSkinDefaultData(name, {}, {nil, nil, 'idle', true})

-- 最小化: 仅覆盖图标，保持原有动画
MakeItemSkinDefaultData(name, {}, {})
```

### 工具函数

| 函数 | 说明 |
|----------|-------------|
| `GetSkin(name)` | 根据名称获取皮肤数据 |
| `GetAllSkin()` | 获取所有人物和物品皮肤 |
| `GetSkinBase(name)` | 获取皮肤对应的基础预制物 |
| `MakeSkinNameMap(base, skinname)` | 将皮肤名称链接到另一个基础预制物 |
| `GetSkinMap(skinname)` | 解析映射的皮肤名称 |
| `GetSkinMapByBase(base)` | 获取链接到某基础预制物的所有皮肤 |
| `GetItemSkinDefaultData(base)` | 获取物品的默认数据 |

## 所有权系统

SkinAPI 通过 Hook `TheInventory` 提供自定义所有权检查：

```lua
-- 自定义所有权检查（客户端）
data.checkfn = function(inventory, name, ...)
    return true  -- 或自定义逻辑
end

-- 自定义所有权检查（服务端验证客户端）
data.checkclientfn = function(inventory, userid, name, ...)
    return true
end
```

默认情况下，所有模组皮肤都被视为"已拥有"。

## UI 集成

SkinAPI 自动 patch 以下 UI 组件：

1. **配方弹窗** (`widgets/recipepopup`)
   - 替换默认皮肤图标
   - 显示自定义皮肤的背包图标

2. **制作菜单皮肤选择器** (`widgets/redux/craftingmenu_skinselector`)
   - 相同的图标替换逻辑

3. **角色选择界面** (`widgets/redux/loadoutselect`)
   - 使模组角色出现在 `DST_CHARACTERLIST` 中
   - 为模组角色启用基础皮肤选择

4. **开箱弹窗**（非侵入式）
   - 使用 `SkinAPIThankYouPopup(...)` 实现礼物开箱兼容性

## 皮肤切换机制

### 物品皮肤初始化/清理

当物品皮肤被应用时：

```lua
function basic_skininit_fn(inst, skinname)
    -- 设置 bank, build, anim
    -- 更新背包图标
    -- 调用自定义 skininit_fn
end

function basic_skinclear_fn(inst, skinname)
    -- 恢复默认 bank, build, anim
    -- 恢复默认背包图标
    -- 调用自定义 skinclear_fn
end
```

### 人物皮肤初始化/清理

通过 Hook `skinner` 组件的 `SetSkinName` 实现：

```lua
-- 从旧皮肤切换到新皮肤时：
old_skin.clear_fn(inst, old)
new_skin.init_fn(inst, new)
```

## 高级特性

### 自定义稀有度

SkinAPI 自动注册自定义稀有度字符串和颜色：

```lua
-- 如果稀有度不存在，会自动添加到：
-- STRINGS.UI.RARITY[rarity] = 显示名称
-- SKIN_RARITY_COLORS[rarity] = {R,G,B,A}
-- RARITY_ORDER[rarity] = 排序顺序
```

### 配方辅助

当 `recipe_help = true`（默认启用）时，SkinAPI 自动将皮肤列表从产品预制物复制到配方名称：

```lua
-- 如果 AllRecipes["aaa_build"].product == "aaa" 且 PREFAB_SKINS["aaa"] 存在：
PREFAB_SKINS["aaa_build"] = PREFAB_SKINS["aaa"]
```

### CreatePrefabSkin 覆盖

SkinAPI 检查 `CreatePrefabSkin` 是否被其他模组修改。如果是，则使用自己的实现来绕过干扰。

## 迁移说明

### v1.12+

使用 `MakeItemSkinDefaultData` 替代已弃用的 `basebuild`、`basebank`、`baseanim`：

```lua
-- 旧版（已弃用）
MakeItemSkin("cookpot", "cookpot_portable", {
    basebuild = "cook_pot",
    basebank = "cook_pot",
})

-- 新版
MakeItemSkinDefaultData("cookpot", {}, {bank="cookpot", build="cookpot", anim="idle", animloop=false})
MakeItemSkin("cookpot", "cookpot_portable", {})
```

### v1.19

`ThankYouPopup` 直接 patch 已禁用。改用 `SkinAPIThankYouPopup`：

```lua
-- 非侵入式方法
local scr = SkinAPIThankYouPopup(...)
```

## 关键内部实现

### 数据结构

```lua
-- 人物皮肤存储
characterskins[skinname] = {
    base_prefab = base,
    ischaracterskins = true,
    -- ... 所有数据字段
}

-- 物品皮肤存储
itemskins[skinname] = {
    base_prefab = base,
    isitemskins = true,
    -- ... 所有数据字段
}

-- 默认物品外观
itembasedata[base] = {
    itemimg = {atlas, image, "default.tex"},
    itemanim = {bank, build, anim, animloop},
    data = {...},
}
```

### Hook 列表

| Hook 目标 | 用途 |
|-------------|---------|
| `TheInventory.CheckOwnership` | 模组皮肤的自定义所有权检查 |
| `TheInventory.CheckClientOwnership` | 服务端所有权检查 |
| `IsDefaultCharacterSkin` | 识别模组人物皮肤 |
| `GetPortraitNameForItem` | 自定义人物肖像名称 |
| `GetFrameSymbolForRarity` | 自定义稀有度边框 |
| `LoadoutSelect._ctor` | 角色列表兼容性 |
| `skinner.SetSkinName` | 人物皮肤切换 |
| `recipepopup.GetSkinOptions` | 背包图标替换 |
| `craftingmenu_skinselector.GetSkinOptions` | 制作菜单图标替换 |
| `Sim.ReskinEntity` | 物品皮肤切换 |

## 最佳实践

1. **使用 `MakeItemSkinDefaultData`** 处理外观与基础预制物不同的物品。

2. **单独注册资源** 通过正常的模组 `Assets` 表。

3. **`checkfn` 仅用于客户端** 所有权检查。使用 `checkclientfn` 进行服务端验证。

4. **使用 `init_fn`/`clear_fn`** 进行运行时调整（如组件修改、粒子效果）。

5. **避免修改核心 SkinAPI 函数** - 改用提供的钩子和回调。

6. **为皮肤名称添加前缀** 避免与其他模组冲突。

## 相关文档

- `references/patterns/skin/skin-patterns.md` - 官方皮肤数据系统
- `references/patterns/asset/animstate-patterns.md` - 动画状态模式
- `references/patterns/character/character-patterns.md` - 模组角色模式