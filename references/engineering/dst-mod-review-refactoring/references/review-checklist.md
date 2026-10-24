# 模组审查清单

## 严重度

- 严重：可崩服、任意客户端改权威状态、破坏存档或无限复制奖励。
- 高：常见流程崩溃、明显不同步、无法清理或旧存档失效。
- 中：边界条件错误、兼容性脆弱、可观察性能问题。
- 低：维护性、诊断性或小范围表现问题。

## 检查域

1. modinfo、入口和配置。
2. GLOBAL、require、Class 和加载时机。
3. Prefab 的 SetPristine 与主客机顺序。
4. Component、Replica、netvar 与 RPC 校验。
5. Action、SG 与 Brain 职责。
6. 事件、任务、睡眠和清理。
7. Component 的 OnSave、OnLoad、LoadPostPass、LongUpdate，以及 Prefab 的 OnSave、OnLoad、OnLoadPostPass、OnLongUpdate。
8. FindEntities、OnUpdate、网络和 FX 性能。
9. UI 焦点、输入和 Kill。
10. 资源路径、动画、Atlas 和字符串。
11. Hook 组合、加载顺序和废弃 API。
12. 专服、洞穴、重连和回滚。

## 单项发现格式

- 严重度
- 文件与行号
- 触发条件
- 实际影响
- 当前源码证据
- 修复方向
- 需要的验证
