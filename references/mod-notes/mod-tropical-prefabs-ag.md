# Tropical Experience mod — scripts\prefabs\ A~G 段精读笔记（补充）

> 覆盖范围：`E:\神秘复苏\饥荒大型mod\1505270912\scripts\prefabs\` 目录中文件名以 A、B、C、D、E、F、G 开头的全部 lua 文件（共337个、约68481行，已逐文件过读；排除 notusedscripts.lua）。
> 说明：本文件为 A-G 全段精读的完整补充笔记（含 G 段详析与 A-F 段要点回顾）。

---

## 一、总览：本段 prefab 覆盖类别与分组清单

| 类别 | 包含 prefab（文件名） |
|---|---|
| **女神内容包（goddess 系）** | goddess_bell / bird / bowtie / butterfly / butterflywings / deer1(goddess_deer_gem) / deer2(goddess_deer) / deer_magic / feather / figure / fish / fishingrod / flower(+rose+planted) / flute(4种龙卷风) / fountain / fountain_lake / fountain_placer / gate1 / goggles / hat / hound / lake / lantern / lantern_fire / magicfx / pouch / rabbit / rabbit_fur / rabbithole / ribbon / shrine / sparklefx / spider_hostile / staff / star / statue / statue2 / statue3 / statue4 / statue5 / statue_fire / sword / telefx / tori —— 完整世界观：喷泉→传送门→湖→鹿驯养链→祭坛→法杖套件 |
| **金系（gold）** | gold_dust / goldbishop / goldentomb / goldmonkey(+tikiman) / goldobi(is_goldobi+s_goldobi) / goldpan |
| **水下/海洋生物** | gnarwailunderwater（gnarwail/gnarwailholefundo/gnarwailholefrente/gnarwail_attack_horn）、glowfly(+cocoon)、grass_water、grasswaterspawner |
| **哈姆雷特植物** | grass_tall（9个含patch系）、grass(+grassnova等)、greengrass、grabbing_vine(+fixo)、grotto_parsnip(4) |
| **熔岩竞技场移植（gw/grotto）** | grotto_grub / grotto_grub_nest / grottoqueen / groundlifts(5) / gw_bonestaff(+proj) / gw_column_angel(+shadow) / gw_rune / gw_yellow_lizardman |
| **quagmire 移植（gorge）** | gorge_crabtrap(quagmire_crabtrap) / gorge_portal / gorge_smallmeat(quagmire_smallmeat/cooked) |
| **绿系/其他** | green_forcefieldfx / greententacle / grilled_peach / gnat(+gnatmound) |
| **A-F 段基础资源类** | 各类植物、动物、物品、建筑，包含本 mod 特色：caminho 图集方案、windy 套装、守卫仇恨、worldsettingstimer 变形等（详见第三、四节） |

---

## 二、逐类分析代表性 prefab（G 段详析 + 核心代码原样复制）

### 1. 女神（goddess）世界观：喷泉→传送门→湖→鹿→祭坛→法杖

**goddess_fountain.lua** — 女神喷泉：fueled 60 + 传送门配对到 goddess_gate1 + activatedgf 标签（激活状态机入口）。
```lua
inst:AddComponent("fueled")
inst.components.fueled:SetMaxFuel(TUNING.MAGIC_MAXFUEL)
inst.components.fueled:InitializeFuelLevel(TUNING.MAGIC_MAXFUEL)
inst.components.fueled:SetDepletedFn(inst.Remove)
...
inst:AddComponent("teleporter")
inst.components.teleporter.targetTeleporter = "goddess_gate1"
inst.components.teleporter.offset = 0
inst.components.teleporter:SetOnActivateFn(function(inst, player) inst:PushEvent("activatedgf") end)
```
锤毁掉落 magicpowder/moonrocknugget×3/empty_bottle_green/full_bottle_green；moondial 满月时循环播放 foley 声。

**goddess_lake.lua** — 湖：满月生成3只 goddess_deer_gem（±8 偏移），SpawnChild 喷泉+8朵 flowers_lake；**GetFish 按钓鱼竿 windy5 标签分流鱼种**：
```lua
if v:HasTag("windy5") then
    if math.random() <= .65 then
        return "goddess_fish"
    else
        return "eel"
    end
end
if math.random() <= .45 then
    return "eel"
end
return "fish"
```
fishable 用 OASISLAKE 参数 + playerprox 12-14 + leader + no_wet_prefix + SetDeployExtraSpacing(6)。

**goddess_deer2.lua（goddess_deer 驯养链核心）** — 戴 ribbon → windy4+companion 标签 + 换 loot 表 goddess_deer1 + StartBlooming；喂 greengem → goddess_telefx → 1秒后变身 gem 鹿。**DoPlantBloom 开花系统**：
```lua
local function DoPlantBloom(inst)
    if inst.components.inventoryitem then
        local x, y, z = inst.Transform:GetWorldPosition()
        local pos = Vector3(x, y, z)
        for k = 1, 3 do
            local result, resultangle = FindValidPositionByFan(math.random() * 2 * PI, math.random(3, 8), 8, function(offset)
                local pt = pos + offset
                if not TheWorld.Map:IsPassableAtPoint(pt:Get()) then return false end
                local ents = TheSim:FindEntities(pt.x, 0, pt.z, 2.5, nil, {"FX"})
                return #ents == 0
            end)
            if result then
                local flower = SpawnPrefab(BLOOM_CHOICES[math.random(#BLOOM_CHOICES)])
                flower.Transform:SetPosition((pos + result):Get())
            end
        end
    end
end
```
（BLOOM_CHOICES = {"deer_flower", "deer_flower_rose"}，rose 概率 0.01 写入 loot 表）hunger 组件（100/0.5率）+ OnHungerDelta：>25% → milkable+flowering；peachy 喂养 → makefriend+忠诚度；普通吃 → 3秒后 poop；sleeper 抗性4。

**goddess_deer1.lua（goddess_deer_gem 施法鹿）** — 数值×2（DEER_GEMMED_HEALTH*2）。**FindCastTargets + NoSpellOverlap 防止重叠施法**：
```lua
local function NoSpellOverlap(inst, pos)
    local x, y, z = pos.Transform:GetWorldPosition()
    local r = 12
    local ents = TheSim:FindEntities(x, 0, z, r, nil, nil, {"greentornado2"})
    return #ents <= 0
end
```
SPELL_MAX_TARGETS 20、player 优先插队；SpawnSpells 里 SPELL_OVERLAP 6→3 降级重试；DoCast 用 timer "deercast_cd" 冷却；`inst:DoTaskInTime(0, leader)` 找 goddess_fountain_gem 当主人；ondeath 25% 掉 gem_flower1。

**goddess_rabbit.lua（疯狂观众机制）** — 原版深度改造：理智过低时观众兔变成胡子怪，且**客户端换 build**：
```lua
local function MakeBeardMonster(inst)
    inst:AddTag("beardmonster")
    inst.AnimState:SetBank("beard_monster")
    inst.AnimState:SetBuild("beard_monster")
    inst.components.inventoryitem:ChangeImageName("beard_monster")
    inst.components.locomotor.runspeed = TUNING.BEARDMONSTER_RUN_SPEED
    ...
end
...
inst:SetClientsideBuildOverride("insane", "rabbit", "beard_monster")
inst:SetClientsideBuildOverride("insane", "rabbit_winter_build", "beard_monster")
```
IsCrazyGuy 判定 `sanity <= DAPPER_BEARDLING_SANITY`（或冬季 BEARDLING_SANITY）；OnPickup/OnDropped 监听容器+sanitydelta 事件决定变身；GetCookProductFn 疯狂时烹饪产物 cookedmonstermeat。

**goddess_lantern.lua（双模式法杖）** — machine（TurnOn/TurnOff + hutch 声）+ reticule（LocalToWorldSpace(5,0,0)）+ spellcaster canuseonpoint；关闭时施法按 PEACH_CHOICES/BETTER_PEACH_CHOICES 权重表（含 peach_juice_bottle_green 0.05 + explode_firecrackers），开启时召唤 goddess_star：
```lua
inst.components.spellcaster:SetSpellFn(function(inst, pos)
    if not inst.components.machine:IsOn() then
        local x, y, z = pos:Get()
        local ents = TheSim:FindEntities(x, y, z, 3, nil, {"FX"})
        ...
        local peach = SpawnPrefab(GetRandomItem(inst.components.machine:IsOn() and BETTER_PEACH_CHOICES or PEACH_CHOICES))
        ...
    else
        local star = SpawnPrefab("goddess_star")
        ...
    end
end)
```
**windy 组合惩罚**：装备 windy1+windy2 不扣血，否则 -15血-25san；fueled 480*3 -0.05/次；标签 nopunch/quickcast/goddess_item。

**goddess_staff.lua（减速/加速法杖）** — 双 tag 组合强化（windy 组合 25范围怪 0.25速15秒 + 玩家1.25速 + goddess_magicfx 绿染；非组合 0.40速（epic 0.60 5秒）+ sanity -10）；finiteuses windy Use(0.5) 否则 Use(1)；spellcaster 组合 `canuseontargets + canonlyuseoncombat + quickcast + ccastingstate "castspell_tornado"`；onequip 换 swap_ruins_bat。

**goddess_statue.lua（3个 DoPeriodicTask 全能守卫）** — 每3秒杀怪（on 时 25范围 hostile 等 -100血 + groundpoundring_fx + finiteuses Use(1) + GoToState("hit")）、每3秒灭火（smolder/fire → Extinguish）、0.2秒动画/灯光切换（>0.1 绿 idle_loop / ≤0.1 黄 idle）；health 1234 + workable HAMMER 5 + machine + playerprox FIRE_DETECTOR_RANGE；OnGetItem：windy +250血/+0.40 否则 +123.4/+0.10。

**goddess_statue2.lua** — 每锤 50% 出 goddess_spider_hostile；四档掉落。
**goddess_statue3.lua** — 250范围 goddess_deer <8 → MaxChildren(2) 否则 0；childspawner + periodicspawner goddess_butterfly 480-481。

**goddess_sword.lua（会跟随的剑）** — 装备时 windy1+windy2 → 成为主人的 follower：
```lua
inst:AddComponent("leader") -- owner
owner.components.leader:AddFollower(inst)
```
combat 100 + tool CHOP/MINE 4 + finiteuses 100 + SGsword + swordbrain + walkspeedmult 0.5。

**goddess_flute.lua（3种龙卷风）** — HearPanFlute 检查 windy 组合 → 召唤：
```lua
local tornado = SpawnPrefab(inst.owner and inst.owner:HasTag("windy2") and "greentornado1" or "greentornado")
```
tornado_fn（greento build、LIFETIME*4、SGgreentornado + 0.15秒 green_leaves_chop）、tornado1_fn（tornado build、SGtornado）、tornado2_fn（**AddTag("greentornado2")** 供 NoSpellOverlap 检查 + SGgreentornado1）。返回4个 Prefab。

**goddess_pouch.lua（50+条目权重 loot 表）** — empty_bottle_green 18 权重最高、full_bottle_green 10×2、seeds 3.9、蓝图×9 0.5、宝石×6 0.5、goddess 系物品；`local num_loots = 1 + math.random(4)` 随机抽取次数；OnUnwrapped 逐项掉落 + InheritMoisture + packaged 音效。

**goddess_shrine.lua** — prototyper 分支：
```lua
inst.components.prototyper.trees = TUNING.PROTOTYPER_TREES.GODDESS_TWO
```
子实体 statue1(goddess_statue5@2.1,0,0)/statue2(goddess_statue4@-2.1,0,0)/page@0,1,0；onturnon/off/activate 动画+火。

**goddess_hat / goddess_goggles.lua（windy1 套装）** — 两文件几乎相同：waterproofer ABSOLUTE + insulator 夏季 LARGE + fueled FUELTYPE.USAGE 480*5 + dapperness 大 + walkspeedmult CANE_SPEED_MULT*1.12；onequip AddTag("windy1")；Prefab 路径 "common/inventory/goddess_hat"（与文件名不一致）。

**goddess_bowtie.lua（windy2）** — armor InitCondition(888,0.88) + damagereflect 88 + bank amulets anim redamulet。

**goddess_fishingrod.lua（windy5）** — fishingrod SetWaitTimes(4,40)/SetStrainTimes(0,5)；glow/unglow 子实体 goddess_lantern_fire；weapon attackwear 4。

**goddess_star.lua（makestafflight 工厂）** — **net_float 脉动同步**：
```lua
inst._pulsetime = net_float(inst.GUID, "goddess_star._pulsetime", "pulse")
...
inst._pulsetask = inst:DoPeriodicTask(PULSE_SYNC_PERIOD, function()
    inst._pulsetime:set(GetTime() + PULSE_SYNC_PERIOD)
end)
```
客户端 sin 脉动（Lerp 11-12 亮度）；timer 480 extinguish；**OnGetItem 万能转换**：食物→复制掉 y+2、magicpowder→冬天 heater 100+cooker+fueled 60 / 夏天 -100 SetThermics(false,true) / 其他 50%随机。`makestafflight("goddess_star", true, "star_cold", {100/255,200/255,100/255}, {"idle_loop"}, false)`。

**goddess_hound.lua** — MakeCritter 工厂（critter_puppy 系统）+ MakeBuilder（petleash:SpawnPetAt）；`inst.Physics:SetDontRemoveOnSleep(true)`；favoritefood="monsterlasagna"；crittertraits + perishable 饥饿小游戏。

**goddess_rabbithole.lua** — spring 洪水模式完整状态机（SetSpringMode/SetNormalMode/OnStartRain/OnIsSpring + iscollapsed net_bool + idle_flooded）；spawner Configure("goddess_rabbit")；OnHaunt ReleaseChild。

**goddess_bird / butterfly / fish / figure / flower / tori / gate1 / telefx / sparklefx / magicfx / lantern_fire / deer_magic / statue_fire / fountain_lake / fountain_placer / feather / rabbit_fur / ribbon / butterflywings** — 要点见第三节模式归纳与第四节特别记录：
- goddess_flower（与 flower.lua 同类改造：ROSE 0.01 + thorny + 守卫仇恨注释掉 + DieInDarkness cave 枯萎 + MakeHauntableChangePrefab "flower_evil"）；返回3个（goddess_flower/goddess_flower_rose/planted_goddess_flower，后两者 SetPrefabName("goddess_flower")）。
- goddess_bird（loot {{"peach",.5},{"smallmeat",.35},{"goddess_feather",.1}}、psprefab "peach"、FOODTYPE.VEGGIE）。
- goddess_butterfly（OnDeploy → goddess_flower + PushEvent("growfrombutterfly")；butterflyspawner 追踪；deployable PLANT + MakePlacer）。
- goddess_fish（3秒后 prepouch → goddess_pouch；rawfn 5秒 dead 动画）。
- goddess_butterflywings（AddIngredientValues({meat=0.5}) + IsCookingIngredient 检查 ingredients[name]；edible 10/15 MEAT）。
- goddess_figure（ondeploy → goddess_statue + MakePlacer）。
- goddess_tori（ondeploy → goddess_gate2（注意不是 gate1）；MakePlacer("common/goddess_tori_placer","goddess_tori","goddess_gate","full")）。
- goddess_gate1（鸟居：scale 4 + teleporter offset 0 + 绿光；MakeObstaclePhysics(.25) 后又被 MakeInventoryPhysics 覆盖）。
- goddess_feather / goddess_rabbit_fur（纯物品：stackable + scale 2.4/3）。
- goddess_telefx（loop→pre + 0.8秒 removal）；goddess_sparklefx（wind_burst FX 35*FRAMES）；goddess_magicfx（deer_ice_circle 绿染减速特效）；goddess_lantern_fire（Light 半径8 绿 150/200/150）；goddess_deer_magic（deer_fire_charge 绿染 FX + TriggerFX）；goddess_statue_fire（Light 半径5 绿 + campfire 循环声，fn/fn1 相同返回2个）；goddess_fountain_lake（装饰 idle_moon）。

### 2. 金系生态（gold）

**goldmonkey.lua（金猴+提基人，G 段最长逻辑之一）** — **SetHarassPlayer（120秒超时骚扰）+ FindTargetOfInterest（10秒周期、香蕉 60%/15% 概率）+ EquipWeapons 运行时创建双武器**：
```lua
local function EquipWeapons(inst)
    if inst.components.inventory ~= nil then
        local weapon = CreateEntity()
        weapon.entity:AddTransform()
        MakeInventoryPhysics(weapon)
        weapon.persists = false
        weapon:AddComponent("weapon")
        weapon.components.weapon:SetDamage(TUNING.GOLDMONKEY_DAMAGE)
        weapon.components.weapon:SetRange(TUNING.GOLDMONKEY_ATTACK_RANGE, TUNING.GOLDMONKEY_ATTACK_RANGE + 4)
        weapon.components.weapon:SetProjectile("goldmonkey_thrower")
        weapon:AddComponent("inventoryitem")
        weapon.components.inventoryitem:SetOnDroppedFn(weapon.Remove)
        weapon:AddComponent("equippable")
        inst.weapon = weapon
        inst.components.inventory:Equip(inst.weapon)
        inst.components.inventory:Unequip(EQUIPSLOTS.HANDS)
    end
end
```
（Thrower 远程 + Hitter 近战双武器，combat SetDefaultDamage(0)）；OnAttacked 55-65秒 ForgetTarget + 30范围共享仇恨；SetNormalMonkey/SetNightmareMonkey（kiki_nightmare_skin 半透明0.6 + 换 brain 到 nightmaremonkeybrain + loot 表切换）——**但触发源 TestNightmareArea/TestNightmarePhase/WatchWorldState("nightmarephase")/areaaware 全部被注释，夜间形态实际不会触发**（半注释状态）；periodicspawner goldnugget（200-400）；tikiman（tiki_mask 帽 + periodicspawner poop + OnAttacked2 找 tiki 共享仇恨）。返回 `Prefab("goldmonkey")` + `Prefab("tikiman")`。

**goldobi.lua（金方尖碑，PF_SHARED 共享墙）** — 玩家可放置的墙体系统：
```lua
local function AddSharedWall(wall, x, y, z)
    -- 3x3 范围内去重，共享墙表
    local ents = TheSim:FindEntities(x, y, z, NEAR_DIST_SQ, {"wall"})
    for i, v in ipairs(ents) do
        if v:HasTag("playerwall") and v ~= wall then
            wall.components.pfshared:AddWall(v)
        end
    end
end
```
OnIsPathFindingDirty（3×3 AddWall）+ refresh 0.2秒（NEAR_DIST_SQ 10*10/FAR_DIST_SQ 11*11、sane 判定 activeonsane）+ SGnightmarerock（conceal/raise/lower）+ ConcealForMinigame + UPDATE_OFFSET 交错刷新；loot goldnugget×4 + HAMMER 5；返回 is_goldobi（activeonsane false）+ s_goldobi。

**goldbishop.lua** — MakeBishop 工厂 + clockwork_common.InitHomePosition/MakeBefriendable/MakeHealthRegen + **UpdateShotFx 弹道逐段特效**（GetSymbolPosition("shot_marker") + CreateShotSegFx + updatelooper）；**net 同步弹道**：`net_float(shotx/shotz) + net_bool(showshot)`；normal_common_postinit SetBuild("goldbishop_build")；SetSharedLootTable goldbishop（gears/purplegem/goldnugget）；embark/drownable/SetAllowPlatformHopping(true) 船跳。

**goldentomb.lua** — walrus_house 改黄金墓：childspawner goldmonkey（Regen 1200/Spawn 30/Max 1）+ shake 周期动画 + loot goldnugget×10 + HAMMER 4 + OnIgniteFn RemoveComponent("childspawner")。

**gold_dust.lua** — edible foodtype = "GOLDDUST" 字符串自定义 + bait/molebait/scarerbait 三合一 + shine 周期闪光。
**goldpan.lua** — weapon AXE_DAMAGE + tool PAN + PAN_USES 30 + hamletinventory.xml。

### 3. 水下/海洋

**gnarwailunderwater.lua（独角鲸，返回5个 Prefab）** — 船伴生物：**TryGnarwailResurface 用 FindSwimmableOffset** 找可出水点；角破坏系统：
```lua
local function OverrideHornBroken(inst)
    inst.AnimState:OverrideSymbol("gn_main_horn", "gnarwail_build", "gn_main_horn_broken")
end
```
（角断 → 换符号 + loot 切换）；GetFormationOffsetNormal 分离转向（SEPARATION_AMOUNT 25、MAX_STEER_FORCE 2、`DESIRED_BOAT_DISTANCE = TUNING.MAX_WALKABLE_PLATFORM_RADIUS + 4`）；OnUpdateSpeed 跟随船速；**MakeObstaclePhysics(1.25) + ClearCollisionMask + CollidesWith(CHARACTERS) + TEMPHACK_DisableSleepDeactivation**；trader+eater(MEAT)+follower；子实体 `inst.buraco2 = SpawnPrefab("gnarwailholefundo")` + buraco1（frente）；fn3 重生点（`local respawndays = 8` + timer 60*8*8）；gnarwail_attack_horn（HORN_HEALTH、`_retreat_timer = horn_inst:DoTaskInTime(TUNING.GNARWAIL.HORN_RETREAT_TIME/2, EndHornAttack)`）。

**glowfly.lua** — GloStandardSleepChecks + ShouldSleep（`TheWorld.Map:IsOceanTileAtPoint` 海洋不能睡）；lantern_fly 标签 + Light 120/255 灰 + fader + hamletinventory.xml + workable NET + SGglowfly + glowflybrain + WatchWorldState isday/isnight/isdusk；begincocoonstage 茧化。**glowfly_cocoon**：mass 100、health 300、`DoTaskInTime(math.random(50,200))` → spawnRabidBeetle（`bug.sg:GoToState("hatch")`）+ 1秒 Remove。返回 forest/monsters/glowfly + glowfly_cocoon。

### 4. 哈姆雷特植物

**grass_tall.lua（高草，9个 Prefab，G 段最复杂植物）** — **machetecut 标签工作切换**：
```lua
inst.components.workable:SetWorkAction(ACTIONS.HACK)
inst.components.workable:SetWorkLeft(3)
-- dig_up 时：
if inst.components.workable.action == ACTIONS.DIG then
    inst.components.workable:SetWorkAction(ACTIONS.DIG)
    inst.components.workable:SetWorkLeft(1)
    inst.components.timer:StartTimer("spawndelay", 60*8*4)
    inst.AnimState:PlayAnimation("grow")
else
    inst.AnimState:PlayAnimation("fall")
    ...
end
```
（HACK 3刀 → 砍完 fall + cutgrass；挖时 machetecut → DIG 1次 + 4天重生 + grow 动画，否则 dug_grass 移除；`--tempo para renascer em dias` 葡萄牙语注释佐证作者 vagner）；weevole 巢（weevole_infested 标签 + isday 停/isdusk 启 + weevolenesttest 概率传染 + spawnweevole TheCamera:GetDownVec）；makefn2 水版（MakeWaterObstaclePhysics(0.35,2,1.25) + ignorewalkableplatforms + SetPrefabNameOverride("grass_tall") + MakeInventoryFloatable bob_percent 0 + OnLandedServer）；**patch 系统**（placeitemoffgrids 随机圆内散点 + round 去网格 + checkIfValidGround 排除八种 OCEAN tile：OCEAN_SWELL/OCEAN_BRINEPOOL/OCEAN_BRINEPOOL_SHORE/OCEAN_HAZARDOUS/OCEAN_ROUGH/IMPASSABLE/OCEAN_COASTAL/OCEAN_WATERLOG/OCEAN_COASTAL_SHORE）；返回 grass_tall/grass_tallwater/grass_tall_patch/deep_jungle_fern_noise/teatree_piko_nest_patch/asparagus_patch/vampirebatcave_potential(20%)/grass_patch；hackable 组件整套注释掉改用 workable+timer 手动实现。

**grass.lua（+grassnova/depleted_grass/grasspartfx）** — **守卫仇恨插入 dig_up/onpickedfn**（标准模板，见第三节模式4）；**ontransplantfn 新增变高草**：
```lua
if tiletype == GROUND.PLAINS or tiletype == GROUND.RAINFOREST or tiletype == GROUND.DEEPRAINFOREST  then	
    local newgrass = SpawnPrefab("grass_tall")
    newgrass.Transform:SetPosition(x,y,z)
    newgrass.components.workable:SetWorkAction(ACTIONS.DIG)
    newgrass.components.workable:SetWorkLeft(1)
    newgrass.components.timer:StartTimer("spawndelay", 60*8*4)
    newgrass.AnimState:PlayAnimation("picked",true)		
    inst:Remove()
end
```
grassgekko 变形全套（worldsettingstimer morphdelay/morphing/morphrelay 三定时器 + triggernearbymorph 扩散 + onmorphtimer 密度检查 GRASSGEKKO_MAX_DENSITY + WorldSettings_Timer_PreLoad/PreLoad_Fix 存档恢复）；grassnova 用 grassgreen_build。

**grass_water.lua（grasswater）** — 与 grass.lua 同构（grassgekko 变形全套）；dig_up 简化无守卫；`if inst.prefab == "grasswater" then inst.AnimState:PushAnimation("picked", true) end`；bank/build 用 "grass_inwater"；标签 silviculture/grasss/mudacamada；MakeInventoryPhysics(inst, nil, 0.7)。

**grasswaterspawner.lua** — 一次性生成器：tentativas=10 重试、FindLandNextToWater（FindValidPositionByFan 找岸边）+ GetSpawnPoint（`not IsAboveGroundAtPoint and not VALID_TILES[ground.MARSH] and not IsPassableAtPoint and IsNotNextToLand`）、半径 48±4、12次尝试。

**greengrass.lua** — 绿色草：pickable cutgreengrass 180 + 烧毁掉落 ash×2-4/charcoal×2-4 随机 + OnSave/OnLoad 存 no_banana（canbepicked 恢复）。

**grabbing_vine.lua** — 抓藤：**SetPrefabNameOverride("grabbing_vine")** + thief 偷窃（onhitotherfn StealItem）+ up 标签不可攻击 + playerprox godown/goup + **OnSave 存 spawnpatch.GUID + LoadPostPass 恢复 + OnKilled → spawnNewVine**；返回 grabbing_vine + grabbing_vinefixo（同函数）。

**grotto_parsnip.lua（4个 Prefab）** — planted（pickable 10 再生 + quickpick + TheWorld:PushEvent("beginregrowth")）；grotto_parsnip（edible VEGGIE + **caminho 用 "map_icons/creepindedeepicon.xml"**——与众不同）；eaten（数值减半 + idle_eaten 动画）；giant（CHOP 8 刀 + loot 8件含 mosquito/jellybug + 双倍 burnable 配置）。

### 5. 熔岩竞技场移植（gw/grotto）

**grotto_grub.lua（熔岩洞螃蟹）** — 数值来自蚁人模板（ANTMAN_DAMAGE = wilson_attack*2/3 = 34*2/3、health 250、AttackPeriod 3）；标签 crab/canbetrapped/cattoy；loot quagmire_crabmeat；OnAttacked 共享仇恨给 ant 标签；SGgrotogrub；日期事件被注释（OnIsDay 不启用）。

**grotto_grub_nest.lua** — 蚁人巢移植：childspawner grotto_grub（Regen 60/Spawn 30/Max 3-4 随机）+ workable MINE 6 + loot rocks×2/honey/honeycomb；Prefab 路径 "common/objects/grotto_grub_nest"。

**grottoqueen.lua** — 蜂后模板改造（mowlth build）：SetSharedLootTable 17条目（royal_jelly×6、honeycomb、honey×4、stinger、hivehat、bundlewrap_blueprint、chesspiece_beequeen_sketch）；**全部战斗组件被注释**（combat/healthtrigger/sleeper 整套注释，只有 health+locomotor+sanityaura），PushMusic 触发 beequeen 音乐事件（20/40/50 距离阈值）；locomotor pathcaps ignorewalls+allowocean；MakeFlyingGiantCharacterPhysics(500, 1.4)。

**groundlifts.lua（单行压紧代码，5个 Prefab）** — lavaarena 地面尖刺 FX 工厂：animover 移除、可选地面碰撞伤害（`B.components.mine:Deactivate()` + 弹飞物品 `b(B,c,.8+.7,.7*.4,.7+B:GetPhysicsRadius(0))`）、SetPrefabNameOverride("boarrior")；返回 lavaarena_groundlift / groundliftembers / groundliftrocks / groundliftwarning / groundliftempty。

**gw_bonestaff.lua（+gw_bonestaff_proj）** — **亡灵法杖**：zombies 表（40+条 物品→怪物映射，如 grass→grassgekko、monstermeat→hound、pig_figure→AnimatePigStatue 函数）；createpower 把 4 半径内物品变怪物（+spawn_fx_medium）、鬼魂复活（respawnfromghost）、其他触发 DoHaunt；消耗 sanity（施法-25、复活-50）+ 自己 -1血；**弹道尾迹系统**：proj 隐藏 + net_event("staff_proj.killtail") + 客户端 DoPeriodicTask(0) UpdateTail（5次随机3次生成尾段、SetMotorVel(10,0,0)）；武器 35 伤害 + finiteuses 30。

**gw_column_angel.lua（column_angel 天使柱符文谜题，+shadow）** — **完整符文玩法**：OnActivate 生成3个 gw_rune（三角布置、maxwell_smoke、GFSoftColourChange 淡入）+ cooldown timer 2400（40分钟）；**runesDone==3 → 闪电 + 三层 loot**（essencesLoot 金块×3-6 + toploot 随机1行 + midloot×2 + lowloot×3）；SpawnItem 用 Physics:Teleport 跳出柱子碰撞体；OnSave/OnLoad 存 rune 存档（GetSaveRecord/SpawnSaveRecord）；GetDebugString 调试；column_angel_shadow（LAYER_BACKGROUND + 0.3 透明度假阴影）。

**gw_rune.lua（符文本体）** — 5 类型（death/beast/sacrifice/rich/magic）各配 **事件驱动灭除**（killed/oneat/builditem/runetradeaccept/gemaccept 事件监听 + doer IsNear 3）；ActivateEvents 表按类型注册/注销事件；trader 动态启用（magic 接受全部7种宝石、rich 接受 goldnugget）；_dtask 600秒超时自动 Deactivate；GFSoftColourChange 渐变到类型色（GetRuneColour）；`inst.components.inspectable:SetDescription(STRINGS.CHARACTERS.GENERIC.DESCRIBE["RUNE_" .. string.upper(inst.type)])`；OnSave/OnLoad。

**gw_yellow_lizardman.lua（黄蜥蜴人）** — 复用原版 lizardman 资源（bank "snapper" + SGlizardman + lizardmanbrain + SetSharedLootTable "lizardman"）；**isFrenzy 狂乱模式**（true 时 reqtags=nil 可打玩家，false 时只打 monster 且 notags 排除 player）；**雷电武器 OnWeaponAttack**：
```lua
local fxdummy = SpawnPrefab("gf_lightning_dummy")
fxdummy.components.gflightningdrawer:SetColour(2)
fxdummy.Transform:SetPosition(x, 0, z)
local lpos = {{start = {x = x, z = z}, finish = {x = xt, z = zt}}}
fxdummy.components.gflightningdrawer:DoLightning(lpos)
```
weapon SetRange(16, 20) 远程 + stimuli "electric" + electricdamageimmune；health 680、damage 45、AttackPeriod 5；talker MakeChatter；colouradder 组件。

### 6. quagmire 移植（gorge）

**gorge_portal.lua（gorge_portal）** — 传送门对：onopen/onclose（playerprox 10-13 生成/移除 quagmire_portal_activeanim）；**DoTaskInTime(1) 遍历 Ents 找另一 portal 互设 targetTeleporter**；OnActivate wormholespit + WORM_DANGER 清理 + sanity -MED；CreateDropShadow（SetParent 非网络）；activefx_fn 粉红光 249/130/117。

**gorge_smallmeat.lua（quagmire_smallmeat/cooked）** — common 工厂：meat/dryable/lureplant_bait/cookable 标签 + tradable goldvalue + PERISH_FAST；raw dryable→smallmeat_dried（SetBuildFile("dried_quagmire")）；cooked PERISH_MED。

**gorge_crabtrap.lua（quagmire_crabtrap）** — trap targettag "canbetrapped" + baitsortorder 1 + finiteuses TRAP_USES + on_usedup RemoveFromOwner（JBK 注释防容器 bug）；**`inst.caminho = "images/images/inventoryimages2.xml"`（多一层 images/ 笔误）**；SGtrap。

### 7. 绿系/昆虫

**greententacle.lua（绿触手）** — 原版 tentacle 强化：700血/37伤害/1.8攻速/distAttackRange 20；retargetfn 可打 monster/animal/character；OnAttacked 切换目标带 TENTACLE_ATTACK_AGGRO_TIMEOUT；**MakeWeapon 运行时建武器**（damage 40 + SetProjectile("tentacle_attack_spike")）；loot 表 greententacle（monstermeat×2/snakeskin 0.5/tentaclespots 0.05）；SGgreententacle；标签 WORM_DANGER。

**green_forcefieldfx.lua** — 客户端驱动的灯光渐变动画：net_tinybyte _lightframe + net_bool _islighton + lightdirty 事件 + OnUpdateLight 每帧补间（3×frame/MAX_LIGHT_FRAME 半径）；kill_fx 播 close 动画 0.6秒后移除。

**grilled_peach.lua** — 烤桃子：edible 18.5/3 VEGGIE + PERISH_MED + scale 1.3 + atlasname 同路径。

**gnat.lua** — 蚊虫：**infester 组件**（bitefn + stopinfesttestfn）；health 1 + invincible（freeze/unfreeze 事件切换）；sanityaura -TINY*2；`inst.special_action = makehome`（生成 gnatmound + TakeOwnership）；findlight 找光源；Prefab("forest/common/gnat")。

**gnatmound.lua** — 蚊巢：workable MINE 6 + childspawner gnat + onhit workleft 4/2/0 掉 loot + ReleaseAllChildren + `inst:WatchWorldState("startday", regen)` 每天恢复 + MakeSnowCovered + SetSharedLootTable。

### 8. A-F 段要点回顾（前段精读摘要）

- **caminho 图集方案**：`inst.caminho = "images/inventoryimages/volcanoinventory.xml"`（或 hamletinventory.xml/inventoryimages2.xml）+ inventoryitem.atlasname 同值——全 mod 统一物品图集方案。
- **windy 套装**：windy1（护目镜/帽）、windy2（蝴蝶结）、windy3（灯笼）、windy4（鹿丝带）、windy5（鱼竿）——双标签组合触发强化（+0.40 燃料/血量加成、更强法术）。
- **原版深度改造**：goddess_rabbit（疯狂查看者）、goddess_spider_hostile（数值×2 + SummonFriends + SoundPath）、elephantcactus/empty_bottle_green/dungball/deco_util/fish_med/flupegg/glass 等（笔误详见第四节）。
- **childspawner 生态**：gnatmound（gnat）、goldentomb（goldmonkey+摇晃）、goddess_statue3（goddess_deer 限量2）、grass_tall（weevole 巢）。
- **MakeInventoryFloatable 参数**：gorge_crabtrap "med",0.05,{0.8,0.5,0.8}、grass_tallwater 水草漂浮+OnLandedServer。
- **spellcaster 组合**：goddess_lantern（reticule+machine+canuseonpoint）、goddess_staff（canuseontargets+canonlyuseoncombat+quickcast+castingstate "castspell_tornado"）。
- **MakeHauntable 系列**：Launch/LaunchAndPerish/Panic/ChangePrefab/Ignite/PanicAndIgnite + AddHauntableCustomReaction。

---

## 三、本 mod 写 prefab 的模式归纳

1. **标准骨架**：CreateEntity → AddTransform/AnimState/Network（+SoundEmitter/Light/Physics/DynamicShadow/MiniMapEntity 按需）→ SetBank/SetBuild/PlayAnimation → 标签 → SetPristine → `if not TheWorld.ismastersim then return inst end` → 服务器组件 → Make*Burnable/Propagator/Freezable/NoGrowInWinter + MakeHauntable* 收尾。

2. **物品三件套**：`inventoryitem.atlasname` + 自定义字段 `inst.caminho`（同值）+ 缩放 `inst.Transform:SetScale` —— 几乎所有新物品统一走此模板，图集集中在 volcanoinventory.xml / hamletinventory.xml / inventoryimages2.xml。

3. **工厂函数批量产 prefab**：单个文件内多次定义 `fn()` 后 `return Prefab(...), Prefab(...)` 返回多个（grass_tall 返回9个、goddess_flute 返回4个、groundlifts 返回5个、gnarwailunderwater 返回5个、grotto_parsnip 返回4个）；或 `grass(name, stage)` 式参数化工厂。

4. **守卫仇恨插入模板**（反复出现于 grass.lua/flower.lua 的 dig_up/onpickedfn）：
```lua
local tiletype = TheWorld.Map:GetTile(TheWorld.Map:GetTileCoordsAtPoint(pt:Get()))
if tiletype == GROUND.SUBURB or tiletype == GROUND.FOUNDATION or tiletype == GROUND.COBBLEROAD or tiletype == GROUND.LAWN or tiletype == GROUND.FIELDS then
    if worker and worker:HasTag("player") and not worker:HasTag("sneaky") then
        local eles = TheSim:FindEntities(x,y,z, 40,{"guard"})
        for k,guardas in pairs(eles) do 
            if guardas.components.combat and guardas.components.combat.target == nil then guardas.components.combat:SetTarget(worker) end
        end 
    end
end
```
即：玩家在特定地面采集 → 40 范围守卫（guard 标签）仇恨玩家。

5. **windy 标签组合强化模式**：onequip AddTag("windyX")；施法/喂食/抚摸时检查 `owner:HasTag("windy1") and owner:HasTag("windy2")` 双标签 → 无代价+强化；否则扣血扣理智。是 goddess 系核心数值杠杆。

6. **运行时创建武器**：`inst:AddComponent("inventory")` + MakeWeapon（CreateEntity → weapon/inventoryitem/equippable → Equip → Unequip(HANDS)），用于怪物（greententacle、gw_yellow_lizardman、goldmonkey 双武器）。

7. **worldsettingstimer 变形**（grass/grass_water/grassgekko）：morphdelay/morphing/morphrelay 三定时器 + triggernearbymorph 连锁扩散 + WorldSettings_Timer_PreLoad/PreLoad_Fix 存档恢复 + 密度上限检查。

8. **net 同步小字段**：net_bool/net_float/net_tinybyte/net_event + 客户端 ListenForEvent 驱动动画/灯光（goldobi _ispathfinding、goddess_star _pulsetime、green_forcefieldfx _lightframe/_islighton、gw_bonestaff_proj _killtail）。

9. **存档自定义**：OnSave/OnLoad/OnPreLoad 存自定义字段（grabbing_vine 存 spawnpatch.GUID + LoadPostPass 恢复、gw_column_angel 存 runes GetSaveRecord、greengrass 存 no_banana、grassgekko 变形状态恢复）。

10. **SetPrefabNameOverride / SetPrefabName**：形态切换共用 prefab 名（grabbing_vinefixo→grabbing_vine、grass_tallwater→grass_tall、goddess_flower_rose/planted→goddess_flower、groundlifts→boarrior）。

11. **随机权重表**：SetSharedLootTable / SetChanceLootTable / 手写权重表（goddess_pouch 50+条目、goddess_lantern PEACH_CHOICES、gw_column_angel 三层 loot）。

---

## 四、特别记录

### 复杂组件交互
- **goddess 传送链**：fountain（fueled+teleporter+activatedgf）↔ gate1 ↔ lake（fullmoon 刷 gem 鹿 + GetFish windy5 分流）→ deer 驯养（ribbon/greengem/peachy 三路线）→ statue 守卫（3 DoPeriodicTask）→ shrine（prototyper GODDESS_TWO）→ 法杖套件（lantern/staff/star/flute/sword）——整个女神玩法闭环。
- **greentornado2 标签反重叠**：goddess_deer_gem 施法前 NoSpellOverlap 检查范围内无 greentornado2，flute 生成的 tornado2_fn 带此标签——施法 AI 与法术实体的标签协议。
- **gw_column_angel + gw_rune**：父实体持有 runes 数组、runesDone 计数、cooldown timer；rune 持有 owner 反向调用 OnRuneDone/DeactivateOtherRunes——双向引用 + 事件监听灭除 + 存档恢复全套。
- **gnarwailunderwater**：子实体 buraco1/buraco2（洞）+ 角实体 + 船速跟随（OnUpdateSpeed）+ 分离转向力（SEPARATION_AMOUNT/MAX_STEER_FORCE/DESIRED_BOAT_DISTANCE）——物理+AI 结合的水下伙伴。
- **gw_bonestaff_proj**：实体隐藏（inst:Hide）+ 客户端每帧尾迹（DoPeriodicTask(0)）+ net_event 通知击杀清理（StopTail + _killtail:push）——弹道尾迹性能优化模式。

### 原版 prefab 深度改造
- grass.lua：插入守卫仇恨 + ontransplantfn 平原变高草（grass_tall）+ grassgekko 变形 + grassnova 换 build。
- goldmonkey：原版猴子换 kiki build + 双武器 + 骚扰 AI + 夜间形态（半注释）。
- goldentomb：walrus_house 全套改黄金墓（动画 shake + 金币生态）。
- grottoqueen：蜂后模板但战斗组件全注释（只剩躯壳 BOSS）。
- gw_yellow_lizardman：复用原版 lizardman SG/brain/loot 表 + isFrenzy 开关 + 雷电远程武器。
- goddess_lake：oasis 改造 + fishable 自定义 GetFish。
- greententacle：tentacle 数值强化 + MakeWeapon + 跨阵营仇恨。
- goddess_spider_hostile：数值×2 + 攻速×2 + SummonFriends 打巢召唤 + SoundPath 标签分流音效 + AddRandomLoot/AddRandomHauntedLoot。

### 笔误/Bug 清单（可作技能文档反面教材）
1. **gorge_crabtrap.lua**：`inst.caminho = "images/images/inventoryimages2.xml"` —— 多一层 images/（fish_med.lua 同模式，quagmire 原版路径移植笔误）。
2. **goddess_gate1.lua**：MakeObstaclePhysics(.25) 之后又被 MakeInventoryPhysics 覆盖，物理类型自相矛盾。
3. **goddess_tori.lua**：ondeploy 生成 goddess_gate2，但本目录只有 goddess_gate1.lua（gate2 在别处或缺失）。
4. **goddess_statue.lua 等 OnGetItem**：先 SetPercent 再检查旧值 `if uses >= 1 then SetPercent(1)` —— 检查的是旧值且百分比 ≥1 恒假，语义混乱（多处 goddess 物品同模式）。
5. **goldmonkey.lua**：SetNormalMonkey/SetNightmareMonkey + OnSave/OnLoad nightmare 标签仍存在，但触发源（TestNightmareArea/TestNightmarePhase/WatchWorldState("nightmarephase")/areaaware）全部注释——夜间形态实际不会触发。
6. **gw_rune.lua**：sacrifice 类型监听 "builditem" 事件但 RemoveEventCallback 用的是 "damaged"（`inst:RemoveEventCallback("damaged", inst.OnEx, inst.doer)`）——监听/移除事件名不一致，灭除后回调残留。
7. **gw_column_angel.lua**：`math.cos(angle + 2,0944)` —— 用逗号写小数（Lua 里是 cos(angle+2) 和 0944 两个参数，等于 cos(angle+2)），120° 定位精度错误（应为 2.0944）。
8. 前段已记录：elephantcactus.lua active 未定义、empty_bottle_green.lua `inst.componwatersource` 笔误、dungball.lua startmoving 未定义、deco_util.lua bckground 拼写、fish_med.lua caminho 多 images、flupegg.lua 孵化 antman_warrior 复制粘贴、glass.lua DES_GLASS_SWORD_THRONS 模块加载时求值。
9. **文件名与 prefab 名/路径不一致**（惯例性）：gorge_crabtrap→quagmire_crabtrap、gorge_smallmeat→quagmire_smallmeat、goddess_bird→forest/animals/goddess_bird、goldentomb→cave/objects/goldentomb、goddess_goggles→common/inventory/goddess_goggles、grasswaterspawner 纯逻辑生成器。

### 合作痕迹
葡萄牙语注释 `--tempo para renascer em dias`（grass_tall respawndays=4）、`--adicionado por vagner`（作者 vagner）与后续中文注释（修改者 Runar 风格）并存；grotto_grub_nest 的英文注释为后期修复痕迹。groundlifts.lua 为极端压紧单行风格（区别于其他文件），gw 系列（gw_ 前缀）与 grotto 系列是熔岩竞技场移植组，代码风格（GF 前缀函数）独立成系。

---

*本笔记为 A-G 全段（337文件/68481行）精读产出，可作为技能文档原料；所有代码片段均原样复制自源码。*
