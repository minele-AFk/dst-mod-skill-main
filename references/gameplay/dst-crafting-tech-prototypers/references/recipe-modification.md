# 配方后处理与拆解配方

本页说明如何安全修改已注册配方，以及 `AddDeconstructRecipe` 的覆盖边界。依据当前安装版 `modutil.lua` 与 `recipe.lua`；游戏更新后重新核对。

## 1. `AddRecipePostInit`

`AddRecipePostInit(recipename, fn)` 按配方名登记回调：

- 若目标配方已经存在，立即调用一次 `fn(recipe)`。
- 之后通过 `Recipe` 构造器创建的命名配方，在构造末尾调用所有匹配的 `RecipePostInit`。
- 对尚未创建的命名配方，回调会在其创建时触发；对已经创建的同名配方，回调已经执行过一次。

不要把它写成“只影响未来配方”或“只影响已存在配方”的单一规则。需要覆盖任意新配方时用 `AddRecipePostInitAny`，需要精确修改一个稳定配方名时用命名版本。

## 2. `AddRecipePostInitAny`

`AddRecipePostInitAny(fn)` 会：

1. 立即遍历当前 `AllRecipes`，对每个配方调用一次。
2. 登记回调，之后每个 `Recipe` 构造器创建完成后再次调用。

这适合统一补字段、设置默认图标或过滤条件。回调必须对配方类型和字段做存在性检查；不要假设每个配方都有 `ingredients`、`filters`、`placer` 或相同的 `product` 形态。

## 3. 修改字段的边界

配方对象在构造时已经完成一部分字段初始化。后处理可以修改数据字段，但不能假设：

- 修改 `ingredients` 会自动重算所有已缓存的 UI 或科技判定。
- 修改 `filters` 会自动重建所有已创建的过滤器菜单。
- 修改 `product`、`image` 或 `atlas` 会自动刷新已缓存图标。

修改后按消费者检查：制作菜单、角色过滤器、制作站、拆解、旧存档、远端客户端和手柄路径。涉及缓存或已创建 UI 时，使用项目已有的刷新入口，不要直接清空共享表。

## 4. `AddDeconstructRecipe`

```lua
AddDeconstructRecipe("mymod_item", {
    { "goldnugget", 1 },
})
```

当前 `AddDeconstructRecipe(name, return_ingredients)` 创建 `DeconstructRecipe` 并写入 `AllRecipes`。它会覆盖同名配方；若目标名已有普通制作配方或另一拆解配方，后注册者成为最终对象。不要把它当成“追加拆解返回”的 API。

需要保留原配方时：

1. 读取当前 `AllRecipes[name]` 并记录类型和关键字段。
2. 确认该名字确实应作为拆解配方，而不是与制作配方共用。
3. 为拆解配方使用独立、稳定的命名，或在明确覆盖前保存并迁移原对象。
4. 测试制作菜单、拆解菜单、材料扣除、产物和保存重载。

## 5. 验证清单

- 命名配方和 `AddRecipePostInitAny` 各自只执行预期次数，不重复改字段。
- 后创建的命名配方能获得回调，已存在的配方不会漏掉首次执行。
- 修改过滤器、图标或材料后，制作菜单和远端客户端刷新正确。
- `AddDeconstructRecipe` 没有意外覆盖同名制作配方。
- 旧存档和重新加载后配方仍可制作、拆解和正确扣料。

本页于 2026-10-22 对照安装版 `modutil.lua:601-625,784-791` 与 `recipe.lua:160-190`；未执行真实制作菜单或拆解实机测试。
