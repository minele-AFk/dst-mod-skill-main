# 容器注册与 Replica 同步

本页说明模组容器从 `containers.params` 注册到客户端 UI 初始化的边界。签名和生命周期按当前安装版 `containers.lua`、`container_replica.lua`、`container_classified.lua` 核对；游戏更新后重新查源码。

## 1. 注册参数

```lua
-- modmain.lua
local containers = require("containers")

containers.params.mymod_chest =
{
    widget =
    {
        slotpos = {
            Vector3(-75, 75, 0),
            Vector3(0, 75, 0),
            Vector3(-75, 0, 0),
            Vector3(0, 0, 0),
            Vector3(-75, -75, 0),
            Vector3(0, -75, 0),
        },
        animbank = "ui_chest_3x3",
        animbuild = "ui_chest_3x3",
        pos = Vector3(0, 200, 0),
    },
    issidewidget = false,
    type = "chest",
    openlimit = 1,
}

containers.MAXITEMSLOTS = math.max(
    containers.MAXITEMSLOTS,
    #containers.params.mymod_chest.widget.slotpos
)
```

`containers.MAXITEMSLOTS` 不是动态 getter。当前 `containers.lua` 在模块末尾遍历一次 `params` 计算最大值；之后新增或扩大的配置不会自动刷新它。`container_classified.lua` 会按该值创建槽位数据，所以槽位较多的模组容器应在注册后手动提高上限。

`widget.numslots` 优先于 `slotpos` 数量。若两者同时存在，确认它们描述同一个 UI；不要只改 `slotpos` 却留下旧的 `numslots`。

## 2. Prefab 名与配置键

服务端可以显式绑定配置：

```lua
-- prefab 主机分支
inst:AddComponent("container")
inst.components.container:WidgetSetup("mymod_chest")
```

Replica 在客户端构造时先执行 `containers.widgetsetup(self)`，默认使用实体 Prefab 名查配置。如果 Prefab 名和 `containers.params` 的键不同，客户端会找不到参数，表现为槽位、图标或布局缺失。

两种修复方式：

```lua
-- 客户端 Prefab 分支：复制完成后补设
inst.OnEntityReplicated = function(inst)
    if inst.replica.container ~= nil then
        inst.replica.container:WidgetSetup("mymod_chest")
    end
end
```

也可在客户端容器初始化后显式调用 `replica.container:WidgetSetup("mymod_chest")`。不要假设服务端的 `WidgetSetup` 会自动把配置键同步给客户端；服务端调用会初始化自己的 classified 槽位，但客户端仍需要可解析的配置。

## 3. `itemtestfn` 的执行端

`itemtestfn` 不是纯服务器过滤器。当前 `container_replica.lua` 的 `CanTakeItemInSlot` 会在客户端读取 `item.replica.inventoryitem`、`stackable` 等 Replica 数据后调用它；服务端 `container.lua` 也会做最终校验。因此：

- 只读取客户端也存在的 Replica 字段、Prefab 名、标签或纯常量。
- 不要读取 `item.components`、服务器专属组件状态或未复制的私有字段。
- 返回 `false` 只表示该槽不接受；资源扣除、归属转移和最终成功仍由服务端确认。
- 过滤规则变化时同时测试主机、远端客户端、满容器、堆叠合并和拖拽预览。

## 4. 客户端初始化顺序

推荐按以下顺序排查：

1. `modmain.lua` 注册 `containers.params`，并在需要时提高 `MAXITEMSLOTS`。
2. 服务端 Prefab 添加 `container` 后调用 `WidgetSetup`。
3. 客户端 Replica 构造时能按 Prefab 名或显式键找到同一份参数。
4. `container_classified` 能创建所需槽位；Replica 的槽位数与服务器一致。
5. `OnEntityReplicated` 只在 Replica 已存在时补设，不重复创建容器或覆盖其他模组配置。

当前 `container_replica.lua` 的构造函数在非主机端调用 `containers.widgetsetup(self)`；如果实体尚未带 `container_classified` 或 opener，后续复制事件再附着。补设逻辑必须允许这些依赖稍后到达。

## 5. 验证清单

- 新容器在主机和远端客户端显示相同槽位数、位置和背景。
- Prefab 名与配置键不同的容器，在首次加入、重连和换分片后仍能打开。
- 超过原版常见槽位数的容器没有缺槽、错位或 classified 初始化异常。
- `itemtestfn` 在客户端不访问服务器组件，非法物品被服务器最终拒绝。
- 保存重载后容器物品、槽位过滤和 opener 状态一致。

本页于 2026-10-22 对照安装版 `containers.lua:5-16,2498-2499`、`container_replica.lua:47,232-233,340-379`、`container_classified.lua:1057`；未执行真实多容器 UI 或联机测试。
