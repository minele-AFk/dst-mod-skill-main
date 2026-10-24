---
name: dst-crafting-tech-prototypers
description: Create Don't Starve Together recipes, crafting filters, technology requirements, prototypers, character recipes, deconstruction returns, and crafting-station behavior. Use when working with AddRecipe2, AddCharacterRecipe, AddRecipeFilter, TechTree, Ingredient, builder tags or skills, recipe atlases, or crafting UI visibility.
---

# DST 制作、科技与制作站

分别定义配方成本、解锁条件、显示过滤器和制作站范围，避免把 UI 分类当作权限。

## 工作流

1. 定义产物、数量、Ingredients、科技等级、制作站、角色标签或技能、过滤器、图标和放置需求。
2. 在主机与客户端加载的 modmain 路径注册 AddRecipe2；角色专属明确 builder_tag/skill，AddCharacterRecipe 只据这些字段选择默认分类，不自动赋予权限。
3. 需要新分类时调用 AddRecipeFilter({name=..., atlas=..., image=...}, index)，第二参为可选位置；通过 AddRecipe2 的 filters 参数或 AddRecipeToFilter 加入配方，不要手写不受支持的 filter_def.recipes。过滤器只影响展示，不替代服务器权限。
4. 制作站通过 prototyper 与 PROTOTYPER_DEFS 提供科技，明确范围、动画、开启关闭和树等级。
5. 为建筑配方接入 placer 和 min_spacing；为拆解行为定义可接受的返回材料。
6. 检查已废弃 AddRecipe 与 AddRecipeTab 用法并迁移到当前 API。
7. 测试已知/未知配方、靠近/远离制作站、角色限制、技能解锁、手柄菜单和远端客户端制作。

## 源码锚点

- recipe.lua、recipes.lua、recipes_filter.lua、techtree.lua。
- components/builder.lua、builder_replica.lua、prototyper.lua。
- widgets/crafting.lua、crafting_sorting.lua。
- modutil.lua：AddRecipe2、AddCharacterRecipe、AddRecipeFilter、AddPrototyperDef。

## 不变量

- 配方 ID、Prefab 名和库存图标名保持一致或显式配置。
- 服务器重新检查材料、科技、角色和技能条件。
- 不要依赖旧版 RecipeTab API。
- 配置关闭配方时同时处理已缓存菜单与旧存档已有物品。

## 验证

- 配方在正确过滤器、角色和制作站条件下显示。
- 制作、重复制作、材料不足和网络延迟不会重复扣料或产物。
- 放置类配方在无效地形和阻挡位置被服务器拒绝。

## 多来源材料扩展

仅在扩展背包、容器或多个材料 Provider 时应用：先确认它们会不会返回同一个实体，再按实体身份去重并共享剩余数量预算；简单累加查询数量或覆盖已有分配都可能算错。若能证明来源互斥，可保持直接组合。

查询结果和分配方案尚未预留或扣除材料。执行跨延迟、排队或可改变状态的回调后，重新检查实体、归属及可用量；扣除失败时按机制定义撤销/补偿，避免先向玩家交付产物。原版普通制作可能先创建产物实例再扣材料；创建与最终交付不同，不机械重排现有 Builder 全流程。同步且无让出的小操作不必为此引入复杂事务框架，也不把 Lua 每行都解释成会被其他任务抢占。

这两点从 [资源规则候选](../../knowledge/dst-engineering-kb/rules/resource.md) 提炼到制作场景，来源为 E1 单案例静态分析；仍需追踪当前 Builder 的查询、分配和消费链路。针对同一物品被两个来源发现、查询后物品移除、剩余堆叠不足分别验证。

## 按需资源

- [recipe-modification.md](references/recipe-modification.md)：`AddRecipePostInit` / `AddRecipePostInitAny` 的时机、命名配方与后创建配方边界、`AddDeconstructRecipe` 覆盖行为。
- [配方模式](../../patterns/recipe/recipe-patterns.md)：AddRecipe2、过滤器、资源、placer、制作站与自定义科技接入边界。
- [人物专属制作](../../patterns/character/character-crafting-patterns.md)：builder_tag、builder_skill、共享门槛、nounlock、canbuild 和 product 复用。

以上基础与角色示例已按 2026-10-22 本机安装包协调；下游客户端、科技同步和实际制作仍须实机验证。
