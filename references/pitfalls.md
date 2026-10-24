# 常见陷阱

使用此页面作为饥荒联机版常见错误的导航。

仅阅读 `references/pitfalls/` 下你需要的特定页面，或 `references/patterns/` 下的诊断页面：

- [diagnostic-patterns.md](patterns/diagnostic-patterns.md)
  - 预制件、配方、放置器、UI、RPC、副本和大脑失败的症状驱动检查清单
- [debug-techniques.md](patterns/debug-techniques.md)
  - 高级 Lua 调试辅助工具，如 `getupvalue` 和 `setupvalue`，用于窄闭包修补
- [context-pitfalls.md](pitfalls/context-pitfalls.md)
  - `ThePlayer`、本地 UI、`ismastersim` 与 `IsDedicated()` 的区别
- [networking-pitfalls.md](pitfalls/networking-pitfalls.md)
  - `components` 与 `replica`、预制件初始化拆分、服务器/客户端变更边界
- [ui-pitfalls.md](pitfalls/ui-pitfalls.md)
  - 错误的 UI 补丁层、清理泄漏、焦点问题和过宽的前端补丁
- [persistence-pitfalls.md](pitfalls/persistence-pitfalls.md)
  - 保存/加载生命周期错误、加载后引用修复和离线追赶错误
- [shard-pitfalls.md](pitfalls/shard-pitfalls.md)
  - 主分片与次分片错误、迁移假设和分片感知的世界 ID
- [performance-pitfalls.md](pitfalls/performance-pitfalls.md)
  - `FindEntities` 扫描、`AddPrefabPostInitAny`、宽热路径工作
- [crash-playbook.md](pitfalls/crash-playbook.md)
  - 按症状查崩溃：启动/加载、实体贴图动画、API nil、食物料理、联机客户端
- [old-rule-corrections.md](pitfalls/old-rule-corrections.md)
  - 旧教程/旧口诀高影响误诊对照（来源可信度与纠错范围）

## 快速导航

- "在主机上工作但在远程客户端上不工作"
  - 从 [networking-pitfalls.md](pitfalls/networking-pitfalls.md) 开始
- "UI 重复、泄漏或修补了错误的屏幕"
  - 从 [ui-pitfalls.md](pitfalls/ui-pitfalls.md) 开始
- "在主机上工作但在专用服务器上崩溃"
  - 从 [context-pitfalls.md](pitfalls/context-pitfalls.md) 开始
- "它存在，但显示、可制作或可选的是错误的东西"
  - 从 [diagnostic-patterns.md](patterns/diagnostic-patterns.md) 开始
- "我可能需要修补一个封闭的本地辅助函数"
  - 从 [debug-techniques.md](patterns/debug-techniques.md) 开始
- "它在重载或世界时间跳跃之前都能正常工作"
  - 从 [persistence-pitfalls.md](pitfalls/persistence-pitfalls.md) 开始
- "它在主世界上工作但在洞穴或迁移期间崩溃"
  - 从 [shard-pitfalls.md](pitfalls/shard-pitfalls.md) 开始
- "代码技术上可行但感觉太重"
  - 从 [performance-pitfalls.md](pitfalls/performance-pitfalls.md) 开始
- "一开游戏就崩 / 有红字 / 功能全无反应"
  - 从 [crash-playbook.md](pitfalls/crash-playbook.md) 开始
- "按某教程写的，但官方源码对不上"
  - 从 [old-rule-corrections.md](pitfalls/old-rule-corrections.md) 开始