# 快速采集/快速制造/快速交互：dolongaction 统一提速

给角色添加「采集快」「制造快」「交互快」三类被动能力。与「快速制作（fastbuilder 标签）」「快速进食（自定义 SG 状态）」不同，本方案走第三条路线：**覆写共享长动作状态 `dolongaction`，把动作时长统一缩短**，一次改动覆盖多类动作。

三种路线的适用场景：
- `fastbuilder` 标签：只需加速官方「建造/制作」，最省事，但倍率固定减半、作用面受限。
- 自定义 SG 状态：需要对单个动作做精细控制（动画、音效、触发时机都自定义）。
- **dolongaction 覆写（本方案）**：要同时加速「采集/建造/收获/拆包」等多类长动作，且倍率可任意调。

## 一、核心：覆写 dolongaction 缩短超时

官方在 `stategraphs/SGwilson.lua` 中，`dolongaction` 状态的 `onenter(inst, timeout)` 会执行 `inst.sg:SetTimeout(timeout)`——**timeout 就是整个长动作的时长**。通过覆写 onenter 把 timeout 缩短（如除以 3），动作更快走完。该状态被采集、建造、收获、拆包等多类动作共享。

```lua
local FAST_ACTIONS = {
    [ACTIONS.PICK]    = true,  -- 采集/拾取
    [ACTIONS.BUILD]   = true,  -- 建造/放置
    [ACTIONS.HARVEST] = true,  -- 收获作物
    [ACTIONS.UNWRAP]  = true,  -- 拆礼物/包裹
}
local FAST_MULT = 3   -- 提速倍率（timeout ÷ 3）

local function FastWork(sg)
    local dolongaction = sg.states.dolongaction
    if dolongaction then
        local onenter = dolongaction.onenter
        if onenter then
            dolongaction.onenter = function(inst, timeout, ...)
                if inst:HasTag("mychar") and inst.bufferedaction ~= nil and
                   FAST_ACTIONS[inst.bufferedaction.action] then
                    if timeout then
                        timeout = timeout / FAST_MULT
                    else
                        timeout = 0.3   -- 未给 timeout 时兜底一个短时长
                    end
                end
                onenter(inst, timeout, ...)
            end
        end
    end
end

-- 服务端与客户端都要改，否则本地预测不一致
AddStategraphPostInit("wilson", FastWork)
AddStategraphPostInit("wilson_client", FastWork)
```

要点：
- `dolongaction.onenter` 的签名是 `(inst, timeout)`，覆写后必须调用原 onenter，把改短的 timeout 传进去。
- **服务端/客户端成对处理**：`wilson` 与 `wilson_client` 都挂 `AddStategraphPostInit`，保证本地预测和服务器一致。
- 原版 timeout > 1 时会给状态加 `slowaction` 标签并显示行动条（actionmeter）；缩短后小于 1 则自然去掉该表现，动作结束得更快。
- 如需对特定目标例外（如某些特殊物品不加速），在覆写里按 `inst.bufferedaction.target.prefab` 判断回退到原逻辑。

## 二、双倍采集：覆写 pickable:Pick

「快速采集」的另一层：**产量翻倍**。覆写 `pickable` 组件的 `Pick`，在原逻辑成功后追加生成一份产物并交给玩家。

```lua
AddComponentPostInit("pickable", function(self)
    local Pick = self.Pick
    function self:Pick(picker, ...)
        local ok, loot = Pick(self, picker, ...)
        if ok and picker ~= nil and picker:HasTag("mychar") and self.product ~= nil then
            local extra = SpawnPrefab(self.product)
            if extra ~= nil then
                if extra.components.inventoryitem ~= nil then
                    extra.components.inventoryitem:InheritWorldWetnessAtTarget(self.inst)
                end
                if picker.components.inventory ~= nil then
                    picker.components.inventory:GiveItem(extra, nil, self.inst:GetPosition())
                else
                    extra.Transform:SetPosition(self.inst:GetPosition():Get())
                end
            end
        end
        return ok, loot
    end
end)
```

要点：
- 追加产物走 `SpawnPrefab(self.product)`，与 `pickable` 的 `product` 字段保持一致。
- `numtoharvest > 1` 的堆叠情况，原版 `Pick` 已把首份设为对应堆叠数；追加份默认单份，如需完全一致可在生成后同步 `SetStackSize`。
- 若目标带 `lootdropper`（掉地物），也可改为在 `Pick` 内把产物生成部分复制两份（掉落与入包路径同时翻倍），效果相同、写法更长。

## 三、一键范围收获：按键 + RPC + 服务端批量 Pick

「快速采集」的第三层：**按一个键，一次性拾取周围所有可采摘物**。客户端监听按键发 RPC，服务端在 12 码范围内批量执行 `Pick`。

客户端：

```lua
TheInput:AddKeyHandler(function(key, down)
    if ThePlayer == nil or not ThePlayer:HasTag("mychar") or not down then
        return
    end
    if key == MY_HARVEST_KEY then   -- 建议做成模组配置项，方便玩家改键
        SendModRPCToServer(MOD_RPC[MY_MOD_RPCNAME]["harvest"])
    end
end)
```

服务端：

```lua
AddModRPCHandler(MY_MOD_RPCNAME, "harvest", function(inst)
    local x, y, z = inst.Transform:GetWorldPosition()
    local ents = TheSim:FindEntities(x, y, z, 12)   -- 半径 12 码
    for _, ent in ipairs(ents) do
        if ent.components.pickable ~= nil and ent.components.pickable:CanBePicked() then
            ent.components.pickable:Pick(inst)
        end
    end
end)
```

要点：
- **服务端权威**：批量拾取必须在服务端执行（`AddModRPCHandler`），客户端只发键位通知。
- 用 `CanBePicked()` 过滤掉不可摘状态（未成熟、已摘空等）。
- 键位应做成模组配置（`GetModConfigData`），不要写死。
- 若只想作用于特定形态/持有物，可在服务端先检查 `inst.components.inventory:GetEquippedItem(EQUIPSLOTS.HANDS)` 再触发。

## 常见坑

- **只改服务端 SG 忘了客户端**：动作时长/预测在 `wilson_client` 不处理会出现本地回跳、不同步。
- **覆写 onenter 后忘记调用原函数**：必须 `onenter(inst, timeout, ...)` 把新 timeout 传回，否则该状态行为被破坏。
- **一刀切加速影响过广**：`dolongaction` 是共享状态，覆写时要用动作白名单（`FAST_ACTIONS`）和标签判断收窄作用面，避免误伤其它长动作。
- **RPC 批量拾取的边界**：范围过大、批量执行时要注意性能；`FindEntities` 半径不宜设太大。

官方源码：`stategraphs/SGwilson.lua`（`dolongaction` 状态、`onenter(inst, timeout)` 与 `SetTimeout`）、`scripts/components/pickable.lua`（`Pick`、`CanBePicked`、`product`）、`modutil.lua`（AddModRPCHandler 等 RPC 注册）。

---

## 相关枢纽

- [character-fast-abilities.md](character-fast-abilities.md) - 同主题的另两条路线：内建 `fastbuilder` 标签（快速制作）与自定义 SG 状态（快速进食）。
