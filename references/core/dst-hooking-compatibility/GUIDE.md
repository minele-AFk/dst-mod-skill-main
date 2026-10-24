---
name: dst-hooking-compatibility
description: Extend Don't Starve Together code through supported hooks and compatibility-safe wrappers. Use when applying prefab, component, brain, stategraph, recipe, player, class, or widget post-inits, wrapping methods, coordinating multiple mods, or replacing fragile direct overrides.
---

# DST 钩子与兼容性补丁

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

优先使用公开 PostInit 与注册 API，把修改做成可组合、幂等且能检测失效的补丁。

## 工作流

1. 确定修改对象及其创建时机，选择最窄的 AddPrefabPostInit、AddComponentPostInit、AddBrainPostInit、AddStategraphPostInit 或 AddClassPostConstruct。
2. 读取 modutil.lua 中对应钩子的调用顺序、参数和作用域，再检查目标原版实现。
3. 只修改所需字段或方法；包装函数时保存旧函数，原样转发 self、可变参数和多返回值。
4. 为重复加载或多个 Prefab 实例添加幂等标记，但不要在共享类表上误用实例标记。
5. 对可选组件、其他模组字段和版本差异做 nil 检查与特性检测。
6. UI、事件和任务钩子记录清理路径；实体或 Widget 移除时解除监听。
7. 使用至少两个加载顺序测试本模组与可能冲突的模组。

## 源码锚点

- modutil.lua：全部官方 Add 开头钩子与注册函数。
- mods.lua：模组初始化、优先级和环境。
- entityscript.lua：组件、事件与移除生命周期。
- widgets/、screens/：ClassPostConstruct 常见目标。

## 不变量

- 不要编辑或复制覆盖 data/scripts 原文件。
- 不要为了一个实例修改所有实例共享的类方法，除非需求明确如此。
- 不要吞掉原函数返回值、错误或副作用。
- 无法安全组合的硬替换必须显式说明冲突范围。

## 验证

- 单独启用、重复初始化和不同加载顺序均不会重复注册。
- 原版行为在未命中新增条件时保持不变。
- 更新后若目标字段或签名改变，补丁能给出明确失败信息。

## 按需资源

- 需要查看、新增或包装引擎 userdata（TheNet / TheSim / AnimState / SoundEmitter 等）方法时读取 [userdata-method-extension.md](references/userdata-method-extension.md)。
- 需要选择玩家、世界组件或 PostInit 时机，避免 `AddPlayerPostInit` 和 `TUNING` 缓存陷阱时读取 [post-init-hooks.md](references/post-init-hooks.md)。
- 需要实现「封锁目标治疗」、排查效果一直残留重进才消失、或反制他人对 health.DoDelta 的实例覆盖时读取 [heal-block-restore.md](references/heal-block-restore.md)。
- 需要让某个已有生物不再对玩家做特定动作（如防啜食者扑头、拦截扑头/抓取判定）时读取 [creature-behavior-override.md](references/creature-behavior-override.md)。
- 需要分析原版受击链、自定义受击链、自定义血量落值、限伤/无敌/锁血和死亡事件之间的覆盖关系，或设计一条大部分减伤无法阻止、同时保留明确保护的攻击路径时读取 [custom-damage-death-layers.md](references/custom-damage-death-layers.md)。
- 需要展开真实伤害的完整穿透模板、血上限削减、字段守卫、`ForceKill`/直接落值、死亡副作用回滚或位面免疫双开关时读取 [custom-damage-settlement-and-rollback.md](references/custom-damage-settlement-and-rollback.md)。
- 需要 modmain 全部公开钩子签名与注册函数速查时读取 dst-mod-scaffolding 下 [modmain-api-reference.md](../dst-mod-scaffolding/references/modmain-api-reference.md)。
- 需要大规模给原版打补丁的组织范式（postinit 清单集中管理 / 组件包装三件套 / UpvalueHacker 取闭包上值 / 世界组件模式 / 新动作三步）时查阅 `references/mod-notes/` 下 [mod-uncompromising15.md](../../mod-notes/mod-uncompromising15.md)（不妥协原始笔记，含完整实现/数值/Boss）。
- 需要读取/替换闭包 upvalue，或参考热带 mod 的大量 hack 手法与可复用模板时查阅 `references/mod-notes/` 下 [mod-tropical.md](../../mod-notes/mod-tropical.md)（热带原始笔记）。

## 包装与撤销的边界

钩子拿到的对象不同：ComponentPostInit 是实例；StategraphPostInit 是共享定义；BrainPostInit 在 OnStart 建树后运行，重启可再次触发。先确认修改对象，再为实际实例/新树做幂等，不能靠一个永久布尔跳过未来重建。

需要后处理时保留原函数的多返回值及 nil 空洞：使用带 select("#", ...) 计数的打包和限定范围 unpack；不需要后处理时直接 return old(self, ...) 最稳妥。撤销补丁前确认字段仍是自己的包装函数，避免覆盖其他 Mod 后装的包装。

来源提炼自 [Hook 合同](../../engineering/dst-mod-engineering/core-lua-hooks.md)，Brain 时序由本轮 brain.lua 复核。上值修改仅在公开扩展点不足且源码可证时采用；按名字定位、找不到停止，不无限搜索或盲改固定索引。

## Hook 选择与调用时序

| 修改对象 | 首选入口 | 范围与注意 |
|---|---|---|
| 一个或少数已知 Prefab | AddPrefabPostInit | 修改构造完成的实体实例 |
| 所有带 player 标签的实体 | AddPlayerPostInit | 本质是全局 Prefab 钩子加标签过滤；包括远端/幽灵，不等于本地 HUD |
| 某类组件 | AddComponentPostInit | 组件已构造并赋给 inst.components，仍不保证其他组件齐全 |
| 返回 Class 的 Widget/Screen 模块 | AddClassPostConstruct | 包装类构造，只影响之后创建的实例 |
| 模块中的全局 Class | AddGlobalClassPostConstruct | 从全局表解析类；模块已返回 Class 时不需要此入口 |
| SG / Brain | AddStategraphPostInit / AddBrainPostInit | 分清共享 SG 定义与建树后的 Brain 对象 |
| 任意 Prefab | AddPrefabPostInitAny | 仅在更窄目标不够时使用；回调先做廉价过滤 |
| 模拟启动阶段的一次初始化 | AddSimPostInit | 不保证本地玩家或 HUD 可用，按实际对象与阶段检查 |

当前 mainfunctions 的命名 Prefab postinit 先于通用 postinit，之后才推送世界 entity_spawned。当前 AddComponent 中先 ReplicateComponent、再构造与赋值主组件、然后调用 ComponentPostInit，最后注册组件动作；构造器和 PostInit 的可用上下文不同。AddClassPostConstruct 只改未来实例；已存在 UI 应从自己的持有者处理，选择最窄实际被创建的类。

`AddPlayerPostInit` 本质是 `AddPrefabPostInitAny` 加 `player` 标签过滤，会对所有实体生成路径执行一次过滤。它适合确实要覆盖所有玩家实体的逻辑，不适合访问本地 HUD 或全局只执行一次的世界设置。优先考虑 `AddComponentPostInit("playervision")`、`playerlightningtarget`、`playercontroller` 等更窄入口；需要本地玩家时再结合实际玩家生命周期判断。

`worldsettings_overrides.lua` 会在进入世界时覆盖部分 `TUNING`。文件顶部 `local X = TUNING.Y` 可能已经缓存旧值；修改前搜索该键是否被世界设置覆盖，并在权威端读取覆盖后的值。

当前 gamelogic 启动路径调用 ModManager:SimPostInit(nil)，随后调用 TheWorld:PostInit。旧文“此时 ThePlayer 与 HUD 必然可用”不成立；玩家属性用对应 Prefab/玩家生命周期入口，HUD 用 Controls 构造链。准确签名见 [Hook 签名](../../signatures/hook-signatures.md)，本段于 2026-10-21 对照安装版 mods.lua、modutil.lua、mainfunctions.lua、entityscript.lua 与 gamelogic.lua。
