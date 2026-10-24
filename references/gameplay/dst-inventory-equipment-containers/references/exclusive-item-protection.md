# 专属物品防偷防掉（不能被偷走/捡走/掉落）

目标：让某类「专属物品」只能由指定角色持有使用，防止被小偷偷窃、被其他玩家捡走/拿走、以及死亡/溺水时掉落。
手段分层：官方 `nosteal` 标签防偷 + 角色级 `Thief:StealItem` hook 整体免疫 + `inventoryitem` 抓取/放入权限控制防击落。

## 一、防偷窃（stolen）

### 物品级：`nosteal` 标签

官方偷窃判定直接跳过带 `nosteal` 的条目（`components/thief.lua`）：

```lua
item_is_stealable = function(item)
    return not item:HasTag("nosteal")
end
```

物品加标签即可免疫小偷/坎普斯/盗魔：

```lua
inst:AddTag("nosteal")
```

### 角色级：包 `Thief:StealItem`

更彻底——直接让某角色整体不被偷：

```lua
local oldStealItem = Thief.StealItem
function Thief:StealItem(victim, itemtosteal, attack, ...)
    if victim and victim:HasTag("mychar") then
        return                        -- 指定角色免疫一切偷窃
    end
    return oldStealItem(self, victim, itemtosteal, attack, ...)
end
```

## 二、防被捡 / 防击落（inventoryitem 权限控制）

核心是「只有专属角色能抓取/持有，他人放入强制丢出」：

```lua
function MakeUnPickable(inst)
    inst.components.inventoryitem.grabbableoverridetag = "mychar"  -- 只有带该标签的能抓取
    inst.components.inventoryitem.canbepickedup = false             -- 默认不可被捡起
    inst:ListenForEvent("onputininventory", function(_, owner)
        if owner and owner.HasTag and owner:HasTag("mychar") then
        elseif owner then
            inst:DoTaskInTime(0, function()
                owner.components.inventory:DropItem(inst)          -- 非专属角色放入被强制丢出
            end)
        end
    end)
end
```

加固项（按需组合）：

```lua
inst.components.inventoryitem.canonlygoinpocket = true   -- 只能进快捷栏小口袋，不能进容器
inst.components.inventoryitem.keepondeath = true         -- 死亡不掉落
inst.components.inventoryitem.keepondrown = true         -- 溺水不掉落
```

更严格的「非专属角色放入直接销毁」：

```lua
inst:ListenForEvent("onputininventory", function(_, owner)
    if owner and owner.HasTag and owner:HasTag("mychar") then
    else
        inst:DoTaskInTime(0, function() inst:Remove() end)
    end
end)
```

## 适用分层表

| 威胁 | 手段 |
| --- | --- |
| 被小偷/坎普斯偷 | `nosteal` 标签（物品级）+ `Thief:StealItem` hook（角色级整体免疫） |
| 被其他玩家捡走 | `grabbableoverridetag` + `canbepickedup=false` + 强制 `DropItem`/`Remove` |
| 死亡/溺水掉落 | `keepondeath` / `keepondrown` |
| 被放进容器转移 | `canonlygoinpocket` |

## 注意

- `grabbableoverridetag` 与 `canbepickedup` 需配合，前者是「谁可抓」的标签白名单，后者是默认禁拾取。
- `onputininventory` 里用 `DoTaskInTime(0, ...)` 延迟一拍再丢出/移除，避免在放入回调中途破坏当前迭代。
- 全部在主机端完成，客户端只负责 UI；多人下不可在客户端执行 `DropItem`/`Remove`。
- 若物品同时要长期存在于某角色背包，记得处理保存/读档与物品所有权同步。

官方参考：`components/thief.lua`、`components/inventoryitem.lua`、`components/inventory.lua`。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。