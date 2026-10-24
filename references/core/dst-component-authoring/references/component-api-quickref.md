# 关键组件 API 速查（吸收自源码精读）

> 为 `dst-component-authoring` 补充常用组件的字段/方法速查。与 `component-contract.md`（组件编写契约）互补。
> 出处统一写本地源码 `D:\mods\scripts`；方法签名与行号为版本敏感，以当前源码为准，不要只凭记忆调用。

## 0. 组件三事实（理解组件本质）

1. **组件文件不注册组件名**。注册发生在 prefab：`inst:AddComponent("workable")`；组件文件只返回 `Class(...)` 对象。
2. **Class 第三参是属性 setter 表**：`Class(function(self, inst,...) end, nil, props)` 可在属性写入时执行对应回调；它本身不提供网络同步。是否更新 Replica/netvar 由 setter 的实际实现决定。
3. **保存、退出和调试是不同契约**：组件 `OnSave()` 返回 `data, refs`，`OnLoad(data, newents)` 读数据，`LoadPostPass(newents, data)` 修复引用；`OnRemoveFromEntity()` 用于组件卸载，`GetDebugString()` 用于调试。不要把 Prefab 回调签名套给组件，详见 [存档契约](../../dst-persistence-migration/references/persistence-contract.md)。

以上两项与下方 Teleporter 目标方法已于 2026-10-17 核对当前安装包的 `class.lua`、`entityscript.lua` 和 `components/teleporter.lua`；其余速查仍需按各项源码核对，不因这次纠错宣称全表已验证。

## 1. 组件构造模式

- 构造时读已有组件做初始化：`local workable = inst.components.workable; if workable then self:SetWorkRepairable(...) end`。
- 缺组件自动补：`if inst.components.timer == nil then inst:AddComponent("timer") end`。
- 世界组件访问：`TheWorld.components.undertile:GetTileUnderneath(x,y)`、`TheWorld.components.walkableplatformmanager:RegisterPlatform`。
- 全局函数交互：`GetLocalTemperature(inst)` / `GetTemperatureAtXZ(x,z)`。
- **世界级组件**（挂 TheWorld）：用 `self:OnPostInit` 做加载后初始化，并 `assert(TheWorld.ismastersim, "... should not exist on client")`。
- **给原版组件追加逻辑**：`AddComponentPostInit("workable", function(self, inst) ... end)`。

## 2. 高频组件速查

### workable（★建筑/资源交互核心）
- 字段：`workleft, maxwork, action=ACTIONS.CHOP, savestate, workable, tough, workmultiplierfn, shouldrecoilfn, onwork, onfinish`
- `SetWorkAction(act)`（CHOP/DIG/HAMMER/MINE…）、`GetWorkAction()`、`SetMaxWork`、`SetWorkLeft`、`GetWorkLeft`、`CanBeWorked`
- `WorkedBy(worker, numworks)` 自动算 tool 效率+multiplier，推 `worked/workfinished`；`Destroy(destroyer)`
- `SetOnWorkCallback` / `SetOnFinishCallback` / `SetOnLoadFn`
- `SetRequiresToughWork(tough)` + `SetShouldRecoilFn`（tough 需 toughworker 标签或 tool:CanDoToughWork）
- 事件：worked/workfinished/working；标签 `{action.id}_workable`

### worker / tool（★工具）
- `SetAction(action, effectiveness)`（tool 会 assert TOOLACTIONS[action.id]）、`GetEffectiveness(action)`、`CanDoAction(action)`
- tool：`EnableToughWork(tough)`、`CanDoToughWork()`；监听 `percentusedchange` 推 `toolbroke`；标签 `{action.id}_tool`

### weapon（★武器）
- 字段：`damage, attackrange, hitrange, projectile, stimuli, attackwear, electric_damage_mult`
- `SetDamage(dmg)`、`SetRange(attack, hit)`、`SetOnAttack(fn)`、`SetProjectile(prefab)`、`SetProjectileOffset`、`SetElectric(mult, wetmult)`
- `GetDamage(attacker, target)`（FunctionOrValue + damagetypemult）、`OnAttack(attacker, target, projectile)`（武器磨损）、`LaunchProjectile(attacker, target)`
- `EnableToughFight(tough)`、`CanRangedAttack()`；事件 weapononattack

### sanity
- 字段：`max, current, mode(SANITY_MODE_INSANITY), rate, ratescale, sane, penalty, ghost_drain_mult, custom_rate_fn`
- `DoDelta(delta, reason)`、`SetMax/SetCurrent/SetPercent`、`GetPercent/GetRealPercent/GetPercentWithPenalty`
- `IsSane()/IsInsane()/IsEnlightened()/IsCrazy()`、`IsInsanityMode()/IsLunacyMode()`、`EnableLunacy(enable, source)`
- `AddSanityPenalty(key, mod)/RemoveSanityPenalty/RecalculatePenalty`、`AddSanityAuraImmunity/RemoveSanityAuraImmunity`、`SetPlayerGhostImmunity`、`SetLightDrainImmune`
- `SetInducedInsanity(flag, source)`、`GetAuraMultipliers`;调参 SANITY_MODE_* / RATE_SCALE.NEUTRAL

### temperature（★温度/环境）
- 字段：`current, maxtemp, mintemp, overheattemp, hurtrate, inherentinsulation, shelterinsulation, sheltered`
- `DoDelta(delta, skipinsulation)`（绝缘 SEG_TIME/(SEG_TIME+insulation)）、`SetTemperature`、`SetTemp`
- `SetModifier(source, value)/RemoveModifier`、`SetInsulationModifier/RemoveInsulationModifier`、`GetInsulation`
- `SetTemperatureInBelly`、`IsFreezing()/IsOverheating()`、`GetMoisturePenalty()`

### temperatureoverrider（地热/空调）
- `SetTemperature(t)`、`SetRadius(r)`、`Enable()/Disable()`、`GetActiveRadius()/GetTemperature()`
- 全局：`GetTemperatureAtXZ(x,z)`、`GetLocalTemperature(inst)`；服务端 radius、客户端只读 net_float

### stackable（堆叠）
- 字段：`stacksize, maxsize, originalmaxsize`
- `Put(item, source_pos)`（合并+稀释状态，满返回剩余）、`Get(num)`（拆分成新实例复制状态）、`SetStackSize`
- `CanStackWith(item)`（同 prefab+skinname+自定义fn）、`IsStack()/IsFull()/IsOverStacked()/RoomLeft()`；事件 stacksizechange

### spawner（★刷怪建筑）
- `Configure(childname, delay, startdelay)`、`SpawnWithDelay(delay)`、`CancelSpawning()`
- `ReleaseChild()`（FindWalkableOffset 找位置）、`GoHome(child)`、`TakeOwnership(child)`（自动加 homeseeker）
- `SetOnSpawnedFn/SetOnKilledFn/SetOnOccupiedFn/SetOnVacateFn`、`SetWaterSpawning`、`SetOnlySpawnOffscreen`、`SetQueueSpawning`
- `IsOccupied()/IsSpawnPending()`；child 死亡/捕获/移除 → OnChildKilled 重新计时

### timer
- `StartTimer(name, time, paused, initialtime_override)`、`StopTimer(name)`、`TimerExists(name)`
- `PauseTimer/ResumeTimer/IsPaused`、`GetTimeLeft/SetTimeLeft/GetTimeElapsed`、`LongUpdate(dt)`；事件 timerdone

### stewer（★烹饪）
- 字段：`done, targettime, product, spoiledproduct="spoiled_food", cooktimemult, chef_id`
- `StartCooking(doer)`（cooking.CalculateRecipe+腐坏计算+关容器销毁原料）、`StopCooking(reason)`、`Harvest(harvester)`、`CanCook()`
- `IsDone()/IsCooking()/IsSpoiling()/GetTimeToCook()/GetTimeToSpoil()`；标签 readytocook

### trader
- `SetAcceptTest(fn)`、`SetAbleToAcceptTest(fn)`、`SetOnAccept(fn)`、`SetOnRefuse(fn)`、`SetAcceptStacks()`
- `AbleToAccept(item, giver, count)`、`WantsToAccept`、`AcceptGift`、`Enable()/Disable()`；事件 trade

### teleporter（★传送建筑）
- `Target(otherTeleporter)`、`Activate(doer)`、`Teleport(doer)`、`UseTemporaryExit(doer, exit)`；目标方法名不是 `SetTarget`
- `RegisterTeleportee/UnregisterTeleportee`、`IsActive()/IsBusy()/IsTargetBusy()`、`SetEnabled/GetEnabled`
- 标签 `teleporter`（由 targetTeleporter/enabled 属性 setter 维护）

### trap（★陷阱）
- 字段：`bait, issprung, isset, range, targettag, checkperiod, lootprefabs`
- `Set()/Reset(sprung)/IsFree()/IsBaited()/HasLoot()/IsSprung()`、`SetBait(bait)`（需 bait 组件）、`DoTriggerOn(target)`、`DoSpring()`、`Harvest(doer)`
- `StartStarvation()`（timer "foodspoil"）；自动补 timer 组件；ondropped→Set、onpickup→Reset

### sleeper
- `GoToSleep()/WakeUp()/IsAsleep()/IsHibernating()/IsInDeepSleep()`、`SetNocturnal(b)`
- `SetSleepTest(fn)/SetWakeTest(fn)`、`SetResistance(r)`、`AddSleepiness(amount)`

## 3. 地图/网格数据（DataGrid）与区域感知

- `DataGrid(width, height)` 按 tile 存数据：`GetDataAtPoint/SetDataAtPoint/GetXYFromIndex/GetIndex`。
- 地图尺寸事件：`inst:ListenForEvent("worldmapsetsize", initialize_grids, _world)`。
- 地图 API：`map:GetTileAtPoint(x,y,z)`、`map:GetTile(x,y)`、`map:SetTile(x,y,tile)`、`map:GetEntitiesOnTileAtPoint`、`map:CanTerraformAtPoint`、`map:CanPlowAtPoint`。
- 区域感知：`areaaware.lua` 监听区域节点/地皮 tile 变化（推 `changearea/on_xx_tile`）★地形相关。
