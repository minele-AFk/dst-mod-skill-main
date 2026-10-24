---
name: dst-food-cooking
description: Create Don't Starve Together foods, cooking ingredients, crock-pot recipes, cooker variants, spices, drying behavior, cookbook entries, and edible effects. Use when calling AddIngredientValues or AddCookerRecipe, editing prepared food definitions, calculating recipe priorities and tests, or debugging cookbook and food-stat behavior.
---

# DST 食物与烹饪

先设计食材标签和候选配方竞争关系，再实现成品 Prefab、食用效果与食谱书表现。

## 工作流

1. 定义生食、熟食或料理的 hunger、sanity、health、perish time、foodtype、temperature 和额外效果。
2. 用 AddIngredientValues 给食材提供烹饪标签，避免与现有标签和数值产生非预期候选。
3. 用 AddCookerRecipe 定义 name、test、priority、weight、foodtype、cooktime、potlevel 和 cookbook 条目。
4. 同时检查所有会命中的原版与模组配方；更高 priority 必须有明确理由。
5. 成品 Prefab 配置 edible、perishable、inventoryitem、stackable 和 oneatenfn，并把权威效果放服务器。
6. 需要香料、沃利料理、晾晒或专用 cooker 时分别检查对应管线，不假设普通锅逻辑完全通用。
7. 用边界食材组合、重复标签、不可烹饪物、食谱书未知状态和保存重载测试。

## 源码锚点

- cooking.lua、preparedfoods.lua、preparedfoods_warly.lua、spicedfoods.lua。
- components/edible.lua、stewer.lua、cookable.lua、dryable.lua、perishable.lua。
- cookbookdata.lua、widgets 与 screens 中 cookbook 文件。

## 按需参考

- [pseudo-eating-ability.md](references/pseudo-eating-ability.md) - 伪进食：让正常不能吃的东西（噩梦燃料、启迪碎片等）变得可吃，自定义动作 + 运行时组件 + 手动结算。

## 不变量

- 配方 test 只判断输入，不产生副作用。
- IngredientValues 与 priority 改动可能影响所有锅配方，必须做冲突扫描。
- 食用 Buff 在重复食用、死亡和移除时明确叠加或刷新规则。
- 客户端不直接应用属性变化。

## 验证

- 目标食材组合稳定得到预期料理，邻近组合不会误命中。
- 烹饪锅、便携锅和特殊 cooker 的支持范围明确。
- 料理属性、腐败、食谱书和食用副作用保存重载后正确。

## 配方竞争与产品链

AddCookerRecipe 只登记规则，产品 Prefab、资源和 edible 要单独存在。各 cooker 分别注册；环境包装已经标记 Mod 料理，不需要猜额外 true 开关。AddIngredientValues 会替换对应食材的 tags，改原版食材前保留需要的其他属性。

test(cooker, names, tags) 中 names 是具体食材计数，tags 是累计食材值；缺少键时可能是 nil。精确“几份”用数量比较，不用仅存在检查。烹饪 tags、实体 tag 和 FOODTYPE 枚举是不同集合。

当前 CalculateRecipe 先取最高 priority 档，再按 weight 随机。明确正数 weight：该快照汇总虽有缺省 1，抽取减法却直接读 weight；遗漏不能视为可靠默认。比较候选集合与权重，单次抽到目标菜不能证明冲突处理正确。

调味是另一条数据/实体链：基础料理准入、每种支持香料的配方与变体 Prefab、基础食用回调保留、香料效果、图像和名称。仅加 preparedfood tag 不会自动为任意 Mod 菜生成变体。锅内 overridebuild/overridesymbolname、成品 OverrideSymbol 与库存图集分别核对。

cooktime 的单位沿 stewer 的倍率读取；不是直接把配方数字当秒。食谱图鉴 Cookbook 与 Scrapbook 是不同系统，先确认需求。检查描述使用 STRINGS.CHARACTERS.<角色>.DESCRIBE，不能把 STRINGS.DESCRIBE 当通用入口。

本轮确认 cooking.lua:238-287 与 modutil.lua:636-646；完整链路、支持范围和边界用例查 [料理参考](../../engineering/dst-mod-engineering/cooker-dishes.md)。新菜仍需真实锅、食用、调味、读档和远端图鉴验收。
