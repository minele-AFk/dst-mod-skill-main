# 实体复制：用存档记录复制物品或生物（不改原件）

场景：想做一个"复制/克隆"类能力——用一个工具物品可以把任意实体（物品、生物、植物、建筑）复制一份，原件保持不变。区别于"打包"（打包会 `Remove` 原件装进便携物），这里只**读取**目标的存档记录来生成第二份。

## 核心：仍是 `GetSaveRecord` + `SpawnSaveRecord`

- `target:GetSaveRecord()`：把目标整个序列化成一份保存记录 `data`。
- `SpawnSaveRecord(data)`：用这份记录**新建**一个实体。

因为从不删原件，所以行为是"复制"而非"移动/收纳"。

## 实现（工具组件 `Copy(target, doer)`）

```lua
local COPY_BLACKLIST = {}          -- 可选 prefab 黑名单

function MyCopyComponent:CanCopy(target, doer)
    if not target then return end
    if target.components.unwrappable then return end   -- 拦截已封装的
    if target:HasTag("ban_mycopy") then return end     -- 禁止复制的标签
    if target.prefab and COPY_BLACKLIST[target.prefab] then return end
    return true
end

function MyCopyComponent:Copy(target, doer)
    local data = target:GetSaveRecord()
    if not data then return end

    -- 清掉"所属容器"归属字段，避免副本生成后被判定回原容器/引用失效
    if data and data.data then
        data.data.container = nil
        data.data.mycontainer = nil
    end

    local ent = SpawnSaveRecord(data)
    if not ent then return end

    if ent.components.stackable then
        ent.components.stackable:SetStackSize(1)      -- 堆叠副本只给一份
    end
    if ent.components.inventoryitem then
        doer.components.inventory:GiveItem(ent)       -- 物品类副本进背包
    end

    -- 消耗工具：可堆叠扣一个，否则删本身
    if self.inst.components.stackable ~= nil then
        self.inst.components.stackable:Get():Remove()
    else
        self.inst:Remove()
    end
end
```

## 要点

- **原件不动**：全程只用 `GetSaveRecord` 读取，不调用 `target:Remove()`，所以要复制的实体依然留在原地。
- **清容器归属**：复制前把 `data.data.container`（及自定义容器字段）置 `nil`，防止副本创建后立刻被判定回原容器、或父级引用已失效导致问题。
- **副本整理**：可堆叠设 `SetStackSize(1)`；有 `inventoryitem` 才 `GiveItem`（纯建筑/生物副本只在目标位置生成）。
- **拦截**：`CanCopy` 前置判 `unwrappable`、`ban_` 标签与 prefab 黑名单；通常还带一个总开关配置。
- **触发接线**：actions + 交互监听，`invobject.components.my_copy:CanCopy(target, doer)` 通过才 `Copy`。

## 与"实体打包"的对比

| 能力 | 用 API | 原件 | 产物 |
|---|---|---|---|
| 打包 | `GetSaveRecord` + `Remove` + `SpawnSaveRecord` | 删除 | 一个可携带/可落盘/可释放的"打包物" |
| 复制 | `GetSaveRecord` + `SpawnSaveRecord` | 保留 | 目标原样第二份（物品进背包） |

两者可互为扩展：打包 = "移动/收纳"，复制 = "拆分出一份新的"。相关打包实现见 `entity-to-item-capture.md`。

## 官方源码

- `entityscript.lua`：`GetSaveRecord`。
- `mainfunctions.lua`：`SpawnSaveRecord`。
- `components/inventory.lua`：`GiveItem`。