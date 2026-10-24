# 通过世界事件改变天气（月相/降雨/月雹/月亮风暴）

讲解「一键改变全图天气」的四种做法：月相、降雨、月雹、月亮风暴。它们都通过向 `TheWorld` 推 `ms_*` 事件或调用世界管理器来完成，权威在服务端；常见的触发方式是官方 `spellbook` 组件做出的施法轮盘 + 服务端 RPC 执行。

## 适用场景

- 做一件「呼出轮盘，点一下就改天气」的道具/能力（月圆、月黑、下雨、月雹、月亮风暴等）。
- 在特定条件（地下、月亮风暴中、已经满月）下做前置预检并拦截。
- 想让降雨顺带滋润农田。

## 一、月相（月圆 / 月黑）

官方 `clock` 组件监听了 `ms_setmoonphase` 事件，直接推即可：

```lua
TheWorld:PushEvent("ms_setmoonphase", { moonphase = "full", iswaxing = false })  -- 月圆
TheWorld:PushEvent("ms_setmoonphase", { moonphase = "new",  iswaxing = true })   -- 月黑
```
- `moonphase`：`full` / `new` 等月相名。
- `iswaxing`：是否「渐盈」（月黑/新月设 `true`，满月设 `false`）。
- 地下（`TheWorld:HasTag("cave")`）里没有月亮，通常要前置拦截；`clock` 在地表和洞穴都监听该事件，但表现不同。

## 二、降雨 / 停雨

官方 `weather`（地表）和 `caveweather`（洞穴）都监听 `ms_forceprecipitation`：

```lua
TheWorld:PushEvent("ms_forceprecipitation", true)   -- 开始下雨
TheWorld:PushEvent("ms_forceprecipitation", false)  -- 停雨
```
判断当前是否在下雨，用 `TheWorld.state.precipitation ~= "none"`（官方书籍也这样往返切换）。

### 顺带浇田

若要「下雨时让周边农田变湿」，遍历玩家坐标附近格并给农田加湿度：

```lua
local x, y, z = player.Transform:GetWorldPosition()
for i = x - TILE_SCALE, x + TILE_SCALE do
    for j = z - TILE_SCALE, z + TILE_SCALE do
        if TheWorld.Map:GetTileAtPoint(i, 0, j) == WORLD_TILES.FARMING_SOIL then
            TheWorld.components.farming_manager:AddSoilMoistureAtPoint(i, y, j, 100)
        end
    end
end
```

## 三、月雹（开始容易，停止要取内部函数）

开始月雹有官方事件：

```lua
TheWorld:PushEvent("ms_startlunarhail")
```
它触发 `weather` 内部 `StartLunarHail`，把 `_preciptype` 置为 `lunarhail`、`_lunarhaillevel` 拉到上限。

**难点在「停止」**：原版**没有**停止月雹的公开事件/方法。`StopLunarHail` 只是 `weather:OnUpdate` 里的一个局部闭包（把 `_preciptype` 置回 none、`_lunarhaillevel` 回到底）。mod 的常规做法是用 hook 把内部 upvalue 取出来暴露成方法：

```lua
FLU:AddComponentPostInit("weather", function(self)
    self.Noa_StopLunarHail = FLU.GetUpvalue(self.OnUpdate, "StopLunarHail")
end)
-- 之后就能 TheWorld.net.components.weather.Noa_StopLunarHail()
```
（其中 `FLU` 是用 upvalue-hook 工具按名取闭包 upvalue 的封装；取不到就回退为提示「无法停止」。）

## 四、月亮风暴（开始 / 停止）

由世界管理器 `moonstormmanager` 驱动：

```lua
local pt = player:GetPosition()
if not TheWorld.net.components.moonstorms:IsPointInMoonstorm(pt) then
    local node = TheWorld.Map:GetNodeIdAtPoint(player.Transform:GetWorldPosition())
    if node and TheWorld.topology.nodes[node] then
        TheWorld.components.moonstormmanager:StartMoonstorm(node)   -- 在玩家所在拓扑节点启动
    end
else
    TheWorld.components.moonstormmanager:StopCurrentMoonstorm()    -- 已在风暴中则停止
end
```
- `StartMoonstorm(first_node_index)` 以拓扑节点序号为起点展开风暴。
- `StopCurrentMoonstorm()` 停止当前风暴。
- 用 `moonstormmanager` 是否存在做前置判断（旧世界/某些模式可能没有）。

## 五、触发交互（右键呼出轮盘 + 服务端执行）

上述天气事件都在服务端 `TheWorld` 上生效，所以客户端点选后要把指令送回服务端执行。通用链路：

1. 道具加官方 `spellbook` 组件，用 `SetItems(BASESPELLS)` 配置候选法术（含 `fn` 服务端逻辑、图标 bank/build、anims），`SetRequiredTag` 限权限，`SetRadius/SetFocusRadius` 控轮盘半径。
2. 每个法术的 `execute` 里 `SendModRPCToServer(MOD_RPC[...]["dospellwheel"], index, inst)` 把选择发回服务端。
3. 服务端在 `fn` 里执行天气事件与消耗（每用一次扣一个材料，材料不足时 `talker:Say` 提示并 return）。

`spellbook` 是官方组件（`components/spellbook.lua`），轮盘 UI 与按键绑定都由它处理，mod 只需提供数据表。

## 校验 / 兼容性要点

- **权威只在服务端**：`ms_*` 事件与 `moonstormmanager` 只能由主机推/调；客户端必须走 RPC，否则不会生效。
- **洞穴 vs 地表**：月相/月雹由地表 `weather`/`clock` 处理，洞穴用 `caveweather`；月相在洞穴通常做拦截，降雨洞穴也可用。
- **提前做状态与资源预检**：已满月/已月黑、已在月亮风暴中、没有风暴管理器、材料不足等应在 `fn` 开头判断并 `return`，避免重复扣材料或反复启动。
- **停月雹属 hook 兜底**：官方无公开停止接口，取 upvalue 失败时要能优雅降级（提示不演示/不硬崩）。

官方源码：`components/clock.lua`（`ms_setmoonphase`）、`components/weather.lua`（`ms_forceprecipitation`、`ms_startlunarhail`、局部 `StartLunarHail`/`StopLunarHail`）、`components/caveweather.lua`（`ms_forceprecipitation`）、`components/moonstormmanager.lua`（`StartMoonstorm`/`StopCurrentMoonstorm`）、`components/farming_manager.lua`（`AddSoilMoistureAtPoint`）、`components/spellbook.lua`、`debugcommands.lua`（官方命令对同事件的调用样例）。