# 模板模式

当任务需要实用的入门模板而非概念性指导时，请使用此文件。这些模板是最小化的起点，而非可直接使用的完整模组。

选择最适合请求功能的最小模板。
不要仅仅因为模板看起来都有用就组合不相关的模板。

## 最小化 `modmain.lua`

```lua
local GLOBAL = GLOBAL
GLOBAL.setmetatable(env, {
    __index = function(_, key)
        return GLOBAL.rawget(GLOBAL, key)
    end,
})

PrefabFiles = {
    "my_item",
}

Assets = {
}

-- Shared declarations and registrations go here.

if not TheWorld.ismastersim then
    return
end

-- Server-authoritative logic goes here.
```

此模板的只读规则：

- 仅为查找方便使用透传机制
- 不要赋值给 `GLOBAL`、`TheSim`、`TheNet`、`TheShard`、`TheInput`、`TheFrontEnd`、`TheMixer`、`TheCamera`、`TheFocalPoint`、`TheWorld` 或 `ThePlayer`
- 如果扩展共享注册表（如 `TUNING` 或 `STRINGS`），仅添加所需的键，不要替换整个表

在以下情况使用此模板：

- 模组并非纯粹的世界生成侧
- `modmain.lua` 是正常的运行时入口点
- 仍需要常规的全局透传和权限分离

## `modmain.lua` 中的最小化玩家全局补丁

```lua
AddPlayerPostInit(function(inst)
    inst:AddTag("my_mod_player")

    if not TheWorld.ismastersim then
        return
    end

    inst:ListenForEvent("death", function(player)
        -- authoritative player-wide behavior
    end)
end)
```

在以下情况使用此模板：

- 功能应影响每个玩家，而非单个角色预制件
- 主要缺失的是安全的 `AddPlayerPostInit(...)` 框架
- 如果有本地 HUD 或屏幕工作，将单独保护

## `modmain.lua` 中的最小化角色注册

```lua
local GLOBAL = GLOBAL
GLOBAL.setmetatable(env, {
    __index = function(_, key)
        return GLOBAL.rawget(GLOBAL, key)
    end,
})

PrefabFiles = {
    "mychar",
}

Assets = {
    Asset("IMAGE", "images/avatars/avatar_mychar.tex"),
    Asset("ATLAS", "images/avatars/avatar_mychar.xml"),
    Asset("IMAGE", "images/avatars/avatar_ghost_mychar.tex"),
    Asset("ATLAS", "images/avatars/avatar_ghost_mychar.xml"),
    Asset("IMAGE", "images/avatars/self_inspect_mychar.tex"),
    Asset("ATLAS", "images/avatars/self_inspect_mychar.xml"),
    Asset("IMAGE", "images/saveslot_portraits/mychar.tex"),
    Asset("ATLAS", "images/saveslot_portraits/mychar.xml"),
    Asset("IMAGE", "images/selectscreen_portraits/mychar.tex"),
    Asset("ATLAS", "images/selectscreen_portraits/mychar.xml"),
    Asset("IMAGE", "images/selectscreen_portraits/mychar_silho.tex"),
    Asset("ATLAS", "images/selectscreen_portraits/mychar_silho.xml"),
    Asset("IMAGE", "bigportraits/mychar.tex"),
    Asset("ATLAS", "bigportraits/mychar.xml"),
    Asset("IMAGE", "bigportraits/mychar_none.tex"),
    Asset("ATLAS", "bigportraits/mychar_none.xml"),
}

AddMinimapAtlas("images/map_icons/mychar.xml")
AddModCharacter("mychar", "FEMALE")
```

同样的只读规则适用于此模板。
在连接角色注册时不要重新绑定引擎全局变量。

在以下情况使用此模板：

- 任务是真实的角色模组
- 主要缺失的是注册加上前端资源
- 实际的玩家逻辑将存在于 `prefabs/mychar.lua` 中

如果角色有备用服装或装备预览形式，传递可选的第三个参数：

```lua
local character_modes = {
    { type = "young_skin", play_emotes = true },
    { type = "old_skin", play_emotes = true, scale = 0.9 },
}

AddModCharacter("mychar", "FEMALE", character_modes)
```

仅在前端预览模式中使用此参数。
它不会替换真实游戏玩法侧的形态切换逻辑。

## 最小化 `modworldgenmain.lua`

```lua
AddRoomPreInit("BGForest", function(room)
    room.contents = room.contents or {}
    room.contents.distributeprefabs = room.contents.distributeprefabs or {}
    room.contents.distributeprefabs.my_worldgen_prefab = 0.03
end)
```

在以下情况使用此模板：

- 任务仅在生成时执行
- 功能属于房间、任务、关卡或起始位置
- 运行时游戏玩法钩子不是主要更改

## 最小化 `modservercreationmain.lua`

```lua
AddCustomizeGroup(LEVELCATEGORY.WORLDGEN, "mygroup", "My Group", "Host-facing mod group.", nil, 50)

AddCustomizeItem(LEVELCATEGORY.WORLDGEN, "mygroup", "my_option", {
    text = "My Option",
    desc = "Host-facing worldgen toggle.",
    items = {
        { data = "default", text = "Default", desc = "Use the default behavior." },
        { data = "often", text = "Often", desc = "Bias toward this option." },
    },
})
```

在以下情况使用此模板：

- 主机设置屏幕必须公开模组拥有的选项
- 任务面向预设或设置 UI
- 生成的内容本身可能仍需要在其他地方匹配世界生成侧逻辑

## 最小化预制件

```lua
local assets =
{
    Asset("ANIM", "anim/my_item.zip"),
}

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    inst.AnimState:SetBank("my_item")
    inst.AnimState:SetBuild("my_item")
    inst.AnimState:PlayAnimation("idle")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")

    return inst
end

return Prefab("my_item", fn, assets)
```

在以下情况使用此模板：

- 任务需要一个裸的联网预制件外壳
- 实际行为将通过组件在后续添加
- 需要在添加逻辑前进行安全的 `SetPristine()` 分离

## 最小化自定义组件

```lua
local MyComponent = Class(function(self, inst)
    self.inst = inst
end)

function MyComponent:OnRemoveFromEntity()
end

function MyComponent:OnSave()
    return nil
end

function MyComponent:OnLoad(data)
end

return MyComponent
```

从预制件附加组件：

```lua
inst:AddComponent("mycomponent")
```

## 最小化 Widget 补丁

```lua
AddClassPostConstruct("widgets/controls", function(self)
    -- patch constructor-time widget behavior here
end)
```

仅对已由游戏 `require(...)` 加载的类使用此模板。
如果用户确实想要一个全新的 widget 类，首先创建 widget 文件，然后从所属屏幕进行补丁或实例化。

## 最小化热键

```lua
if not TheNet:IsDedicated() then
    local my_key_handler = TheInput:AddKeyDownHandler(KEY_F, function()
        -- local hotkey logic
    end)
end
```

如果处理器属于 widget 或屏幕，请存储它并在拆解时移除。

如果功能应尊重控件重新映射，优先使用基于控件的模板而非原始按键处理。

## 最小化模组 RPC

```lua
AddModRPCHandler("my_mod", "do_thing", function(player, ...)
    -- server-side authoritative handler
end)

if not TheNet:IsDedicated() then
    local function SendThing(...)
        SendModRPCToServer(GetModRPC("my_mod", "do_thing"), ...)
    end
end
```

在以下情况使用此模板：

- 本地输入或 UI 应请求权威的服务器端操作
- 状态变更不完全属于客户端

## 预制件上的最小化 Netvar

```lua
local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddNetwork()

    inst._enabled = net_bool(inst.GUID, "my_prefab._enabled", "enableddirty")

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst._enabled:set(true)

    return inst
end
```

在以下情况使用此模板：

- 客户端需要一个小的复制值
- 完整的 replica 组件会过于复杂

## 最小化一次性特效预制件

用于不需要持久化或直接点击的短视觉效果。

```lua
local assets =
{
    Asset("ANIM", "anim/my_fx.zip"),
}

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()

    inst:AddTag("FX")
    inst:AddTag("NOCLICK")

    inst.entity:SetCanSleep(false)
    inst.persists = false

    inst.AnimState:SetBank("my_fx")
    inst.AnimState:SetBuild("my_fx")
    inst.AnimState:PlayAnimation("idle")

    inst:ListenForEvent("animover", inst.Remove)

    return inst
end

return Prefab("my_fx", fn, assets)
```

## 最小化发光预制件

用于拥有简单光源的常规游戏玩法预制件。

```lua
local assets =
{
    Asset("ANIM", "anim/my_lamp.zip"),
}

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddLight()
    inst.entity:AddNetwork()

    inst.AnimState:SetBank("my_lamp")
    inst.AnimState:SetBuild("my_lamp")
    inst.AnimState:PlayAnimation("idle")

    inst.Light:SetFalloff(0.7)
    inst.Light:SetIntensity(0.8)
    inst.Light:SetRadius(2)
    inst.Light:SetColour(180 / 255, 195 / 255, 150 / 255)
    inst.Light:EnableClientModulation(true)

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")

    return inst
end

return Prefab("my_lamp", fn, assets)
```

## 最小化纯音效代理

当服务器应触发提示但声音可以在客户端本地生成时使用此模板。

```lua
local function PlayLocalSound(proxy, sound)
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddSoundEmitter()
    inst.entity:SetParent(TheFocalPoint.entity)

    inst.SoundEmitter:PlaySound(sound)
    inst:Remove()
end

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddNetwork()

    inst:AddTag("FX")
    inst:AddTag("NOCLICK")

    if not TheNet:IsDedicated() then
        inst:DoTaskInTime(0, PlayLocalSound, "dontstarve/common/click_stone")
    end

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst.entity:SetCanSleep(false)
    inst.persists = false
    inst:DoTaskInTime(1, inst.Remove)

    return inst
end

return Prefab("my_sound_proxy", fn)
```

## 最小化配方和放置器

```lua
AddRecipe2(
    "my_structure",
    {
        Ingredient("rocks", 4),
    },
    TECH.NONE,
    {
        placer = "my_structure_placer",
        min_spacing = 2,
    },
    {
        "STRUCTURES",
    }
)
```

```lua
return Prefab("my_structure", fn, assets),
    MakePlacer("my_structure_placer", "my_structure", "my_structure", "idle")
```

## 最小化字符串

```lua
STRINGS.NAMES.MY_ITEM = "My Item"
STRINGS.RECIPE_DESC.MY_STRUCTURE = "Place a structure."
STRINGS.CHARACTERS.GENERIC.DESCRIBE.MY_ITEM = "A custom thing."
```

对于少量字符串添加使用直接赋值。
如果任务是"真正的区域设置支持"，请停止并切换到 `references/patterns/runtime-i18n-patterns.md`。

## 最小化运行时 I18n 加载器

当模组需要真正的运行时本地化而非几个直接字符串写入时使用此模板。

```lua
local supported = {
    en = true,
    zh = true,
}

local function ResolveLocale()
    local locale = GetModConfigData("LANGUAGE")
    if locale == nil or locale == "auto" then
        locale = LOC.GetLocaleCode()
    end
    if not supported[locale] then
        locale = "en"
    end
    return locale
end

local function DeepCopy(value)
    if type(value) ~= "table" then
        return value
    end
    local result = {}
    for k, v in pairs(value) do
        result[k] = DeepCopy(v)
    end
    return result
end

local function DeepMerge(dst, src)
    for k, v in pairs(src) do
        if type(v) == "table" then
            if type(dst[k]) ~= "table" then
                dst[k] = {}
            end
            DeepMerge(dst[k], v)
        else
            dst[k] = v
        end
    end
end

local locale = ResolveLocale()

DeepMerge(STRINGS, require("languages/common_" .. locale))

local speech = DeepCopy(STRINGS.CHARACTERS.GENERIC)
DeepMerge(speech, require("languages/speech_mychar_" .. locale))
STRINGS.CHARACTERS.MYCHAR = speech
```

推荐在以下情况使用：

- 模组有公共区域设置数据和角色语音覆盖
- 区域设置文件应保持稀疏
- 角色语音应从通用基类继承缺失的行

不要将此代码复制到 `modinfo.lua`。
这仅在运行时侧使用。

## 最小化可玩角色预制件

```lua
local MakePlayerCharacter = require("prefabs/player_common")

local assets =
{
    Asset("SCRIPT", "scripts/prefabs/player_common.lua"),
    Asset("ANIM", "anim/player_mychar.zip"),
    Asset("ANIM", "anim/player_idles_mychar.zip"),
}

local prefabs = {}

local start_inv = {}
for mode, items in pairs(TUNING.GAMEMODE_STARTING_ITEMS) do
    start_inv[string.lower(mode)] = items.MYCHAR
end

local function common_postinit(inst)
    inst:AddTag("mychar")
    inst.customidleanim = "idle_mychar"
end

local function master_postinit(inst)
    inst.starting_inventory = start_inv[TheNet:GetServerGameMode()] or start_inv.default

    inst.components.health:SetMaxHealth(TUNING.MYCHAR_HEALTH)
    inst.components.hunger:SetMax(TUNING.MYCHAR_HUNGER)
    inst.components.sanity:SetMax(TUNING.MYCHAR_SANITY)
end

return MakePlayerCharacter("mychar", prefabs, assets, common_postinit, master_postinit)
```

在以下情况使用此模板：

- 任务是真实的可玩角色
- 需要来自 `player_common.lua` 的正常玩家基线
- 角色还不需要自定义技能树

## 最小化角色技能树注册

仅在角色确实需要可解锁的进度时使用此模板。

```lua
local skilltreedefs = require("prefabs/skilltree_defs")
local BuildMyCharSkillTreeData = require("prefabs/skilltree_mychar")

local data = BuildMyCharSkillTreeData(skilltreedefs.FN)

skilltreedefs.CreateSkillTreeFor("mychar", data.SKILLS)
skilltreedefs.SKILLTREE_ORDERS.mychar = data.ORDERS

if data.BACKGROUND_SETTINGS ~= nil then
    skilltreedefs.SKILLTREE_METAINFO.mychar.BACKGROUND_SETTINGS = data.BACKGROUND_SETTINGS
end

if data.CUSTOM_FUNCTIONS ~= nil then
    skilltreedefs.CUSTOM_FUNCTIONS.mychar = data.CUSTOM_FUNCTIONS
end
```

配合以下内容使用：

- `Asset("SCRIPT", "scripts/prefabs/skilltree_mychar.lua")`
- `scripts/prefabs/skilltree_mychar.lua` 数据模块
- 可选的 `builder_skill` 配方门限用于技能解锁的制作

## 最小化 Brain

```lua
require "behaviours/wander"

local MyBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
end)

function MyBrain:OnStart()
    local root = PriorityNode({
        Wander(self.inst, function() return self.inst:GetPosition() end, 6),
    }, .25)

    self.bt = BT(self.inst, root)
end

return MyBrain
```

从预制件附加：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
local brain = require("brains/mybrain")

...

inst:SetBrain(brain)
inst:SetStateGraph("SGmycreature")
```

## 变体预制件工厂

当许多预制件共享相同设置且仅通过小配置表区分时使用此模板。

```lua
local assets =
{
    Asset("ANIM", "anim/my_weapons.zip"),
    Asset("ANIM", "anim/swap_my_weapons.zip"),
}

local variants =
{
    {
        prefab = "my_blade_red",
        anim = "red",
        damage = 34,
        uses = 100,
    },
    {
        prefab = "my_blade_blue",
        anim = "blue",
        damage = 42,
        uses = nil, -- infinite durability
    },
}

local function MakeWeaponVariant(data)
    local function fn()
        local inst = CreateEntity()

        inst.entity:AddTransform()
        inst.entity:AddAnimState()
        inst.entity:AddNetwork()

        inst.AnimState:SetBank("my_weapons")
        inst.AnimState:SetBuild("my_weapons")
        inst.AnimState:PlayAnimation(data.anim)

        inst.entity:SetPristine()

        if not TheWorld.ismastersim then
            return inst
        end

        inst:AddComponent("inspectable")
        inst:AddComponent("inventoryitem")
        inst:AddComponent("equippable")
        inst:AddComponent("weapon")
        inst.components.weapon:SetDamage(data.damage)

        if data.uses ~= nil then
            inst:AddComponent("finiteuses")
            inst.components.finiteuses:SetMaxUses(data.uses)
            inst.components.finiteuses:SetUses(data.uses)
        end

        return inst
    end

    return Prefab(data.prefab, fn, assets)
end

local prefabs = {}
for _, data in ipairs(variants) do
    table.insert(prefabs, MakeWeaponVariant(data))
end

return unpack(prefabs)
```

推荐在以下情况使用：

- 大部分设置是共享的
- 差异由表驱动
- 一个文件应拥有整个物品系列

如果变体开始需要许多不相关的分支，请拆分文件或将共享助手向下移动一级。

当用户请求以下内容时，这是正确的默认选择：

- 整个法杖或宝石系列
- 具有相同基本流程的多种食物
- 主要通过表数据区分的多种武器或护甲变体

## 经验法则

- 从最适合的最小模板开始。
- 仅在读取最接近的官方文件后替换占位符。
- 保持模板范围狭窄；仅在需要时将复杂性移至专用文件。
- 如果任务有明确的负面约束（如"无耐久度"、"不可检查"或"仅客户端"），在编码前移除违反该约束的模板部分。