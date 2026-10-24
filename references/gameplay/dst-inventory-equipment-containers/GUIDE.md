---
name: dst-inventory-equipment-containers
description: Build Don't Starve Together inventory items, equipment, stacks, durability, fuel, perishables, armor, and containers. Use when creating or modifying inventoryitem, equippable, stackable, finiteuses, fueled, perishable, container, container_replica, inventory UI, equip symbols, or item ownership behavior.
---

# DST 物品、装备与容器

围绕物品在地面、物品栏、容器、装备栏和移除阶段的状态转换组织实现。本子技能的参考文档按 3 类主题收敛：**容器存储**（多槽容器与扩容储物）、**物品行为**（防偷防掉、耐久维护）、**实体封装**（把任意实体打包/复制为可携带物）。机制类/触发类文档（如投喂升级）归各自更贴合的子技能，不在此重复。

## 工作流

1. 选择最接近的原版物品，列出地面物理、拾取、堆叠、装备、耐久、燃料、腐败和容器需求。
2. 在 SetPristine 前建立库存图标、标签和客户端所需网络状态；主机分支添加 inventoryitem 等组件。
3. 配置 stackable、finiteuses、fueled、perishable、weapon、armor 或 tool，并明确耗尽、熄灭、腐败和破损回调。
4. equippable 的 onequip 与 onunequip 对称处理 SymbolOverride、速度、伤害、防护、标签和跟随 FX。
5. 容器同时配置 containers.lua 的 widgetsetup、槽位、过滤规则、open/close 回调和 container_replica 可见性。
6. 处理进入库存、掉落、转移容器、角色死亡、堆叠合并、皮肤 Build 和实体移除。
7. 测试鼠标与手柄、远端客户端、满容器、不可接受物品和保存重载。

## 源码锚点

- components/inventoryitem.lua、inventory.lua、stackable.lua、equippable.lua。
- components/finiteuses.lua、fueled.lua、perishable.lua、weapon.lua、armor.lua。
- components/container.lua、container_replica.lua 与 containers.lua。
- widgets/inventorybar.lua、containerwidget.lua、itemtile.lua。

## 按需参考

**容器存储（Container & Storage）**
- [container-registration.md](references/container-registration.md) - 容器注册与 Replica 同步：`containers.params`、`MAXITEMSLOTS`、Prefab 名与配置键分离、`itemtestfn` 两端执行边界，以及 `WidgetSetup`/`OnEntityReplicated` 的客户端初始化。
- [portable-chef-container.md](references/portable-chef-container.md) - 便携厨具容器：一个 container 划分数个功能分区（保鲜储物/批量烹饪/调味/晾晒烤制研磨/三维存储补给/特效料理），含槽位过滤、instant 加工与 RPC 动作按钮。
- [dual-container-expansion.md](references/dual-container-expansion.md) - 双容器扩容储物：主可见容器 + 隐藏子容器，开合搬移 + `GiveItem` 重定向装满两格，后台 `fakeOpen` 不弹 UI，倾倒类 API 需双容器兜底。

**物品行为（Item Behavior & Upkeep）**
- [exclusive-item-protection.md](references/exclusive-item-protection.md) - 专属物品防偷防掉：`nosteal` 标签 + `Thief:StealItem` hook 防偷，`grabbableoverridetag`/`canbepickedup`/强制 `DropItem` 防被捡与掉落。
- [auto-repair-maintenance.md](references/auto-repair-maintenance.md) - 耐久维护（能力系统）：周期任务对容器内 `fueled/armor/finiteuses` 逐件补耐久，含维修间隔/修复量/上限封顶三参数，双容器需分别遍历。

**实体封装（Entity Capture & Duplication）**
- [entity-to-item-capture.md](references/entity-to-item-capture.md) - 实体打包：用 `GetSaveRecord`/`SpawnSaveRecord` 把任意实体（物品/建筑/生物/植物）压缩成可携带、可落盘、可释放的便携"打包物"。
- [entity-duplication.md](references/entity-duplication.md) - 实体复制：用 `GetSaveRecord`/`SpawnSaveRecord` 复制物品或生物且不改原件（区别于打包，可堆叠副本只给一份并清容器归属）。

## 不变量

- 装备和卸下必须恢复完全对称的状态。
- 容器过滤在服务器最终校验，客户端 UI 只是预览。
- 不要让堆叠物品保存每个单件不一致的隐藏状态，除非设计明确禁止堆叠。
- 物品进入 Limbo 或容器时停止不应继续的世界任务与物理效果。

## 验证

- 地面、库存、容器、装备、堆叠拆分和角色死亡路径均正确。
- 耐久、燃料和腐败只结算一次。
- 远端客户端的槽位、图标、可用动作和服务器状态一致。

## 容器配置与物品归属

containers.params 使用私有配置名，两端加载同一参数；服务端 container:WidgetSetup 会通知其 Replica，客机按实际复制初始化链检查，避免不分场景重复设置。openlimit 是同一个容器同时打开者上限，不是全世界同类容器数量。

`containers.MAXITEMSLOTS` 只在 `containers.lua` 模块末尾扫描一次。若模组在 `require("containers")` 之后追加槽位更多的 `params`，必须同步提高该值；否则 `container_classified` 的槽位初始化循环可能覆盖不到新增槽位。Prefab 名与 `containers.params` 配置键不同时，客户端需要 `replica.container:WidgetSetup("配置键")`，或在 `OnEntityReplicated` 中补设。

槽位 UI 不构成权限。服务端检查物品、操作者与容器当前状态，处理自嵌套/循环嵌套；隐藏容器、宠物容器还要定义召回、变身、despawn、断线、死亡和磁盘重启时物品去哪，不能只在 death 掉落。

堆叠上限的主组件字段 maxsize 有 setter；Replica 的 SetMaxSize 是另一层接口。原版最大堆叠档位和数量编码分别限制，任意 maxsize 不保证能编码；优先现有档位，不全局抢占某编码。两端协议相同仍需组合兼容验证。

修复消耗优先区分 repairable/repairer、MakeForgeRepairable/forgerepair 与 trader 接受物品机制；当前 forge 支持 finiteuses，不能沿用“有限次数武器无法 forge 修复”的旧结论。客户端菜单沿 tag/动作注册检查，服务端最终消费单件，失败不删整叠。

发射前如需让物品离开原有地雷/激活形态，使用 `DeactivateInventoryItemBeforeLaunch(inst)`。它优先 `mine:Deactivate()`，其次调用 `inventoryitem_DeactivateBeforeLaunch()`，并返回是否处理；退出库存或物理形态不等于自动保存内容、归还物品或重建实体。成功发射后的资源消费、容器槽位和地面落点仍由调用者明确处理。

可对目标使用或停止使用的物品优先查 `useabletargeteditem`，而不是在动作收集里直接改世界。其 `SetOnUseFn` 返回 `(success, failreason)`，目标菜单筛选可在公共区配置 `UseableTargetedItem_ValidTarget`，服务端回调仍须重验。完整合同和 `security_pulse_cage_full` 例子见 [useabletargeteditem.md](../../components/items/useabletargeteditem.md)。

本轮源码：containers.lua:5-16,2498-2499、container.lua:86-96,728-736、container_replica.lua:47,232-233,340-379、stackable_replica.lua:24-35,98-115；修复进一步查 [物品参考](../../engineering/dst-mod-engineering/items-food-plants.md)。这是接口与边界补充，未证明具体多容器或宠物实现已经通过实机。
