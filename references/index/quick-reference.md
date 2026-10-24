# DST 快速定位与合同索引

本页用于选择原文，不再重复维护一套庞大的 API/固定数值清单。方法参数、字段和运行端在对应专题及当前源码核对，API 10 不代表所有版本兼容。

## 按任务进入

| 问题 | 先读 |
|---|---|
| 新建 Mod、配置与入口 | [脚手架](../core/dst-mod-scaffolding/GUIDE.md)、[入口 API](../core/dst-mod-scaffolding/references/modmain-api-reference.md) |
| GLOBAL、require/modimport、Class | [Lua 环境](../core/dst-lua-runtime/GUIDE.md) |
| Prefab 公共/主机区 | [Prefab 合同](../core/dst-prefab-authoring/references/prefab-contract.md) |
| 自定义组件/Replica | [组件合同](../core/dst-component-authoring/references/component-contract.md)、[最小案例](../cases/case-custom-component.md) |
| RPC、数据初值、预测 | [联机合同](../core/dst-networking-rpc/references/network-contract.md) |
| 动作出现却执行失败 | [Action 链](../core/dst-action-authoring/references/action-pipeline.md) |
| 事件/任务/效果残留 | [生命周期](../core/dst-events-tasks-lifecycle/GUIDE.md) |
| 保存、实体引用、旧档 | [持久化合同](../core/dst-persistence-migration/references/persistence-contract.md) |
| 伤害、范围、投射物 | [战斗](../gameplay/dst-combat-weapons-projectiles/GUIDE.md)、[combat](../components/combat/combat.md) |
| 食物/调味/图鉴 | [烹饪](../gameplay/dst-food-cooking/GUIDE.md) |
| 材料/科技/配方菜单 | [制作](../gameplay/dst-crafting-tech-prototypers/GUIDE.md) |
| 容器/装备/堆叠/修复 | [物品](../gameplay/dst-inventory-equipment-containers/GUIDE.md) |
| 生长/农田/种植 | [植物](../gameplay/dst-plants-farming-regrowth/GUIDE.md) |
| Brain/SG | [AI](../gameplay/dst-brain-authoring/GUIDE.md)、[SG](../gameplay/dst-stategraph-authoring/GUIDE.md) |
| 世界生成/地皮/旧档补内容 | [生成](../gameplay/dst-worldgen-authoring/GUIDE.md)、[Retrofit](../world-ui-assets/dst-worldgen-layouts-retrofit/GUIDE.md) |
| HUD/输入/Screen | [HUD](../world-ui-assets/dst-hud-screens-input/GUIDE.md)、[TheInput](../systems/theinput.md)、[屏幕栈](../systems/thefrontend.md) |
| 图集/bank/build/symbol | [资源](../world-ui-assets/dst-assets-animation-atlas/GUIDE.md) |
| FX/声音/Shader | [粒子](../world-ui-assets/dst-fx-vfx-authoring/GUIDE.md)、[音频](../world-ui-assets/dst-audio-camera-effects/GUIDE.md)、[Shader](../world-ui-assets/dst-shader-authoring/GUIDE.md) |

## 常用对象的边界

TheWorld 是当前分片世界，ThePlayer 是本地玩家而非服务器请求者。前端和生成阶段未必有这些运行对象。世界当前阶段/季节查 TheWorld.state.phase/season，不复制旧单机 GetSeasonManager/GetDayPhase 习惯。

组件存在性检查 inst.components.name；客户端读取已存在的 Replica。Transform、AnimState、Light、Physics 是 entity 的引擎对象，不按普通 Lua 组件伪造源文件或注册。

原生 API 在 Lua 找不到定义时查真实调用点；不据此直接断言不存在。物品代码名先查 [物品名表](../prefabs/物品名字.txt)，文件名、注册名和显示名分别核对。

## 时间、网络类型与标签

- 时间数值从目标 TUNING 与消费者读取；不要沿用旧表“一天 80 秒、SEG 16 秒”的错误常数。FRAMES 参与 TimeEvent 的秒换算。
- net_smallbyte 是 6-bit 的 0–63，不足以表达 0–800。net_byte 是 0–255；net_ushortint 是 0–65535。小数值按需求选择 net_float，范围、精度和初值都要定义。
- 实体 tag、SG state tag 与烹饪 tags 是不同协议；busy 不意味着绝对不可打断。tag 是否影响行为取决于真实消费者，不根据名字赋予通用能力。

## 查询与验收

入口不明确时执行 knowledge docs/lookup；读命中的原文、范围和源码定位，再应用。完整命令见 [知识入口](../knowledge/README.md)，50 专题全表见 [目录](../topic-index.md)。

静态解析、声明核对、专服业务、真实客机、图像与声音分层验收。候选 not_run 和未复现 failure 不升级；当前源码正确也不证明当前 Mod 已走完该调用链。
