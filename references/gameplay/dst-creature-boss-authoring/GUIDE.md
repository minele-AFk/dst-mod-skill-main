---
name: dst-creature-boss-authoring
description: Orchestrate complete Don't Starve Together creatures and bosses. Use when building a mob or boss that combines prefabs, components, brains, stategraphs, combat, phases, minions, loot, networking, persistence, world integration, and multiplayer encounter testing.
---

# DST 生物与 Boss 编排

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

先设计跨 Prefab、Component、Brain、SG、网络和存档的职责表，再分别实现和联调。

## 工作流

1. 写出遭遇规格：生成条件、生态位、属性、阵营、感知、技能、阶段、掉落、离场和重生规则。
2. 选择两个以上相近原版生物或 Boss，分别提取 Prefab 装配、Brain 优先级、SG 技能和阶段管理模式。
3. 将持久阶段、冷却和外部引用放入 Component 或 Prefab；Brain 选择技能意图；SG 执行动画和伤害时间线。
4. 先实现最小可战斗闭环，再逐个加入技能、召唤物、场地机制和阶段转换，每次保持可测试。
5. 为血量、阶段、特殊目标和 UI 提供最小网络状态；所有玩家请求在服务器校验。
6. 定义死亡、脱战、卸载、世界重载、回滚、玩家全灭、召唤物残留和重复生成的清理规则。
7. 用单人、多人、高延迟、洞穴、保存中途重载和极端伤害测试完整遭遇。

## 源码锚点

- prefabs/ 中机制相近的 Boss；先按真实注册/文件名查，不把攻略名称直接当作文件名。
- components/ 中与血量、阶段、技能相关的组件。
- brains/ 和 behaviours/ 中的 Boss 意图范例。
- stategraphs/ 中的多阶段状态范例。

## 不变量

- Boss 阶段数据必须可存档和迁移。
- 召唤物有明确的归属和清理路径，不会在 Boss 死亡后残留。
- 多玩家场景下技能目标选择不会因客户端预测产生重复效果。
- 洞穴和地表切换时 Boss 状态正确迁移或重置。

## 验证

- 每个阶段都能独立触发、持续和退出。
- 高延迟客户端能看到正确的 Boss 状态和动画。
- 保存重载后 Boss 从正确阶段恢复。

## 按需资源

- 需要生物 Prefab 骨架时读取 assets/creature-template.lua，并配套项目真实 Brain/SG 和动画；它不再把三个模块拼成一个不可解析文件，也不默认定义仇恨。
- 需要设计生存生物与 Boss 的防御属性和战斗模式（护甲/减伤、盾反、受击反馈、技能与阶段切换节奏），或参考 Boss 工厂/幻化/浸泡等完整实现时查阅 `references/mod-notes/` 下 [mod-legion.md](../../mod-notes/mod-legion.md)（棱镜 Legion 原始笔记）。
