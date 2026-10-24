---
name: dst-building-deployment-physics
description: Create Don't Starve Together structures, deployable items, placers, workable objects, collision, physics, burning, destruction, and placement rules. Use when implementing MakePlacer, deployable, workable, construction, obstacle physics, platform-aware placement, hammering, burning, or server-side placement validation.
---

# DST 建筑、部署与物理

让客户端 Placer 提供预览，让服务器用同一规则最终验证并生成持久建筑。

## 工作流

1. 定义部署物、成品建筑、Placer、占地半径、合法地形、平台支持、碰撞层和拆除方式。
2. 从同类建筑复制物理模式，使用 MakeObstaclePhysics、MakeInventoryPhysics 或专用标准函数。
3. 用 MakePlacer 创建纯表现预览；旋转、偏移、网格吸附和动画与成品占地一致。
4. deployable 的 candeployfn 与 ondeploy 在服务器重查位置、阻挡、地皮、船和资源消耗。
5. 建筑添加 workable、burnable、propagator、lootdropper、hauntable 或 repairable，并为损坏/烧毁/拆除定义状态。
6. SetPristine 前设置网络和客户端动画；主机分支保存建造者、耐久、升级和关联实体。
7. 测试岸边、船、洞穴、阻挡边界、旋转、保存重载、燃烧中卸载和多人同时部署。

## 源码锚点

- prefabutil.lua：MakePlacer 与 MakeDeployableKitItem。
- standardcomponents.lua、physics.lua：物理、燃烧、漂浮和碰撞。
- components/deployable.lua、workable.lua、burnable.lua、propagator.lua。
- componentactions.lua 与 actions.lua：DEPLOY、HAMMER 等动作。

## 不变量

- Placer 可放置不代表服务器必须接受，最终条件必须重新计算。
- 改变碰撞时保存并恢复完整 collision mask。
- 烧毁、锤毁和正常移除不能重复掉落。
- 平台相对坐标与世界坐标不要混用。

## 验证

- 客户端预览与服务器放置结果一致。
- 所有摧毁路径正确掉落并清理关联实体和阻挡。
- 多个玩家同时部署同一点不会重叠生成。

