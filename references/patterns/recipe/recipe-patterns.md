# 配方注册、过滤器与放置模式

先读 [制作专题](../../gameplay/dst-crafting-tech-prototypers/GUIDE.md)。本页负责通用注册、资源、过滤器、placer 和制作站边界；角色/技能权限、共享配方与 canbuild 示例集中在 [人物专属制作](../character/character-crafting-patterns.md)。

## 文件与运行端

| 文件/材料 | 责任 |
|---|---|
| `modmain.lua` 或由其加载的模块 | AddRecipe2、过滤器与字符串注册；供主机和客户端加载，不能整体放在 ismastersim 截断之后 |
| `scripts/prefabs/<module>.lua` | 返回产物 Prefab，建筑可同时返回 MakePlacer；用 PrefabFiles 加载文件模块 |
| 字符串 | STRINGS.NAMES、RECIPE_DESC；可检查实体另提供相应 DESCRIBE |
| atlas/tex/anim | 制作图标、产物与预览真实资源；注册配方不会生成资源 |

文件模块名、配方 ID、产物名与 placer 名是不同标识，可保持命名一致方便维护，也可显式配置。详见 [Prefab 契约](../../core/dst-prefab-authoring/references/prefab-contract.md)、[功能配方入口](../../feature-recipes.md)。

## AddRecipe2 注册

modmain 环境使用 `AddRecipe2(name, ingredients, tech, config, filters)`；新工作优先现代 API，旧 AddRecipe/RecipeTab 教程不能直接套用。

```lua
local G = GLOBAL
AddRecipe2("my_mod_item", {
    G.Ingredient("rocks", 2),
}, G.TECH.SCIENCE_ONE, {}, { "TOOLS" })

G.STRINGS.NAMES.MY_MOD_ITEM = "示例物品"
G.STRINGS.RECIPE_DESC.MY_MOD_ITEM = "用石头制作的示例。"
G.STRINGS.CHARACTERS.GENERIC.DESCRIBE.MY_MOD_ITEM = "一个示例。"
```

这里 rocks 取自 [名称表](../../prefabs/物品名字.txt)。项目须另外提供 my_mod_item Prefab、真实资源和加载声明；片段不是完整 Mod。

## 配方配置字段

| 字段 | 用途与边界 |
|---|---|
| product | 产物注册名；可不同于配方 ID，配套处理图标和显示文本 |
| atlas / image | 显式指定制作图标；核对 XML Element、纹理与真实路径 |
| placer / min_spacing | 预览 Prefab 名与间距；不替代服务器有效位置检查 |
| numtogive | 一次配方的产出数量；仍需产物与堆叠等实际支持 |
| nounlock | 阻止普通 UnlockRecipe 将配方永久学会；不等于“强制需要制作站”，还取决于 tech 和其他条件 |
| builder_tag / builder_skill | 实际标签/已注册技能 ID 的门槛，见人物专属制作页 |
| canbuild | 服务器 DoBuild 的额外谓词；不是 UI 显示过滤器，见人物专属制作页的签名 |
| testfn | 额外的 placer 位置测试；与 canbuild 的阶段和参数不同 |

业务留在相关组件、产物和回调，不把未知字段放进 config 后假设生效。配置、科技、范围、角色权限和 UI 分类分别核对。

## AddRecipeFilter 与 AddRecipeToFilter

`AddRecipeFilter(filter_def, index)` 的定义至少有 name、atlas、image，index 是可选插入位置；另配置 `STRINGS.UI.CRAFTING_FILTERS[NAME]`。原版会将 name 转成大写。`filter_def.recipes` 不受支持，注册后内部会重建该列表。

将配方放入已有或新过滤器用 AddRecipe2 的第五参，或 `AddRecipeToFilter(recipe_name, filter_name)`。同一个配方需要多个入口时加多个过滤器，不复制同义配方。

当前 AddRecipe2 对非拆解配方默认加入 MODS；config.nounlock 为真时改进 CRAFTING_STATION，再追加显式 filters。AddCharacterRecipe 有自己的默认路由规则，不能概括成完全相同的包装，见 [角色配方](../character/character-crafting-patterns.md#addcharacterrecipe-与角色权限)。

CHARACTER、TOOLS、WEAPONS、ARMOR、STRUCTURES、FOOD 是展示分类。加入 CHARACTER 不能限制角色；自定义过滤器也不是新的一套角色权限系统。旧独立 RecipeTab 与现代自定义过滤器要区分。

## MakePlacer 与产物

当前 prefabutil.lua 签名为：

`MakePlacer(name, bank, build, anim, onground, snap, metersnap, scale, fixedcameraoffset, facing, postinit_fn, offset, onfailedplacement)`。

建筑模块的返回示意（fn/assets/prefabs 由项目在同一文件定义）：

```lua
return Prefab("my_mod_structure", fn, assets, prefabs),
    MakePlacer("my_mod_structure_placer", "my_mod_structure", "my_mod_structure", "idle")
```

配方 config.placer 指向上述 placer 注册名，产物仍是 my_mod_structure。MakePlacer 生成本地预览实体、添加 CLASSIFIED/NOCLICK/placer 标签和 placer 组件，并配置对齐/动画/可选回调；预览不等于已在服务器生成建筑。

完整基础构造见 [建筑模板](../../core/dst-prefab-authoring/assets/building-template.lua)。部署型物品的部署位置、地形和消费还有自己的执行路径，不把 placer 和实际部署混为一谈。

## 制作站与自定义科技边界

制作站的 prototyper 提供科技树和开启/关闭/激活行为；`AddPrototyperDef(prefab, data)` 注册 PROTOTYPER_DEFS 的元数据，不会自动给实体添加组件或实现科技同步。角色门槛也不自动创建制作站。

同一科技轴上的不同站可配置自己的范围、动画与树等级。需要全新科技轴时，检查当前 techtree.lua 的 AVAILABLE_TECH、TechTree.Create、派生字段缓存、已有 TECH/TUNING.PROTOTYPER_TREES/配方等级，以及 player_classified 的科技 netvar 与 dirty 读取链。

仅追加 `TechTree.AVAILABLE_TECH`、定义 `TECH.MYTECH_ONE` 和 `TUNING.PROTOTYPER_TREES` 不是经过验证的完整接入：当前 techtree 在加载时生成派生字段表，player_classified 另有复制协议。扩展时按目标版本逐端接入并查初始化顺序；本页不提供遗漏这些环节的“可直接运行”模板。

## 图标与症状定位

自定义图标按使用者声明 Asset("ATLAS", ...) 与 Asset("IMAGE", ...)，真实库存图集路径和 Element 要一致；资源具体规则见 [资源模式](../asset/asset-patterns.md)、[纹理模式](../asset/texture-patterns.md)。字符串与本地化见 [本地化模式](../runtime-i18n-patterns.md)。

| 症状 | 优先检查 |
|---|---|
| 配方不存在 | 注册是否在双方加载、唯一 ID、实际启用条件 |
| 分类不正确 | filters、过滤器先注册、AddCharacterRecipe 的配置门槛 |
| 分类有条目但角色权限错误 | builder_tag/skill 的真实来源与服务器/Replica 检查 |
| 图标或描述缺失 | atlas/tex/Element、显示字符串键、产物与配方名差异 |
| 建筑可制作但没有预览 | config.placer、模块返回、bank/build/anim |
| 预览可见但不能放置 | 间距、地形、testfn 与实际服务器执行条件 |
| 离站后行为不符预期 | tech、nounlock、已解锁记录和制作站生命周期 |

2026-10-22 核对本机安装包 modutil.lua、recipe.lua、builder/builder_replica、techtree.lua、prototyper、player_classified 与 prefabutil.lua；未执行真实客户端制作、科技同步、手柄菜单、存档或放置测试。
