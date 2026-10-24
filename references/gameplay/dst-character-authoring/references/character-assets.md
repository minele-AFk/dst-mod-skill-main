# 模组角色资源与注册辅助 API

本页说明模组角色在各 UI 中的固定资源路径、头像覆盖和角色列表辅助 API。依据当前安装版 `characterutil.lua`、`recipes_filter.lua`、`widgets/targetindicator.lua`、`widgets/inventorybar.lua`、`screens/morguescreen.lua`、`prefabs/player_common.lua`、`components/skinner.lua`、`networking.lua` 和 `modutil.lua`；游戏更新后重新核对。

下文 `<c>` 代表角色 Prefab 名。

## 1. 资源清单

| 用途 | Atlas 路径 | 元素名 | 缺失时 |
|---|---|---|---|
| 选人大立绘（无皮肤） | `bigportraits/<c>.xml` | `<c>.tex` | 空白或报错 |
| 选人大立绘（有皮肤） | `bigportraits/<c>_none.xml` | `<c>_none_oval.tex`，回退 `<c>_none.tex` | 日志提示无效 portrait |
| 名字图（灰） | `images/names_<c>.xml` | `<c>.tex` | 名字图不显示 |
| 名字图（金，可选） | `images/names_gold_<c>.xml`；本地化后缀可能为 `_cn` | `<c>.tex` | 回退灰色名字图 |
| 头像 | `images/avatars/avatar_<c>.xml` | `avatar_<c>.tex` | 使用 `avatar_mod.tex` 等回退 |
| 鬼魂/状态头像 | `images/avatars/avatar_ghost_<c>.xml`，可带 `_1`/`_2`/`_3` | 同名 `.tex` | 目标指示器图标缺失 |
| 制作栏角色过滤器 | `images/crafting_menu_avatars/avatar_<c>.xml` | `avatar_<c>.tex` | 回退普通头像 |
| 自检按钮 | `images/avatars/self_inspect_<c>.xml` | `self_inspect_<c>.tex` | 回退通用自检图标 |
| 讣告（Morgue） | `images/saveslot_portraits/<c>.xml` | `<c>.tex` | 图标缺失 |
| 小地图 | 通过 `AddMinimapAtlas` 注册 | `<c>.png` | 地图不显示角色图标 |

- `MOD_AVATAR_LOCATIONS[<c>]` 可改头像目录；制作栏头像用 `MOD_CRAFTING_AVATAR_LOCATIONS`。
- 每张图在 `Assets` 中声明 `Asset("ATLAS", xml)` 和 `Asset("IMAGE", tex)`；前端选人图还要确认 `FrontEndAssets` 能在建服前端阶段加载。
- 小地图图标名由 `player_common.lua` 固定为 `<c>.png`。可在 XML 中使用该元素名，或在 `common_postinit` 中改 `inst.MiniMapEntity:SetIcon(...)`。
- `images/selectscreen_portraits/` 在当前脚本中没有消费者，属于旧教程遗留，不要要求提供。

## 2. 皮肤与角色注册

`AddModCharacter(name, gender, modes)` 只调用一次，并显式传 `'FEMALE'`、`'MALE'`、`'ROBOT'`、`'NEUTRAL'` 或 `'PLURAL'`。角色名、Prefab 名、字符串键和资源名保持一致并使用唯一前缀。

只有实际提供皮肤时才添加 `STRINGS.SKIN_NAMES` 等皮肤键；基础角色缺少可选皮肤时应仍能选择、生成和重连。

## 3. `ExcludeClothingSymbolForModCharacter`

```lua
ExcludeClothingSymbolForModCharacter("mychar", "torso")
ExcludeClothingSymbolForModCharacter("mychar", "arm_upper")
```

- 作用：应用衣物时跳过该角色被排除的 symbol，避免衣物覆盖角色特殊身体部件。
- 只影响衣物 symbol 覆盖，不影响角色皮肤 build 和装备的 `OverrideSymbol`。
- 每个 symbol 单独调用一次；查询时会遍历所有已启用模组的排除表。

## 4. `RemoveDefaultCharacter`

```lua
RemoveDefaultCharacter("wilson")
```

- 把原版角色加入 `MODCHARACTEREXCEPTIONS_DST`；选人、大厅、衣柜和服务器生成校验都使用同一张表。
- 只接受 `DST_CHARACTERLIST` 中的原版角色名，其他名字只打印警告。
- 影响所有玩家的可选角色，通常应做成 modinfo 选项，并说明已有存档中使用该角色时的后果。

## 5. 验证清单

- 新建、重选、死亡、复活、换洞穴、断线重连和保存重载后头像、名字图、小地图均正确。
- 没有皮肤时基础角色仍可选中；有皮肤时默认皮肤和无皮肤回退都可用。
- 远端客户端看到相同头像、状态后缀和目标指示器。
- 制作栏过滤器、Morgue、自检按钮没有使用错误的回退图。

本页于 2026-10-22 对照安装版 `characterutil.lua:9-100`、`targetindicator.lua:175-205`、`recipes_filter.lua:5-20`、`player_common.lua:2444` 与 `modutil.lua:92-97,928-971`；未执行真实角色选择或远端客户端 UI 测试。
