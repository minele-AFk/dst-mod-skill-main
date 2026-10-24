# DST 专题与详细文档索引

完整保留原有专题目录，按当前任务读取，不默认加载全部文档。新增工程工具与知识库见 [融合工程入口](engineering/dst-mod-engineering/README.md)。

本索引第二区的 50 个 `GUIDE.md` 是流程主入口；后面的模式、组件和工程补充页提供专项细节，遇到同主题时先以主专题确定任务边界。旧模式页和融合工程细节页的具体归属可查询 [专题路由表](knowledge/document-routes.json)，或执行 `knowledge topics --query '关键词'`；该表是导航关系，不增加事实证据。

## 二、专题参考文档库

共 50 个专题：49 个按 4 大类别存放于 `references/<分类>/<skill名>/GUIDE.md`，另有 1 个独立目录（reverse-engineering/）。

### 核心基础 (core/) — 11 个

| 专题文档                                                                                                                                                                                      | 职责                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------- |
| [dst-source-research](core/dst-source-research/GUIDE.md)               | 搜索源码、追踪调用链和原版范例     |
| [dst-lua-runtime](core/dst-lua-runtime/GUIDE.md)                       | Class、GLOBAL、模块和调度环境      |
| [dst-component-authoring](core/dst-component-authoring/GUIDE.md)       | Component 设计、Replica 与生命周期 |
| [dst-hooking-compatibility](core/dst-hooking-compatibility/GUIDE.md)   | PostInit、包装和模组兼容           |
| [dst-events-tasks-lifecycle](core/dst-events-tasks-lifecycle/GUIDE.md) | 事件、任务、睡眠和清理             |
| [dst-networking-rpc](core/dst-networking-rpc/GUIDE.md)                 | netvar、Replica 与 RPC 处理        |
| [dst-persistence-migration](core/dst-persistence-migration/GUIDE.md)   | 保存、加载、引用和数据迁移         |
| [dst-action-authoring](core/dst-action-authoring/GUIDE.md)             | Action、BufferedAction 与预测      |
| [dst-debugging-testing](core/dst-debugging-testing/GUIDE.md)           | 日志、最小复现与测试矩阵           |
| [dst-mod-scaffolding](core/dst-mod-scaffolding/GUIDE.md)               | modinfo 与各入口脚手架             |
| [dst-prefab-authoring](core/dst-prefab-authoring/GUIDE.md)             | 网络安全的 Prefab 构造             |

### 玩法系统 (gameplay/) — 16 个

| 专题文档                                                                                                                                                                                                          | 职责                      |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| [dst-stategraph-authoring](gameplay/dst-stategraph-authoring/GUIDE.md)                     | SG 状态、时间线和预测     |
| [dst-brain-authoring](gameplay/dst-brain-authoring/GUIDE.md)                               | Brain 与 Behaviour Tree   |
| [dst-combat-weapons-projectiles](gameplay/dst-combat-weapons-projectiles/GUIDE.md)         | 战斗、武器、护甲与弹道    |
| [dst-creature-boss-authoring](gameplay/dst-creature-boss-authoring/GUIDE.md)               | 生物和 Boss 跨系统编排    |
| [dst-character-authoring](gameplay/dst-character-authoring/GUIDE.md)                       | 可玩角色跨系统编排        |
| [dst-skilltree-authoring](gameplay/dst-skilltree-authoring/GUIDE.md)                       | 角色技能树                |
| [dst-food-cooking](gameplay/dst-food-cooking/GUIDE.md)                                     | 食物、料理与食谱          |
| [dst-inventory-equipment-containers](gameplay/dst-inventory-equipment-containers/GUIDE.md) | 物品、装备与容器          |
| [dst-status-buffs-survival](gameplay/dst-status-buffs-survival/GUIDE.md)                   | 生存属性、Buff 与 Debuff  |
| [dst-followers-mounts-pets](gameplay/dst-followers-mounts-pets/GUIDE.md)                   | 随从、宠物和坐骑          |
| [dst-crafting-tech-prototypers](gameplay/dst-crafting-tech-prototypers/GUIDE.md)           | 配方、科技与制作站        |
| [dst-building-deployment-physics](gameplay/dst-building-deployment-physics/GUIDE.md)       | 建筑、部署、Placer 与物理 |
| [dst-plants-farming-regrowth](gameplay/dst-plants-farming-regrowth/GUIDE.md)               | 植物、农作物与再生        |
| [dst-world-systems-events-weather](gameplay/dst-world-systems-events-weather/GUIDE.md)     | 世界系统、事件和天气      |
| [dst-ocean-boats-fishing](gameplay/dst-ocean-boats-fishing/GUIDE.md)                       | 海洋、船和海钓            |
| [dst-worldgen-authoring](gameplay/dst-worldgen-authoring/GUIDE.md)                       | TaskSet、Task、Room 与生成 |

### 世界/UI/资源 (world-ui-assets/) — 17 个

| 专题文档                                                                                                                                                                                                               | 职责                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| [dst-ui-widget-authoring](world-ui-assets/dst-ui-widget-authoring/GUIDE.md)                     | Widget 控件编写                      |
| [dst-hud-screens-input](world-ui-assets/dst-hud-screens-input/GUIDE.md)                         | HUD、Screen 与全局输入               |
| [dst-assets-animation-atlas](world-ui-assets/dst-assets-animation-atlas/GUIDE.md)               | 动画、Build、Atlas 与纹理            |
| [dst-fx-vfx-authoring](world-ui-assets/dst-fx-vfx-authoring/GUIDE.md)                           | FX 与粒子特效                        |
| [dst-audio-camera-effects](world-ui-assets/dst-audio-camera-effects/GUIDE.md)                   | 音频、音乐与相机控制                 |
| [dst-shader-authoring](world-ui-assets/dst-shader-authoring/GUIDE.md)                           | 着色器与后处理效果                   |
| [dst-worldgen-layouts-retrofit](world-ui-assets/dst-worldgen-layouts-retrofit/GUIDE.md)         | Static Layout、Setpiece 与旧世界补丁 |
| [dst-tiles-map-minimap](world-ui-assets/dst-tiles-map-minimap/GUIDE.md)                         | 地皮、地图和小地图                   |
| [dst-shards-caves-portals](world-ui-assets/dst-shards-caves-portals/GUIDE.md)                   | 分片、洞穴与迁移                     |
| [dst-scenarios-setpieces-cutscenes](world-ui-assets/dst-scenarios-setpieces-cutscenes/GUIDE.md) | 场景、布景与演出                     |
| [dst-client-frontend-mods](world-ui-assets/dst-client-frontend-mods/GUIDE.md)                   | 纯客户端和建服前端扩展               |
| [dst-localization-speech](world-ui-assets/dst-localization-speech/GUIDE.md)                     | 本地化与角色台词                     |
| [dst-skins-symbol-overrides](world-ui-assets/dst-skins-symbol-overrides/GUIDE.md)               | 模组外观变体和 Symbol                |
| [dst-character-parts](world-ui-assets/dst-character-parts/GUIDE.md)                             | 按 Spriter/SCML 模板的人物拆件       |
| [dst-texture-style](world-ui-assets/dst-texture-style/GUIDE.md)                                 | 匹配 DST 画风的透明纹理              |
| [dst-make-scml-animation](world-ui-assets/dst-make-scml-animation/GUIDE.md)                     | SCML 动作设计与审计                  |
| [dst-action-create-workflow](world-ui-assets/dst-action-create-workflow/GUIDE.md)               | 角色动作制作全流程（三视图→拆件→OpenSpine骨骼→SCML导出与官方编译→游戏接入） |

### 工程化 (engineering/) — 5 个

| 专题文档                                                                                                                                                                                                 | 职责                       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| [dst-performance-profiling](engineering/dst-performance-profiling/GUIDE.md)       | 性能监控、热点定位与优化   |
| [dst-workshop-release](engineering/dst-workshop-release/GUIDE.md)                 | 创意工坊发布准备与检查     |
| [dst-api-update-diff](engineering/dst-api-update-diff/GUIDE.md)                   | 游戏更新后的模组兼容性检查 |
| [dst-dedicated-server-testing](engineering/dst-dedicated-server-testing/GUIDE.md) | 专服与多分片测试           |
| [dst-mod-review-refactoring](engineering/dst-mod-review-refactoring/GUIDE.md)     | 证据驱动的审查与重构       |

### 逆向分析 (reverse-engineering/) — 1 个（独立目录，不在 engineering 下）

| 专题文档                                                                                                                                                                        | 职责                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------ |
| [dst-reverse-engineering](reverse-engineering/GUIDE.md)                                                                                                             | 混淆 mod 分析与架构笔记  |
| [解密案例与保护形态](reverse-engineering/decryption-case-patterns.md)                                                                                               | 跨案例保护识别与恢复边界 |

使用示例：调用主 skill 后，按需读取 [联机专题](core/dst-networking-rpc/GUIDE.md)。本索引只负责定位文档，专题均不作为独立 skill 调用；具体步骤见 [任务指南](task-playbook.md)，跨系统契约不足时再读 [融合补充](engineering/dst-mod-engineering/README.md)。

---

## 三、Mod基本结构

理解 mod 的目录布局，以及 modinfo.lua（元数据/配置）与 modmain.lua（注册中心）的写法。完整文档如下：

- 创建/引导新 mod 的最小文件集与默认值：[mod-bootstrap.md](mod-bootstrap.md)
- modmain.lua 职责、环境传递、PrefabFiles/Assets、modimport 拆分：[modmain-patterns.md](patterns/startup/modmain-patterns.md)
- modinfo.lua 元数据、兼容性标志、configuration_options、本地化：[modinfo-patterns.md](patterns/startup/modinfo-patterns.md)
## 四、全局函数与API

常用全局函数（查找实体、实体操作、时间、数学）速查与安全边界见：

- 高频运行时全局函数速查表：[module-environments.md](core/dst-lua-runtime/references/module-environments.md)
- 实体扫描（FindEntity/FindPlayers/FindEntities）参数与性能：[entity-query-patterns.md](patterns/runtime/entity-query-patterns.md)
- 权威性判断与 ThePlayer/TheWorld 使用：[module-environments.md](core/dst-lua-runtime/references/module-environments.md)
## 五、常用组件速查

按组件名查阅说明与代码示例：

- 完整组件文档：[components/](components/)（20+ 组件，按生存/战斗/存储/物品等细分）
## 六、核心游戏机制

核心机制的公式、数值表与实现方式见对应分支：

- 战斗系统、攻击伤害公式、攻速、火焰固定伤害：[combat.md](components/combat/combat.md)
- 标签系统：[tag-patterns.md](patterns/prefab/tag-patterns.md)
- 合成配方（AddRecipe2 等）：[recipe-patterns.md](patterns/recipe/recipe-patterns.md)
- 人物专属制作栏：[character-crafting-patterns.md](patterns/character/character-crafting-patterns.md)
## 七、设计模式与最佳实践

### 7.1 组件设计

组件通用性（动态前缀、按需网络变量、Init 方法）与主客机组件优越性详见：[component-contract.md](core/dst-component-authoring/references/component-contract.md)、[component-patterns.md](component-patterns.md)

### 7.2 网络与同步

网络变量类型（`net_bool`/`net_int`/`net_float`/`net_string`/`net_entity`）与使用时机详见：[network-contract.md](core/dst-networking-rpc/references/network-contract.md)、[player-network-patterns.md](patterns/network/player-network-patterns.md)

### 7.3 性能优化

避免 `Update()` 中做复杂计算、用 `DoPeriodicTask()` 替代高频事件、善用缓存等陷阱详见：[performance-pitfalls.md](pitfalls/performance-pitfalls.md)

---

## 八、分支文档索引

### 组件参考（20+）

- [combat.md](components/combat/combat.md) - 战斗系统
- [health.md](components/survival/health.md) - 生命组件
- [weapon.md](components/combat/weapon.md) - 武器组件
- [equippable.md](components/combat/equippable.md) - 可装备组件
- [armor.md](components/combat/armor.md) - 护甲组件
- [inventory.md](components/storage/inventory.md) - 背包组件
- [container.md](components/storage/container.md) - 容器组件
- [edible.md](components/items/edible.md) - 可食用组件
- [cookable.md](components/items/cookable.md) - 可烹饪组件
- [blinkstaff.md](components/system/blinkstaff.md) - 瞬移杖组件
- [recallmark.md](components/system/recallmark.md) - 召回标记组件
- [worldmigrator.md](components/system/worldmigrator.md) - 世界迁移器组件
- [inventoryitemtemperature.md](components/system/inventoryitemtemperature.md) - 物品温度扩展
- [useabletargeteditem.md](components/items/useabletargeteditem.md) - 定向使用与停止使用物品
- [deflectable.md](components/combat/deflectable.md) - 可偏转实体
- [full list...](components/)

### 设计模式（30+）

- [component-contract.md](core/dst-component-authoring/references/component-contract.md) - 组件通用性
- [effects-patterns.md](patterns/asset/effects-patterns.md) - 特效模式
- [network-contract.md](core/dst-networking-rpc/references/network-contract.md) - 网络模式
- [brain-node-behaviour-quickref.md](gameplay/dst-brain-authoring/references/brain-node-behaviour-quickref.md) - AI大脑模式
- [stategraph-contract.md](gameplay/dst-stategraph-authoring/references/stategraph-contract.md) - 状态机模式
- [tag-patterns.md](patterns/prefab/tag-patterns.md) - 标签模式
- [common-abilities.md](patterns/character/common-abilities.md) - 常用能力添加（防脱手、免疫击退、攻击倍率修正等）

### 实战案例（分类）

#### 人物与角色系统

- [case-player-character.md](cases/case-player-character.md) - 联机人物模板
- [case-custom-creature.md](cases/case-custom-creature.md) - 自定义生物

#### 技能与属性系统

- [case-skill-tree.md](cases/case-skill-tree.md) - 技能树系统
- [case-skill-wheel.md](cases/case-skill-wheel.md) - 技能轮盘
- [case-custom-stat.md](cases/case-custom-stat.md) - 自定义能力值（魔力值、怒气值等）
- [case-custom-debuff.md](cases/case-custom-debuff.md) - 自定义Buff/Debuff系统
- [ability-index.md](ability-index.md) - 能力系统索引（角色/装备可获得的被动与增益能力的统一归口）

#### 物品与装备系统

- [case-weapon-armor.md](cases/case-weapon-armor.md) - 武器和护甲系统（含雷电、冰杖、瞬移等特殊属性）
- [case-weapon-system.md](cases/case-weapon-system.md) - 武器系统

#### 传送系统

- [case-teleport-system.md](cases/case-teleport-system.md) - 传送系统模板（含瞬移、召回、跨碎片传送、急援技能）

#### 任务与交易系统

- [case-quest-system.md](cases/case-quest-system.md) - 任务系统模板（含稀有度、刷新、建筑交互）
- [case-shop-system.md](cases/case-shop-system.md) - 商店系统模板（含双货币、等级解锁、特价商品）

#### UI与视觉效果

- [case-dynamic-portrait.md](cases/case-dynamic-portrait.md) - 动态立绘

#### 基础组件开发

- [case-custom-component.md](cases/case-custom-component.md) - 自定义组件

### 实战指南

- [stategraph-practical-guide.md](patterns/ai/stategraph-practical-guide.md) - 状态机实战
- [brain-practical-guide.md](patterns/ai/brain-practical-guide.md) - AI大脑实战
- [network-contract.md](core/dst-networking-rpc/references/network-contract.md) - 网络同步实战
- [action-practical-guide.md](patterns/action/action-practical-guide.md) - 动作系统实战
- [vfx-particle-practical-guide.md](patterns/asset/vfx-particle-practical-guide.md) - VFX粒子特效实战

### 项目管理

- [file-management-patterns.md](patterns/project/file-management-patterns.md) - 文件管理模式

### 测试与调试工具链

- [dst-server-test-toolchain.md](testing/dst-server-test-toolchain.md) - DST 无头服务器 Lua 快速测试工具链（向运行中的专用服务器注入 Lua 代码并取回结果，含桥接模组源码 `testing/dst_test_mod/` 与 Python 工具链 `references/tools/testing/`）
  - 适用：已授权独立测试环境中的自动化测试和调试；Python 工具链保留 macOS 布局，Windows 待移植，不可直接视为本机可用
- [release-checklist.md](testing/release-checklist.md) - 发布前自检清单（代码正确性 / 资产 / 数值一致 / 功能验证 / 打包）
- [crash-playbook.md](pitfalls/crash-playbook.md) - 崩溃排雷手册（症状 → 根因 → 修法对照表）
- [old-rule-corrections.md](pitfalls/old-rule-corrections.md) - 旧教程/旧口诀纠错索引（高影响误诊对照）

### 参考资料

- [item-name-reference.md](prefabs/item-name-reference.md) - 物品名称参考（代码名与中文名称映射）
- [dst-wiki-scrape.md](tools/dst-wiki-scrape.md) - DST 维基在线数据抓取（6873 篇文章，用于查询原版物品/生物/机制说明）
- [recipe-patterns.md](patterns/recipe/recipe-patterns.md) - 配方模式
- [character-crafting-patterns.md](patterns/character/character-crafting-patterns.md) - 人物专属制作栏
- [full list...](patterns/)

### 常见陷阱

- [networking-pitfalls.md](pitfalls/networking-pitfalls.md) - 网络陷阱
- [performance-pitfalls.md](pitfalls/performance-pitfalls.md) - 性能陷阱
- [context-pitfalls.md](pitfalls/context-pitfalls.md) - 上下文陷阱
- [persistence-pitfalls.md](pitfalls/persistence-pitfalls.md) - 持久化陷阱
- [shard-pitfalls.md](pitfalls/shard-pitfalls.md) - 分片陷阱
- [ui-pitfalls.md](pitfalls/ui-pitfalls.md) - UI陷阱
- [crash-playbook.md](pitfalls/crash-playbook.md) - 崩溃排雷（启动/实体/API/食物/联机 症状对照）
- [old-rule-corrections.md](pitfalls/old-rule-corrections.md) - 旧规则纠错（来源可信度与高影响误诊）

### 函数签名

- [entityscript-signatures.md](signatures/entityscript-signatures.md) - EntityScript 方法
- [hook-signatures.md](signatures/hook-signatures.md) - modutil 注册 API
- [helper-signatures.md](signatures/helper-signatures.md) - 高频辅助函数
- [runtime-signatures.md](signatures/runtime-signatures.md) - 运行时全局变量

### 系统组件与全局对象

- [animstate.md](systems/animstate.md) - AnimState 动画播放与控制
- [light.md](systems/light.md) - Light 光照与光源控制
- [physics.md](systems/physics.md) - Physics 物理、碰撞与速度
- [thefrontend.md](systems/thefrontend.md) - TheFrontEnd 前端与屏幕切换
- [theinput.md](systems/theinput.md) - TheInput 键鼠输入监听

### 实用模板

- [template-patterns.md](templates/template-patterns.md) - 按功能选择最小起步模板
- [network-contract.md](core/dst-networking-rpc/references/network-contract.md) - 服务器/客户端网络实现模板
- [persistence-contract.md](core/dst-persistence-migration/references/persistence-contract.md) - 实体/世界保存最小实现模板

### 索引与速查手册

- [quick-reference.md](index/quick-reference.md) - 常用API、组件和模式速查
- [patterns.md](patterns.md) - 模式索引（patterns/ 分组导航）
- [pitfalls.md](pitfalls.md) - 陷阱导航（按症状定位错误）
- [signatures.md](signatures.md) - 签名查询导航
- [feature-recipes.md](feature-recipes.md) - 功能配方（"制作武器/容器/生物/角色"等任务入口）
- [mod-api-map.md](mod-api-map.md) - modutil.lua 注册 API 紧凑路由映射
- [task-playbook.md](task-playbook.md) - 任务决策树（编码前检查与文档路由）
- [official-examples.md](official-examples.md) - 官方示例索引（按子系统找原版文件）
- [official-files.md](official-files.md) - 官方文件映射（本地安装路径速查）

---
