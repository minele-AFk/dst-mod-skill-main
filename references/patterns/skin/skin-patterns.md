# 皮肤模式

当任务涉及官方皮肤数据系统时使用本文件：

- `PREFAB_SKINS`
- `CreatePrefabSkin(...)`
- 衣柜或角色选择界面的皮肤选择
- 人物基础皮肤（超出普通肖像和预览模式）

不要将本文件用于普通模组外观变体。

## 第三方皮肤库

当任务涉及 **[FL] SkinAPI** 模组（v1.19）时，请参考：
- `references/patterns/skin-api-guide.md` - SkinAPI 使用完整指南

如果任务只是"切换到另一个 build"、"制作强化形态"或"添加多个外观相同的变体"，请优先使用：

- `references/patterns/asset/animstate-patterns.md`
- `references/core/dst-prefab-authoring/references/prefab-contract.md`
- `references/templates/template-patterns.md`

## 两个不同的问题

请区分这两个概念：

- 模组角色的预览模式
  - `AddModCharacter(name, gender, modes)`
- 真正的官方皮肤数据和衣柜所有权流程
  - `PREFAB_SKINS`, `CreatePrefabSkin(...)`, `TheInventory:CheckOwnership(...)`

模组角色可以使用预览模式，而无需使用完整的官方皮肤库存系统。

## 官方文件参考

首先阅读以下官方文件：

- `scripts/prefabskin.lua`
  - 定义 `CreatePrefabSkin(...)`
- `scripts/prefabskins.lua`
  - 生成 `PREFAB_SKINS` 和 `PREFAB_SKINS_IDS`
- `scripts/prefabs/skinprefabs.lua`
  - 生成皮肤预制物数据
- `scripts/skinsutils.lua`
  - `GetSkinData(...)`, `GetBuildForItem(...)`, `GetPortraitNameForItem(...)`, `GetSkinModes(...)`
- `GetPrefabSkinsForReleaseGroup(releasegroup)` 返回 `prefab → 皮肤列表`，适合按发布组枚举已有皮肤；不要把返回值当成单层数组。
- `scripts/widgets/redux/loadoutselect.lua`
  - 预览模式路由和基础皮肤 UI 行为
- `scripts/screens/redux/defaultskinselection.lua`
  - 所有权限制的皮肤列表构建

## 加载器实际流程

观察到的官方流程：

- `scripts/mods.lua`
  - 在注册模组的 `PrefabFiles` 之前加载 `modmain.lua`
- `scripts/mainfunctions.lua`
  - 通过 `LoadPrefabFile(...)` 加载每个预制物文件
- `scripts/prefabs.lua`
  - 当 `Prefab(name, ...)` 被构造时，将 `PREFAB_SKINS[name]` 中的所有名称追加到该预制物的依赖列表中
- `scripts/skinsutils.lua`
  - `GetAllItemCategories()` 从 `Prefabs` 开始，因此加载的皮肤预制物可以通过 `GetSkinData(...)` 被发现

实际影响：

- 没有专门的 `PrefabSkinFiles` 模组钩子
- 模组皮肤预制物仍然通过普通的 `PrefabFiles` 加载
- 如果模组需要自定义皮肤元数据，应在基础预制物文件加载之前填充 `PREFAB_SKINS.<base_prefab>`，通常在 `modmain.lua` 中

## 模组角色限制

在 `scripts/widgets/redux/loadoutselect.lua` 中观察到：

- `self.have_base_option = table.contains(DST_CHARACTERLIST, self.currentcharacter)`
- 因此模组角色默认不会获得普通的基础皮肤选择器

在 `scripts/screens/redux/defaultskinselection.lua` 中观察到：

- 皮肤选择通过 `TheInventory:CheckOwnership(item_type)` 进行过滤

实际影响：

- 除非同时 patch UI 和所有权假设，否则不要承诺为模组角色提供 Klei 风格的衣柜可选择基础皮肤
- 对于大多数模组角色，预览模式加上普通肖像和资源连接是更稳定的路径

## 人物基础皮肤数据结构

官方人物皮肤条目（如 `wormwood_none`、`wormwood_victorian`、`wurt_none` 和 `wurt_victorian`）使用 `CreatePrefabSkin(...)` 并设置 `type = "base"`。

高频字段：

- `base_prefab`
- `type = "base"`
- `skin_tags`
- 默认 `_none` 皮肤在需要时的 `build_name_override`
- `skins = { normal_skin = ..., ghost_skin = ..., extra_mode = ... }`

观察到的官方示例：

- `wormwood_none`
  - 映射 `stage_2`, `stage_3`, 和 `stage_4`
- `wurt_none`
  - 映射 `powerup`

实际影响：

- `skins` 键是基础皮肤数据和预览模式之间的桥梁
- 默认人物基础皮肤通常命名为 `<character>_none`
- 如果添加自定义预览模式（如 `powerup` 或 `young_skin`），每个真实基础皮肤都应提供匹配的 `skins.<mode_key>` 条目

## Symbol 覆盖与形态优先级

`CLOTHING` 的 `symbol_overrides_*` 不只是资源表。当前 `skinner` 会先按形态取表，再与 `symbol_overrides_by_character[prefab]` 或 `["default"]` 合并：

- `old_skin` 对应 `symbol_overrides_old`。
- 新增的 `young_skin` 对应 `symbol_overrides_young`。
- 这两类形态表的单个 symbol 优先于按角色覆盖；其他形态通常由按角色覆盖优先。

因此同一 symbol 同时存在形态表和角色表时，不能只根据键名猜优先级。还要检查 `CLOTHING[name].symbol_overrides` 是否列出该 symbol、Wolfgang 的手臂/躯干允许条件、`symbols_to_use_base` 与 `ModManager:IsModCharacterClothingSymbolExcluded`。覆盖结束时只撤销本项目拥有的层，确保形态切换、卸装和远端同步后符号恢复。

多部件或子实体的外观切换要按绘制层级成对处理。当前 `thurible` 同时更新父实体和 `_body`，清除时两边都恢复 `"thurible"`；`king_cane` 则覆盖并逐个清除 `inst.fx` 上的 `swap_king_cane_art` 与 `king_cane01`。这可以作为通用检查点：父实体、子实体、特效和各自默认 build/symbol 必须一起进入、一起退出，不能只改最外层 `AnimState`。

多部件皮肤还可能通过独立 FX 实体表现。当前 `armor_voidcloth` 和 voidcloth/bat corpse hat FX 由服务端读取拥有物品的 `AnimState:GetSkinBuild()`，把皮肤 build 哈希写入 `net_hash`；客户端监听 `skinhashdirty` 并调用 `SetSkin(hash, fx.build)`，让每个 FX 在自身基础 build 上恢复对应皮肤，哈希为 0 时用 `SetBuild(fx.build)` 回默认。网络字段只携带身份，部件基础 build、symbol 与资源仍要由客户端正确提供，不能假设父实体换皮会自动传播到所有 FX。

## 高级模组自有数据模式

仅当任务确实需要官方风格的皮肤元数据时才使用此模式。
这不是第一个可玩角色模组的默认路径。

`modmain.lua`:

```lua
PrefabFiles = {
    "mychar",
    "mychar_skinprefabs",
}

PREFAB_SKINS.mychar = {
    "mychar_none",
    "mychar_formal",
}
```

`prefabs/mychar_skinprefabs.lua`:

```lua
local prefs = {
    CreatePrefabSkin("mychar_none", {
        base_prefab = "mychar",
        type = "base",
        build_name_override = "mychar",
        skin_tags = { "BASE", "CHARACTER", "MYCHAR" },
        skins = {
            normal_skin = "mychar",
            ghost_skin = "ghost_mychar_build",
            powerup = "mychar_powerup",
        },
    }),
    CreatePrefabSkin("mychar_formal", {
        base_prefab = "mychar",
        type = "base",
        skin_tags = { "BASE", "MYCHAR", "FORMAL" },
        skins = {
            normal_skin = "mychar_formal",
            ghost_skin = "ghost_mychar_formal",
            powerup = "mychar_formal_powerup",
        },
    }),
}

return unpack(prefs)
```

重要提示：

- 这仅注册皮肤元数据
- 它本身不会授予所有权、添加衣柜 UI 或解锁选择流程
- 通过普通预制物或模组 `Assets` 单独声明真实的动画压缩包和肖像资源
- 当前 `versioning_skins.lua` 暴露 `VERSION = 186` 表字段，`versioning.lua` 与调试命令读取 `.VERSION`；旧代码若把模块当作字符串使用会失效

## 不要盲目复制整个生成的表

官方生成的皮肤数据还包含更深层次的字段，如几何提示、服装身体元数据、胡须链接、声音或特效钩子。

实践规则：

- 仅在阅读匹配的官方人物或物品示例后才复制高级字段
- 如果任务仍然只是"一个模组角色的多个外观"，请停止并使用预览模式或普通运行时 `AnimState` 逻辑

## 快速路由

- "我想要一个在角色选择界面中有替代预览姿态或形态的模组角色。"
  - 使用 `references/patterns/character/character-patterns.md`
- "我想要完整的官方风格人物皮肤数据或衣柜基础皮肤行为。"
  - 阅读本文件并将其视为高级 UI 加数据问题
- "我只需要几个共享游戏玩法的外观变体。"
  - 使用工厂预制物或普通 `AnimState` 模式代替皮肤系统
