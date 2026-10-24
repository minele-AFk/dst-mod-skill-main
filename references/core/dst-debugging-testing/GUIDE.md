---
name: dst-debugging-testing
description: Diagnose and test Don't Starve Together mods. Use when investigating load errors, Lua stack traces, nil access, crashes, desync, missing assets, broken actions, save corruption, dedicated-server differences, cave or shard failures, or when building a repeatable multiplayer regression matrix.
---

# DST 调试与测试

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

先保留第一条有效错误和最小复现，再按加载阶段、运行端与生命周期定位根因。

## 工作流

1. 记录游戏版本、启用模组、配置、世界类型、主机/客户端/分片、复现步骤和预期行为。
2. 从日志中提取第一条相关错误、完整堆栈和前置警告；后续连锁 nil 通常不是根因。
3. 按 modinfo 加载、入口加载、Prefab 构造、运行时事件、网络、保存、资源或性能分类。
4. 用最小世界和最少模组复现；冲突问题用二分启用或交换加载顺序。
5. 沿堆栈进入模组代码，再用当前安装包 data/databundles/scripts.zip 中的对应文件 查原版调用契约；不要只在报错行加 nil 判断。
6. 添加带模组前缀、实体 GUID、端类型和状态的临时日志；高频路径做限流。
7. 修复后执行主机、远端客户端、专服、洞穴、保存重载和目标生命周期回归，并移除临时噪声日志。

## 源码锚点

- stacktrace.lua、debugprint.lua、debughelpers.lua：堆栈与调试输出。
- consolecommands.lua、debugcommands.lua、debugkeys.lua：控制台和诊断入口。
- profiler.lua、perfutil.lua：性能诊断。
- mods.lua、modindex.lua：加载阶段错误。

## 不变量

- 不要把未亲自启动的游戏、专服或图形资源测试描述为已通过。
- 不要用吞错、pcall 包裹整段逻辑或无条件 nil return 掩盖状态损坏。
- 先使用只读控制台检查；会生成、删除、回滚或改存档的命令需明确风险。
- 日志中避免输出用户身份、令牌或大表。

## 验证

- 修复能解释第一条错误为何发生，而非只消除最后一个症状。
- 最小复现和原始复现都不再出现问题。
- 测试结果明确区分已执行、静态检查和仍需用户在游戏中验证。

## 按需资源

- 需要让测试/调试代码只在开发环境运行、避免带入发布版时读取 [dev-environment-guard.md](references/dev-environment-guard.md)（开发环境守卫：文件夹名 / 用户名 / 用户 ID 三种判断方式）。
- 需要系统化覆盖测试场景时读取 [test-matrix.md](references/test-matrix.md)（测试矩阵）。
- 需要控制台查询、实体选择、远程执行和坐标边界时读取 [console-commands.md](references/console-commands.md)。
- 需要**按症状查崩溃根因与修法**（启动失败 / 手持无贴图 / API nil / 食物料理 / 联机客户端）时读取 [crash-playbook.md](../../pitfalls/crash-playbook.md)。
- 需要**验证组件/实体方法是否真实存在**（`inventory:Count` 这类语法合法、运行即崩）时运行 `references/tools/general/check_api.py`。
- 需要**旧教程误诊对照**（bank=build=symbol、pcall 全禁、帧数上限等口诀）时读取 [old-rule-corrections.md](../../pitfalls/old-rule-corrections.md)。
- 需要排查/避免常见坑（日志解读盲点、误删状态、错误覆盖、伪修复、prefab 文件名/命名不一致等）时查阅 `references/mod-notes/` 下 [mod-tropical-prefabs-ag.md](../../mod-notes/mod-tropical-prefabs-ag.md)（热带 prefabs A~G 精读，含反面教材清单与模式归纳）。

- 需要按症状选择第一条检查链时读取 [诊断模式](../../patterns/diagnostic-patterns.md)；仅普通暴露点不足、需要局部闭包修改时读取 [debug-techniques.md](../../patterns/debug-techniques.md)。
