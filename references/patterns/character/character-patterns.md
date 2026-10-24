# 角色模式

当任务是可玩角色 mod 而不是普通生物 prefab 时，使用此文件。

如果任务主要涉及入口文件选择，先阅读 `references/core/dst-mod-scaffolding/references/entrypoints.md`。
如果任务主要涉及运行时国际化布局，也请阅读 `references/patterns/runtime-i18n-patterns.md`。
如果任务主要涉及角色进度解锁的配方，也请阅读 `references/patterns/recipe/recipe-patterns.md`。
如果任务主要涉及通用图集、图标或角色特定前端资源之外的动画压缩包，也请阅读 `references/patterns/asset/asset-patterns.md`。
如果任务主要涉及真正的衣柜可选角色皮肤，而不是头像或预览模式，也请阅读 `references/patterns/skin/skin-patterns.md`。

## 可玩角色不从普通生物 Prefab 开始

官方可玩角色通过 `scripts/prefabs/player_common.lua` 构建。

观察到的官方结构：

- 角色 prefab 文件，如 `scripts/prefabs/wilson.lua`、`scripts/prefabs/wendy.lua` 和 `scripts/prefabs/wormwood.lua`
- `local MakePlayerCharacter = require("prefabs/player_common")`
- `return MakePlayerCharacter(name, prefabs, assets, common_postinit, master_postinit, starting_inventory)`

实际结果：

- 不要从普通的 `CreateEntity()` 物品或生物模板开始创建可玩角色
- 首先使用玩家角色模式，然后在 post-init 回调中添加自定义行为

## 典型的 Mod 文件集

通常涉及：

- `modinfo.lua`
- `modmain.lua`
- `prefabs/<character>.lua`
- 运行时字符串文件
- 角色美术和头像资源
- 可选的 `scripts/prefabs/skilltree_<character>.lua`

常见资源系列：

- `images/avatars/`
- `images/map_icons/`
- `images/saveslot_portraits/`
- `images/selectscreen_portraits/`
- `bigportraits/`
- 可选的技能图集或技能背景美术

## 角色前端资源约定

角色 mod 通常除了游戏玩法 prefab 外，还需要前端资源集。

高频文件路径：

- `images/avatars/avatar_<character>.xml`
- `images/avatars/avatar_ghost_<character>.xml`
- `images/avatars/self_inspect_<character>.xml`
- `images/saveslot_portraits/<character>.xml`
- `images/selectscreen_portraits/<character>.xml`
- `images/selectscreen_portraits/<character>_silho.xml`
- `bigportraits/<character>.xml`
- 可选的 `bigportraits/<character>_none.xml`
- 可选的 `images/names_<character>.xml`

观察到的官方消费者：

- `scripts/widgets/targetindicator.lua`
  - 查找 `avatar_<character>.xml` 或 `avatar_ghost_<character>.xml`
- `scripts/widgets/inventorybar.lua`
  - 查找 `images/avatars/self_inspect_<character>.xml`
- `scripts/screens/redux/serverslotscreen.lua`
  - 对于 mod 角色，从 `images/saveslot_portraits/<character>.xml` 解析存档槽位头像
- `scripts/screens/lobbyscreen.lua`
  - 读取 `images/names_<character>.xml`
  - 读取 `bigportraits/<character>.xml`
  - 如果可用，优先使用 `bigportraits/<character>_none.xml`

实用规则：

- 如果角色显示错误的头像或回退美术，在调试游戏玩法代码之前先检查确切的 UI 面向文件路径
- 使用 `AddMinimapAtlas(...)` 注册地图图标，但将头像和头像图集视为具有自己文件名的独立资源

## 大头像命名略有技巧

观察到的官方头像调用：

- 一些前端路径读取 `bigportraits/<character>.xml` 和 `<character>.tex`
- 大厅和装备流程可能优先使用 `bigportraits/<character>_none.xml`
- 大厅路径可能会要求 `_none.xml` 图集提供 `<character>_none_oval.tex`

实际结果：

- 如果您发布 `bigportraits/<character>_none.xml`，请验证它公开的图集元素名称，而不仅仅是纹理文件名
- 当头像选择行为异常时，检查消费屏幕实际请求的图集元素名称

保守的好规则：

- 将常见头像文件命名为与 prefab 完全相同
- 如果您添加 `_none` 或皮肤样式的头像变体，请根据实际前端调用站点进行验证

## `modmain.lua` 中应该放什么

对于角色 mod，`modmain.lua` 通常负责：

- `PrefabFiles = { "<character>" }`
- 顶级共享 `Assets`
- `AddMinimapAtlas("images/map_icons/<character>.xml")`
- `AddModCharacter("<character>", "FEMALE")` 或匹配的性别
- 可选的启动物品粘合代码
- 可选的技能树注册粘合代码

保持根文件作为注册中心。
将实际的玩家 prefab 逻辑移到 `prefabs/<character>.lua`。

## `AddModCharacter(...)` 中的可选角色模式

观察到的官方路由：

- `scripts/modutil.lua`
  - 将第三个 `AddModCharacter(...)` 参数存储在 `MODCHARACTERMODES[name]` 中
- `scripts/widgets/redux/loadoutselect.lua`
  - 如果 `MODCHARACTERMODES[currentcharacter]` 存在，用默认模式加上 mod 定义的模式替换正常的预览模式列表
- 每个模式条目可以公开：
  - `type`
  - `anim_bank`
  - `idle_anim`
  - `play_emotes`
  - `scale`
  - `offset`
- `scripts/widgets/skinspuppet.lua`
  - 使用 `skinmode.type` 进行预览 build 选择
  - 使用 `anim_bank`、`idle_anim`、`scale` 和 `offset` 进行衣柜木偶

实际结果：

- `modes` 表主要是前端预览和衣柜/装备功能
- 它不会自动实现游戏玩法变换、玩家状态逻辑或运行时形态切换
- 当角色有衣柜或装备流程应该循环的替代预览形态时使用它
- 对于只需要普通正常和幽灵表现的普通角色，跳过它

最小结构：

```lua
local character_modes = {
    { type = "young_skin", play_emotes = true },
    { type = "old_skin", play_emotes = true, scale = 0.9 },
}

AddModCharacter("mychar", "FEMALE", character_modes)
```

重要提示：

- `scripts/widgets/skinspuppet.lua` 尝试在基础皮肤数据存在时通过 `GetSkinData("<character>_none").skins[skinmode.type]` 映射 `skinmode.type`
- 保持自定义 `type` 名称与您发布的任何基础皮肤映射对齐
- 如果角色有真正的替代游戏玩法形态，仍然在玩家 prefab、组件和 SG 代码中实现权威运行时行为

## 角色 Prefab 结构

官方角色 prefabs 通常包含：

- 本地 `assets`
- 本地 `prefabs`
- 可选的按游戏模式路由的起始物品栏表
- `common_postinit(inst)`
- `master_postinit(inst)`
- `return MakePlayerCharacter(...)`

实用规则：

- 将客户端可见标签、AnimState 覆盖、netvar 和本地辅助方法放在 `common_postinit` 中
- 将权威属性调整、服务端仅组件和权威监听器放在 `master_postinit` 中

## `player_common.lua` 已经为您提供的内容

在 `scripts/prefabs/player_common.lua` 中观察到：

- 玩家实体部件和常见标签
- talker 和许多基线玩家系统
- 客户端/服务端拆分和 `SetPristine()`
- classified、inventory、locomotor、combat、health、hunger、sanity 和其他基线玩家组件
- `skilltreeupdater`

实际结果：

- 不要手动重建整个玩家基线
- 调整或扩展现有玩家，而不是从头重新添加普通玩家系统
- 角色 mod 通常不需要手动添加 `talker`，因为共享玩家基础已经添加了

## `common_postinit` 与 `master_postinit`

观察到的原版模式：

- `common_postinit`
  - 添加角色身份标签
  - 设置客户端可见动画覆盖
  - 定义本地辅助方法或网络事件
  - 添加属于 pristine 拆分之前的客户端可见组件
- `master_postinit`
  - 分配 `starting_inventory`
  - 调整 `health`、`hunger`、`sanity` 或 combat
  - 添加服务端仅角色组件
  - 注册权威监听器和回调

好规则：

- 如果逻辑依赖于权威组件和真实游戏玩法变更，将其放在 `master_postinit` 中
- 如果逻辑必须在两侧都存在或在客户端/服务端返回拆分之前存在，将其放在 `common_postinit` 中

## 字符串和语音

角色 mod 通常需要两者：

- 常见运行时字符串
- `STRINGS.CHARACTERS.<NAME>` 下的角色语音

推荐路由：

- 常见字符串
  - 运行时字符串文件
- 语音
  - 从 `STRINGS.CHARACTERS.GENERIC` 开始
  - 然后稀疏地覆盖仅差异部分

接下来阅读：

- `references/patterns/runtime-i18n-patterns.md`
- `references/patterns/runtime-i18n-patterns.md`

对于前端标题卡文本，也请验证角色是否应该发布 `images/names_<character>.xml`。

## 可选技能树

将技能树视为可选的角色特定进度，而不是强制性的样板代码。

当角色确实需要以下功能时使用：

- 可解锁的被动加成
- 分支进度
- 技能门控的配方或形态
- 角色特定进度 UI

当角色只需要以下功能时跳过：

- 固定属性
- 固定加成
- 无可解锁进度

## 官方技能树连接

观察到的官方组件：

- `scripts/prefabs/player_common.lua`
  - 向玩家基线添加 `skilltreeupdater`
- `scripts/components/skilltreeupdater.lua`
  - 激活技能、奖励技能经验值、保存技能数据，并路由 RPC/客户端更新
- `scripts/prefabs/skilltree_defs.lua`
  - 存储 `SKILLTREE_DEFS`、`SKILLTREE_ORDERS` 和辅助函数，如 `CreateSkillTreeFor(...)`
- `scripts/prefabs/skilltree_<character>.lua`
  - 返回一个角色技能树的数据模型

实际结果：

- 可玩角色可以没有自定义技能树存在
- 如果添加一个，将其设计为单独的数据模块，而不是将整个树混合到角色 prefab 文件中

## 推荐的 Mod 自有技能树模式

这是从 `scripts/prefabs/skilltree_defs.lua` 和原版 `skilltree_<character>.lua` 文件推断出的推荐 mod 模式。

1. 当树存在时，将 `Asset("SCRIPT", "scripts/prefabs/skilltree_<character>.lua")` 添加到角色 prefab 资源中。
2. 创建 `scripts/prefabs/skilltree_<character>.lua`，返回：
   - `SKILLS`
   - `ORDERS`
   - 可选的 `BACKGROUND_SETTINGS`
   - 可选的 `CUSTOM_FUNCTIONS`
3. 在 `modmain.lua` 或导入的启动文件中，require `prefabs/skilltree_defs`。
4. 构建角色的技能树数据模块。
5. 调用 `CreateSkillTreeFor("<character>", data.SKILLS)`。
6. 填充 `SKILLTREE_ORDERS["<character>"] = data.ORDERS`。
7. 如果存在，填充 `SKILLTREE_METAINFO["<character>"].BACKGROUND_SETTINGS`。
8. 如果存在，填充 `CUSTOM_FUNCTIONS["<character>"]`。

最小注册结构：

```lua
local skilltreedefs = require("prefabs/skilltree_defs")
local BuildMyCharSkillTreeData = require("prefabs/skilltree_mychar")

local data = BuildMyCharSkillTreeData(skilltreedefs.FN)

skilltreedefs.CreateSkillTreeFor("mychar", data.SKILLS)
skilltreedefs.SKILLTREE_ORDERS.mychar = data.ORDERS

if data.BACKGROUND_SETTINGS ~= nil then
    skilltreedefs.SKILLTREE_METAINFO.mychar.BACKGROUND_SETTINGS = data.BACKGROUND_SETTINGS
end

if data.CUSTOM_FUNCTIONS ~= nil then
    skilltreedefs.CUSTOM_FUNCTIONS.mychar = data.CUSTOM_FUNCTIONS
end
```

## 技能树字符串和美术约定

观察到的官方技能树 UI 行为：

- `scripts/widgets/redux/skilltreewidget.lua`
  - 请求名为 `<character>_background.tex` 的背景图像
- `scripts/widgets/redux/skilltreebuilder.lua`
  - 将每个节点 `icon` 值转换为 `<icon>.tex`
  - 通过 `GetSkilltreeIconAtlas(...)` 解析图集
- 原版技能树文件从 `STRINGS.SKILLTREE.<CHARACTER_BUCKET>` 读取本地化文本

实际结果：

- 将节点标题和描述保存在 `STRINGS.SKILLTREE.<UPPERCASE_CHARACTER>` 中
- 每个技能键通常需要一个 `_TITLE` 字符串和一个 `_DESC` 字符串
- 保持节点 `icon` 名称稳定，因为控件通过文件名查找它们
- 如果角色有自定义树背景，将图像命名为 `<character>_background.tex`

推荐的字符串结构：

```lua
STRINGS.SKILLTREE.MYCHAR = {
    MYCHAR_BRANCH_1_TITLE = "Branch One",
    MYCHAR_BRANCH_1_DESC = "Unlocks the first branch.",
}
```

推荐的技能数据结构：

```lua
mychar_branch_1 = {
    title = STRINGS.SKILLTREE.MYCHAR.MYCHAR_BRANCH_1_TITLE,
    desc = STRINGS.SKILLTREE.MYCHAR.MYCHAR_BRANCH_1_DESC,
    icon = "mychar_branch_1",
    root = true,
    group = "core",
    pos = { x = 0, y = 0 },
}
```

重要提示：

- `GetSkilltreeIconAtlas(...)` 背后的确切图集解析器未在正常 Lua 文件中定义
- 当您添加自定义技能图标时，在真实 UI 中验证图集查找是否成功，而不是假设助手会自动找到它们

## 值得记住的技能树数据规则

在 `scripts/prefabs/skilltree_defs.lua` 中观察到：

- 树应该有一个 `defaultfocus` 技能用于控制器导航
- 技能应该通过 `root`、`connects` 或 `locks` 连接
- 超过 32 个实际技能会破坏网络可见性

实际结果：

- 避免浮动技能
- 保持树可读
- 不要过大 modded 树的第一个版本

## 技能门控配方

技能树不仅影响被动属性。
它们还路由到配方门控。

观察到的官方行为：

- `scripts/recipe.lua`
  - 配方数据支持 `builder_skill`
- `scripts/components/builder.lua`
  - 检查建造者是否具有所需技能
- `scripts/components/builder_replica.lua`
  - 在客户端镜像该检查

实际结果：

- 当配方应该从树中解锁时，在 `Recipe2(...)` 上使用 `builder_skill = "mychar_some_skill"`
- 保持技能名称稳定，因为配方、UI 和技能树都依赖相同的键

## 快速路由

- "我需要一个具有属性、标签、头像和语音的普通 modded 角色。"
  - 在基础角色模式处停止
- "我需要用于替代角色形态的衣柜或装备预览。"
  - 添加可选角色模式，并根据预览 build 映射验证模式 `type` 名称
- "我需要 mod 角色的完整官方风格角色皮肤。"
  - 切换到 `references/patterns/skin/skin-patterns.md`，将其视为高级 UI 加数据任务
- "我需要可解锁的加成或技能门控配方。"
  - 添加可选技能树
- "我需要自定义玩家动作或 SG 更改。"
  - 阅读 `references/core/dst-action-authoring/references/action-pipeline.md` 和 `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`
- "我需要本地 UI 或自定义角色面板。"
  - 阅读 `references/world-ui-assets/dst-ui-widget-authoring/GUIDE.md`