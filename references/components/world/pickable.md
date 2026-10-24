# `pickable`

> 适用版本：API 10+
> 最后更新：2026-09-21

当任务涉及修改世界节点上的采集、再生、**移植（transplant）**、贫瘠状态或施肥流程时，使用此文件。

官方源码：

- `scripts/components/pickable.lua`

相关官方预制件示例：

- `scripts/prefabs/berrybush.lua`

## 术语：移植作物 vs 农作物

- **移植作物**：挖出再种下的本组件实例（浆果丛、草、树枝等），`OnTransplant` → 常 `ontransplantfn` → `MakeBarren`，种下往往**要施肥**。
- **不是**农田 `farm_plant`（`farming_manager` 养分/压力是另一套）。
- 用户说「移植作物 / 免施肥」默认指本组件；详细 hook 见  
  [transplant-pickable.md](../../gameplay/dst-plants-farming-regrowth/references/transplant-pickable.md)。

高频方法：

- `SetUp(product, regen, number)`
- `SetOnPickedFn(fn)`
- `SetOnRegenFn(fn)`
- `SetMakeBarrenFn(fn)`
- `SetMakeEmptyFn(fn)`
- `OnTransplant()` — 种下；设 `transplanted` 并调 `ontransplantfn`
- `CanBeFertilized()` — 贫瘠或枯萎时为 true
- `Fertilize(fertilizer, doer)`
- `CanBePicked()`
- `Regen()`
- `MakeBarren()`
- `MakeEmpty()`
- `Pick(picker)`
- 字段：`transplanted`、`cycles_left`、`max_cycles`（`cycles_left == nil` 表示无限采）

常见组件搭配：

- `pickable` + `inspectable`
- `pickable` + `workable`（挖掘/移植）

常见陷阱：

- `pickable` 用于世界可采集物，不是松散的背包物品。
- 许多可采集物也使用 `workable` 来处理挖掘或破坏行为。
- 再生 bug 通常涉及存档、读档或 `LongUpdate(...)`，不仅仅是 `Pick(...)`。
- **移植默认可能 `MakeBarren`**；改「免施肥」勿误伤农田 `farmplantstress`。

后续阅读：

- [transplant-pickable.md](../../gameplay/dst-plants-farming-regrowth/references/transplant-pickable.md) — 移植术语与免施肥 hook
- [workable.md](workable.md)
- [persistence-contract.md](../../core/dst-persistence-migration/references/persistence-contract.md)
