# 模组入口 API 与调用边界

这是一份入口选择与签名参考，不承诺覆盖全部 API。环境版 modutil 包装、底层全局函数和组件实例方法分别核对，不能只看同名符号。

## 入口与注册对象

| API | 回调/参数合同 |
|---|---|
| AddPrefabPostInit(prefabname, fn) | 实体实例 fn(inst)，不表示已激活本地玩家/HUD |
| AddPlayerPostInit(fn) | 玩家构造扩展；不是所有角色都叫 player Prefab |
| AddComponentPostInit(name, fn) | fn(component, inst)，不会替实体添加组件 |
| AddClassPostConstruct(package, fn) | 类构造完成后的 self 与原构造参数，影响未来实例 |
| AddBrainPostInit(name, fn) | OnStart 建树后执行，重启可能再执行 |
| AddStategraphPostInit(name, fn) | 共享 SG 定义表，不是某实体 inst.sg |
| AddStategraphState/ActionHandler | 使用 StateGraph 内部名称，玩家通常 wilson/wilson_client |
| AddReplicableComponent(name) | 注册 components/name_replica.lua 的复制接口；不自动同步普通字段 |
| GetModConfigData(optionname, get_local_config) | 第二参是强制本地配置，缺省值由调用者显式处理 nil |

AddSimPostInit/AddGamePostInit 等阶段回调按目标版本实际调用者确认，不能从旧参数名推导所有场景一定有玩家。modmain 顶层不假设世界已建立；组件/HUD 的依赖在对应构造完成后连接。

## 配方、料理与角色

- AddRecipe2(name, ingredients, tech, config, filters)：配置字段在 config，过滤器按名称加入；菜单分类不替代权限。不要把旧 Recipe 的长位置参数复制进来。
- AddCookerRecipe(cooker, recipe)：环境包装已标记 Mod food，产品 Prefab 仍需单独注册。
- AddIngredientValues(names, tags, cancook, candry)：会替换相应食材标签，改已有食材前核对影响。
- AddModCharacter(name, gender, modes)：性别为语法/代词类别；角色资源、玩家工厂与存档包装另按角色专题。
- AddAction/AddComponentAction/AddStategraphActionHandler：分别登记语义、候选发现与 SG 执行入口；不直接写 ACTIONS 替代模组注册流程。

配方、动作等新 API 在普通 require 模块中不一定可见；由入口注册，或显式将环境函数传入模块。不向模块猜传 modname，也不污染全局为每个模块制造“当前 Mod”。

## 网络句柄与值

RPC 注册与发送按方向对应：服务端接收用 AddModRPCHandler/GetModRPC；客户端接收用 AddClientModRPCHandler/GetClientModRPC；分片用 Shard 对应接口。不要用服务端句柄发送客户端 RPC。当前请求者、距离、物品归属、资源和冷却由服务端业务再次校验。

普通 Prefab 公共构造区的 netvar 例子：

```lua
-- inst 已有 Network，尚未 SetPristine。
inst._my_mod_value = net_float(inst.GUID, "my_mod.value", "my_mod_value_dirty")
-- 权威 setter 中写入：inst._my_mod_value:set(value)
-- 客户端读取：inst._my_mod_value:value()
```

这是实体直接 netvar 的示意；Replica/classified 有自己的复制构造时机，不机械套同一位置。netvar 第三参是 dirty 事件名，不是回调函数；不通过虚构的 Network:SetXxx/GetXxx 或通用 GetReplica 来同步自定义组件。

## 世界生成与地皮

AddRoom/AddTask/AddTaskSet 等是模组环境包装，底层 AddMod* 可能额外要求 modname。修改内置对象用限定 ID 的 PreInit；AddTaskSet 不是向默认集自动合并。

AddTile(tile_name, tile_range, tile_data, ground_tile_def, minimap_tile_def, turf_def) 自动管理 TileManager 保护；调用者不改保护开关。使用注册范围名和 WORLD_TILES 大写名称。当前运行也先加载 modworldgenmain，地皮可集中于此并防重入，不能在 modmain 再无条件登记。

## 最小组织与环境

```text
my_mod/
  modinfo.lua
  modmain.lua
  modworldgenmain.lua         # 有生成需求时
  scripts/
    prefabs/ components/ brains/ stategraphs/ widgets/
    my_mod/                  # 私有 require 模块/注册文件
  anim/ images/ sound/        # 按实际资源需求
```

modmain 使用 local G = GLOBAL；普通 require 模块按其真实 loader 使用游戏全局。不要以 local GLOBAL = _G 把入口私有 env 误当完整全局。原版存在 GLOBAL 引用不代表所有字段可在前端/生成阶段使用。

## 来源与进一步读取

本轮直接核对 modutil.lua 的生成、配置、AddTile、Component/Brain/Replica 包装与 entityscript/entityreplica；其他 API 使用前仍读当前定义和调用者。[快照表](../../dst-source-research/references/source-research.md#2026-10-17-知识内容复核)。

- [环境](../../dst-lua-runtime/references/module-environments.md)。
- [组件契约](../../dst-component-authoring/references/component-contract.md)。
- [联机契约](../../dst-networking-rpc/references/network-contract.md)。
- [世界生成](../../../gameplay/dst-worldgen-authoring/GUIDE.md)。
- [来源线索](../../../engineering/dst-mod-engineering/core-lua-hooks.md)。

示意代码不包含资源或完整玩法，静态解析不能证明注册顺序、复制或游戏行为。
