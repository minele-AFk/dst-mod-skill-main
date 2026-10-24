# [DST] 丰耘秘境源码 Harvest Mysterious Realm — 深度拆解笔记

> 资料来源：E:\神秘复苏\饥荒大型mod\3609964985\（~2196 文件，全部源码经过 DST Mod Encryptor 加密，已解密为 .dec 文件后阅读）
> 本文档为技能文档原材料，供 dst-mod-creater 工具链使用。所有代码片段均从解密源码逐字摘录。

---

## 1. Mod 总览

### 1.1 基本信息

| 项 | 值 |
|---|---|
| 名称 | [DST]丰耘秘境源码 Harvest Mysterious Realm |
| 作者 | 丰耘秘境团队（晴浅/策划代码动画、娜娜/策划美术宣发、糊桃/美术、素冥真仙/美术、幽冥Dim/美术；特别鸣谢 mooncake/代码与介绍网页） |
| 版本 | 1.1.0.3 |
| 优先级 | -999999999（极低，确保最后加载） |
| api_version | 10 |
| 模式 | dst_compatible=true, all_clients_require_mod=true |
| 服务器标签 | {"丰耘秘境","HMR","Harvest Mysterious Realm"} |
| 配置项 | CHERRY_ISLAND_GENERATION(0/30/52/60,默认52), HONOR_COCONUT_PLANTED(0聚集/1分散/2不生成), TERROR_COFFEE_PLANTED(同), TERROR_EVENT(maze/creature/none,默认maze), HONOR_BACKPACK_SLOTS(16/30), HONOR_BACKPACK_ENERGY_CONSUME_SPEED(0~2), HONOR_STOWER_MAX_CONSUME(0~1), TERROR_HAT_LIGHT_TARGET(active/passive), HMR_FACTORY_BLESSING_PERMISSION(ANYONE/OWNER_OR_SELF/ADMIN_ONLY) |

世界设定：双能量（辉煌 honor / 凶险 terror）与永恒大陆共生，靠耕种、捕猎、收获、发展。内置"丰耘百科"介绍模组。

### 1.2 目录结构（scripts/）

```
scripts/
├── components/          # 自定义组件（约40个 .lua + .dec 成对）
│   ├── hmrhouse.lua           # 秘境（屋内空间）世界组件：房屋注册表
│   ├── hmrhousevisitor.lua    # 玩家进入秘境复组件（服务端）
│   ├── hmrhousevisitor_replica.lua # 玩家进入秘境复组件（客户端replica）
│   ├── hmrteleporter.lua      # 传送器组件（入口/出口成对）
│   ├── hmrroom.lua            # 单实体房间判定组件
│   ├── hmrroommanager.lua     # BFS房间识别管理器（世界组件）
│   ├── hmrterrorevent_new.lua # 凶险迷踪事件（极坐标环形迷宫生成器）
│   ├── hmrterrorevent.lua     # 凶险事件（蜂拥而至，旧版）
│   ├── hmrarearegrowthmanager.lua # 区域资源再生管理器（世界组件）
│   ├── hmrcherryislandmanager.lua # 樱海岛资源/景观管理（世界组件）
│   ├── hmr_cherry_island_center.lua # 樱海岛中心标记（CLASSIFIED）
│   ├── hmrfactory*.lua        # 工厂（灵枢织造箱）系列：farmland/workshop/powergenerator/waterwell/techcore/widget
│   ├── hmrchest*.lua          # 箱子系列：store/transmit/recycle/factory/display
│   ├── hmrstatusmodifier.lua  # 全局装备状态修正
│   └── ...（hpick/hcurable/hmrrepairer/hmrtransplanter/hmrcherrystaff/hmruseableitem 等）
├── hmrmain/             # 主逻辑模块（modimport 引入）
│   ├── hmr_util.lua          # 3966行 工具库（GLOBAL.HMR_UTIL）
│   ├── hmr_init.lua          # 7618行 巨型初始化文件（全部系统postinit）
│   ├── hmr_house_api.lua     # 1194行 秘境（室内空间）世界规则适配层
│   ├── hmr_houses.lua        # 619行 房屋工厂：布局生成 + 传送器配对
│   ├── hmr_lists.lua         # 2450行 全部数据表：地皮/作物/种子映射/烤炉能量
│   ├── hmr_farm_plant.lua    # 作物定义 PLANT_DEFS
│   ├── hmr_recipes.lua       # 2347行 全部配方
│   ├── hmr_techtrees.lua     # 自定义科技树
│   ├── hmr_sgactions.lua     # 1271行 自定义Action/组件动作/状态机状态
│   ├── hmr_assets.lua        # 资源注册（图集/动画/声音/皮肤图片）
│   ├── hmr_skin.lua          # 6084行 皮肤系统（最大单文件）
│   ├── hmr_net_api.lua       # HTTP代理通信（皮肤同步）
│   ├── hmr_config_data.lua   # 按键绑定/UI数据
│   ├── hmr_containers.lua / hmr_spicedfoods.lua / hmr_preparedfoods.lua / hmr_fxs.lua
│   ├── hmr_terrorevents.lua  # 凶险事件触发（包裹PICK/DIG）
│   ├── hmr_factory_blessings.lua / hmr_factory_buildings.lua / hmr_chest_transmit_defs.lua
│   ├── hmr_coconut_cannon_ammo.lua / hmr_cherry_staff_preview.lua / hmr_cherry_cat_*.lua
│   ├── hmr_userdatahook_api.lua / hmr_blink_api.lua / hmr_extratagspace_api.lua
│   └── hmr_*（gifts/introduce_data/itemslist/skinpage_data/junkpiles 等）
├── hmrlanguages/hmr_ch.lua  # 全部中文字符串（947+行 STRINGS）
├── map/
│   ├── hmr_retrofit_island.lua   # 旧档补偿樱海岛（RetrofitSaveData.DoRetrofitting 覆盖）
│   ├── static_layouts/hmr_cherry_island.lua  # 39×39 静态岛屿布局
│   ├── static_layouts/replace.lua            # 39×39 地皮数字矩阵
│   ├── rooms/forest/honor_coconut_planted.lua # 倭椰树房间（月亮海滩）
│   ├── rooms/caves/terror_coffee_planted.lua  # 咖啡枝房间（泥潭）
│   └── layouts.lua?（引用 map/layouts 原版）
├── prefabs/             # 全部自建prefab（hmr_cherry_island_center 等）
├── widgets/             # hmr_cherry_kiln 烤炉界面等自定义widget
├── stategraphs/ / brains/ / behaviours/  # 自建AI（凶险生物）
├── images/              # 8个子目录：foodimages(20)/fx(16)/icons(5)/inventoryimages(509)/largeimages(16)/mapicons(17)/slotimages(79)/widgetimages(12)
├── anim/                # zip动画包：farm_plant_hmr_*_*.zip, hmr_cherry_*.zip, honor_*.zip, terror_*.zip
└── tests/               # 测试文件（双重加密，解密失败）
readme/
├── readme.lua           # 外部联动声明（风铃草皮肤系统/实体信息修改系统）
├── fengling_skinapi.lua # 840行 风铃草皮肤API（授权参考）
├── fengling_userdatahookapi.lua # 204行 UserDataHook API
├── 樱花花盆联动方法.lua   # 跨mod API模板
└── 凶险裹挟者联动方法.lua
exported/terror_blueberry_projectile/  # 空目录（导出残留）
```

### 1.3 功能系统清单

1. **双阵营装备体系**：辉煌系（honor_backpack 16/30格能量背包、honor_armor 护甲、honor_multitool 多用工具、honor_staff 法杖、honor_hat、honor_blowdarts、honor_coconut_handgun 椰子手枪、honor_coconut_cannon 椰子船炮）/ 凶险系（terror_staff、terror_sword、terror_vine、terror_hat 光球、terror_armor、terror_bomb、terror_sower 凶险裹挟者、terror_lemon_bomb、terror_blueberry_juicybag、terror_blueberry_cannon 蓝莓船炮、terror_whip、terror_machine、terror_tower）
2. **农作物体系**：16种自建作物（honor_coconut 倭椰、terror_coffee 咖啡、honor_hybrid_rice 杂交水稻、荔枝、柠檬、蓝莓、金灯笼果等），双阵营随机种子（honor_seeds/terror_seeds）+ 季节性加权识别 + ReplaceWithPlant 替换生长
3. **世界生成**：5种新地皮（樱花草/樱花花/樱花秘境/樱花小径/悉樱樱）、樱海岛静态布局（39×39）、旧档补偿retrofit、倭椰树/咖啡枝世界种植（聚集房间/分散注入两种模式）
4. **秘境（室内空间）系统**：小房子（hmr_houses）+ 传送门（hmrteleporter 入口/出口配对）+ 房屋内世界规则重写（相机/天气/温湿度/寻路/潮湿度）+ BFS房间识别（hmrroommanager）
5. **凶险事件**：极坐标环形迷宫（terror_spike_wall 尖刺墙 + terror_spike_shooter 射手 + terror_spike_cage 囚笼 + terror_spike_core 核心），玩家采撷凶险植物触发，难度随天数/次数增长
6. **工厂体系**（灵枢织造箱）：hmr_factory_center 核心 + farmland 农圃 + workshop 作坊 + waterwell 水井 + powergenerator 电机 + techcore 科技核心 + widget 部件；跨shard祝福系统（hmrfactoryblessingregistry）
7. **物流箱体系**：5种箱子（青衢纳宝箱 store / 云梭递运箱 transmit 跨箱物流 / 龙龛探秘箱 recycle 垃圾回收 / 灵枢织造箱 factory / 华樽耀勋箱 display 雕像展示）
8. **樱花烤炉**（hmr_cherry_kiln）：烧木头/木板产生能量，驱动烤炉科技（HMR_CHERRY_KILN_ENERGY 配方消耗），带自定义widget界面
9. **科技树**：HONOR_TECH / TERROR_TECH / HMR_TECH / HMR_CHERRY_TECH 四条自定义科技 + 2个原型机（honor_machine 自然亲和机器 / terror_machine）+ 烤炉原型
10. **皮肤系统**：6084行 hmr_skin.lua，装备皮肤 + 人物皮肤（风铃草皮肤API），CDK/HTTP代理同步（hmr_net_api → 127.0.0.1:28910）
11. **樱海岛生态**：樱花树/樱花草/樱花花/樱花蝴蝶/樱花绵羊(hmr_cherry_meltboo)/樱花猫+猫窝+毛球/烤炉+餐桌+椅子+灯笼 景观，区域资源再生（hmrarearegrowthmanager 保证可持续发展）
12. **NPC与战斗**：贪婪甲虫（terror_greedybeetle 吃农作物）、樱花守卫（honor_coconuttreeguard）、hmr_bees/hmr_beesghost 凶险蜂群
13. **其他**：辉煌修补套件（hmr_kits）、香料（hmr_spices）、调味料理（hmr_preparedfoods）、精华（hmr_primes）、buff系统、花盆移栽（hmrtransplanter）、研究者组件（hmrresearcher 扫描学习配方）、引燃者（hmr_igniter）、装饰家具（hmr_furnitures/hmr_flower_arch）、地毯terraform、樱花喷涂（防火/防工作）

### 1.4 加密情况说明

- 所有 scripts/ 下 .lua 经 DST Mod Encryptor 加密为 .lua.dec（十六进制文本），本项目解密为同名 .dec 文件阅读。
- 解密管线：LCG 线性同余（X=(X*1664525+1013904223)%4294967296）逐字节异或，文件头 0:8 magic "d75391c4"、8:10 版本01、16:24 签名 1525156183、24:32 种子、32:40 哈希校验。modmain.lua 与 modworldgenmain.lua 为双重加密（第一层解密出 loader 代码，再解密内嵌块）。
- tests/ 下文件为第二种双重加密，无法解出（哈希校验失败），按低价值跳过。
- modinfo.lua、readme/、images/、anim/、exported/ 未加密。

---

## 2. 框架架构：modworldgenmain vs modmain 分工

### 2.1 入口文件

- **modworldgenmain.lua**（世界生成期）：地皮注册 → 静态布局注册 → 岛屿setpiece → 旧档补偿 → 世界种植注入。仅在生成世界时运行。
- **modmain.lua**（运行期 loader）：PrefabFiles 清单 + GLOBAL.HMR_CONFIGS 配置缓存 + modimport 依次加载 20+ 个 hmrmain 模块。模组所有实体/组件/配方/科技/动作都在运行期挂载。

### 2.2 modmain 加载顺序（modmain.entry.lua 逐字摘录）

```lua
GLOBAL.setmetatable(env, {__index = function(t, k) return GLOBAL.rawget(GLOBAL, k ) end})
GLOBAL.HMR_LANTERN_POST_SKIN_DATA = {}

PrefabFiles ={
    "hmr_skin_ground_fxs", "hmr_skin_change_fxs", "hmr_cherry_paint_fxs",
    "hmr_furnitures", "hmr_houses", "hmr_factory_buildings", "hmr_flower_arch",
    "hmr_primes", "hmr_igniter_fx", "hmr_naturalmaterials", "hmr_spices",
    "hmr_preparedfoods", "hmr_kits", "hmr_buffs", "hmr_particle_fxs", "hmr_planted",
    "hmr_chests", "hmr_chest_factory_core", "hmr_dug_cavebananatree", "hmr_junkpiles",
    "hmr_seeds", "hmr_farm_plant_products", "hmr_farm_plant_products_special",
    "honor_goldenlanternfruit_lamp", "honor_hybrid_rice", "honor_coconuttreeguard",
    "honor_backpack", "honor_armor", "honor_multitool", "honor_staff", "honor_hat",
    "honor_blowdarts", "honor_coconut_handgun", "honor_coconut_cannon",
    "honor_machine", "honor_cookpot", "honor_tower", "honor_stower", "honor_balance_maintainer",
    "hmr_bees", "hmr_beesghost", "terror_spike",
    "terror_staff", "terror_sword", "terror_vine", "terror_hat", "terror_armor",
    "terror_bomb", "terror_sower", "terror_lemon_bomb", "terror_blueberry_juicybag",
    "terror_blueberry_cannon", "terror_whip", "terror_machine", "terror_tower",
    "terror_greedybeetle",
    "hmr_cherry_island_center",
    "hmr_cherry_grass", "hmr_cherry_flower", "hmr_cherry_butterfly",
    "hmr_cherry_meltboo", "hmr_cherry_rock", "hmr_cherry_tree",
    "hmr_cherry_carpet", "hmr_cherry_chair", "hmr_cherry_table",
    "hmr_cherry_lantern_post", "hmr_cherry_flowerpot", "hmr_cherry_decors",
    "hmr_cherry_kiln", "hmr_cherry_kiln_products", "hmr_cherry_paints",
    "hmr_cherry_spray", "hmr_cherry_backpack", "hmr_cherry_staff",
    "hmr_cherry_cat", "hmr_cherry_cat_ball", "hmr_cherry_cat_den",
}

-- 套装名称
GLOBAL.EQUIPMENTSETNAMES.HONOR = "HONOR"
GLOBAL.EQUIPMENTSETNAMES.TERROR = "TERROR"

-- 模组配置（集中缓存，供全模组读取）
GLOBAL.HMR_CONFIGS = {
    HONOR_BACKPACK_SLOTS = GetModConfigData("HONOR_BACKPACK_SLOTS") or 16,
    HONOR_BACKPACK_ENERGY_CONSUME_SPEED = GetModConfigData("HONOR_BACKPACK_ENERGY_CONSUME_SPEED") or 1.00,
    HONOR_STOWER_MAX_CONSUME = GetModConfigData("HONOR_STOWER_MAX_CONSUME") or 0.00,
    TERROR_HAT_LIGHT_TARGET = GetModConfigData("TERROR_HAT_LIGHT_TARGET") or "passive",
    TERROR_EVENT = GetModConfigData("TERROR_EVENT") or "maze",
    HMR_FACTORY_BLESSING_PERMISSION = GetModConfigData("HMR_FACTORY_BLESSING_PERMISSION") or "ANYONE",
}

-- 语言配置文件需优先导入
modimport("scripts/hmrmain/hmr_util")
modimport("scripts/hmrlanguages/hmr_ch")

modimport("scripts/hmrmain/hmr_tuning")
modimport("scripts/hmrmain/hmr_userdatahook_api")
modimport("scripts/hmrmain/hmr_blink_api")
modimport("scripts/hmrmain/hmr_house_api")

modimport("scripts/hmrmain/hmr_assets")
modimport("scripts/hmrmain/hmr_containers")
modimport("scripts/hmrmain/hmr_techtrees")
modimport("scripts/hmrmain/hmr_sgactions")
modimport("scripts/hmrmain/hmr_recipes")

modimport("scripts/hmrmain/hmr_fxs")
modimport("scripts/hmrmain/hmr_farm_plant")
modimport("scripts/hmrmain/hmr_spicedfoods")
modimport("scripts/hmrmain/hmr_terrorevents")
modimport("scripts/hmrmain/hmr_init")
modimport("scripts/hmrmain/hmr_cherry_staff_preview")

modimport("scripts/hmrmain/hmr_skin")
modimport("scripts/hmrmain/hmr_cherry_cat_clothing")
modimport("scripts/hmrmain/hmr_cherry_cat_soul_heal")

modimport("scripts/hmrmain/hmr_net_api")
```

要点：
- env metatable 挂 GLOBAL，使模块内裸变量名可直接访问全局。
- `GLOBAL.HMR_CONFIGS` 为全模组配置缓存模式（别处 `GLOBAL.HMR_CONFIGS.X` 读取）。
- 加载顺序即依赖顺序：util（基础工具）→ 语言 → tuning（数值）→ 三方API（userdatahook/blink）→ house_api（秘境规则）→ 资源/容器/科技/动作/配方 → fx/作物/香料/事件/init（挂载全部postinit）→ 皮肤/猫 → 网络。

### 2.3 组件挂载方式（hmr_init 的模式）

自定义组件以 `AddPrefabPostInit("world"/"player", ...)` 挂到 world 或 player 上，例如：

```lua
-- hmr_init.lua.dec ~3412 樱花岛管理组件
AddPrefabPostInit("world", function(inst)
    if not TheWorld.ismastersim then return end
    inst:AddComponent("hmrarearegrowthmanager")
    inst:AddComponent("hmrcherryislandmanager")
end)
```

```lua
-- hmr_init.lua.dec ~3426 人物跃迁组件
AddPlayerPostInit(function(player)
    player:AddComponent("hmrblinker")
    player.components.hmrblinker:SetBlinkFX()
end)
```

复组件（客户端可见状态）统一 `AddReplicableComponent("名字")` 声明：

```lua
-- hmr_init.lua.dec ~1588 工厂
AddReplicableComponent("hmrfactory")
AddReplicableComponent("hmrfactoryresources")
AddReplicableComponent("hmrfactoryfarmland")
AddReplicableComponent("hmrfactoryworkshop")
AddReplicableComponent("hmrfactorypowergenerator")
AddReplicableComponent("hmrfactorywaterwell")
AddReplicableComponent("hmrfactorytechcore")
AddReplicableComponent("hmrfactorywidget")
```

### 2.4 自定义 Action / 组件动作 / 状态机动作 三件套（hmr_sgactions.lua.dec）

这是本模组交互系统的骨架，三个注册点配套使用：

1) `AddModAction(id, data)` 包装 `Action()` + `AddAction`，支持 queue 行为学队列注册：

```lua
local function AddModAction(id, data)
    local action = Action()
    for k, v in pairs(data) do
        action[k] = v
    end
    action.id = id
    action.str = data.str or STRINGS.ACTIONS[id]
    AddAction(action)

    -- 添加行为学队列
    if data.queue ~= nil then
        local success, _ = pcall(require, "components/actionqueuer")
        if AddActionQueuerAction ~= nil then
            AddActionQueuerAction(data.queue.category or "allclick", id, data.queue.testfn or true)
        end
        if data.queue.init_fn ~= nil then
            AddComponentPostInit("actionqueuer", data.queue.init_fn)
        end
    end
end

for action, data in orderedPairs(HMR_ACTIONS) do
    local id = string.upper(MOD_NAME.."_"..data.id)  -- HMR_PICK / HMR_REPAIR ...
    AddModAction(id, data)
end
```

Action 定义实例（采集自定义植物）：

```lua
pick = {
    id = "PICK",
    fn = function(act)
        if act.target ~= nil then
            if act.target.components.hpick ~= nil then
                act.target.components.hpick:Pick(act.doer)
                return true
            elseif act.target.components.searchable ~= nil then
                return act.target.components.searchable:Search(act.doer)
            end
        end
    end,
    queue = { category = "leftclick", },
},
```

2) `AddComponentAction(kind, component, fn)` 按组件名分发场景动作（kind 为 SCENE/USEITEM/POINT/EQUIPPED/INVENTORY）：

```lua
HMR_COMPONENT_ACTIONS = {
    SCENE = {  -- args: inst, doer, actions, right
        hpick = function(inst, doer, actions)
            if inst:HasTag("pickable") and not (inst:HasTag("fire") or inst:HasTag("intense")) then
                table.insert(actions, ACTIONS.HMR_PICK)
            end
        end,
        ...
    },
    ...
}
for k, v in orderedPairs(HMR_COMPONENT_ACTIONS) do
    for component, fn in orderedPairs(v) do
        AddComponentAction(k, component, fn)
    end
end
```

3) `AddStategraphActionHandler("wilson"/"wilson_client", ActionHandler(action, state))` 绑定动作到状态机：

```lua
local HMR_ACTION_HANDLERS = {
    pick = "doshortaction",
    repair = "dolongaction",
    cure = "blowdart",
    ...
    cherry_staff = "veryquickcastspell",
}
local function AddModStategraphActionHandler(action, data)
    AddStategraphActionHandler("wilson", ActionHandler(action, data.fn))
    AddStategraphActionHandler("wilson_client", ActionHandler(action, data.clientfn or data.fn))
end
```

4) 复用原版动作钩子（WAX 改造为喷涂的例子，体现"包装原Action而非新建"的技法）：

```lua
local old_wax_strfn = ACTIONS.WAX.strfn
ACTIONS.WAX.strfn = function(act)
    if act.invobject ~= nil and act.invobject:HasTag("hmr_cherry_spray") then
        return "HMR_CHERRY_SPRAY"
    end
    return old_wax_strfn ~= nil and old_wax_strfn(act) or nil
end
...
local old_wax_fn = ACTIONS.WAX.fn
ACTIONS.WAX.fn = function(act)
    if act.invobject ~= nil and act.invobject.components.hmrcherryspray ~= nil then
        return act.invobject.components.hmrcherryspray:Spray(act.target, act.doer)
    end
    return old_wax_fn(act)
end
```

5) 自定义状态机状态（手炮射击状态，wilson + wilson_client 双端，含 server_states 关联）：

```lua
AddStategraphState("wilson", State{
    name = HONOR_COCONUT_HANDGUN_STATE,   -- "honor_coconut_handgun_shoot"
    tags = {"attack", "notalking", "abouttoattack", "busy"},
    onenter = function(inst)
        if inst.components.combat:InCooldown() then
            inst.sg:RemoveStateTag("abouttoattack")
            inst:ClearBufferedAction()
            inst.sg:GoToState("idle", true)
            return
        end
        local buffaction = inst:GetBufferedAction()
        local target = buffaction ~= nil and buffaction.target or nil
        if IsRiding(inst) then inst.Transform:SetFourFaced() end
        inst.AnimState:PlayAnimation("hand_shoot")
        inst.components.combat:SetTarget(target)
        inst.components.combat:StartAttack()
        inst.components.locomotor:Stop()
        if target ~= nil then
            inst.components.combat:BattleCry()
            if target:IsValid() then
                inst:FacePoint(target:GetPosition())
                inst.sg.statemem.attacktarget = target
            end
        end
        inst.sg:SetTimeout(math.max(inst.components.combat.min_attack_period, 24 * FRAMES))
    end,
    onexit = function(inst)
        if IsRiding(inst) then inst.Transform:SetSixFaced() end
    end,
    timeline = {
        TimeEvent(17 * FRAMES, function(inst)
            inst.SoundEmitter:PlaySound(HONOR_COCONUT_HANDGUN_SOUND)
            inst:PerformBufferedAction()
            inst.sg:RemoveStateTag("abouttoattack")
        end),
        TimeEvent(20 * FRAMES, function(inst)
            inst.sg:RemoveStateTag("attack")
        end),
    },
    ontimeout = function(inst) inst.sg:GoToState("idle", true) end,
    events = {
        EventHandler("animover", function(inst) inst.sg:GoToState("idle") end),
    },
})
-- 客户端状态：server_states = {HONOR_COCONUT_HANDGUN_STATE}, onenter 用 PerformPreviewBufferedAction 预览
```

替换攻击动作目标的钩子（ActionHandler.deststate 包装）：

```lua
local function PatchAttackActionHandler(sg)
    local handler = sg.actionhandlers ~= nil and sg.actionhandlers[ACTIONS.ATTACK] or nil
    if handler == nil or handler._hmr_honor_coconut_handgun_patched then return end
    local old_deststate = handler.deststate
    handler.deststate = function(inst, action)
        local old_state = old_deststate ~= nil and old_deststate(inst, action) or nil
        if old_state == "attack" and IsHonorCoconutHandgun(GetEquippedWeapon(inst)) then
            return HONOR_COCONUT_HANDGUN_STATE
        end
        return old_state
    end
    handler._hmr_honor_coconut_handgun_patched = true
end
AddStategraphPostInit("wilson", PatchAttackActionHandler)
AddStategraphPostInit("wilson_client", PatchAttackActionHandler)
```

（防重复修补用 `handler._hmr_..._patched = true` 哨兵标志——本模组全篇通用。）

---

## 3. 关键设计模式

### 3.1 地皮/地形/世界生成（重点）

#### 3.1.1 自定义地皮：HMRAddTile 包装器（modworldgenmain.entry.lua 逐字）

```lua
local function HMRAddTile(id, name, data)
	local TileRanges =
	{
		LAND = "LAND",      --陆地
		NOISE = "NOISE",    --噪波
		OCEAN = "OCEAN",    --海
		IMPASSABLE = "IMPASSABLE",  --不可逾越
	}
	local tile_name = string.upper(id)
	-- AddTile的具体定义可以去看游戏文件 /scripts/modutil.lua 第356~425行 和 /scripts/tilemanager.lua
	if WORLD_TILES[tile_name] == nil then
		AddTile(
			tile_name,  --地皮名称  注意这个是唯一的，不要和其他的重复 必须为大写
		TileRanges[data.ranges or "LAND"],    --地皮类型
		{
			ground_name = name, --自定义名字，随便填
			-- old_static_id = GROUND.MOSAIC_BLUE,  --旧版地皮编号 由于旧版地皮范围只能在0~255，已经不用了容易冲突，现在会自动给地皮分配编号，而且最大可以到8448。
		},
		{
			name = data.edge or "carpet",      --边缘样式 比如 牛毛地毯carpet 棋盘blocky 也可以自己做。这里设置为我们文件里的
			noise_texture = data.tex,     --这里是图片
			--定义在地皮上行走的声音
			runsound = data.runsound or "dontstarve/movement/run_marble",
			walksound = data.walksound or "dontstarve/movement/walk_marble",
			snowsound = data.snowsound or "dontstarve/movement/run_ice",
			mudsound = data.mudsound or "dontstarve/movement/run_mud",
			flooring = data.flooring or false,    	--标记为true则上面不能生长植物
			hard = data.hard or false,        	--标记为true则上面不可种植植物
			roadways = data.roadways or false,     	--标记为true则玩家在上面可以加速，类似于卵石路
			cannotbedug = data.cannotbedug,  	--标记为true则不能挖掉
			-- 海洋部分
			colors = data.colors or nil,
			ocean_depth = data.ocean_depth or nil,
			is_shoreline = data.is_shoreline or nil,
			wavetint = data.wavetint or nil,
		},
		{
			name = "map_edge",
			noise_texture = data.mini_tex,    --小地图图片
		},
		--挖掉的定义，如果这个表为空则挖掉之后不掉地皮
		data.item_prefab ~= nil and {
			name = data.item_prefab, -- 掉落物的代码
			anim = data.item_anim, -- Ground item
			bank_build = "hmr_turfs",
			invicon_override = data.item_prefab.."_turf",
			pickupsound = data.pickupsound or "vegetation_grassy",
		} or nil
		)
	end
	-- 设置地皮层级关系(前者在后者之下)
	local tile_over = data.tile_over or WORLD_TILES.FARMING_SOIL
	ChangeTileRenderOrder(WORLD_TILES[tile_name], tile_over)
	ChangeMiniMapTileRenderOrder(WORLD_TILES[tile_name], tile_over)
end

local TURF_LIST = require("hmrmain/hmr_lists").TURF_LIST
for _, data in pairs(TURF_LIST) do
	HMRAddTile(string.upper(data.id), data.name, data)
end
```

要点：
- AddTile 的 5 个参数：名字（大写唯一）、TileRange（LAND/NOISE/OCEAN/IMPASSABLE）、{ground_name}、{边缘+噪音贴图+声音+地面属性}、{小地图噪音贴图}、挖掉掉落定义（nil 则不可挖掉成地皮）。
- 地皮贴图 Asset 注册在 hmr_assets.lua：`Asset("IMAGE", "levels/tiles/"..data.edge..".tex")`（hmr_init 3400 行附近同样注册并可按 tile 挂 wavemanager 海浪）。
- 新地皮 ID 自动分配（可到 8448），不再用 old_static_id。
- `ChangeTileRenderOrder(WORLD_TILES[tile], tile_over)` 决定与既有地皮（默认 FARMING_SOIL）的渲染层级关系。

地皮数据表（hmr_lists.lua.dec 第26~80行）：

```lua
local TURF_LIST = {
    cherry_flower = {   -- 樱海岛樱花地皮
        id = "HMR_CHERRY_FLOWER",
        name = STRINGS.NAMES.TURF_HMR_CHERRY_FLOWER,
        tex = "hmr_cherry_flower_noise",
        edge = "hmr_cherry_grass",
        mini_tex = "hmr_cherry_flower_noise",
        item_prefab = "hmr_cherry_flower",
        item_anim = "cherry_grass",
    },
    cherry_grass = {    -- 樱海岛樱草地皮
        id = "HMR_CHERRY_GRASS", tex = "hmr_cherry_grass_noise",
        edge = "hmr_cherry_grass", mini_tex = "hmr_cherry_grass_noise",
        item_prefab = "hmr_cherry_grass", item_anim = "cherry_grass",
    },
    cherry_mystery = {  -- 樱海秘境地皮
        id = "HMR_CHERRY_MYSTERY", tex = "hmr_cherry_mystery_noise",
        edge = "hmr_cherry_grass", mini_tex = "hmr_cherry_mystery_noise",
        item_prefab = "hmr_cherry_mystery", item_anim = "cherry_mystery",
    },
    cherry_road = {     -- 樱花小径地皮（道路，加速）
        id = "HMR_CHERRY_ROAD", tex = "hmr_cherry_road_noise",
        edge = "blocky",
        runsound = "dontstarve/movement/run_dirt",
        walksound = "dontstarve/movement/walk_dirt",
        snowsound = "dontstarve/movement/run_ice",
        mudsound = "dontstarve/movement/run_mud",
        mini_tex = "hmr_cherry_road_noise",
        roadways = true,
        item_prefab = "hmr_cherry_road", item_anim = "cherry_road",
        pickupsound = "rock",
        tile_over = WORLD_TILES.COTL_BRICK
    },
    cherry_xmm = {      -- 悉樱樱地皮
        id = "HMR_CHERRY_XMM", tex = "hmr_cherry_xmm_noise",
        edge = "hmr_cherry_grass", mini_tex = "hmr_cherry_xmm_noise",
        item_prefab = "hmr_cherry_xmm", item_anim = "cherry_xmm",
    }
}
```

#### 3.1.2 静态岛屿布局（STATICLAYOUT.Get + ground_types + add_topology）

```lua
-- modworldgenmain.entry.lua 第79~102行
local LAYOUTS = require("map/layouts").Layouts
local STATICLAYOUT = require("map/static_layout")

-- 樱海岛
LAYOUTS["hmr_cherry_island"] = STATICLAYOUT.Get("map/static_layouts/hmr_cherry_island",{
	start_mask = PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
	fill_mask = PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
	layout_position = LAYOUT_POSITION.CENTER,
	disable_transform = true,--ground_noise_monkeyisland
	add_topology = {room_id = "StaticLayoutIsland:HMRCherryIsland", tags = {"hmr_cherry", "RoadPoison", "nohunt", "nohasslers", "not_mainland"}}
})
LAYOUTS["hmr_cherry_island"]["ground_types"] = {
	[1] = WORLD_TILES.OCEAN_COASTAL_SHORE,		-- 1
	[2] = WORLD_TILES.OCEAN_COASTAL,			-- 2
    [3] = WORLD_TILES.HMR_CHERRY_GRASS,			-- 3
    [4] = WORLD_TILES.HMR_CHERRY_FLOWER,		-- 4
	[5] = WORLD_TILES.HMR_CHERRY_MYSTERY,		-- 5
	[6] = WORLD_TILES.HMR_CHERRY_ROAD,			-- 6
}

AddLevelPreInitAny(function(level)
	if level.location == "forest" then
		if level.ocean_prefill_setpieces ~= nil then
			level.ocean_prefill_setpieces["hmr_cherry_island"] = {count = 1}
		end
	end
end)
```

要点：
- `STATICLAYOUT.Get("map/static_layouts/hmr_cherry_island", opts)` 读取 scripts/map/static_layouts/hmr_cherry_island.lua 返回的布局表（含 ground 地皮矩阵 + setpiece 数据）。
- `disable_transform = true`：关闭猴子岛式噪音变换。
- `add_topology.room_id = "StaticLayoutIsland:HMRCherryIsland"`：拓扑房间 ID 前缀 `StaticLayoutIsland:`（椰岛同款），tags 里 `not_mainland` 表示非大陆。
- `ground_types` 把布局矩阵数字映射到具体 WORLD_TILES（含自建地皮 ID）。
- `level.ocean_prefill_setpieces["hmr_cherry_island"] = {count = 1}`：作为海洋预填充 setpiece，在世界生成时放置到海里（与椰岛 monkeyisland 同机制）。

布局文件（scripts/map/static_layouts/hmr_cherry_island.lua.dec）：返回 `{ ground = 39x39 数字矩阵（数据来自 replace.lua 的 data 表）, setpieces = {...} }`。39×39 矩阵中 0=空白(海洋)、1=海岸、2=沿海、3=樱花草、4=樱花花、5=樱花秘境、6=樱花小径。中心含烤炉等 setpiece 摆放数据。

#### 3.1.3 旧档补偿岛屿（RetrofitSaveData.DoRetrofitting 覆盖）

modworldgenmain.entry.lua 第107~131行：

```lua
local function ShouldRetrofit(island, savedata)
	print("【丰耘秘境】补偿岛屿为正常操作，并非报错")
	for prefab, ents in pairs(savedata.ents) do
		if prefab == island.."_center" then
			print(string.format("【丰耘秘境】发现岛屿 %s ，跳过补偿", island))
			return false
		end
	end
	print(string.format("【丰耘秘境】未发现岛屿 %s ，尝试补偿", island))
	return true
end

local HMRRetrofitIsland = require("map/hmr_retrofit_island")
local RetrofitSaveData = require("map/retrofit_savedata")
local oldDoRetrofitting = RetrofitSaveData.DoRetrofitting
RetrofitSaveData.DoRetrofitting = function(savedata, world_map)
	-- 补偿樱海岛
	if TheWorld:HasTag("forest") and ShouldRetrofit("hmr_cherry_island", savedata) then
		HMRRetrofitIsland.RetrofittingCherryIsland(world_map, savedata, 1, CHERRY_ISLAND_GENERATION)
	end

	if oldDoRetrofitting ~= nil then
		oldDoRetrofitting(savedata, world_map)
	end
end
```

补偿实现（scripts/map/hmr_retrofit_island.lua.dec，核心逻辑逐字）：

```lua
local function RetrofittingCherryIsland(map, savedata, max_count, radius)
	max_count = max_count or 3
	local obj_layout = require("map/object_layout")

	local topology = savedata.map.topology
	local map_width = savedata.map.width
	local map_height = savedata.map.height
	local entities = savedata.ents

	local add_fn = {fn=function(prefab, points_x, points_y, current_pos_idx, entitiesOut, width, height, prefab_list, prefab_data, rand_offset)
				local x = (points_x[current_pos_idx] - width/2.0)*TILE_SCALE
				local y = (points_y[current_pos_idx] - height/2.0)*TILE_SCALE
				x = math.floor(x*100)/100.0
				y = math.floor(y*100)/100.0
				if entitiesOut[prefab] == nil then
					entitiesOut[prefab] = {}
				end
				local save_data = {x=x, z=y}
				if prefab_data then
					if prefab_data.data then
						if type(prefab_data.data) == "function" then
							save_data["data"] = prefab_data.data()
						else
							save_data["data"] = prefab_data.data
						end
					end
					if prefab_data.id then save_data["id"] = prefab_data.id end
					if prefab_data.scenario then save_data["scenario"] = prefab_data.scenario end
				end
				table.insert(entitiesOut[prefab], save_data)
			end,
			args={entitiesOut=entities, width=map_width, height=map_height, rand_offset = false, debug_prefab_list=nil}
		}

	local function is_rough_ocean(_left, _top, tile_size)
		for x = 0, tile_size do
			for y = 0, tile_size do
				if map:GetTile(_left + x, _top + y) ~= WORLD_TILES.OCEAN_ROUGH then
					return false
				end
			end
		end
		return true
	end
	-- (is_swell_ocean / is_rough_or_swell_ocean 同构，略)

	local function TryToAddLayout(name, topology_delta, isvalidareafn)
	    local layout = obj_layout.LayoutForDefinition(name)
		local tile_size = #layout.ground
		topology_delta = topology_delta or 1
		local candidtates = {}
		local num_steps = math.floor((map_width - tile_size) / tile_size)
		for x = 0, num_steps do
			for y = 0, num_steps do
				local left = 8 + (x > 0 and ((x * math.floor(map_width / num_steps)) - tile_size - 16) or 0)
				local top  = 8 + (y > 0 and ((y * math.floor(map_height / num_steps)) - tile_size - 16) or 0)
				if isvalidareafn(left, top, tile_size) then
					table.insert(candidtates, {top = top, left = left})
				end
			end
		end
		if #candidtates > 0 then
			local world_size = (tile_size + (topology_delta*2))*4
			shuffleArray(candidtates)
			for _, candidtate in pairs(candidtates) do
				local top, left = candidtates[1].top, candidtates[1].left
				local world_top, world_left = (left-topology_delta)*4 - (map_width * 0.5 * 4), (top-topology_delta)*4 - (map_height * 0.5 * 4)
				local ents_to_remove = FindEntsInArea(savedata.ents, world_top - 5, world_left - 5, world_size + 10, {"boat", "malbatross", "oceanfish_shoalspawner", "chester_eyebone", "glommerflower", "klaussackkey"})
				if ents_to_remove ~= nil then
					for i = #ents_to_remove, 1, -1 do
						table.remove(savedata.ents[ents_to_remove[i].prefab], ents_to_remove[i].index)
					end
				end
				obj_layout.Place({left, top}, name, add_fn, nil, map)
				if layout.add_topology ~= nil then
					AddSquareTopology(topology, world_top, world_left, world_size, layout.add_topology.room_id, layout.add_topology.tags)
				end
				return true
			end
		end
		return false
	end

    local success = TryToAddLayout("hmr_cherry_island", radius, is_rough_ocean) or TryToAddLayout("hmr_cherry_island", radius, is_rough_or_swell_ocean)
    return success
end
```

要点（这是"旧档补偿岛屿"的标准模板，直接可复用）：
- 用 `savedata.ents`（存档实体表）+ `obj_layout.LayoutForDefinition` + `obj_layout.Place` 在保存数据层面铺布局；add_fn 把布局坐标换算为世界坐标（减 map 尺寸一半 × TILE_SCALE=4）直接写回 savedata.ents。
- 候选位置网格采样（num_steps 步进），`isvalidareafn` 检查该区域全为 OCEAN_ROUGH（或 OCEAN_SWELL），保证放海里。
- `shuffleArray` 随机化候选后逐个尝试；放置前用 `FindEntsInArea` 清理区域内会破坏岛屿的原版实体（boat/malbatross/chester_eyebone 等）。
- 手工补拓扑节点：`AddSquareTopology(topology, world_top, world_left, world_size, room_id, tags)` 在 savedata.map.topology 里追加一个方形节点（area=size², poly=四角, type=NODE_TYPE.Default），保证寻路/地图信息一致。
- 难度参数 CHERRY_ISLAND_GENERATION 实际作为 topology_delta（0/30/52/60）控制包围岛屿的海带大小——数值越大可选位置越少。

#### 3.1.4 自定义房间 + 任务注入（AddRoom + AddTaskPreInit）

倭椰树房间（scripts/map/rooms/forest/honor_coconut_planted.lua.dec 全文件）：

```lua
AddRoom("HonorCoconut", {
	colour = {r=.8,g=1,b=.8,a=.50},
	value = WORLD_TILES.PEBBLEBEACH, -- 月亮海滩
	contents = {
		countprefabs = {
			honor_coconut_planted = function () return 12 + math.random(5) end
		},
		distributepercent = 0.3,
		distributeprefabs = {
            cactus = 0.2,
			succulent_plant = 0.3,
			oasis_cactus = 0.1,
			rock1 = 0.1,
			rock2 = 0.05,
			cavein_boulder = 0.1,
			flint = 0.1,
			rocks = 0.2,
		}
	}
})

AddTaskPreInit("Dig that rock", function(task)
    task.room_choices["HonorCoconut"] = function() return math.clamp(1 + math.random(SIZE_VARIATION), 1, 3) end
end)
AddTaskPreInit("The hunters", function(task)
    task.room_choices["HonorCoconut"] = function() return math.clamp(math.random(SIZE_VARIATION), 0, 1) end
end)
AddTaskPreInit("Mole Colony Rocks", function(task)
    task.room_choices["HonorCoconut"] = function() return math.clamp(1 + math.random(SIZE_VARIATION), 1, 2) end
end)
```

咖啡枝房间（scripts/map/rooms/caves/terror_coffee_planted.lua.dec）：结构相同，value=WORLD_TILES.MUD（泥潭），countprefabs 12+random(5) 咖啡枝，distributeprefabs 洞穴花/蕨/蘑菇/草，AddTaskPreInit 注入 MudWorld/MudCave/MudLights/MudPit 任务。

要点：
- `AddRoom(name, {colour, value=基础地皮, contents={countprefabs, distributepercent, distributeprefabs}})`。
- `AddTaskPreInit(taskname, fn)` 修改原版任务的 room_choices：key=房间名，value=数量函数（用 SIZE_VARIATION 随机）。即"在原版任务里塞自定义房间"的标准做法。
- 房间文件由 modworldgenmain 按配置 mode 决定是否 modimport（见下）。

#### 3.1.5 一次性采摘植物世界注入（双模式配置驱动）

modworldgenmain.entry.lua 第136~155行：

```lua
local WORLD_PLANTED_LIST = require("hmrmain/hmr_lists").WORLD_PLANTED_LIST
local function GetGenerateMode(plant)
	return GetModConfigData(string.upper(plant)) or 0
end
for name, data in pairs(WORLD_PLANTED_LIST) do
	local mode = GetGenerateMode(name)
	if mode == 0 then
		local world_name = string.find(name, "honor") and "forest" or "caves"
		modimport("scripts/map/rooms/"..world_name.."/"..name)
	elseif mode == 1 then
		for roomname, distribute in pairs(data) do
			AddRoomPreInit(roomname, function(room)
				if room.contents ~= nil and room.contents.distributeprefabs ~= nil then
					print("添加植物", name, "到", roomname)
					room.contents.distributeprefabs[name] = distribute
				end
			end)
		end
	end
end
```

WORLD_PLANTED_LIST 数据（hmr_lists.lua.dec）：

```lua
WORLD_PLANTED_LIST = {
    honor_coconut_planted = { Rocky=0.1, BGRocky=0.1, ... },   -- 聚集：modimport房间文件；分散：注入这些房间的distributeprefabs
    terror_coffee_planted = { LightPlantField=0.1, ... },
}
```

要点：
- 配置 0=聚集生成（import 自定义房间文件，该文件内含 AddRoom + AddTaskPreInit）；1=分散生成（AddRoomPreInit 把 prefab 塞进指定原版房间的 distributeprefabs）；2=不生成。
- 数据表 key=房间名，value=权重；`string.find(name,"honor")` 判断地表/洞穴。

#### 3.1.6 樱海岛资源再生（hmrcherryislandmanager + hmrarearegrowthmanager）

樱海岛中心实体（scripts/prefabs/hmr_cherry_island_center.lua.dec 全文件）——世界组件的"触发器"：

```lua
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst:AddTag("CLASSIFIED")
    inst.entity:SetPristine()
    inst.Remove = function() end
    if not TheWorld.ismastersim then
        return inst
    end
    inst:DoTaskInTime(0, function()
        if not POPULATING and
            TheWorld:HasTag("forest") and
            TheWorld.components and
            TheWorld.components.hmrcherryislandmanager ~= nil
        then
            local manager = TheWorld.components.hmrcherryislandmanager
            local area = manager:EnsureArea(inst:GetPosition())
            if area ~= nil and not area.initialized then
                manager:InitializeArea()
            end
        end
    end)
    return inst
end
return Prefab("hmr_cherry_island_center", fn)
```

关键模式：`CLASSIFIED` tag（不出现在保存/计数中）+ `inst.Remove = function() end`（不可删除）+ `SetPristine()` 后客户端直接 return + DoTaskInTime(0) 延迟初始化（POPULATING 检查保证生成期不触发）。

区域资源再生管理器（scripts/components/hmrarearegrowthmanager.lua.dec，657行）核心模式：

```lua
-- 关键常量
UPDATE_PERIOD = 60              -- 每60秒扫描一次
MAX_POSITION_ATTEMPTS = 100     -- 找点最多尝试100次
DEFAULT_PLAYER_BLOCK_RADIUS = ENTITY_POPOUT_RADIUS or 30

-- 区域配置结构（RegisterAreaConfig）
area_config = {
    radius = ...,               -- 区域半径（格子数）
    spawn_half_span = ...,      -- 初始散布半跨度
    player_block_radius = ...,  -- 玩家阻挡半径（区域内离玩家太近不刷）
    resources = {
        [key] = {
            tag = ...,                  -- 实体tag（FindEntities查找）
            tile = ...,                 -- 要求的落地地皮（可选）
            spacing_radius = ...,       -- 间距（同资源之间）
            min_count = ...,            -- 最少数量（低于则排队补）
            max_count = ...,
            respawn_threshold = ...,    -- 低于该值开始补
            target_count = ...,         -- 补到该值
            max_respawns_per_cycle = ..., -- 每周期最多补几个
            respawn_time = ...,         -- 补的间隔
            retry_time = ...,
            spawn_jitter = ...,
            initial_spawn = true/false, -- 是否初始生成
            spawn_weights = {...},      -- 多prefab权重
            is_available = function() end,
            should_queue_on_remove = true,
        },
        ...
    },
}
```

核心机制：
- **pending 队列**：`pending = { [key] = { ready_time = GetTime() + respawn_time } }`，时间到才 spawn。
- **live_counts / live_entities**：按 GUID 追踪已生成实体；`BindResourceEntity(inst, key)` 挂 `onremove` 回调 → 数量低于 respawn_threshold 就 QueueRespawn。
- **GetSpawnPosition**：IsValidPoint 检查 = 在区域内(distsq<=radius²) + 地皮匹配(GetGroundAtPoint==tile) + `CanPlacePrefabFilteredAtPoint` + 无玩家在 player_block_radius 内 + 不与其它资源资源冲突（间距）。
- **UpdateAllAreas** 每 60 秒周期执行，处理所有到期 pending。
- 存档：pending 只存 ready_time 相对时间，OnLoad 恢复。

樱海岛配置（scripts/components/hmrcherryislandmanager.lua.dec 713行）核心数值：

```lua
CHERRY_ISLAND_RADIUS = 39*4          -- 156 格
CHERRY_ISLAND_SPAWN_HALF_SPAN = 35*4 -- 140 格
TILE_SCALE = 4
ROAD_CLUSTER_MIN_SIZE = 4

-- 资源：树45~55（2天重生）、草48~60、岩石38~50、花28~40、猫窝2~6
-- 场景摆放：kiln_broken + 桌 + 凳 + 灯笼（FindRoadClusterKilnPoint 用BFS找道路集群）
-- 散落配置 SCATTER_CONFIGS：rock_item 撒草地6~10 / tree_fruit 撒花地5~8 / tree_flower 撒花地7~11
```

道路集群找点（kiln 摆放位置选择，BFS）：

```lua
-- 用BFS找出>=ROAD_CLUSTER_MIN_SIZE的连续樱花小径(HMR_CHERRY_ROAD)集群，
-- 每个候选格得分 = 道路邻居数*1000 - 到中心距离²，取最高分者
```

猫窝/烤炉等景观由 `InitializeScenicSpawns` 一次放置，资源则走 hmrarearegrowthmanager 循环再生。

### 3.2 农作物/农业体系

#### 3.2.1 PLANT_DEFS 数据驱动（scripts/hmrmain/hmr_farm_plant.lua.dec 617行）

作物全部用 PLANT_DEFS 表定义，通过 hmr_init 的循环自动挂 postinit：

```lua
-- hmr_init.lua.dec 第63~73行
local FARM_PLANT_LIST = HMR_LISTS.FARM_PLANTS_LIST
for name, data in pairs(FARM_PLANT_LIST) do
    if data.farm_plant_master_postinit ~= nil then
        AddPrefabPostInit("farm_plant_"..name, function(inst)
            if not TheWorld.ismastersim then return end
            data.farm_plant_master_postinit(inst)
        end)
    end
end
```

PLANT_DEFS 结构（honor_coconut 为代表，含生长时间/季节/肥料/阶段覆盖）：

```lua
-- hmr_farm_plant.lua.dec（关键字段摘录）
PLANT_DEFS["honor_coconut"] = {
    name = "honor_coconut",
    phases = {2, 2, 3, 4},        -- 各阶段天数
    regrow = false,
    num_phases = 4,
    water_consumption = {1, 1, 2, 2},
    nutrient_consumption = {0.8, 1, 1.5, 2},       -- 养分消耗
    nutrient_restoration = {0.6, 0.8, 1.2, 1.6},   -- 收获后养分恢复
    good_seasons = { spring = true, summer = true }, -- 季节偏好
    honor_plant = true,
    honor_weight = 1,
    terror_weight = 0,
    ...
}
```

- `MakeGrowTimes` 辅助函数生成各阶段生长时间。
- 随机种子权重 `SEED_WEIGHT_SEASON_MOD`：好季节权重乘系数。
- 肥料定义 FERTILIZER_DEFS 注册到 farmplant 组件的肥料表。
- plantregistryinfo / farm_plant_defs 与原版植物共存（weed_defs.weighted_seed_table 用于随机种子出杂草）。

#### 3.2.2 双阵营随机种子 + 识别 + 替换生长（hmr_init.lua.dec 第75~171行逐字核心）

```lua
local WEIGHTED_SEED_TABLE = require("prefabs/weed_defs").weighted_seed_table
local PLANT_DEFS = require("prefabs/farm_plant_defs").PLANT_DEFS
local RANDOM_SEED_STAGES_CACHE = {}
for _, name in pairs({"honor_seeds", "terror_seeds"}) do
    local function PickFarmPlant()
        if math.random() < TUNING.FARM_PLANT_RANDOMSEED_WEED_CHANCE then
            return weighted_random_choice(WEIGHTED_SEED_TABLE)
        else
            local season = TheWorld.state.season
            local weights = {}
            local season_mod = TUNING.SEED_WEIGHT_SEASON_MOD
            for k, v in pairs(PLANT_DEFS) do
                if name == "honor_seeds" and v.honor_plant then
                    weights[k] = v.honor_weight * ((PLANT_DEFS[k] and PLANT_DEFS[k].good_seasons[season]) and season_mod or 1)
                elseif name == "terror_seeds" and v.terror_plant then
                    weights[k] = v.terror_weight * ((PLANT_DEFS[k] and PLANT_DEFS[k].good_seasons[season]) and season_mod or 1)
                end
            end
            return "farm_plant_"..weighted_random_choice(weights)
        end
        return "weed_forgetmelots"
    end

    local function BeIdentified(inst, doer)
        inst._identified_plant_type = inst._identified_plant_type or PickFarmPlant()
        doer:PushEvent("idplantseed")
        inst:RemoveTag("israndomseed")
        return inst._identified_plant_type
    end

    local function ReplaceWithPlant(inst)
        if inst == nil or not inst:IsValid() then return end
        local x, y, z = inst.Transform:GetWorldPosition()
        if x == nil or z == nil then return end
        local plant_prefab = inst._identified_plant_type or PickFarmPlant()
        local plant = SpawnPrefab(plant_prefab)
        if plant == nil then return end
        plant.Transform:SetPosition(x, y, z)
        if plant.plant_def ~= nil then
            plant.no_oversized = true
            plant.long_life = inst.long_life
            plant.components.farmsoildrinker:CopyFrom(inst.components.farmsoildrinker)
            plant.components.farmplantstress:CopyFrom(inst.components.farmplantstress)
            plant.components.growable:DoGrowth()
            plant.AnimState:OverrideSymbol("veggie_seed", "farm_soil", "seed")
        end
        inst.grew_into = plant -- so the caller can get the new plant that replaced this object
        inst:Remove()
    end

    AddPrefabPostInit("farm_plant_"..name, function(inst)
        if not TheWorld.ismastersim then return end
        inst.BeIdentified = BeIdentified
        local function GetStages(stages)
            if RANDOM_SEED_STAGES_CACHE[name] ~= nil then return RANDOM_SEED_STAGES_CACHE[name] end
            local stages_copy = deepcopy(stages)
            for k, v in pairs(stages_copy) do
                if v ~= nil and v.name == "sprout" then
                    v.fn = ReplaceWithPlant
                    break
                end
            end
            RANDOM_SEED_STAGES_CACHE[name] = stages_copy
            return stages_copy
        end
        local stages = inst.components.growable ~= nil and inst.components.growable.stages
        local new_stages = GetStages(stages)
        if stages ~= nil and new_stages ~= nil then
            inst.components.growable.stages = new_stages
        end
    end)
end
```

要点：
- 随机种子本体是 farm_plant_honor_seeds / farm_plant_terror_seeds（走原版growable管线）。
- 生长到 sprout 阶段时（fn=ReplaceWithPlant）替换为真实作物实体；状态复制：farmsoildrinker（吸肥）、farmplantstress（压力）CopyFrom，DoGrowth() 立即发育，OverrideSymbol 换外观。
- 识别（BeIdentified）在玩家使用种子时触发（PickFarmPlant 按阵营权重×季节修正加权随机；israndomseed tag 移除）。
- 缓存 deepcopy 后的 stages（RANDOM_SEED_STAGES_CACHE）避免每实例重复深拷贝。

#### 3.2.3 一次性采摘植物（倭椰树 honor_coconut_planted）

- hmr_planted prefab 文件组：`hmr_planted`（一次性采摘植物预制体），通过 hmr_lists 的 WORLD_PLANTED_LIST 注入世界。
- 采摘走自定义组件 `hpick`（ACTIONS.HMR_PICK → hpick:Pick），摘完即消失不重生。
- 倭椰果实（honor_coconut 水果）：不可直接吃（RemoveComponent edible/perishable），需 HAMMER 敲开（workable 组件，workleft=ROCK_FRUIT_MINES*堆叠数），产出 honor_coconut_meat（60%）/ honor_coconut_juice（40%）+ 20% honor_plantfibre——"工具处理型食材"设计。

### 3.3 建筑/物品/配方体系

#### 3.3.1 自定义科技树（scripts/hmrmain/hmr_techtrees.lua.dec 104行全文件核心）

```lua
-- 逐字核心
TECH_INGREDIENT.HMR_CHERRY_KILN_ENERGY = TECH_INGREDIENT.HMR_CHERRY_KILN_ENERGY or "hmr_cherry_kiln_energy_material"
table.insert(TechTree.AVAILABLE_TECH, "HONOR_TECH")
table.insert(TechTree.AVAILABLE_TECH, "TERROR_TECH")
table.insert(TechTree.AVAILABLE_TECH, "HMR_TECH")
table.insert(TechTree.AVAILABLE_TECH, "HMR_CHERRY_TECH")

local Create_old = TechTree.Create
TechTree.Create = function(t, ...)
    local newt = Create_old(t, ...)
    newt["HONOR_TECH"] = newt["HONOR_TECH"] or 0
    newt["TERROR_TECH"] = newt["TERROR_TECH"] or 0
    newt["HMR_TECH"] = newt["HMR_TECH"] or 0
    newt["HMR_CHERRY_TECH"] = newt["HMR_CHERRY_TECH"] or 0
    return newt
end

TECH.NONE.HONOR_TECH = 0
TECH.HONOR_TECH = { HONOR_TECH = 1 }
TECH.TERROR_TECH = { TERROR_TECH = 1 }
TECH.HMR_TECH = { HMR_TECH = 1 }
TECH.HMR_CHERRY_TECH = { HMR_CHERRY_TECH = 1 }

TUNING.PROTOTYPER_TREES.HONOR_TECH = TechTree.Create({ HONOR_TECH = 1 })
TUNING.PROTOTYPER_TREES.TERROR_TECH = TechTree.Create({ TERROR_TECH = 1 })
TUNING.PROTOTYPER_TREES.HMR_TECH = TechTree.Create({ HMR_TECH = 1 })
TUNING.PROTOTYPER_TREES.HMR_CHERRY_TECH = TechTree.Create({ HMR_CHERRY_TECH = 1 })

for _, v in pairs(AllRecipes) do
    if v.level.HONOR_TECH == nil then v.level.HONOR_TECH = 0 end
    ...
end
```

要点：
- 新科技 = TechTree.AVAILABLE_TECH 插入 + TechTree.Create 补默认 0 + TECH.NONE 归零 + TECH.X = {X=1}（一级）+ TUNING.PROTOTYPER_TREES 注册原型机树。
- 遍历 AllRecipes 给所有既有配方补 0 级（否则报错）。
- TECH_INGREDIENT.HMR_CHERRY_KILN_ENERGY：配方消耗"烤炉能量"这种特殊材料。

原型机注册（hmr_recipes.lua.dec）：

```lua
AddPrototyperDef("honor_machine", {
    icon_atlas = "images/inventoryimages/honor_machine.xml",
    icon = "honor_machine.tex",
    is_crafting_station = false,          -- 不是制作台（学习式）
    action_str = "HONOR_STUDY",           -- 自定义学习动作
    filter_text = "辉煌",
})
AddPrototyperDef("terror_machine", { ... action_str = "TERROR_STUDY" ... })
AddPrototyperDef("hmr_cherry_kiln", {
    is_crafting_station = true,
    filter_text = "樱花烤炉",
    action_str = "HMR_CHERRY_STUDY",
})
AddRecipeFilter("HONOR_SCIENCE")
AddRecipeFilter("TERROR_SCIENCE")
AddRecipeFilter("HMR_SCIENCE")
```

#### 3.3.2 配方注册（hmr_recipes.lua.dec 2347行）

普通配方（物品）：

```lua
AddRecipe2("honor_staff", {
    Ingredient("honor_prime_honor", 1),
    Ingredient("twigs", 2),
    Ingredient("flint", 2),
}, TECH.HONOR_TECH, { tech = TECH.HONOR_TECH, filter = {"HONOR_SCIENCE", "MAGIC"}, atlas = "images/inventoryimages/honor_staff.xml" })
```

箱子配方（带自定义图集图片的5参 Ingredient 形式 + 分类过滤）：

```lua
-- 青衢纳宝箱（存储箱）
AddRecipe2("hmr_chest_store", {
    Ingredient("boards", 4, "images/inventoryimages/boards.xml", nil, "boards.tex"),
    Ingredient("cutstone", 2),
    Ingredient("honor_prime_honor", 2),
}, TECH.HMR_TECH, { filter = {"HMR_SCIENCE", "STRUCTURES", "CONTAINERS"}, atlas = "images/inventoryimages/hmr_chest_store.xml" })
```

工厂建筑配方（带条件函数 canbuild/testfn —— 只能在工厂室内建造）：

```lua
-- HMRFactoryBuildingCanPlace(name) 检查 HMR_FACTORY_BUILDINGS.CanPlaceAtPoint
-- HMRFactoryFarmlandCanBuild：tile中心对齐 |x-tx|<=0.1 且 house.prefab=="hmr_factory_center"
AddRecipe2("hmr_factory_farmland", {
    Ingredient("boards", 2), Ingredient("flint", 4), ...
}, TECH.HMR_TECH, {
    filter = {"HMR_SCIENCE", "STRUCTURES"},
    canbuild = HMRFactoryFarmlandCanBuild,   -- 能不能造（菜单显示）
    testfn = HMRFactoryBuildingCanPlace("hmr_factory_farmland"), -- 造的时候再验证
    ...
})
```

#### 3.3.3 樱花烤炉能量经济（CHERRY_KILN_LIST）

```lua
-- hmr_lists.lua.dec
CHERRY_KILN_LIST = {
    log = 5,      -- 木头 → 5能量
    boards = 15,  -- 木板 → 15能量
    ...
}
```

- 烤炉（hmr_cherry_kiln）自带 widget 界面（widgets/hmr_cherry_kiln），ContainerWidget.Open 时叠加自定义 UI（hmr_init 7564行：AddClassPostConstruct("widgets/containerwidget")）。
- 按钮 RPC 带距离/反垃圾校验：

```lua
AddModRPCHandler("HMR", "HMR_CHERRY_KILN_BTN", function(player, kiln, status)
    if kiln ~= nil and kiln.prefab == "hmr_cherry_kiln"
        and CanPlayerReachRPCEntity(player, kiln, 64)
        and AllowHMRAntiSpam(player, "HMR_CHERRY_KILN_BTN", 0.1, kiln.GUID) then
        ...
    end
end)
```

#### 3.3.4 资源自动注册（hmr_assets.lua.dec 611行）

- `Assets` 表：SOUNDPACKAGE mod_music.fev + DLC002/DLC003，ANIM hmr_turfs/hmr_placement/player_actions_*。
- `MINIMAPIMAGES_LIST` 循环：AddMinimapAtlas + Asset(ATLAS/IMAGE) 批量注册小地图图标。
- `INVENTORYIMAGES_LIST` ~300 项，含皮肤项（honor_armor_swan/lbb/zt、terror_staff_26vip 等）。
- `AddFarmPlantImages(plant, data)`：自动注册 farm_plant_X、fruits、cooked、seeds（跳过 common_seeds）、X_oversized/_waxed/_rotten 全套图。
- preparedfoods + spicedfoods（product.."_over"）循环注册。
- `RegisterScrapbookIconAtlas + RegisterInventoryItemAtlas + ScrapBookData[item]={name,tex,prefab}` + `Asset("ATLAS_BUILD", xml, 256)`：图鉴+物品图集双注册。
- MiniSign 系列 postinit：`OverrideSymbol("SWAP_SIGN"/"SWAP_SIGN_BG")` 让告示牌显示自定义纹理。

### 3.4 秘境（室内空间）机制 —— 本模组最独特的系统

整套系统 = 世界注册（hmrhouse）+ 玩家状态（hmrhousevisitor 双端）+ 传送（hmrteleporter）+ 房屋工厂（hmr_houses）+ 世界规则重写（hmr_house_api）+ 房间识别（hmrroom/hmrroommanager）。

#### 3.4.1 世界注册：hmrhouse（scripts/components/hmrhouse.lua.dec 141行）

```lua
-- 关键：房屋注册表，GetHouseAtPoint 通过 areafn 判断点是否在屋内
-- pos={x=2000,y=0,z=2000} 房屋中心预设在地图外（OnPos wrap：x<-2000 时 x=2000, z-=200 —— 环形地外空间）
-- AddHouse(id, areafn, data) / GetHouseAtPoint(x,z) → house, housedata
-- IsHouseEmpty()：扫描范围内所有实体，排除 hmr_house_part tag
```

要点：秘境空间放在世界坐标 (2000,0,2000) 附近（地图外），用 areafn（自定义区域函数）判定坐标归属，无需真的建第二张地图。

#### 3.4.2 玩家状态：hmrhousevisitor（replicable，双端文件）

服务端组件（scripts/components/hmrhousevisitor.lua.dec）+ 客户端 replica（scripts/components/hmrhousevisitor_replica.lua.dec 全文件）：

```lua
-- hmrhousevisitor_replica.lua.dec 全文件核心
local function RefreshHouseData(inst, self)
    if inst == nil or not inst:IsValid() then return false end
    self = self or (inst.replica ~= nil and inst.replica.hmrhousevisitor or nil)
    if self == nil then return false end
    if self:IsInHouse() and TheWorld.components.hmrhouse ~= nil then
        local x, y, z = inst.Transform:GetWorldPosition()
        local house, housedata = TheWorld.components.hmrhouse:GetHouseAtPoint(x, z)
        if house ~= nil then
            self.house = house
            self.housedata = housedata
            return true
        else
            self.house = nil
            self.housedata = nil
        end
    else
        self.house = nil
        self.housedata = nil
    end
    return false
end

local REFRESH_DELAYS = { 0, 0.5, 1, 3 }
local function QueueRefreshHouseData(inst, self)
    if inst == nil or inst.DoTaskInTime == nil then return end
    for _, delay in ipairs(REFRESH_DELAYS) do
        inst:DoTaskInTime(delay, RefreshHouseData, self)
    end
end

local function OnInHouseDirty(inst)
    local self = inst.replica ~= nil and inst.replica.hmrhousevisitor or nil
    RefreshHouseData(inst, self)
    if self ~= nil then QueueRefreshHouseData(inst, self) end
end

local HouseVisitor = Class(function(self, inst)
    self.inst = inst
    self._inhouse = net_bool(inst.GUID, "hmrhousevisitor._inhouse", "hmr_inhouse_dirty")
    inst:ListenForEvent("hmr_inhouse_dirty", OnInHouseDirty)
    inst:ListenForEvent("playeractivated", OnInHouseDirty)
    inst:ListenForEvent("changearea", OnInHouseDirty)
    self.housedata = nil
    self.house = nil
    QueueRefreshHouseData(inst, self)
end)
```

要点：
- `net_bool(inst.GUID, name, dirty_event)` 复写脏标记；监听 dirty/playeractivated/changearea 刷新房屋缓存。
- 分层延迟刷新 {0, 0.5, 1, 3}——进房瞬间位置未稳定，多拍重试。
- 客户端凭 `replica.hmrhousevisitor:GetHouseData()` 拿到相机/温度等房屋参数（供 hmr_house_api 使用）。
- 服务端 hmrhousevisitor 负责 SetInHouse 状态 + 与传送器联动。

#### 3.4.3 传送器：hmrteleporter（scripts/components/hmrteleporter.lua.dec 435行）

```lua
-- 入口/出口成对：Activate(doer) → Teleport(target, doer)
-- Target() 获取配对的另一端（GUID引用，OnSave/OnLoad 持久化）
-- ReceivePlayer：ScreenFade + 慢镜头过渡 travelcameratime=3（SnapCamera）+ travelarrivetime=4（GoToState hmr_teleportarrivestate）
-- ReceiveItem：AddChild + RemoveFromScene + 0.5秒后弹回（到达动画）
-- FindWalkableOffset/FindSwimmableOffset 找落点；target_in_house 时跳过海洋/陆地检查
-- 随从传送：ShouldTeleportFollower（chesters/宠物）
-- OnRemoveEntrance：踢出玩家(kill=true)、销毁可工作物、perish掉物品 —— 出口被拆时屋内清场
```

#### 3.4.4 房屋工厂：hmr_houses.lua（scripts/hmrmain/hmr_houses.lua.dec 619行）

```lua
-- 工厂屋参数
FACTORY_WIDTH_TILES = 7
FACTORY_HEIGHT_TILES = 5
TILE_SIZE = 4
FACTORY_CAMERA_DISTANCE = max(28, 20) + 14  -- 42

-- 房屋定义（SetUpHouse(entrance, type, pt)）：
-- 1) 在 (2000,0,2000) 偏移位置生成布局 prefab（hmr_factory_exit/center/backwall/leftwall/rightwall/ground）
-- 2) 布局 prefab 上带 hmrteleporter 组件，与门口入口 Target() 配对
-- 3) 空气墙 hmr_air_wall 围边界（boundary {width=30, height=22, wallprefab="hmr_air_wall"}）
-- 4) 房屋数据：
house_data = {
    camera = { pitch=35, heading=0, distance=42, yoffset=6, fov=30, offset=Vector3(0,2,0) },
    temp_override = 25,          -- 恒温25度
    snap_to_tile_grid = true,
    boundary = {...},
    areafn = function(x,z) |x-cx|<=H/2 and |z-cz|<=W/2 end,
}
-- 5) 多皮肤室内装修：hmr_factory_indoor_blue / _blueberry / _coconut（DynamicAnimAssets: DYNAMIC_ANIM + PKGREF）
```

#### 3.4.5 世界规则重写：hmr_house_api.lua（scripts/hmrmain/hmr_house_api.lua.dec 1194行）

这是"室内空间"是否成立的关键——在 TheWorld 层面把室内当独立世界：

| 系统 | 处理 |
|---|---|
| 相机 | followcamera.Apply 包装：读 `ThePlayer.replica.hmrhousevisitor:GetHouseData().camera` → `TheSim:SetCameraPos/Dir/Up/FOV/Listener` 覆盖 |
| 地图 | `Map.IsAboveGroundAtPoint` / `IsVisualGroundAtPoint` 在屋内强制 true（当陆地渲染） |
| 温度 | `GetTemperatureAtXZ` 返回 temp_override |
| 天气 | frograin/wildfire/sinkhole 全部抑制；EmitterManager.PostUpdate 清除雨雪粒子；雪隐藏（snow 不可见） |
| 潮湿度 | moisture / inventoryitemmoisture 强制 dry；`EntityScript.GetIsWet` 打补丁返回 false |
| 腐败 | perishable 工厂 `perish_rate_multiplier` 屋内=0（不腐） |
| 寻路 | areaaware house=area -1；birdspawner 屏蔽 |
| 脚步 | PlayFootstep 替换为木质声音 |
| 技能封锁 | telestaff 禁用、playercontroller.EnableMapControls 禁用（不能看地图）、HAMMER 不能拆（非空房） |
| 视觉 | playervision colourcube 覆盖（屋内永远是白天色调） |
| 动画 | 玩家动画 build 替换（室内专用动作） |

自定义进入动作 + 状态机（hmr_house_api 核心逐字）：

```lua
local HOUSE_ACTION = Action({ priority = 1, mount_valid = true, ghost_valid = true, encumbered_valid = true, distance = 2 })
HOUSE_ACTION.id = "HMR_HOUSE"
AddAction(HOUSE_ACTION)
AddStategraphActionHandler("wilson", ActionHandler(ACTIONS.HMR_HOUSE, "hmr_enterhouse"))

-- hmr_enterhouse / hmr_enterhouse_pst 状态：
-- 进门前：ToggleOffPhysics → ClearCollisionMask(只留GROUND) → invincible → Hide
-- 传送器 Activate → DoneTeleporting 恢复完整碰撞掩码(WORLD/OBSTACLES/SMALLOBSTACLES/CHARACTERS/GIANTS)
```

#### 3.4.6 BFS 房间识别：hmrroom + hmrroommanager（scripts/components/hmrroom.lua.dec 129行 + hmrroommanager.lua.dec 471行）

```lua
-- hmrroom：单实体房间组件
-- PointToWallCenter = floor + 0.5（石墙中心格）
-- IsPointInRoom 用 point_map 键 "wx_wz" 查哈希

-- hmrroommanager（世界组件）：
-- BFS洪泛：从起点格向四邻扩展，检查 Pathfinder:IsClear(x,0,z,nx,0,nz, {ignorewalls=false, ignorecreep=false, allowocean=false, ignoreLand=false})
--   且邻格不是 door/wall/fence 实体（通过 FindEntities 查障碍 tag）
-- 房间合法：0 < #points <= max_size（10~400）
-- 事件：enterroom / leaveroom / roommemberremoved / newroommember
-- moving_ents 周期刷新（追踪移动实体所在房间）
-- 用途：工厂屋内自动识别"房间"，供物流箱/农圃绑定
```

#### 3.4.7 凶险迷踪事件（极坐标环形迷宫，scripts/components/hmrterrorevent_new.lua.dec 1154行）

触发链：采撷凶险植物（hmr_terrorevents.lua 包裹 ACTIONS.PICK.fn/DIG.fn → PushEvent("ms_startterrorevent")）→ world 组件 OnTerrorPicked → StartTerrorEvent。

```lua
-- 常量
TERROREVENT_TIMER_NAME = "terror_event_timer"
TERROREVENT_COOLDOWN_TIMER_NAME = "terror_event_cooldown_timer"
TERROREVENT_MAX_DURATION = 600
TERROREVENT_COOLDOWN_DURATION = 240

-- 难度 = 平均天数 × 累计采摘次数 重映射
-- GetDifficulty: return Remap(days_remap * pick_remap, 0, 10000, 5, 100)
-- data.size = math.clamp(difficulty, 5, 50)

-- 形状选择（加权）
-- SHAPES = {[10]=2, [9]=1, [8]=4, [7]=1, [6]=8, [5]=2, [4]=3, [3]=1}  → mode（每环顶点数）

-- 生成位置：HMR_UTIL.FindPoint(target:GetPosition(), data.size+5, data.size+20)
```

迷宫生成（极坐标环形）：

```lua
-- SpawnMaze(pt, data)：以 pt 为中心，半径 2..size 步长4 的同心环层
-- 每层 mode 个顶点构成多边形，沿边铺墙（PRECISION=100 取整坐标）
-- 开洞：open_length=3.0、same_layer_open_distance=8、cross_layer_open_horizontal=5、path_safe_margin=0.35
--   target_open_count = get_open_count(radius, level)，系数 0.5/1/1.5（层越外越多开洞）
--   每次尝试<50次，选角距最优边，t1/t2 开洞区间；同层开洞间距约束 + 跨层水平距离约束
-- 径向隔离墙：small_wall_count_per_pair=3，is_block 检查 path_safe_margin（不堵死路）
-- 墙实体：terror_spike_wall，rot=random()*360，delay=random()*3 后 DelayShow（渐现）
```

分帧生成（避免一次生成卡帧，SPAWN_PER_FRAME=8 + YIELD_AFTER_MS=4 时间片）：

```lua
local SPAWN_PER_FRAME = 8
local YIELD_AFTER_MS = 4
...
while count < SPAWN_PER_FRAME and spawn_index <= total_walls do
    ...
    local wall = self:SpawnMember("terror_spike_wall")
    wall.Transform:SetPosition(d.x, 0, d.z)
    wall.Transform:SetRotation(d.rot)
    if wall.DelayShow then wall:DelayShow(d.delay) end
    if (GetTimeReal() - start_time) * 1000 > YIELD_AFTER_MS then break end
end
self.maze_spawn_task = inst:DoTaskInTime(0, spawn_chunk)
```

事件生命周期（StartTerrorEvent / StopTerrorEvent 逐字核心）：

```lua
-- StartTerrorEvent(picker, plant, data)
worldsettingstimer:StartTimer(TERROREVENT_TIMER_NAME, TERROREVENT_MAX_DURATION)
self.isterror = true
-- 分步骤生成（避免帧阻塞）：
self.start_tasks[1] = self.inst:DoTaskInTime(0,   function() if self:IsInTerrorEvent() then self:SpawnMaze(pt, data) end end)
self.start_tasks[2] = self.inst:DoTaskInTime(0.1, function() if self:IsInTerrorEvent() then self:SpawnShootersInMaze(pt, {size = data.size}) end end)
self.start_tasks[3] = self.inst:DoTaskInTime(0.2, function() if self:IsInTerrorEvent() then self:SpawnShooters() end end)
self.start_tasks[4] = self.inst:DoTaskInTime(0.3, function() if self:IsInTerrorEvent() then self:SpawnCages() end end)
-- 玩家buff：RemoveTimerForActivePlayers(self, "terror_event_cooldown") + AddTimerForActivePlayers(self, "terror_event")

-- StopTerrorEvent(doer, reason, skip_cooldown)：取消全部任务、停计时器、reason=="corepicked"时 RemoveMembers(true)清场、
-- 非skip_cooldown且曾激活 → 启动240秒冷却 + 玩家换 cooldown buff

-- 射手（terrorspike_shooter）：围绕玩家5~10格刷，GetShooterSpawnDuration = 3/difficulty*100 + random()*3 秒一只
-- 囚笼（terror_spike_cage_parent）：刷在玩家脚下 SetTarget(player)，GetCageSpawnDuration = 5/difficulty*100 + random()*3 + 距核心距离约束
-- 存档：pick_record（每人每植物采摘次数）、core_point、members_guid（GUID数组，LoadPostPass 还原）
```

要点：
- 玩家加入/离开动态管理（OnPlayerJoined/OnPlayerLeft + ResumeTerrorEventForPlayer/StopTerrorEventForPlayer，每个玩家独立 spawn 任务表）。
- prevent_source（其他模组/本模组可禁止事件）。
- buff 作为玩家 UI 计时器（terror_event_buff / terror_event_cooldown_buff）。

### 3.4.8 装备机制范例：辉煌护甲霸体/防击退 + 辉煌工具切模式（hmr_init.lua.dec 第204~361行）

护甲套装效果全部通过 wilson 状态机事件包装实现（attacked 无硬直 / knockback 防击退 / suspended 防恶液 / devoured 防吞噬），判定用 `replica.inventory:EquipHasTag("honor_armor")`（跨端一致）：

```lua
-- 受击无硬直
local attacked_event = sg.events["attacked"]
if attacked_event ~= nil then
    local oldfn = attacked_event.fn
    attacked_event.fn = function(inst, data, ...)
        if not inst.components.health:IsDead() and not inst.sg:HasStateTag("drowning") then
            if not inst.sg:HasStateTag("sleeping") then
                if inst.replica.inventory and inst.replica.inventory:EquipHasTag("honor_armor") then
                    inst.SoundEmitter:PlaySound("dontstarve/wilson/hit")
                    DoHurtSound(inst)
                    return
                end
            end
        end
        return oldfn and oldfn(inst, data, ...)
    end
end

-- 防击退（黑名单例外）
local KNOCKBACK_BLACK_LIST = { gelblob = true, worm_boss = true, worm_boss_tail = true }
local knockback_event = sg.events["knockback"]
if knockback_event ~= nil then
    local oldfn = knockback_event.fn
    knockback_event.fn = function(inst, data, ...)
        if inst.replica.inventory and inst.replica.inventory:EquipHasTag("honor_armor") and
            not (data and data.knocker and data.knocker.prefab and KNOCKBACK_BLACK_LIST[data.knocker.prefab])
        then
            return
        end
        return oldfn and oldfn(inst, data, ...)
    end
end
```

按键技能（键盘 RPC 模式，HMR_UTIL.AddKeyboardControl 双注册 down/up）：

```lua
HMR_UTIL.AddKeyboardControl("honor_armor_skill_enabled", {
    {name = "honor_armor_skill_enable", down = true, key = "HONOR_ARMOR_SKILL", params = true},
    {name = "honor_armor_skill_disable", down = false, key = "HONOR_ARMOR_SKILL", params = false}
}, function(player, enabled)
    local function FindEquippedHonorArmor()
        if player and player.components.inventory then
            for k, v in pairs(player.components.inventory.equipslots) do
                if v and v.prefab == "honor_armor" then return v end
            end
        end
    end
    local armor = FindEquippedHonorArmor()
    if armor ~= nil then
        if enabled then armor:EnableSkill(player) else armor:DisableSkill(player) end
    end
end)
```

其它：辉煌工具（honor_multitool）按键切换耕地模式（`tool:ChangeMode(player)`）；finiteuses 组件扩展 `SetOnUsedAsItem` 钩子；主动兼容《一田十格》模组的 snaptillplacer 圆圈显示（AddComponentPostInit("snaptillplacer")）。

### 3.4.9 物流箱网络 + 容器UI叠加层模式（hmr_init.lua.dec 第851~963行）

云梭递运箱（hmr_chest_transmit）构成跨箱物流网络：

```lua
-- 网络 = world 组件 hmrchesttransmitnetwork + 每个箱子的两个复组件
AddReplicableComponent("hmrchesttransmitmode")
AddReplicableComponent("hmrchesttransmitter")
AddPrefabPostInit("world", function(inst)
    if TheWorld.ismastersim and inst.components.hmrchesttransmitnetwork == nil then
        inst:AddComponent("hmrchesttransmitnetwork")
    end
end)
-- 所有"chest"或"hmr_factory_building" tag 的容器自动获得模式组件（AddPrefabPostInitAny 全量兜底）
-- hmrinfodisplayer:AddAdditionalInfo("hmr_chest_transmit_mode", fn, -20) 在悬停信息里追加当前模式
```

容器界面叠加自定义控件（在 ContainerWidget.Open 时挂子widget——自定义箱子UI的标准做法）：

```lua
AddClassPostConstruct("widgets/containerwidget", function(ContainerWidget)
    local oldOpen = ContainerWidget.Open
    function ContainerWidget:Open(container, ...)
        oldOpen(self, container, ...)
        local mode = container ~= nil and container.replica ~= nil and container.replica.hmrchesttransmitmode or nil
        if mode ~= nil then
            if self.hmr_chest_transmit_controls == nil then
                self.hmr_chest_transmit_controls = self:AddChild(HMRChestTransmitControls(self.owner, self))
            end
            self.hmr_chest_transmit_controls:MoveToFront()
            self.hmr_chest_transmit_controls:SetContainer(container)
        elseif self.hmr_chest_transmit_controls ~= nil then
            self.hmr_chest_transmit_controls:SetContainer(nil)
            self.hmr_chest_transmit_controls:Hide()
        end
    end
    local oldClose = ContainerWidget.Close
    function ContainerWidget:Close(...)
        if self.hmr_chest_transmit_controls ~= nil then
            self.hmr_chest_transmit_controls:SetContainer(nil)
            self.hmr_chest_transmit_controls:Hide()
        end
        oldClose(self, ...)
    end
end)
```

配套：TheFrontEnd.hmr_notification_feed 通知流（HUD级widget，MoveToFront 常驻顶层）+ hmrinfodisplayer 悬停信息注入（AddAdditionalInfo(key, fn, priority)）。

### 3.5 网络与跨端模式

#### 3.5.1 跨shard祝福系统（hmr_factory_blessings + hmrfactoryblessingregistry）

```lua
-- hmr_init.lua.dec 1605行起
AddShardModRPCHandler("HMR", "HMR_FACTORY_BLESSING_SOURCE", function(shard_id, source_id, encoded)
    local registry = TheWorld ~= nil and TheWorld.components.hmrfactoryblessingregistry or nil
    if registry ~= nil then registry:ReceiveSourceReport(shard_id, source_id, encoded) end
end)
AddShardModRPCHandler("HMR", "HMR_FACTORY_BLESSING_PLAYERS", function(shard_id, encoded) ... ReceivePlayerReport ... end)
AddShardModRPCHandler("HMR", "HMR_FACTORY_BLESSING_SYNC", function(shard_id) ... BroadcastSnapshot ... end)
AddShardModRPCHandler("HMR", "HMR_FACTORY_BLESSING_SNAPSHOT", function(shard_id, encoded) ... ApplySnapshot ... end)
```

- 主世界（master shard）持有祝福注册表，各 shard 汇报本源/玩家数据，主世界广播快照同步——跨洞穴祝福一致。
- AddDebuff 包装：工厂来源的 buff 暂停 buffover 计时器（无限期），区分 `_hmr_factory_blessing_mode` "factory"/"food" 并在 OnSave/OnLoad 持久化。

#### 3.5.2 客户端通知（PushHudNotification）

```lua
UTIL.PushHudNotification = function(player, message)
    if player == nil or player.userid == nil or type(message) ~= "string" or message == "" then return false end
    local rpc = CLIENT_MOD_RPC ~= nil and CLIENT_MOD_RPC.HMR ~= nil and CLIENT_MOD_RPC.HMR.HMR_NOTIFICATION or nil
    if rpc == nil then return false end
    SendModRPCToClient(rpc, player.userid, message)
    return true
end
```

#### 3.5.3 HTTP 代理（hmr_net_api.lua.dec 184行）

```lua
-- TheSim:QueryServer 请求 http://127.0.0.1:28910（本地代理服务）
-- 参数：url/method/request_id URL编码；响应 JSON {status="success", code, data}
-- data = base64 + XOR 加密，密钥 "qianqianzuiainanala520****"
-- 用途：GLOBAL.HMRGetSkinDataFromNet 皮肤同步（userid + action=get_user_info + mod=HMR）
```

#### 3.5.4 RPC 安全校验惯例

- `CanPlayerReachRPCEntity(player, ent, range)` 距离校验（烤炉按钮 64）。
- `AllowHMRAntiSpam(player, name, interval, key)` 反垃圾（0.1秒节流）。
- 服务端二次校验（HMR_FACTORY_BLESSING_PERMISSION 提示"服务端会再次校验，无法通过界面绕过"）。

### 3.6 工具库亮点（scripts/hmrmain/hmr_util.lua.dec 3966行）

- `UTIL.RegisterPrefab(...)`：批量注册prefab（勋章同款），128个一批用依赖注入 dummy prefab（HMR_pre_reg_N）防止单帧注册过多——超大mod必需品。
- `UTIL.AddPrefabPreInit(name, fn)`：AddPrefabPostInit("world") 后包装 Prefabs[name].fn 实现"pre-fn 钩子"。
- `UTIL.UV_Get/UV_Set/UV_GetAll`：upvalue 手术（debug.getupvalue 按 file_pattern 过滤文件），实现跨函数局部变量读写。
- `UTIL.DiscardComponent(inst, name)`：安全移除组件（pcall 包 StopUpdatingComponent 等）。
- `UTIL.FindPoint(pos, min_dist, max_dist)`：环形搜索找安全点（10个半径步 × 扇区角度尝试）——凶险事件/射手刷点通用。
- `UTIL.AddKeyboardControl`：RPC 绑键（客户端按键 → 服务端 RPC 执行）。
- `UTIL.AddCharacterSkill/RemoveCharacterSkill/HasCharacterSkill`：SKILL_TAGS 哈希 + net_bool 技能系统。
- `UTIL.GetLocalVar`：debug.sethook 行钩子抓模块局部变量（调试神器）。
- `UTIL.PrintTable`：环检测 + 分块打印。
- `UTIL.AddDeployHelper/MakePlacerWithRange`：放置范围圈。
- `UTIL.GetFarmingHolePositions`：耕地孔位计算。
- `UTIL.QuickGrow`、`UTIL.EnableWaterWalking`、`UTIL.AddConstantTemperatureSource`、`UTIL.AddTailEffect`、`UTIL.AppearGradually/DisappearGradually/FadeIn/FadeOut`（渐现渐隐）。
- `UTIL.IsModEnabled(modname)`：KnownModIndex 扫描，检测其他mod是否启用。
- `UTIL.IsTerrorPlant`：PLANT_DEFS.terror_plant 判定。
- `UTIL.FunctionTest/matcher`：源码级函数定位工具（match_file 按文件模式）。

---

## 4. 高价值技法（Top 5）

### 4.1 室内空间（秘境）完整实现 —— "世界规则覆盖层"模式
本模组最值得抄的系统。核心思想：**不建新地图，在 (2000,0,2000) 地图外坐标放布局，用"点归属函数"(areafn) 判定室内，然后系统性覆盖世界API**（相机/温度/天气/潮湿度/腐败/寻路/脚步声/地图开关）。复组件用 net_bool 同步"在屋内"状态，客户端凭 replica 数据算相机。进房动画走自定义 Action + 状态机 + 物理掩码切换。传送器成对 GUID 引用，出口被拆自动清场。
来源：hmr_houses.lua / hmr_house_api.lua / hmrhouse.lua / hmrhousevisitor*.lua / hmrteleporter.lua

### 4.2 极坐标环形迷宫 + 分帧生成 —— 不卡服的百万级实体事件
迷宫按同心环层生成（半径2起步长4，每层 mode 顶点多边形），开洞算法带同层/跨层距离约束，隔离墙保证通路。所有批量实体用 `SPAWN_PER_FRAME=8` + `GetTimeReal()*1000 > YIELD_AFTER_MS(4ms)` 时间片分帧 + `DoTaskInTime(0)` 续帧，整座迷宫生成不造成单帧卡顿；墙用 `DelayShow(delay)` 随机延迟渐现，视觉上"生长"出来。事件生命周期用 worldsettingstimer（存读档自动恢复）+ 每玩家独立任务表。
来源：hmrterrorevent_new.lua

### 4.3 区域资源再生管理器 —— 可持续资源点通用方案
通用配置驱动：`{radius, spawn_half_span, player_block_radius, resources{key={tag, tile, spacing, min/max_count, respawn_time, spawn_weights,...}}}`。60秒周期 + pending 队列（ready_time）+ GUID 追踪 + onremove 回调排队补刷 + FindEntities 按 tag 数活体 + IsValidPoint 五重校验（区域/地皮/放置过滤器/玩家距离/资源间距）。樱海岛 6 类资源一套配置全搞定。
来源：hmrarearegrowthmanager.lua / hmrcherryislandmanager.lua

### 4.4 旧档补偿岛屿 —— RetrofitSaveData 挂钩
在 `RetrofitSaveData.DoRetrofitting` 前插入补偿逻辑：按存档实体表判断缺岛屿 → 网格采样候选位置（全 rough 海）→ obj_layout.Place 写回 savedata.ents → 清理冲突实体（boat/eyebone 等）→ 手工 AddSquareTopology 补拓扑节点。玩家旧档开新版本自动长出岛屿，且打上了"补偿为正常操作"的日志安抚。
来源：hmr_retrofit_island.lua / modworldgenmain.entry.lua

### 4.5 Action 三件套 + 复用原版 Action —— 交互系统的工业化
`AddModAction`（数据驱动批量注册 Action + 行为学队列）/ `AddComponentAction`（按组件名分发场景/物品/装备/背包/指向动作）/ `AddStategraphActionHandler`（绑定 wilson/wilson_client 状态）三件套一次性定义完一个交互；对原版 Action（WAX/BOAT_CANNON_SHOOT/ATTACK）用"先存旧函数再包装"的方式扩展而不破坏原逻辑；状态机修补用 `_hmr_xxx_patched` 哨兵防重复。手炮双端状态（server_states + PerformPreviewBufferedAction）是自定义攻击状态的完整范例。
来源：hmr_sgactions.lua

---

## 5. 可复用模板代码

### 5.1 模板：自定义地皮（含挖掉掉落物）

```lua
-- modworldgenmain.lua 中
if WORLD_TILES[string.upper(id)] == nil then
    AddTile(
        string.upper(id),              -- 唯一大写ID
        "LAND",                        -- LAND/NOISE/OCEAN/IMPASSABLE
        { ground_name = "我的地皮" },
        {
            name = "carpet",           -- 边缘样式（或自建 edge 名）
            noise_texture = "my_turf_noise",   -- 贴图（需要 Asset("IMAGE","levels/tiles/my_turf_noise.tex")）
            runsound = "dontstarve/movement/run_marble",
            walksound = "dontstarve/movement/walk_marble",
            snowsound = "dontstarve/movement/run_ice",
            mudsound = "dontstarve/movement/run_mud",
            flooring = false,          -- true=不可长植物
            hard = false,              -- true=不可种植
            roadways = false,          -- true=道路加速
            cannotbedug = false,       -- true=不可挖掉
        },
        { name = "map_edge", noise_texture = "my_turf_noise" },  -- 小地图
        {  -- 挖掉掉落（nil=不掉）
            name = "my_turf_item",
            anim = "my_turf_anim",
            bank_build = "hmr_turfs",
            invicon_override = "my_turf_item_turf",
            pickupsound = "vegetation_grassy",
        }
    )
end
ChangeTileRenderOrder(WORLD_TILES.MY_TURF, WORLD_TILES.FARMING_SOIL)
ChangeMiniMapTileRenderOrder(WORLD_TILES.MY_TURF, WORLD_TILES.FARMING_SOIL)
```

### 5.2 模板：静态布局岛屿 + 旧档补偿

```lua
-- modworldgenmain.lua
local LAYOUTS = require("map/layouts").Layouts
local STATICLAYOUT = require("map/static_layout")
LAYOUTS["my_island"] = STATICLAYOUT.Get("map/static_layouts/my_island",{
    start_mask = PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    fill_mask = PLACE_MASK.IGNORE_IMPASSABLE_BARREN_RESERVED,
    layout_position = LAYOUT_POSITION.CENTER,
    disable_transform = true,
    add_topology = {room_id = "StaticLayoutIsland:MyIsland", tags = {"my_island", "not_mainland"}}
})
LAYOUTS["my_island"]["ground_types"] = {
    [1] = WORLD_TILES.OCEAN_COASTAL_SHORE,
    [2] = WORLD_TILES.OCEAN_COASTAL,
    [3] = WORLD_TILES.MY_TURF,
}
AddLevelPreInitAny(function(level)
    if level.location == "forest" and level.ocean_prefill_setpieces ~= nil then
        level.ocean_prefill_setpieces["my_island"] = {count = 1}
    end
end)
-- 补偿：覆盖 RetrofitSaveData.DoRetrofitting，调用 RetrofittingCherryIsland 同款实现
-- （照抄 hmr_retrofit_island.lua：网格候选 + is_rough_ocean + obj_layout.Place + AddSquareTopology）
```

布局文件 scripts/map/static_layouts/my_island.lua 返回：
```lua
return {
    ground = { ...39x39数字矩阵... },  -- 数字对应 ground_types 键
    setpieces = { ... }
}
```

### 5.3 模板：自定义房间塞进原版任务 + 分散注入

```lua
-- scripts/map/rooms/forest/my_plant.lua（聚集模式 modimport 的文件）
AddRoom("MyPlantRoom", {
    colour = {r=.8,g=1,b=.8,a=.50},
    value = WORLD_TILES.PEBBLEBEACH,
    contents = {
        countprefabs = { my_plant = function() return 12 + math.random(5) end },
        distributepercent = 0.3,
        distributeprefabs = { rock1 = 0.1, rocks = 0.2 },
    }
})
AddTaskPreInit("Dig that rock", function(task)
    task.room_choices["MyPlantRoom"] = function() return math.clamp(1 + math.random(SIZE_VARIATION), 1, 3) end
end)

-- modworldgenmain.lua（分散模式）
AddRoomPreInit("Rocky", function(room)
    if room.contents ~= nil and room.contents.distributeprefabs ~= nil then
        room.contents.distributeprefabs.my_plant = 0.1
    end
end)
```

### 5.4 模板：自定义科技树 + 原型机 + 配方

```lua
-- 科技树（hmr_techtrees.lua 模式）
TECH_INGREDIENT.MY_ENERGY = TECH_INGREDIENT.MY_ENERGY or "my_energy_material"
table.insert(TechTree.AVAILABLE_TECH, "MY_TECH")
local Create_old = TechTree.Create
TechTree.Create = function(t, ...)
    local newt = Create_old(t, ...)
    newt["MY_TECH"] = newt["MY_TECH"] or 0
    return newt
end
TECH.NONE.MY_TECH = 0
TECH.MY_TECH = { MY_TECH = 1 }
TUNING.PROTOTYPER_TREES.MY_TECH = TechTree.Create({ MY_TECH = 1 })
for _, v in pairs(AllRecipes) do
    if v.level.MY_TECH == nil then v.level.MY_TECH = 0 end
end

-- 原型机
AddPrototyperDef("my_machine", {
    icon_atlas = "images/inventoryimages/my_machine.xml",
    icon = "my_machine.tex",
    is_crafting_station = false,
    action_str = "MY_STUDY",
    filter_text = "我的科技",
})
AddRecipeFilter("MY_SCIENCE")

-- 配方
AddRecipe2("my_item", {
    Ingredient("boards", 4),
    Ingredient("cutstone", 2),
}, TECH.MY_TECH, {
    filter = {"MY_SCIENCE", "STRUCTURES"},
    atlas = "images/inventoryimages/my_item.xml",
})
```

### 5.5 模板：区域资源再生管理器接入

```lua
-- world postinit
AddPrefabPostInit("world", function(inst)
    if not TheWorld.ismastersim then return end
    inst:AddComponent("hmrarearegrowthmanager")
end)

-- 配置注册（照 hmrcherryislandmanager.MakeCherryIslandConfig 模式）
local manager = TheWorld.components.hmrarearegrowthmanager
manager:RegisterAreaConfig("my_area", {
    radius = 156,
    spawn_half_span = 140,
    resources = {
        tree = {
            tag = "my_tree_tag",
            spacing_radius = 12,
            min_count = 45,
            max_count = 55,
            respawn_threshold = 40,
            target_count = 50,
            max_respawns_per_cycle = 3,
            respawn_time = 2*TUNING.TOTAL_DAY_TIME,  -- 2天
            retry_time = 60,
            initial_spawn = true,
            spawn_weights = { my_tree = 1 },
        },
    },
})
-- 中心标记实体（CLASSIFIED + Remove=function() end + DoTaskInTime(0) EnsureArea/InitializeArea）
```

### 5.6 模板：自定义复组件（客户端可见状态）

```lua
-- 服务端组件 components/mycomp.lua
local MyComp = Class(function(self, inst)
    self.inst = inst
    self._flag = net_bool(inst.GUID, "mycomp._flag", "mycomp_dirty")
end)
function MyComp:SetFlag(v) self._flag:set(v == true) end
function MyComp:GetFlag() return self._flag:value() end
return MyComp

-- 客户端 replica components/mycomp_replica.lua
local MyComp = Class(function(self, inst)
    self.inst = inst
    self._flag = net_bool(inst.GUID, "mycomp._flag", "mycomp_dirty")
    inst:ListenForEvent("mycomp_dirty", function() ... end)
end)
return MyComp

-- hmr_init 中：AddReplicableComponent("mycomp")
```

### 5.7 模板：传送器成对（入口/出口）

```lua
-- 入口实体：AddComponent("hmrteleporter")，SetHouseMode(true)，OnSave 存 GUID
-- 出口实体（屋内布局 prefab）：AddComponent("hmrteleporter")，与入口 Target() 互指
-- 玩家触发入口：RegisterTeleportee + Activate → ReceivePlayer（ScreenFade + 3s/4s过渡）
-- 屋出口 prefab 上绑 hmr_house_part tag（IsHouseEmpty 排除统计）
```

### 5.8 模板：批量注册 prefab（超大mod防卡）

```lua
-- HMR_UTIL.RegisterPrefab 模式（128/批）
local PRE_REGISTER_ID = 0
local PRE_REGISTER_BATCH_SIZE = 128
local function RegisterPrefab(...)
    local prefabnames = {}
    local function RegModPrefab(data)
        data.search_asset_first_path = MODS_ROOT .. MODNAME .. "/"
        RegisterSinglePrefab(data)
        PREFABDEFINITIONS[data.name] = data
        table.insert(prefabnames, data.name)
    end
    for i, v in ipairs(select(1, ...)) do RegModPrefab(v) end
    for first = 1, #prefabnames, PRE_REGISTER_BATCH_SIZE do
        local deps = {}
        for i = first, math.min(first + PRE_REGISTER_BATCH_SIZE - 1, #prefabnames) do
            table.insert(deps, prefabnames[i])
        end
        PRE_REGISTER_ID = PRE_REGISTER_ID + 1
        local batchprefab = Prefab(MODNAME.."_pre_reg_"..PRE_REGISTER_ID, nil, nil, deps, true)
        batchprefab.search_asset_first_path = MODS_ROOT .. MODNAME .. "/"
        RegisterSinglePrefab(batchprefab)
        PREFABDEFINITIONS[batchprefab.name] = batchprefab
        env.Prefabs[batchprefab.name] = batchprefab
    end
end
```

### 5.9 模板：跨mod联动 API（对外暴露）

```lua
-- readme/樱花花盆联动方法.lua 模式：postinit_fns + AddSimPostInit pcall(require)
local postinit_fns = {}
function AddHMRCherryFlowerPotPrefab(prefab_name, pot_data)
    postinit_fns[prefab_name] = postinit_fns[prefab_name] or {}
    table.insert(postinit_fns[prefab_name], pot_data)
end
AddSimPostInit(function()
    local ok, res = pcall(require, "hmrmain/hmr_lists")
    if ok then
        for name, fns in pairs(postinit_fns) do
            for _, fn in ipairs(fns) do fn(res) end
        end
    end
end)
```

---

## 6. 附：未解细节与注意事项

1. tests/ 目录（hmr_chest_transmit_capacity_test.lua / hmr_userdatahook_api_test.lua）为第二套双重加密，无法解密，内容未读（低价值）。
2. hmr_skin.lua（6084行）与 hmr_cherry_cat_clothing / hmr_cherry_cat_soul_heal 为皮肤与猫时装系统，核心模式（AddSkinPostInit、装备皮肤图集切换）未逐行展开。
3. 辉煌围墙 honor_walls 在 PrefabFiles 中被注释禁用。
4. AddModCharacter("hmr_lingna", ...) 在 hmr_init 末尾被注释（角色未启用）。
5. 世界种植房间文件只在 mode==0 时 modimport；若玩家改配置需新开档。
6. 解密产物（.dec/.entry.lua）为研究用，未删除任何原始文件。
