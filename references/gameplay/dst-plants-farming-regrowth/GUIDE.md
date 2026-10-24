---
name: dst-plants-farming-regrowth
description: Create Don't Starve Together plants, crops, farm-soil interactions, growth stages, stress, nutrients, tending, harvesting, and world regrowth. Use when working with growable, pickable, farmplantstress, farming_manager, plantregrowth, regrowthmanager, crop stage data, seasonal growth, or plant save and long-update behavior.
---

# DST 植物、农作物与再生

把生长阶段、环境输入、收获、枯萎、离线推进和世界再生分别建模。

**先分清两条线**（用户口径见细分参考）：

| 线 | 系统 | 细分参考 |
|----|------|----------|
| **移植作物**（浆果丛等挖了再种） | `pickable` + 移植/施肥 | [transplant-pickable.md](references/transplant-pickable.md) |
| **农田农作物**（种子、养分、压力） | `farm_plant` + `farming_manager` | [farm-stress-and-hooks.md](references/farm-stress-and-hooks.md) |

## 工作流

1. 选择普通可采集植物、Growable 多阶段实体、农田作物或世界再生资源中的正确模型。
2. 定义阶段表、动画、持续时间、季节条件、产物、工作动作和阶段切换回调。
3. 农作物按 farming_manager、farmplantstress、养分、水分、照料和家庭/拥挤规则接入。
4. 服务器推进生长与压力；客户端只复制阶段、动画和可见提示。
5. 实现 OnSave、OnLoad 与 LongUpdate，限制长时间离线推进并防止重复收获。
6. 世界资源使用 plantregrowth 或 regrowthmanager，明确最大密度、合法地形、玩家距离和旧实例登记。
7. 测试季节切换、干旱、积雪、过熟、铲除、燃烧、保存重载和大规模农田性能。

## 细分参考

- **移植作物术语 + 永远免施肥 hook**（`pickable`，非农田）：[transplant-pickable.md](references/transplant-pickable.md)
- **农田**压力系统（累加逻辑、免疫的正确写法、`stressors_testfns` 坑）、"一次浇满"、收获额外产出：[farm-stress-and-hooks.md](references/farm-stress-and-hooks.md)
- 组件 API：`pickable` → [pickable.md](../../components/world/pickable.md)

## 源码锚点

- components/growable.lua、pickable.lua、harvestable.lua、plantable.lua。
- components/farming_manager.lua、farmplantstress.lua、farmplanttendable.lua、farmsoildrinker.lua。
- components/plantregrowth.lua、regrowthmanager.lua。
- 原版 farm_plant 与普通植物 Prefab（如 `prefabs/berrybush.lua`）。

## 不变量

- 阶段切换回调必须允许实体在回调中被替换或移除。
- 客户端动画不能推进服务器生长状态。
- 再生搜索限制范围、密度和尝试次数。
- 离线推进不可绕过季节、环境或一次性奖励规则。

## 验证

- 所有阶段可达且动画、可采集性和产物匹配。
- LongUpdate 与在线经过同等时间产生兼容结果。
- 大量植物和长期世界运行不会造成任务或实体无限增长。

## growable 阶段与部署

阶段 fn 应用当前外观/静态状态，time 函数决定时长，pregrowfn/growfn 在转移链执行；具体时机查当前 DoGrowth。SetStage 不自动表示已重建新阶段计时。

缺少 time 函数会使用组件回退时长，不能当暂停。停止用 StopGrowing，或按当前 StartGrowing 合同让 time 函数返回 nil。即使是最后阶段，手动 StartGrowing 也不能仅凭“最后一段”判断无任务。睡眠追赶、魔法生长、loopstages 与保存各自核对。

种植先验证和成功建立新实体，再消费一颗种子；失败保留原堆叠。CUSTOM 部署可先检查公共字段 _custom_candeploy_fn 是否已满足两端查询，避免为单株植物全局覆盖 Replica。服务器真正执行时仍复查地形、阻挡和归属。

本轮核对 components/growable.lua:42-81,121-148；提炼自 [植物参考](../../engineering/dst-mod-engineering/items-food-plants.md)。验收 SetStage 后计时、缺 time、返回 nil、最后阶段手动启动、读档及休眠追赶，不能只验证首次生成动画。
