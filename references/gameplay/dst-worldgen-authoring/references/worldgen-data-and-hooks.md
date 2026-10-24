# 世界生成数据与注册接口

## 环境接口与底层函数

Mod 入口使用 modutil 注入的 AddRoom、AddTask、AddTaskSet、AddLevel、AddLocation、AddStartLocation，底层 AddMod* 负责额外的 modname/登记上下文。先核对实际函数签名，不能把两者以斜线列成可直接互换的调用。

修改已有对象使用限定 ID 的 PreInit；新增保持命名唯一。Layouts 通过 map/layouts 返回表登记，再由实际 room/taskset 消费；StaticLayout.Get 使用可 require 的 Lua 表。

## 数据最小合同

| 对象 | 核心内容 | 易误解处 |
|---|---|---|
| Room | value、colour、tags、contents | contents 是生成数据，不是实体组件 |
| Task | locks、keys_given、room_choices、room_bg、background_room | room_choices 是各房间数量/函数，不是泛指抽样权重 |
| TaskSet | tasks、optionaltasks、numoptionaltasks、valid_start_tasks、set_pieces | 新建独立 TaskSet 不自动被预设选中 |
| Layout | type、scale、layout、ground、ground_types、放置约束 | 地面矩阵保存的是映射索引，非直接 tile ID |
| Level/预设 | task_set、overrides、出生与世界设置 | 生成选项与运行时世界设置不是同一阶段 |

Lua 动态字符串键使用 { ["RoomName"] = 2 }，不能写 { "RoomName" = 2 }。文档中的省略项只作字段说明，不能直接当可解析模板。

## 内容数量与密度

countprefabs 的数字或函数按每个生成节点处理，函数可接收 area、prefab、scratchpad。过滤、多个同名房间与空间不足会影响总数。distributeprefabs 是候选权重，distributepercent 控制密度；不要把目标总数填到权重里。

overrides 的合法键与值来自当前生成配置和相应消费者。针对 prefab 的 count 扩展是否适用，沿 forest_map 的转换表确认；不能任意给所有键套 {count="rare"}。

required_prefabs、setpiece 数量与 min_dist_from_land 是约束/计划，不是生成成功证据。需要日志、多种 seed 与最终存档的数量和可达性检查。

## 进一步读取

- [层级与锁钥](worldgen-graph.md)：Location → Level → TaskSet → Task → Room。
- [地皮](worldgen-tile-terrain.md)：环境 AddTile、资源、ID 与运行时地形。
- [Hook、Scenario 与布局](worldgen-scenarios-hooks.md)：可用接入与持久化责任。
- [世界与空间来源](../../../engineering/dst-mod-engineering/worldgen-spatial.md)。
- 本轮复核 modutil.lua:238-305、map/graphnode.lua:340-403 和 static_layout.lua:27-65；[源码快照](../../../core/dst-source-research/references/source-research.md#2026-10-17-知识内容复核)。

这里不提供未经运行的“完整世界模板”承诺；新增世界还要验证锁钥可达、出生点、关键内容、地形与客户端表现。
