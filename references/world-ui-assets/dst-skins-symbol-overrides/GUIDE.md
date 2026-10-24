---
name: dst-skins-symbol-overrides
description: Implement mod-owned appearance variants, animation build swaps, clothing and symbol overrides in Don't Starve Together. Use when changing AnimState builds, overriding symbols for equipment or forms, managing skin-like local variants, registering related atlases, or avoiding conflicts with official skin, entitlement, and trading systems.
---

# DST 外观变体与 Symbol Override

把模组自有外观变体与 Klei 官方皮肤经济分开，只实现可由模组资源和 Lua 合法控制的 Build 与 Symbol。

## 工作流

1. 定义变体影响完整 Build、单个 Symbol、装备 swap、UI 图标还是角色形态，并列出恢复目标。
2. 从原版装备和形态切换查 SetBuild、OverrideSymbol、OverrideItemSkinSymbol 与 ClearOverrideSymbol 的契约。
3. 所有外观切换使用稳定 source 或状态，进入与退出、装备与卸下、加载与重生完全对称。
4. 需要客户端看到的变体通过网络字段或已有 skin/build 数据同步，不读取服务器临时表。
5. 库存、配方、头像和世界动画分别提供正确 Atlas 或 Build 资源。
6. 如果需求涉及官方 entitlement、交易、掉落或受控皮肤发布，明确说明普通模组无法仿造该服务端体系。
7. 测试多个装备覆盖同一 Symbol、皮肤 Build 切换、变身、死亡、重连和资源缺失。

## Symbol 覆盖优先级

当前 `skinner` 会先按角色形态选择 `CLOTHING` 的覆盖表，再与 `symbol_overrides_by_character` 合并。`old_skin` 和 `young_skin` 的 `symbol_overrides_old` / `symbol_overrides_young` 被标记为高优先级，覆盖对应角色的通用表；其他形态通常是角色专用表优先。新增 `young_skin` 分支后，不能继续假定只有 `old_skin` 有形态级优先规则。

同一 symbol 是否存在、是否允许覆盖仍由 `CLOTHING` 的符号列表、Wolfgang 手臂/躯干限制、`symbols_to_use_base` 和 Mod 角色排除规则共同决定。仅设置覆盖表而不提供实际 build/symbol，或忽略 `ClearOverrideSymbol`，仍会出现缺失与残留。

## 多部件与子实体

外观切换不能只看父实体的 `AnimState`。当前 `prefabskin.lua` 中，`thurible` 换皮会同时给父实体和 `inst._body` 调用 `SetSkin(build_name, "thurible")`，清除时分别恢复父实体与 `_body` 的 `"thurible"` build；`king_cane` 换皮还会覆盖 `inst.fx` 上的 `swap_king_cane_art` 和 `king_cane01` 两个 symbol，清除时逐个调用 `ClearOverrideSymbol`。

因此要先列出实际绘制外观的父实体、子实体、特效层及其默认 build/symbol。进入和退出必须覆盖同一组对象，只改父实体可能留下旧子件或特效；只清除父层也可能让子层继续保留换皮 symbol。验证时同时检查换皮、卸下、重载和远端客户端。

需要把多部件皮肤同步到客户端时，可沿用当前 `armor_voidcloth`、`voidclothhat_fx` 和 `bat_bosscorpsehat_fx` 的模式：服务端从拥有物品的 `AnimState:GetSkinBuild()` 取得皮肤 build 哈希，写入 FX 的 `net_hash`；客户端监听 `skinhashdirty`，在 dirty 回调中按每个部件自己的 `fx.build` 调用 `SetSkin(skinbuildhash, fx.build)`。哈希为 0 时改用 `SetBuild(fx.build)` 恢复默认 build。同步的是“皮肤 build 身份”，客户端仍要用目标部件的基础 build/symbol 还原完整外观，不能把父实体直接抄成所有子件。

## 源码锚点

- prefabskin.lua、prefabskins.lua、prefabswaps.lua、skinsutils.lua。
- clothing.lua、beefalo_clothing.lua 与装备 Prefab。
- AnimState OverrideSymbol、ClearOverrideSymbol、SetBuild 调用点。
- skins_defs_data.lua 等只作为官方体系行为参考。
- `components/skinner.lua:113-230`：形态覆盖、按角色覆盖与优先级。
- `skinsutils.lua:GetPrefabSkinsForReleaseGroup`：返回按 prefab 分组的皮肤列表。
- `versioning_skins.lua` 当前以 `{ VERSION = 186 }` 表字段供 `versioning.lua` 和调试命令读取；不要再假定它返回裸字符串。
- `prefabskin.lua:1704-1742`：`thurible` 的 `_body` 子实体皮肤、`king_cane` 的 `fx` 双 symbol 覆盖及各自恢复路径。
- `prefabs/armor_voidcloth.lua:218-276`；`prefabs/hats.lua` 的 voidcloth/bat corpse hat FX：服务端 skin build hash 到客户端 `SetSkin` / 默认 `SetBuild` 的同步路径。

## 不变量

- 不要伪造 entitlement、交易、稀有度或官方拥有状态。
- 清除覆盖时只撤销本模组拥有的层，避免破坏其他装备或模组。
- Build 与 Symbol 名必须来自实际编译资源。
- 视觉变体不能绕过服务器玩法权限。

## 验证

- 装备、卸下、换皮肤和形态切换后符号恢复正确。
- 远端客户端看到相同变体。
- 缺少可选资源时回退基础 Build，不导致 invisible 或崩溃。

