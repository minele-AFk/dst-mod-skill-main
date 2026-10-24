# 便携跨世界迁移：一键传送到最近已链接传送门

场景：想做一个"随时随地穿越"的能力/按钮——不需要走到传送门跟前，点一下就用 `worldmigrator` 把玩家送到**最近的、已链接的**另一世界（地表↔洞穴）。

适合给便携物品、角色能力或装备按钮做"一键回程/穿越"。基础组件 API 见 `references/components/system/worldmigrator.md`，这里讲的是**程序化选点 + 触发迁移**的完整一波。

## 一、扫描找最近的已链接传送门

遍历全局 `ShardPortals`，从所有已 `linkedWorld` 的传送门里挑离玩家最近的：

```lua
local closedportal, mindist
for _, v in pairs(ShardPortals) do
    if v.components.worldmigrator and v.components.worldmigrator.linkedWorld then
        if not mindist or distsq(doer:GetPosition(), v:GetPosition()) < mindist then
            mindist = distsq(doer:GetPosition(), v:GetPosition())
            closedportal = v
        end
    end
end
```

- 只在服务端执行（找世界、迁移都是权威操作），客户端点按钮走 RPC。
- `distsq` 比较距离，避免每次 `sqrt`。

## 二、触发迁移（常规传送门）

对普通传送门，推官方的跨世界迁移事件即可：

```lua
TheWorld:PushEvent("ms_playerdespawnandmigrate", {
    player = doer,
    worldid = closedportal.components.worldmigrator.linkedWorld,
    portalid = closedportal.components.worldmigrator.id,
})
```

## 三、海洋漩涡出口特判（上岸而非去洞穴）

若最近传送门是**海洋漩涡出口**`oceanwhirlbigportalexit`，迁移语义不同——是"上岸"而不是跨碎片。这会拉起一段上岸演出：隐藏玩家 → 停移动 → 屏幕淡出 → 瞬移+潮湿 → 淡入 → 播放 `abyss_drop` 落地状态：

```lua
if closedportal and closedportal.prefab == "oceanwhirlbigportalexit" then
    doer:Hide()
    doer.components.locomotor:Stop()
    doer:ScreenFade(false, 1)
    doer:DoTaskInTime(1, function()
        doer.Physics:Teleport(closedportal.Transform:GetWorldPosition())
        DoDeltaMoistureToEntity(doer, 100, nil, true, true)  -- 从漩涡出来一身湿
        doer:ScreenFade(true, 1)
    end)
    doer:DoTaskInTime(2, function()
        doer:Show()
        doer:SnapCamera()
        doer.sg:GoToState("abyss_drop")
    end)
elseif closedportal then
    -- 常规跨世界迁移
end
```

> `abyss_drop` 与 `ScreenFade` 是官方上岸演出的惯用段，搬用时按需求裁剪。

## 四、防重复触发 + 确认弹窗

- **防连点**：用 `doer._migrate_lock` 在演出/迁移期间加锁，完成后清空，避免重复迁移。
- **确认弹窗**：客户端点迁移按钮前先 `PopupDialogScreen` 二次确认；确定后才 `SendModRPCToServer`，服务器执行上面的逻辑。

## 五、要点与陷阱

- **目标必须是已 `linkedWorld` 的传送门**：没链接的走不了，选点时务必过滤，否则 `worldmigrator.linkedWorld` 为 nil 会崩。
- **海洋出口 vs 普通出口语义不同**：以 `prefab == "oceanwhirlbigportalexit"` 分支区分"上岸"与"跨碎片"。
- **服务端权威**：找传送门、推迁移事件都必须在 `TheWorld.ismastersim` 分支。
- **迁移要锁**：跨世界迁移是异步演出，加锁防重复是必须项。

## 官方源码

- `components/worldmigrator.lua`：`linkedWorld`、`id`。
- `prefabs/portal_exit` 系列：`ShardPortals` 表与 `oceanwhirlbigportalexit`。
- `components/locomotor.lua`：`Stop`；`entityscript.lua`：`ScreenFade`、`Physics:Teleport`、`SnapCamera`。
- `ocean.lua` / `util.lua`：`DoDeltaMoistureToEntity`。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。