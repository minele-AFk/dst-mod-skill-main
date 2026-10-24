---
name: dst-scenarios-setpieces-cutscenes
description: Create Don't Starve Together scenarios, scripted set pieces, staged encounters, and cutscenes. Use when working in scripts/scenarios, map static layouts, scenario callbacks, stage props, NIS sequences, scripted camera or dialogue flow, or ensuring one-shot scenes persist and clean up correctly.
---

# DST Scenario、Setpiece 与演出

把空间布局、触发条件、演出状态、玩家控制和一次性完成标记分离。

## 工作流

1. 定义场景触发者、空间范围、参与实体、可重复性、完成条件、中断条件和保存需求。
2. 静态物件通过 Layout 或 Setpiece 放置；运行时行为放入 Scenario 或控制 Prefab，不在布局数据内塞复杂逻辑。
3. 触发时再次验证玩家、实体和世界状态，并用服务器状态机推进阶段。
4. 对话、动画、声音、相机和 UI 只消费阶段状态；多人场景明确是全体、附近玩家还是单个客户端表现。
5. 临时锁定控制、不可见、无敌、碰撞或相机时保存原状态，并在完成、跳过、断线和异常中断时恢复。
6. 一次性场景保存完成标记；可重复场景保存冷却和当前阶段所需的最小数据。
7. 测试玩家离场、加入中、死亡、跳过、保存中途重载、多个玩家同时触发和实体缺失。

## 源码锚点

- scenarios/：运行时场景脚本。
- map/static_layouts/、map/object_layout.lua：Setpiece 与空间布置。
- nis/：NIS 演出范例。
- 舞台、事件和小游戏 Prefab、SG 与 Screen。

## 不变量

- 演出客户端不能直接修改服务器奖励或世界进度。
- 任何控制锁和相机接管都必须有异常恢复路径。
- 多人场景不要依赖 ThePlayer 代表所有参与者。
- 一次性奖励与完成标记按服务器原子顺序处理。

## 验证

- 正常完成、跳过、失败和断线中断都能恢复玩家状态。
- 保存重载不会重复奖励或卡在中间阶段。
- 未加载客户端或后来加入者不会破坏服务器场景。

