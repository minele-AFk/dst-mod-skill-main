# 实体打包：把任意实体压缩成一个便携可携带物品

场景：想做一个"万物打包/收纳"类物品——用一个工具物品可以把任意实体（物品、建筑、生物、植物）"装"走，变成一个可放背包、可携带、可落盘、能再释放回来的便携物品（类似"纪念品封装/任意实体收纳"）。

这**不是**往普通容器格子里塞物品，而是把整个实体的**存档记录**当成数据装进一个便携容器实体里。包进来的是任意可入档实体的序列化记录，所以能打包几乎一切。

## 核心：两个官方 API

- `ent:GetSaveRecord()`（`entityscript.lua`）：把任意实体整个序列化成一份保存记录 `data`（含 prefab 与组件状态）。
- `SpawnSaveRecord(data)`（`mainfunctions.lua`）：用这份记录原样重建实体。

## 结构：一个"打包工具" + 一个"打包物容器"

- **打包工具**（如"奇点"）：带一个 `my_pack` 组件，可堆叠、可对手边实体执行打包。
- **打包物容器**（`my_pack_wrapper`）：一个普通便携物品，内部存 `data`（目标实体存档记录），可改名、可入库、可部署释放；带"禁止再打包"标签防止嵌套。

## 打包（工具组件 `Pack(target, doer)`）

```lua
function MyPack:CanPack(target, doer)
    if not target then return end
    if target:HasTag("ban_mypack") then return end   -- 禁止再被打包（防嵌套）
    if TARGETBLACKLIST[target.prefab] then return end -- 可选黑名单
    return true
end

function MyPack:Pack(target, doer)
    local data = target:GetSaveRecord()      -- 1 任意实体序列化成存档记录
    if not data or not data.prefab then return end
    local name = target:GetDisplayName()     -- 记下原名用来改名
    target:Remove()                          -- 2 删除原实体

    local wrapper = SpawnPrefab("my_pack_wrapper")   -- 3 生成"打包物"
    doer.components.inventory:GiveItem(wrapper)      --    进背包
    wrapper.components.my_pack_wrapper:SetData(data) -- 4 存档记录存入容器组件
    wrapper.components.named:SetName("打包的" .. name) -- 5 改成"打包的<原名>"

    -- 6 消耗工具（若可堆叠则扣一个，否则删自身）
    if self.inst.components.stackable ~= nil then
        self.inst.components.stackable:Get():Remove()
    else
        self.inst:Remove()
    end
end
```

## 打包物容器（`my_pack_wrapper`）与释放

```lua
function MyPackWrapper:SetData(data)
    self.data = data
end

function MyPackWrapper:ReleaseData(pos, doer, rot)
    if not self.data or not self.data.prefab then self.inst:Remove() return end
    local ent = SpawnSaveRecord(self.data)          -- 用存档记录原样重建
    ent.Transform:SetPosition(pos.x, pos.y, pos.z)
    -- 若原实体是"已栽种植物(deployedplant)"，重跑 ondeploy 让它重新落地
    if ent.components.deployable and ent:HasTag("deployedplant")
        and not ent:HasTag("ban_deployedplant") then
        local max_try_num = 1000
        while max_try_num > 0 do
            max_try_num = max_try_num - 1
            local new = ent.components.stackable and ent.components.stackable:Get(1)
            if new and new:IsValid() then
                new.Transform:SetPosition(pos.x, pos.y, pos.z)
                if new.components.deployable.ondeploy ~= nil then
                    new.components.deployable.ondeploy(new, pos, doer, rot or 0)
                end
            elseif ent and ent:IsValid() then
                if ent.components.deployable.ondeploy ~= nil then
                    ent.components.deployable.ondeploy(ent, pos, doer, rot or 0)
                end
                break
            else
                break
            end
        end
    end
    self.inst:Remove()
end

-- 让存档记录随打包物一起落盘：退出重进不丢
function MyPackWrapper:OnSave()
    if self.data then return { data = self.data } end
end
function MyPackWrapper:OnLoad(data)
    if data and data.data then self.data = data.data end
end
```

打包物 prefab 侧：
- 加 `deployable`，`SetDeployMode(DEPLOYMODE.CUSTOM)`，`ondeploy = OnDeploy`，`OnDeploy` 里调 `ReleaseData` → 玩家点地面使用即释放。
- 加 `named` 组件用于改名。
- 打上 `ban_mypack`（以及所需互斥）标签，确保它本身不能再被同类打包，防止无限嵌套。

## 触发接线

actions + 交互监听：当玩家对一个目标使用打包工具时，先 `invobject.components.my_pack:CanPack(target, doer)` 通过才 `Pack(target, doer)`。

## 要点

- **打包任意实体靠存档记录**，不是往容器塞物品，因此生物/建筑/植物也能"装走"。
- **可落盘的关键**：打包物的 `OnSave/OnLoad` 必须把 `data` 一起持久化，否则退出重进后打包物成空壳。
- **防嵌套**：打包物自带 `ban_xxx` 标签 + 工具侧的 `CanPack` 黑名单。
- **已栽种植物释放**：重建后若原是 `deployedplant`，需重跑 `ondeploy` 才能正确落点。
- `GetSaveRecord` 无法入档的实体返回空，需判空。

## 官方源码

- `entityscript.lua`：`GetSaveRecord`、`GetDisplayName`。
- `mainfunctions.lua`：`SpawnSaveRecord`。
- `components/deployable.lua`：`DEPLOYMODE.CUSTOM` 与 `ondeploy`。

---

## 相关枢纽

- [能力索引](../../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。