# 夜视 Buff（强制夜视 / 玩家视野渲染）

通过 `playervision` 组件的「强制夜视栈」实现让玩家夜晚也能看清世界的渲染效果。
夜视本质是**覆盖全屏 ColourCube（色调分级）**，从视觉上取消夜晚的黑暗滤镜。

## 适用场景

- 给某个 Buff / 状态 / 被动能力附加夜视（临时或永久）。
- 制作「夜晚像白天」或带偏色的夜视效果。
- 多个来源同时加夜视时按照优先级叠放，后消失的来源不会把先消失的也一起关掉。

## 核心 API（组件 `playervision`，见 official 源码 `components/playervision.lua`）

| 函数 | 作用 |
| --- | --- |
| `PushForcedNightVision(source, priority, cctable, blend, ambienttable, nonightvisioncc)` | 把一组夜视数据压入栈，按 `priority` 降序，栈顶生效。以 `source` 作为唯一键，重复 push 会先 pop 旧的。 |
| `PopForcedNightVision(source)` | 按 source 移除，栈空则完全关闭夜视。 |
| `ForceNightVision(force)` | 直接强制开关夜视（无栈）。 |
| `SetCustomCCTable(cctable, blend)` | 覆盖 ColourCube 表，夜视真正改色调的地方。 |
| `GetCCTable()` / `ccoverrides` 事件 | 引擎据此读取当前 ColourCube 表来做后处理。 |

**参数注意：**
- `source`：唯一标识，必须能和 pop 时用的同一个对象/字符串。
- `priority`：数字，缺省 0；越大越优先。
- `cctable`：一张表，key 为 `day / dusk / night / full_moon`，value 为 `.tex` 的 ColourCube 路径。

## 推荐写法：独立 Buff Prefab（纯客户端渲染实体）

推荐写法如下：

```lua
local function OnEnabled(inst)
    local parent = inst.entity:GetParent()
    if parent and parent ~= nil and parent.components.playervision ~= nil then
        parent.components.playervision:PushForcedNightVision(inst, nil, {
            day        = "images/colour_cubes/identity_colourcube.tex",
            dusk       = "images/colour_cubes/identity_colourcube.tex",
            night      = "images/colour_cubes/identity_colourcube.tex",
            full_moon  = "images/colour_cubes/identity_colourcube.tex",
        })
        inst.player = parent
    end
end

local function OnRemove(inst)
    if inst.player and inst.player.components.playervision ~= nil then
        inst.player.components.playervision:PopForcedNightVision(inst)
    end
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddNetwork()
    inst:AddTag("CLASSIFIED")      -- 纯客户端透明实体
    inst.entity:SetPristine()
    inst:DoTaskInTime(0.1, OnEnabled)  -- 等 playervision 组件初始化好
    inst:ListenForEvent("onremove", OnRemove)
    if not TheWorld.ismastersim then
        return inst
    end
    inst.entity:Hide()
    inst.persists = false
    return inst
end
return Prefab("my_nightvision", fn)
```

**关键点：**
1. **不要直接在生成实体那一刻调用** `PushForcedNightVision`，因为 `DoTaskInTime(0)` 阶段 `playervision` 可能还没初始化，官方代码里 playervision 是在 `OnInit`（DoTaskInTime(0)）里监听事件的。用 `DoTaskInTime(0.1)` 兜底。
2. **`onremove` 里必须对称 `PopForcedNightVision`**，否则夜视会残留。
3. `CLASSIFIED` 标签 + `SetPristine()` + 客户端直接 return，让它成为不落盘、纯在客户端做渲染的透明实体。

## 怎么挂到玩家身上

生成该 buff 实体后 `entity:SetParent("玩家实体")` 即可。常见两处：

```lua
-- 永久被动（如角色能力）
inst.my_nightvision = SpawnPrefab("my_nightvision")
inst.my_nightvision.entity:SetParent(inst.entity)

-- 可控开关：创建时挂载，移除时 Remove（Remove 会触发 onremove 自动 pop）
if builder.my_nightvision then
    builder.my_nightvision:Remove()
    builder.my_nightvision = nil
else
    builder.my_nightvision = SpawnPrefab("my_nightvision")
    builder.my_nightvision.entity:SetParent(builder.entity)
end
```

## ColourCube 选型（决定夜视观感）

| ColourCube | 效果 |
| --- | --- |
| `images/colour_cubes/mole_vision_on_cc.tex` | 官方常规夜视，青绿色暗视觉。 |
| `images/colour_cubes/identity_colourcube.tex` | **恒等/无偏色**，等于取消黑暗滤镜，夜晚几乎像白天，更亮更白。 |
| `images/colour_cubes/ghost_cc.tex` | 幽灵视野。 |
| 自定义 `xxx.tex` | 可按需做任意偏色夜视。 |

要「夜晚像白天」用 `identity_colourcube`；要生灵视感用官方 `mole_vision_on_cc`。

## 另一种写法：net_bool + 事件回调（状态驱动的开关式夜视）

如果夜视是**某个角色状态 / 开关能力**（例如「兴奋状态」开启时夜视），且需要服务端权威控制、跨端同步，可用 `net_bool` + 客户端事件回调，而不是独立 Buff Prefab。

### 服务端：状态变化时置位网络变量

```lua
-- 进入状态时开启夜视
if inst._nightvision_enabled ~= nil then
    inst._nightvision_enabled:set(true)
    if TheWorld.ismastersim then
        inst:PushEvent("mychar_on_nightvision_dirty")  -- 手动推送，让客户端立刻刷新
    end
end
-- 退出状态时 set(false) 并同样 PushEvent
```

### 客户端：监听 dirty 事件执行 Push/Pop

```lua
-- 按季节选"白天"的 ColourCube，夜视观感更贴近真实白天
local VISION_CC = {
    spring = { dust = "images/colour_cubes/spring_day_cc.tex", night = "images/colour_cubes/spring_day_cc.tex" },
    summer = { dust = "images/colour_cubes/summer_day_cc.tex", night = "images/colour_cubes/summer_day_cc.tex" },
    autumn = { dust = "images/colour_cubes/day05_cc.tex",       night = "images/colour_cubes/day05_cc.tex" },
    winter = { dust = "images/colour_cubes/snow_cc.tex",        night = "images/colour_cubes/snow_cc.tex" },
}

local function OnNightVisionDirty(inst)
    if inst.components.playervision ~= nil then
        if inst._nightvision_enabled:value() then
            inst.components.playervision:PushForcedNightVision(inst, 1, VISION_CC[TheWorld.state.season], true)
        else
            inst.components.playervision:PopForcedNightVision(inst)
        end
    end
end

local function OnPlayerActivated(inst)
    inst:ListenForEvent("mychar_on_nightvision_dirty", OnNightVisionDirty)
    inst:ListenForEvent("equip", OnNightVisionDirty)     -- 换装备可能重置视野，需重应用
    inst:ListenForEvent("unequip", OnNightVisionDirty)
    OnNightVisionDirty(inst)
end

local function OnPlayerDeactivated(inst)
    inst:RemoveEventCallback("mychar_on_nightvision_dirty", OnNightVisionDirty)
    inst:RemoveEventCallback("equip", OnNightVisionDirty)
    inst:RemoveEventCallback("unequip", OnNightVisionDirty)
end

AddPlayerPostInit(function(inst)
    inst._nightvision_enabled = net_bool(inst.GUID, "_nightvision_enabled", "mychar_on_nightvision_dirty")
    inst:ListenForEvent("playeractivated", OnPlayerActivated)
    inst:ListenForEvent("playerdeactivated", OnPlayerDeactivated)
end)
```

### 要点

- `net_bool(guid, name, dirtyevent)`：网络布尔，服务端 `set()` 后通过 dirty 事件同步到各客户端；**dirty 事件名必须与 net_bool 第三参一致**。
- `playeractivated` / `playerdeactivated` 配对挂/摘监听，保证只在玩家激活期间存在，避免监听泄漏。
- `equip` / `unequip` 也要重应用：切换装备可能重置 `playervision` 的渲染状态。
- Push 与 Pop 严格对称：置 `true` 时 Push、置 `false` 时 Pop；同一 `source` 重复 Push 会先 Pop 旧的。
- 服务端只负责置位标记，渲染由各客户端各自执行，互不影响。

### 与独立 Buff Prefab 写法怎么选

| 场景 | 推荐写法 |
| --- | --- |
| 通用可挂载/可移除的 Buff（生成即开、移除即关） | 独立 Buff Prefab（`onremove` 自动 pop） |
| 角色状态 / 被动能力驱动的开关式夜视，需服务端权威 + 跨端同步 | `net_bool` + 事件回调 |

官方源码：`components/playervision.lua`（Push/Pop 栈）、`netvars.lua`（`net_bool` 网络布尔同步，引擎级全局函数）。

## 权威性与多人

- 这个效果只影响**本地渲染**，`playervision` 的 `ccoverrides` 是客户端走的事件，服务器不参与颜色计算。
- 实体加 `CLASSIFIED`、`SetPristine()`、非主机 return、`persists=false`，保证不落盘、不复置、不产生服务器逻辑。
- 纯主机（专服）下只有宿主自己看得到这个渲染；对其他玩家各自有各自的 `playervision`，互不影响。

## 验证

- 开启后夜晚视角明显变亮；关闭/移除 buff 后恢复正常色调，不残留。
- 死亡、换角色、跨分片、保存重载后不会残留夜视。
- 多个来源叠加时，只撤销各自 pop 的 source，其他来源不受影响。

官方源码：`components/playervision.lua`（Push/Pop 栈、UpdateCCTable、SetCustomCCTable）。
官方使用范例：`prefabs/ghostvision_buff.lua`、`prefabs/woodie.lua`、`prefabs/player_common.lua`。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。