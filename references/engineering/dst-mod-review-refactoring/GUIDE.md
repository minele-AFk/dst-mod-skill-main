---
name: dst-mod-review-refactoring
description: Review and refactor Don't Starve Together mods. Use when auditing Lua code for correctness, master-client authority, save compatibility, event and task cleanup, performance, hook conflicts, deprecated APIs, assets, stategraphs, brains, actions, world generation, or when implementing a scoped cleanup after an evidence-backed review.
---

# DST 模组审查与重构

先按严重度报告可复现问题和源码证据；只有用户要求修改时才进行范围明确的重构。

## 工作流

1. 读取整个目标模组结构、modinfo、所有入口、PrefabFiles、Assets 和自定义 scripts，不根据单个片段下结论。
2. 建立数据流：入口到钩子、Prefab、Component、Brain、SG、Action、RPC、UI 与保存。
3. 优先审查崩溃、数据丢失、客户端信任、重复奖励、无法清理和存档不兼容。
4. 再审查主客机分支、netvar/Replica、事件任务、OnSave/OnLoad、硬覆盖和其他模组兼容。
5. 检查高频扫描、OnUpdate、闭包分配、网络发送、FX 实体和 UI 重建性能。
6. 用当前 data/scripts 验证 API 与原版范例；按严重度、文件行号、触发条件、影响和修复方向输出。
7. 用户要求实施时保留行为边界，分小补丁修改，并运行静态检查与可用测试。

## 源码锚点

- 目标模组全部 Lua、资源清单和配置。
- modutil.lua 与目标使用的原版类、组件、Prefab、SG 和 Brain。
- networkclientrpc.lua、netvars.lua、保存与性能相关框架文件。

## 不变量

- 审查请求本身不授权发布、改服务器或大范围重写。
- 不要把偏好型风格意见与正确性缺陷混为一谈。
- 保留用户现有改动，不覆盖无关文件。
- 无法运行游戏时将结论标为静态验证，不宣称运行通过。

## 验证

- 每项发现有具体触发路径和证据，不列无依据猜测。
- 重构前后公开配置、Prefab ID、存档 schema 和玩家行为保持兼容或明确迁移。
- 测试覆盖修改涉及的主机、客户端、保存和生命周期路径。

## 按需资源

- 需要系统检查项与严重度定义时读取 [review-checklist.md](references/review-checklist.md)。

## 从知识候选到本项目结论

先把知识记录的触发条件映射到当前调用链。E1 案例的同类症状仅是调查方向；例如任务残留需要找到实际长寿命 owner，重复资源需要证实 Provider 重叠，不能仅因命中关键词就报缺陷。

每项发现包含：受影响对象与运行端、前置条件、可达路径、现有证据、修复后的可观察结果。缺少运行复现时写明“静态路径可达/待复现”，不把 failure.runtime_reproduced=false 改写成已重现。

更正记录优先于其明确推翻的旧结论；来源内容缺失或仅有历史哈希时，保留不可复核边界。审查已满足范围后停止，不为凑数量添加风格项。

参见 [知识查询与证据](../../knowledge/README.md) 与 [来源和更正](../dst-mod-engineering/sources-and-corrections.md)。
