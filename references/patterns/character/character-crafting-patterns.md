# 人物专属制作：角色标签、技能与权限

基础注册、图标、过滤器与放置流程见 [配方模式](../recipe/recipe-patterns.md)。本页只处理角色/技能门槛、多个角色共享、额外构建条件和产物复用，不重复基本 Prefab/placer 模板。

## AddCharacterRecipe 与角色权限

`AddCharacterRecipe(name, ingredients, tech, config, extra_filters)` 与 AddRecipe2 一样创建 Recipe2。当前 modutil.lua 仅在 config.builder_tag 或 builder_skill 非 nil 时默认加入 CHARACTER；两个字段都没有时给出警告并加入 MODS。它**不会自动识别目标角色、添加标签或建立权限**。

modmain 环境示例：

```lua
local G = GLOBAL
AddCharacterRecipe("my_mod_character_item", {
    G.Ingredient("cutgrass", 3),
    G.Ingredient("flint", 1),
}, G.TECH.NONE, {
    builder_tag = "my_mod_crafter",
}, { "TOOLS" })
```

my_mod_crafter 是项目自有标签，须在实际目标角色的公共初始化路径建立，使客户端判断与服务器一致。片段未提供角色、产物或资源；材料代码名来自 [名称表](../../prefabs/物品名字.txt)。不需要再把相同配方重复加入 CHARACTER；extra_filters 只追加需要的其他入口。

也可用 AddRecipe2 的 config.builder_tag 并显式 filters={"CHARACTER"}，或注册后 AddRecipeToFilter。三种路由都不能绕开 builder 的权限检查；单纯把公开配方放入 CHARACTER 仍是公开配方。

## builder_tag 不是角色 prefab 名

builder_tag 是由 HasTag 检查的单个字符串。标签必须从目标源码/自有角色实际初始化中确认，不能照搬 wilson/willow/wolfgang 等 prefab 名作为标签。当前 Wilson 的角色代码明确有 scientist 标签；这不意味着所有角色都自动有与自身注册名同名的标签。

多个角色共享同一配方时，可在已授权目标角色的公共初始化区赋予同一命名空间标签，并用该单一 builder_tag。它不是标签数组或逻辑 OR；设置 builder_tag="wilson" 再加一个额外 canbuild 检查，不会自动允许其他未满足该 tag 的角色。

通用配方可不设置 builder_tag，但仍检查是否有 builder_skill、科技或其他限制。不复制完整 MakePlayerCharacter 构造器来只加一个标签；按 [角色专题](../../gameplay/dst-character-authoring/GUIDE.md) 的公共初始化合同接入。

## builder_skill 技能 ID

builder_skill 是已注册的技能标识字符串；当前 builder 与 builder_replica 用 skilltreeupdater:IsActivated(recipe.builder_skill) 判断。不是凭空存在的 SKILLS.MY_SKILL 全局常量，也不是一个带技能名称的标签。

仅有技能门槛时可设置 builder_skill；同时设置 builder_tag 与 builder_skill 时需满足相应两项检查。项目自有技能必须先按真实技能树定义注册，并分别验证未激活、激活、重置/换人和重连后的显示与服务器行为。

## canbuild 执行阶段与失败

recipe.lua 保留 config.canbuild；当前服务器 Builder:DoBuild 调用：

`canbuild(recipe, builder, pt, rotation, current_prototyper, skin)` → `success, failure_message_key`。

这是额外的最终构建检查，不能只靠它隐藏客户端配方。它不自动登记“世界只许一个”状态，不预留材料，不代替 builder_tag/skill、材料或位置合同。

```lua
local function CanBuildMyItem(recipe, builder, pt, rotation, prototyper, skin)
    -- my_mod_build_blocked 是由项目维护的实际阻止标签。
    return not builder:HasTag("my_mod_build_blocked")
end
```

将该函数作为配方 config.canbuild；若返回自定义失败键，补齐对应构建失败提示。谓词只读判断，资源消费与产物交付由正确执行链管理。

若玩法要求唯一实体、计数或持久化限制，还要定义生成/移除、读档、取消、排队和失败恢复。TheWorld 上随意放一个标签并不构成完整的唯一性系统；不把查询时满足当成永久预留。

## nounlock 与科技要求

nounlock=true 阻止普通 UnlockRecipe 的永久学习流程；它不是一个直接的“必须靠站”开关。是否离站不可制作取决于所需科技、可用站、其他解锁来源和当前配方状态。TECH.NONE + nounlock 不会凭空生成站需求。

角色标签和技能不会替代科技条件；反过来靠近制作站也不会给玩家附加角色权限。普通角色共享玩法优先表达实际门槛，不为一个角色标签要求凭空扩展科技轴。科技站和自定义轴的接入边界见基础配方页。

## 配方 ID 与 product 复用

一个新配方 ID 可通过 config.product 指向已有 Prefab，不必复制其实现。例如下面只示范对原版 amulet 的另一个配方入口，并沿用其图标；是否应采用这些成本属于项目设计。

```lua
local G = GLOBAL
AddCharacterRecipe("my_mod_amulet_recipe", {
    G.Ingredient("goldnugget", 1),
}, G.TECH.NONE, {
    builder_tag = "my_mod_crafter",
    product = "amulet",
    image = "amulet.tex",
})
G.STRINGS.NAMES.MY_MOD_AMULET_RECIPE = "护符配方"
G.STRINGS.RECIPE_DESC.MY_MOD_AMULET_RECIPE = "制作一件护符。"
```

product、配方 ID、图标和显示文本分别配置；复用已有物品并不自动保证新配方名有本地化。避免把自定义辅助函数命名为 AddCharacterRecipe 覆盖官方 API，尤其不要把自己省略 tech 参数的包装签名当成官方签名。

## 排查与验收

- 双方 modmain 都应注册配方与过滤器，服务器执行最终检查；不能为了“服务端权威”只让服务器知道配方定义。
- 同一配方只需注册一次，多分类用 filters；新增自定义过滤器受现代 API 支持，旧独立标签页教程另行迁移。
- 分别检查角色实际 tag、激活 skill、科技、是否已知、nounlock、图标和入口；配方不显示并不只有缺过滤器一种原因。
- 实机检查目标角色/非目标角色、共享角色、技能重置、制作站远近、重连/读档和服务器拒绝。不要因静态注册无错就标通过。

2026-10-22 核对当前安装包 modutil.lua、recipe.lua、builder.lua、builder_replica.lua 及 Wilson 标签声明；本页示例均未实机运行。
