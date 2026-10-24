# 功能配方

当用户描述完整的功能形式（如"制作武器"、"制作容器"、"制作生物"或"制作可玩角色"）时，请使用此文件。

此页面是任务入口层：

- 通常涉及哪些文件
- 通常存在哪些组件
- 哪些标签或字符串通常很重要
- 接下来应该打开哪些相邻的参考页面

有关最小代码片段，也请阅读 `references/templates/template-patterns.md`。

## 武器物品

当用户想要一个普通手持武器时使用此模板。

通常涉及：

- `modmain.lua`
  - 将预制件添加到 `PrefabFiles`
- `prefabs/<weapon>.lua`
  - 定义物品预制件
- `images/inventoryimages/<weapon>.xml + .tex`
  - 需要自定义图标时的库存图标图集对
- `anim/<weapon>.zip`
  - 地面或库存动画
- 通常 `anim/swap_<weapon>.zip`
  - 玩家手部的装备视觉
- `strings`
  - `STRINGS.NAMES.<WEAPON>`
  - `STRINGS.CHARACTERS.GENERIC.DESCRIBE.<WEAPON>`

典型组件：

- `inspectable`
- `inventoryitem`
- `weapon`
- `equippable`
- 可选的 `finiteuses`

常见相邻工作：

- 装备回调中的 `owner.AnimState:OverrideSymbol(...)`
- `SetDamage(...)`
- 可选的 `SetProjectile(...)`
- 可选的 `SetOnAttack(...)`

常见路由：

- 阅读 `references/component-patterns.md`
- 阅读 `references/patterns/asset/animstate-patterns.md`
- 阅读 `references/patterns/asset/asset-patterns.md`
- 如果物品需要标准物理、漂浮或闹鬼助手设置，阅读 `references/patterns/prefab/standard-helper-patterns.md`

## 护甲或服装

当用户想要一个改变防御、精神恢复或移动的可穿戴物品时使用此模板。

通常涉及：

- `modmain.lua`
- `prefabs/<item>.lua`
- `anim/<item>.zip`
- 通常 `anim/swap_<item>.zip`
- 如果自定义，库存图标图集对
- `strings`

典型组件：

- `inspectable`
- `inventoryitem`
- `equippable`
- 可选的 `armor`

常见相邻工作：

- 槽位选择
- 装备和卸下回调
- 可穿戴视觉的符号覆盖
- 可选的 `SetAbsorption(...)` 或 `InitCondition(...)`

常见路由：

- 阅读 `references/components/combat/equippable.md`
- 阅读 `references/components/combat/armor.md`
- 阅读 `references/patterns/asset/animstate-patterns.md`

## 容器物品或结构

当用户想要背包、箱子、冰箱或便携式容器时使用此模板。

通常涉及：

- `modmain.lua`
- `prefabs/<container>.lua`
- 可能是 `scripts/widgets/<widget>.lua` 或现有容器 widget 配置
- 如果是库存物品，图标图集对
- `strings`

典型组件：

- 库存物品路由
  - `inspectable`
  - `inventoryitem`
  - 如果可穿戴，`equippable`
  - `container`
- 结构路由
  - `inspectable`
  - `container`
  - 通常 `workable`

常见相邻工作：

- `WidgetSetup(...)`
- 槽位数量和接受规则
- 打开和关闭行为
- replica 端 UI 期望

常见路由：

- 阅读 `references/components/storage/container.md`
- 阅读 `references/components/items/inventoryitem.md`
- 阅读 `references/world-ui-assets/dst-ui-widget-authoring/GUIDE.md`
- 如果交互过滤很重要，阅读 `references/patterns/prefab/tag-patterns.md`
- 如果物品或结构使用标准漂浮器、可燃或障碍物助手，阅读 `references/patterns/prefab/standard-helper-patterns.md`

## 可采摘植物或采集节点

当用户想要浆果、树苗、草药或具有再生功能的世界节点时使用此模板。

通常涉及：

- `modmain.lua`
- `prefabs/<plant>.lua`
- 满、空、贫瘠或再生状态的动画资源
- 掉落物字符串和检查字符串

典型组件：

- `inspectable`
- `pickable`
- 通常 `workable`
- 通常 `lootdropper`

常见相邻工作：

- `SetUp(product, regen, number)`
- 采摘、再生、贫瘠或施肥回调
- 收获状态与生长状态的动画状态更新

常见路由：

- 阅读 `references/components/world/pickable.md`
- 阅读 `references/patterns/world-system-patterns.md`
- 阅读 `references/patterns/asset/animstate-patterns.md`
- 如果植物使用雪、季节、障碍物或闹鬼助手，阅读 `references/patterns/prefab/standard-helper-patterns.md`

## 生物或怪物

当用户想要普通 AI 生物、追随者或类似 Boss 的敌人时使用此模板。

通常涉及：

- `modmain.lua`
- `prefabs/<creature>.lua`
- `brains/<brain>.lua`
- `stategraphs/SG<creature>.lua`
- 动画资源
- 语音或检查字符串

典型组件：

- `health`
- `combat`
- 通常 `lootdropper`
- 通常 `inspectable`
- 通常 `talker`
- 通常来自 standardcomponents 的移动相关世界助手

常见相邻工作：

- `inst:SetBrain(...)`
- `inst:SetStateGraph(...)`
- 重新定位和保持目标逻辑
- SG 中的攻击时机
- 可选的聊天或 Boss 台词

常见路由：

- 阅读 `references/gameplay/dst-brain-authoring/references/brain-node-behaviour-quickref.md`
- 阅读 `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`
- 阅读 `references/components/combat/combat.md`
- 阅读 `references/components/behavior/talker.md`
- 如果生物设置依赖于标准物理、可燃或可冰冻助手，阅读 `references/patterns/prefab/standard-helper-patterns.md`

## 结构

当用户想要工作站、机器、祭坛、可部署建筑或可检查的世界道具时使用此模板。

通常涉及：

- `modmain.lua`
- `prefabs/<structure>.lua`
- 配方和放置器注册
- 动画资源
- 如果需要，小地图或库存资源
- 字符串

典型组件：

- `inspectable`
- 通常 `workable`
- 可选的 `container`
- 可选的 `prototyper`
- 可选的 `trader`
- 可选的 `fueled`、`burnable`、`hauntable`

常见相邻工作：

- `AddRecipe2(...)`
- `MakePlacer(...)`
- 放置间距和标签
- 结构状态动画和声音
- 可选的光效或特效助手

常见路由：

- 阅读 `references/patterns/world-system-patterns.md`
- 阅读 `references/patterns/recipe/recipe-patterns.md`
- 如果结构发光或发射特效，阅读 `references/patterns/asset/effects-patterns.md`
- 如果结构使用标准可燃、障碍物、雪或闹鬼助手，阅读 `references/patterns/prefab/standard-helper-patterns.md`

## 可玩角色

当用户想要完整的角色模组而非普通生物时使用此模板。

通常涉及：

- `modmain.lua`
- 角色预制件文件
- 语音字符串
- 如果本地化，运行时 i18n 文件
- 头像、地图图标、选择屏幕或库存图标资源
- 可选的 `scripts/prefabs/skilltree_<name>.lua`
- 可选的自定义 SG 或玩家行为的 post-init 钩子

典型组件或系统：

- 通过 `prefabs/player_common.lua` 的玩家预制件钩子
- `MakePlayerCharacter(...)`
- 生存属性调整
- `STRINGS.CHARACTERS.<NAME>` 下的角色特定字符串
- 可选的自定义制作、动作、RPC 或 UI
- 可选的技能门限配方或进度

常见相邻工作：

- 从 `modinfo.lua` 分类模组类型
- 从 `modmain.lua` 注册角色
- 从 `STRINGS.CHARACTERS.GENERIC` 继承角色语音
- 谨慎地修补玩家初始化
- 决定角色是否确实需要技能树

常见路由：

- 阅读 `references/patterns/character/character-patterns.md`
- 如果请求实际上是玩家全局补丁而非单个角色的本地身份，阅读 `references/patterns/player-patterns.md`
- 阅读 `references/patterns/runtime-i18n-patterns.md`
- 阅读 `references/patterns/runtime-i18n-patterns.md`
- 阅读 `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`
- 如果角色有技能门限或角色门限制作，阅读 `references/patterns/recipe/recipe-patterns.md`
- 如果添加了自定义客户端可见系统，阅读 `references/core/dst-networking-rpc/references/network-contract.md`

## 发光、特效或音效驱动的预制件

当用户主要想要表现行为而非属性丰富的游戏玩法对象时使用此模板。

通常涉及：

- 预制件文件
- 动画资源或图集资源
- 可选的着色器或粒子纹理
- 可选的声音事件

典型标签或实体部分：

- `FX`
- 可选的 `NOCLICK`
- `AddLight()`
- `AddSoundEmitter()`
- `AddAnimState()`
- 可选的 `AddVFXEffect()`

常见路由：

- 阅读 `references/patterns/asset/effects-patterns.md`
- 阅读 `references/patterns/asset/animstate-patterns.md`
- 阅读 `references/patterns/asset/asset-patterns.md`

## 世界预设、自定义选项或起始位置

当用户想要主机可选择的世界选项、预设面向的调整或自定义生成起始位置时使用此模板。

通常涉及：

- `modworldgenmain.lua`
  - 生成侧注册
- 有时 `modservercreationmain.lua`
  - 主机面向的设置或预设面向的前端行为
- `scripts/map/customize.lua`
  - 类别和选项路由
- `scripts/map/levels.lua`
  - 预设查找和组合预设行为
- `scripts/map/startlocations.lua`
  - 起始位置定义

典型助手：

- `AddCustomizeGroup`
- `AddCustomizeItem`
- `RemoveCustomizeGroup`
- `RemoveCustomizeItem`
- `AddStartLocation`
- 有时 `AddLevelPreInit`
- 有时 `AddTaskSetPreInit`

常见相邻工作：

- 选择 `LEVELCATEGORY.SETTINGS` 与 `LEVELCATEGORY.WORLDGEN`
- 确认更改是面向预设、面向生成还是两者兼而有之
- 检查组合预设行为
- 验证主机设置 UI 刷新行为

常见路由：

- 阅读 `references/patterns/world/worldgen-patterns.md`
- 阅读 `references/task-playbook.md`
- 阅读 `references/mod-api-map.md`

## 经验法则

- 使用此页面将请求的功能映射到可能的文件集。
- 然后打开狭窄的子系统页面获取确切的实现细节。
- 如果用户给出负面约束（如"无限耐久度"或"不可检查"），移除通常会存在的默认部分。