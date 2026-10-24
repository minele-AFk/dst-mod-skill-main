# Prefab 编写模式（吸收自源码精读）

> 与 `prefab-contract.md`（固定顺序/契约）互补。本文件提供从大量原版 prefab 反向归纳的**设计模式**，
> 用于"写得像原版、少踩网同步/存档/事件坑"。原始线索来自本地源码快照；本轮构造、加载与回调签名核对当前安装包 scripts.zip，其他具体用例按目标文件继续查证。

## 1. 常见构造分层（按实体职责选择）

1. **资源声明层**：`assets` 表（`Asset("ANIM", ...)` / `Asset("MINIMAP_IMAGE", ...)` / `Asset("SOUND", ...)`；皮肤用 `DYNAMIC_ANIM`）。
2. **依赖声明层**：`prefabs` 表声明依赖 Prefab（掉落物/子实体/升级目标），作为 `Prefab` 第 4 参 deps；不是 SpawnPrefab 白名单。
3. **brain 导入层**：`require "brains/xxxbrain"`（仅生物）。
4. **事件处理函数层**：`OnAttacked/OnDeath/retargetfn/keeptargetfn/ShouldSleep/ShouldWake` 纯函数，用 `TUNING` 常量。
5. **构造函数层**：`fn` 内 `CreateEntity` → 加子系统 → 物理 → 标签 → `AnimState:SetBank/Build/PlayAnimation` → `SetPristine` → 客户端 `return` → 组件链 → `SetStateGraph/SetBrain` → 事件注册 → `return inst`。
6. **变体层**：`common` 工厂 + 变体 `fn`（一文件多 prefab）。
7. **导出层**：`return Prefab(...)` 或 `return MakePlayerCharacter(...)`。

## 2. fn 内标准骨架（服务端/客户端分离）

```lua
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddSoundEmitter()
    inst.entity:AddMiniMapEntity()
    inst.entity:AddNetwork()            -- 有交互的网络实体必须有
    inst.AnimState:SetBank("xxx")
    inst.AnimState:SetBuild("xxx")
    inst.AnimState:PlayAnimation("idle", true)
    MakeObstaclePhysics(inst, .25)
    inst:AddTag("plant")
    inst.entity:SetPristine()           -- ★ 分界线
    if not TheWorld.ismastersim then
        return inst
    end
    inst:AddComponent("pickable")
    -- ... 服务端逻辑
    return inst
end
```

**Classified**：用于复制状态的辅助实体，不能概括为纯客户端实体，也不统一限定子系统或 ismastersim 分支。按实际 prefab 核对生成端、父实体、网络目标、持久化和移除；不要将 damagenumber 等表现实体一概视为同一模式。见 [网络契约](../../dst-networking-rpc/references/network-contract.md)。

## 3. 网同步三原则

1. **`SetPristine()` 不同步任意 Lua 字段或组件**。公共初始化、原生网络状态、netvar 与 Replica 各有协议，具体分界见 [构造契约](prefab-contract.md)。
2. **能复制的标签提前到 pristine 前手动 `AddTag`**（优化注释 `added to pristine state for optimization` 遍布源码），主机分支再 `RemoveTag` 交给组件重建。
3. **跨端数值用 `net_*` 字段 + dirty 事件**：`net_bool(guid,key,dirtyevent)` / `net_smallbyte` / `net_tinybyte` / `net_entity`。服务端 `set()`，客户端 `ListenForEvent(dirtyevent)` 或 `OnEntityReplicated` 处理本地表现。

```lua
inst._isrose = net_bool(inst.GUID, "flower._isrose", "isrose")   -- SetPristine 前
-- 服务端: inst._isrose:set(true)
-- 客户端: inst:ListenForEvent("isrose", fn)
```

## 4. 常用辅助函数（分布于 prefabutil、standardcomponents 与物理相关模块）

| 分类 | 函数 |
|---|---|
| 物理 | MakeObstaclePhysics / MakeSmallObstaclePhysics / MakeHeavyObstaclePhysics / MakeInventoryPhysics / MakeBlastResistantPhysics |
| 燃烧 | MakeSmall/Medium/LargeBurnable + MakeSmall/Medium/LargePropagator |
| 幽魂 | MakeHauntableWork / MakeHauntableIgnite / MakeHauntableLaunch / MakeHauntableWorkAndIgnite / MakeHauntableChangePrefab |
| 其他 | MakeInventoryFloatable / MakeSnowCovered / MakeSnowCoveredPristine / MakePlacer / MakeNoGrowInWinter / MakeWaxablePlant / MakeDeployableKitItem / SetLunarHailBuildupAmount* / RemoveLunarHailBuildup |

树木/植物标准"燃烧三件套"：
```lua
MakeMediumBurnable(inst)
MakeSmallPropagator(inst)
MakeNoGrowInWinter(inst)
inst.components.burnable:SetOnIgniteFn(tree_startburn)
inst.components.burnable:SetOnBurntFn(tree_burnt)
```

## 5. 燃烧-掉落-再生完整回调链

- `burnable:SetOnIgniteFn`（起火烧毁前禁用可交互）→ `SetOnBurntFn`（烧完换 `xxx_burnt` 变体或掉木炭）。
- 烧毁换 prefab：`SpawnPrefab("xxx_burnt")` + `Transform:SetPosition(取世界坐标)` + `inst:Remove()`。
- 砍伐换 prefab：树倒动画播完再换 stump —— `inst:ListenForEvent("animover", setupstump)`。
- 存档记录 `data.burnt = true` / `data.no_banana`（OnSave/OnLoad）。

## 6. brain 与 SG 挂载规律

- SG：`inst:SetStateGraph("SG名字")` 使用文件模块名，加载器构造实例并进入默认状态；SG 模块返回定义，不手动把 require 的定义当运行实例。
- brain：`local brain = require "brains/xxxbrain"` + `inst:SetBrain(brain)`；换形态/换 AI 时整体换 brain+SG。
- brain 可动态开关：`inst:SetBrain(nil)` / `inst:SetBrain(enable and brain or nil)`；`inst:StopBrain("my_mod_reason")` 与 `inst:RestartBrain("my_mod_reason")` 用同一个停止原因配对；参数不是 Brain 名称。
- SetStateGraph 会立即进入初始状态；若该状态使用 locomotor，必须先装配它。不能推导所有 SG 都需要 locomotor。

## 7. teamwork 五件套（战斗协作）

1. `combat:ShareTarget(attacker, dist, filterfn, max)`：共享仇恨。
2. `combat:SetRetargetFunction(period, fn)` 周期重选目标；`SetKeepTargetFunction(fn)` 是否放弃。
3. `PushEvent("suggest_tree_target")` / `"gohome"` 自定义事件广播。
4. `leader`/`follower` 组件：收随从、忠诚度。
5. 群体谓词函数（IsPig / IsHost / IsGuardPig…）按阵营筛选共享对象。

## 8. 形态 / 升级 / 阶段三大状态系统

- **形态（werebeast）**：`SetWereFn/SetOnNormalFn` + 整体重配函数（pigman）。
- **升级（level 1-3）**：`levelupsource` 记录 + `WantsToLevelUp` + `OverrideSymbol` 换部件（shadowchesspieces）。
- **阶段（phase 1-4）**：`healthtrigger:AddTrigger(amount, fn)`（阈值与回调）（toadstool、wagboss_robot）。

## 9. 数据驱动工厂（一文件 N 个 prefab）

- `data` 表 + 闭包工厂：`local ret={}; table.insert(ret, MakeXxx(v)); return unpack(ret)`。
- `extra_data` 表覆盖参数（spider 8 变体，可换 sg/brain/pathcaps）。
- 技能树 `SKILLS` 表（skilltree_wilson.lua）。
- 共享掉落表 `SetSharedLootTable`（顶部集中，或 `lootdropper:AddRandomLoot(prefab, chance)`）。
- 一行式 FX：`fx.lua` 遍历定义表批量生成。

## 10. 事件总线偏好

- 已有合适事件时优先监听：`attacked/death/newcombattarget/timerdone/onpickup/ondropped/onremove` 全 `ListenForEvent`。
- 世界状态：`WatchWorldState("iscaveday", fn)` / `WatchWorldState("iswinter", fn)`；使用实际存在的状态名，销毁时撤销跨实体监听。
- 实体生命周期：`OnEntitySleep`/`OnEntityWake` 做离线清理/定时（兔子冬眠、沃尔夫斯回窝、worm_boss 卸载分节）。
- 跨实体通信：`target:PushEvent` / `home:PushEvent("onwenthome")`。

## 11. 临时实体（FX / 武器 / 碰撞件）

- `inst.persists = false` 不存档。
- 非网络实体：只 `AddTransform` 甚至加 `CLASSIFIED` 标签。
- FX：`inst:ListenForEvent("animover", inst.Remove)` 或 `DoTaskInTime(t, fn)` 后 `inst:Remove()`。
- 挂父级：`fx.entity:SetParent(inst.entity)`。

## 12. 存档钩子五件套

| 钩子 | 用途 |
|---|---|
| `inst.OnSave` | 存 `data.build / phase / level` |
| `inst.OnLoad` | 恢复形态/阶段/形态 |
| `inst.OnPreLoad` | 组件 OnLoad 前的预处理；具体时机见 entityscript.lua |
| `inst.OnLoadPostPass` | 需全部实体加载后恢复（worm_boss 分节重建） |
| `inst.OnRemoveEntity` | 清理子实体（移除全部 chunk/segment） |

## 13. 数值与常量纪律

- 可调玩法数值集中配置；只有确有对应键时读取 TUNING，不根据 prefab 大写猜键。局部实现常量无需一律塞入 TUNING。
- 掉落权重集中（SetSharedLootTable 或用例级 AddRandomLoot）。
- 距离常量 `TARGET_DIST / DIST_SQ` 预计算。

## 14. 客户端表现技巧

- `AnimState:SetClientsideBuildOverride("insane", "rabbit_build", "beard_monster")`：客户端按状态换 build。
- `SetClientSideInventoryImageOverride` / `inst.drawimageoverride`：画布/物品图标覆写。
- `AnimState:UsePointFiltering(true)`：点采样（暗影风格）。
- `AnimState:SetMultColour(1,1,1,.5)` 半透明；`SetLightOverride` / `EnableClientModulation(true)`。

## 15. 特殊事件活动挂接

- `event_server_data("quagmire", "prefabs/rabbit").master_postinit(inst)`：按游戏模式注入扩展。
- `IsSpecialEventActive(SPECIAL_EVENTS.YOTB)`：按活动换 build。
- `TheNet:GetServerGameMode() == "lavaarena"/"quagmire"` 分支。

## 进阶组件速查（n-z 高频）

| 组件 | 用途 |
|---|---|
| healthtrigger | 血量阶段触发 |
| grouptargeter | 多目标 |
| groundpounder | 震地攻击 |
| incrementalproducer | 定时产仔 |
| amphibiouscreature | 水陆双栖 |
| rideable | 可骑乘 |
| growable | 成长阶段（smallbird → 大鸟） |
| werebeast | 变身 |
| herdmember / teamattacker | 群组 / 团队攻击 |
| centipedebody | 分节身体（worm_boss / shadowthrall） |
| planarentity / planardamage | 位面系统 |
| updatelooper | 每帧更新 |
| npc_talker | NPC 对话 |
| constructionsite | 建造点 |
| prototyper | 科技解锁 |
