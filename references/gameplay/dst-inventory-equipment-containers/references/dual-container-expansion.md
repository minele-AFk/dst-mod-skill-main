# 双容器扩容储物：隐藏子容器翻倍存储空间

场景：想让一个可携带的储物盒容量超出 UI 显示——例如 UI 只有 8×8=64 格，但实际能存两倍。做法是给物品挂**两个容器**：玩家看到的"主容器" + 一个隐藏的"子容器"，配合开合搬移把两个容器都装满。

## 一、两容器 + 开合搬移

- 主容器：可见，正常渲染，玩家往里面放东西。
- 子容器：`NOCLICK / NOBLOCK / notarget` 标签，UI 隐藏到屏幕外（`widget.pos = Vector3(0,-1100,0)`、隐藏 `bganim/bgimage`），是一个"不显示的备用储物"。子容器不跟随实体持久化（`persists = false`），其内容由父项的存档记录带走。

开/合时在两个容器之间来回倒腾，保证**两格区都物尽其用**：

```lua
-- 打开：把子容器物品搬进可见主容器展示
function onopen(inst)
    local child = inst.components.my_storage.child_containers
    local items = RemoveAllItems(child)   -- 用 RemoveItemBySlot 批量取出
    for slot, item in ipairs(items) do
        inst.components.container:GiveItem(item, slot, nil, true)
    end
end

-- 关闭/收回：把主容器物品搬回子容器，并让子容器在后台保持"可接收"
function onclose(inst)
    local child = inst.components.my_storage.child
    local items = RemoveAllItems(inst.components.container)
    for slot, item in ipairs(items) do
        child.components.container.noa_allownitem = true      -- 暂时放开子容器过滤
        child.components.container:GiveItem(item, slot, nil, true)
        child.components.container.noa_allownitem = false
    end
    child.components.container:Open(owner)  -- 后台打开但不弹 UI
    child.receiveitem = true                -- 置位：新物品重定向到子容器
end
```

## 二、GiveItem 重定向：新物品进子容器

覆盖主容器的 `GiveItem`，当携带状态下 `receiveitem = true` 时，把新放入的物品**拦截并改投给隐藏子容器**：

```lua
local oldGiveItem = inst.components.container.GiveItem
inst.components.container.GiveItem = function(container, item, slot, src_pos, drop_on_fail, ...)
    if child and child:IsValid() and child.receiveitem then
        child.components.container.noa_allownitem = true
        local r, b, c = child.components.container:GiveItem(item, slot, src_pos, drop_on_fail, ...)
        child.components.container.noa_allownitem = false
        return r, b, c
    end
    return oldGiveItem(container, item, slot, src_pos, drop_on_fail, ...)
end
```

这样物品栏里持续往盒子塞东西，也会进入隐藏子容器，使两格区都被利用。

## 三、后台"打开"但不弹 UI（fakeOpen）

`container:Open(owner)` 默认会拉起 UI。为让子容器在后台维持"打开/可接收"而不打扰玩家，手动实现一个精简版 Open：只登记 `inventory.opencontainers`、`openlist`、`opencount`，**跳过真正的 UI 打开与声音**：

```lua
local function fakeOpen(self, doer, ...)
    if doer ~= nil and self.openlist[doer] == nil then
        self.openlist[doer] = true
        self.opencount = self.opencount + 1
        self.inst.replica.container:AddOpener(doer)
        if doer.components.inventory then
            doer.components.inventory.opencontainers[self.inst] = true -- 登记但不弹窗
        end
        self.inst:PushEvent("onopen", { doer = doer })
    end
end
child.components.container.Open = fakeOpen
```

## 四、防泄漏兜底：倾倒类操作必须两容器都清

隐藏子容器里的物品最怕"掉落/丢弃"时漏掉。把原版的"倾倒"类方法整体重定向，令其**同时**作用于主、子两个容器：

```lua
local need_redir = { "DropEverything", "DropEverythingWithTag",
                     "DropEverythingByFilter", "DropEverythingUpToMaxStacks" }
for _, k in pairs(need_redir) do
    local old = inst.components.container[k]
    inst.components.container[k] = function(self, ...)
        child.components.container[k](child.components.container, ...)  -- 先清子容器
        return old(self, ...)                                            -- 再清主容器
    end
end
```

同样，`OnPutInInventory`（收进物品栏）也要触发一次"物品回填子容器 + 后台打开"，避免带着盒子到处走时物品留在看不到的地方。

## 五、持久化

主容器内容会随自身存档保存；**子容器内容**需在父项 `OnSave` 用 `child:GetPersistData()` 打包、`OnLoad` 用 `SetPersistData()` 还原（期间临时放开子容器过滤 `noa_allownitem`），否则重进后子箱内容丢失。

## 六、要点与陷阱

- **过滤要能临时放开**：搬移/还原时子容器若有 `itemtestfn`，需用 `noa_allownitem = true` 包裹，否则自己搬回去的东西也被拒收。
- **receiveitem 置位时机**：只有进入"携带/关闭"状态才置真，避免孩子容器拦截正常摆放。
- **倾倒兜底**：凡是"清空/丢弃"类 API 都要主、子双容器处理，否则隐蔽泄漏。
- **容量错觉**：两容器各 64 格，但要玩家**开合一次**才能让两格都可用，属于"技巧性扩容"，不是 UI 直接显示 128 格，需要配套说明。

## 官方源码

- `components/container.lua` / `container_replica.lua`：`GiveItem`、`RemoveItemBySlot`、`Open`、`openlist`、`opencount`。
- `scripts/containers.lua`：`widgetsetup`、`itemtestfn` 与 `widget.pos`。
- `entityscript.lua`：`SetPersistData` / `GetPersistData`、`SetParent`。