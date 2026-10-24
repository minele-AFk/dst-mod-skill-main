# 模式索引

按主题查找模式、合同和实战示例；已合并的主题直接指向保留页。

## 入口、启动与文件布局 (startup)

- [entrypoints.md](core/dst-mod-scaffolding/references/entrypoints.md) - 入口阶段、安装类型与兼容标志
- [modinfo-patterns.md](patterns/startup/modinfo-patterns.md) - modinfo配置模式
- [modmain-patterns.md](patterns/startup/modmain-patterns.md) - modmain模式
- [Hook 选择与时序](core/dst-hooking-compatibility/GUIDE.md) - 按目标选最窄钩子

## 预制件与组件 (prefab)

- [prefab-contract.md](core/dst-prefab-authoring/references/prefab-contract.md) - 文件加载、构造、类型组合与变体工厂
- [prefab-authoring-patterns.md](core/dst-prefab-authoring/references/prefab-authoring-patterns.md) - 燃烧、协作、阶段与生命周期设计
- [standard-helper-patterns.md](patterns/prefab/standard-helper-patterns.md) - 标准辅助函数模式
- [component-contract.md](core/dst-component-authoring/references/component-contract.md) - 组件通用性模式
- [tag-patterns.md](patterns/prefab/tag-patterns.md) - 标签模式

## 组件模式

- [component-patterns.md](component-patterns.md) - 组件模式

## 动作系统 (action)

- [action-pipeline.md](core/dst-action-authoring/references/action-pipeline.md) - 注册分层、收集签名与权威执行
- [action-practical-guide.md](patterns/action/action-practical-guide.md) - 动作实践指南

## AI系统 (ai)

- [stategraph-contract.md](gameplay/dst-stategraph-authoring/references/stategraph-contract.md) - 钩子选择、事件消费、时间线与预测
- [stategraph-practical-guide.md](patterns/ai/stategraph-practical-guide.md) - 状态机实践指南
- [brain-node-behaviour-quickref.md](gameplay/dst-brain-authoring/references/brain-node-behaviour-quickref.md) - Brain 入门、优先级、节点与 Behaviour
- [brain-practical-guide.md](patterns/ai/brain-practical-guide.md) - AI大脑实践指南

## 运行时系统 (runtime)

- [module-environments.md](core/dst-lua-runtime/references/module-environments.md) - 加载环境、运行端与全局对象
- [hud-customization.md](world-ui-assets/dst-hud-screens-input/references/hud-customization.md) - 运行时本地UI
- [input-patterns.md](patterns/runtime/input-patterns.md) - 热键、control 与焦点覆写选型；参数见 [TheInput](systems/theinput.md)
- [entity-query-patterns.md](patterns/runtime/entity-query-patterns.md) - 实体查询模式

## 网络系统 (network)

- [network-contract.md](core/dst-networking-rpc/references/network-contract.md) - netvar、Replica、RPC、初值与模板
- [player-network-patterns.md](patterns/network/player-network-patterns.md) - 玩家网络模式
- [protected-call-patterns.md](patterns/network/protected-call-patterns.md) - 保护调用模式
- [shard-patterns.md](patterns/network/shard-patterns.md) - 分片模式

## 持久化 (persistence)

- [persistence-contract.md](core/dst-persistence-migration/references/persistence-contract.md) - 存档生命周期、引用、子实体与模板
- [persistent-string-patterns.md](patterns/persistence/persistent-string-patterns.md) - 持久化字符串模式

## UI系统 (ui)

- [widget-contract.md](world-ui-assets/dst-ui-widget-authoring/references/widget-contract.md) - 模块、控件树、布局、时间与清理
- [ui-patch-patterns.md](patterns/ui/ui-patch-patterns.md) - controls/playerhud/Screen/frontend 的所有权与补丁选择

## 资源与动画 (asset)

- [asset-patterns.md](patterns/asset/asset-patterns.md) - 资源模式
- [texture-patterns.md](patterns/asset/texture-patterns.md) - 纹理模式
- [animation-build-patterns.md](patterns/asset/animation-build-patterns.md) - 动画构建模式
- [animstate-patterns.md](patterns/asset/animstate-patterns.md) - AnimState模式
- [effects-patterns.md](patterns/asset/effects-patterns.md) - 特效模式
- [vfx-particle-practical-guide.md](patterns/asset/vfx-particle-practical-guide.md) - VFX粒子实践指南

## 角色与人物 (character)

- [character-patterns.md](patterns/character/character-patterns.md) - 角色模式
- [character-crafting-patterns.md](patterns/character/character-crafting-patterns.md) - 人物专属制作栏

## 配方系统 (recipe)

- [recipe-patterns.md](patterns/recipe/recipe-patterns.md) - 配方模式

## 皮肤系统 (skin)

- [skin-patterns.md](patterns/skin/skin-patterns.md) - 皮肤模式

## 世界生成 (world)

- [worldgen-patterns.md](patterns/world/worldgen-patterns.md) - 世界生成模式

## 综合参考

- [runtime-i18n-patterns.md](patterns/runtime-i18n-patterns.md) - 少量字符串、语言表与运行时国际化
- [player-patterns.md](patterns/player-patterns.md) - 玩家模式
- [skin-api-guide.md](patterns/skin-api-guide.md) - 皮肤API指南
- [world-system-patterns.md](patterns/world-system-patterns.md) - 世界系统模式
- [feature-recipes.md](feature-recipes.md) - 功能实现配方

## 调试与诊断

- [debug-techniques.md](patterns/debug-techniques.md) - 调试技术
- [diagnostic-patterns.md](patterns/diagnostic-patterns.md) - 诊断模式
- [signatures.md](signatures.md) - 函数签名索引
- [pitfalls.md](pitfalls.md) - 常见陷阱索引
- [official-examples.md](official-examples.md) - 官方示例
- [task-playbook.md](task-playbook.md) - 任务执行手册

## 使用原则

- 当你知道大致子系统但不确定具体页面时，从这里开始
- 当参数顺序是问题时，跳转到 [signatures.md](signatures.md)
- 当代码已经存在但行为异常时，跳转到 [pitfalls.md](pitfalls.md)
