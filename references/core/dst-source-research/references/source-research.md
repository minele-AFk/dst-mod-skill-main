# 源码研究方法

源码路径、第三方访问和版本标注沿用 [共用约定](../../../development-contract.md)。`scan-dst-source.ps1` 接受 `-Root` 或 `DST_SCRIPTS_DIR`，未指定时使用本工作区的 `D:\mods\scripts` 快照；该快照不保证最新。

## 选择入口

| 问题 | 首选入口 |
| --- | --- |
| 模组钩子或注册 API | modutil.lua、mods.lua |
| 实体构造 | prefabs/、prefabutil.lua、standardcomponents.lua |
| 玩法状态 | components/、entityscript.lua |
| 自定义动作 | actions.lua、componentactions.lua、bufferedaction.lua |
| AI | brain.lua、behaviourtree.lua、brains/、behaviours/ |
| 动画状态 | stategraph.lua、stategraphs/ |
| 联机 | netvars.lua、networkclientrpc.lua、entityreplica.lua |
| 世界生成 | worldgen_main.lua、map/ |
| UI | widgets/、screens/、frontend.lua、input.lua |

## 搜索顺序

1. 先按文件名定位同类原版对象。
2. 搜索公开符号定义。
3. 搜索该符号的所有调用点。
4. 追踪 require、Class、Prefab 和回调注册。
5. 搜索相关组件名、标签、事件名和 SG 状态名。
6. 比较至少一个最接近的完整实现。
7. 将结论分为源码明示、多个调用点推断和未知。

示例：

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/scan-dst-source.ps1 -Root "D:\mods\scripts" -Mode Summary
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/scan-dst-source.ps1 -Root "D:\mods\scripts" -Mode Symbol -Pattern AddBrainPostInit
    rg -n SetPristine <source-root>/prefabs -g *.lua

## 引擎原生边界

Entity:AddTransform、AnimState、Physics、TheSim 等接口可能由引擎绑定。找不到 Lua 定义时：

1. 搜索所有调用点。
2. 按接收对象类型分组。
3. 比较参数数量、nil 用法和调用前置条件。
4. 检查 SetPristine 前后以及主机、客户端上下文。
5. 检查返回值如何被使用。
6. 将契约标为调用点推断，不声称掌握未公开实现。

## 报告格式

- 源码根目录和研究日期
- 用户问题与目标运行端
- 关键文件和行号
- 调用链
- 已验证事实
- 推断及其证据
- 风险和未解决项
- 推荐原版范例

## 2026-10-17 知识内容复核

本轮于北京时间 2026-10-17 至 18 日维护知识正文。直接证据来自本机安装版 data/databundles/scripts.zip，SHA256：

`f8d7cff2e9f86cdab3de08c6e750ecec2986c9bc95b364724f4c77244a798bf1`

这是本机快照，不保证线上最新版本，也没有据此推定 Steam Build。与手动维护的 D:/mods/scripts 分开记录；原有历史案例仍保留其自己的版本与证据等级。

| 已核实内容 | 安装包内源码入口 |
|---|---|
| 组件构造早于 inst.components 写入；PostInit 在其后 | entityscript.lua:610-645 |
| Replica 注册、主客机构造与有效接口 | entityreplica.lua:30-84；modutil.lua:852-855 |
| Class 属性 setter，非自动网络机制 | class.lua:36-44,83-106 |
| 环境配置第二参语义、生成 API 包装 | modutil.lua:238-305,329-332 |
| 运行也加载 worldgen 入口；前端可重入 | mods.lua:443-465,578-584 |
| 网络数值类型范围；配置过滤器签名 | netvars.lua:6-14；modutil.lua:674-680 |
| AddTile 六参、范围名、保护包装与大写 ID | modutil.lua:356-375；tilemanager.lua:128-159 |
| Brain 建树后 PostInit、条件与 RUNNING 状态 | brain.lua:206-225；behaviourtree.lua:319-375,768-788 |
| SG 事件继续传播、帧/秒与状态内存 | stategraph.lua:183-198,463-470,529-550 |
| 普通/特殊伤害、范围主目标排除 | components/combat.lua:568-657,1287-1314 |
| 投射物已结算攻击、乘数语义 | components/projectile.lua:225-251；damagetypebonus.lua:10 |
| 同名 Buff 延期、来源 modifier 和冷却 | debuffable.lua:95-149；debuff.lua；util/sourcemodifierlist.lua:64-120；rechargeable.lua:108-174（组件名均在 components 下） |
| 容器初始化、打开者数量与堆叠编码 | components/container.lua:86-96,728-736；stackable_replica.lua:24-35,98-115 |
| 料理最高 priority 与 weight、烹饪时间倍率 | cooking.lua:238-287；modutil.lua:636-646；components/stewer.lua:140-175 |
| growable 缺 time 与阶段/任务分离 | components/growable.lua:42-81,121-148,207-218 |
| CUSTOM 部署公共查询、finiteuses 修复 | components/deployable.lua:124-125；inventoryitem_replica.lua:348-349；forgerepair.lua:35-42 |
| 多来源制作的创建/消费/交付区别 | components/builder.lua:717-800 |
| Tiled require 与地皮索引、节点计数 | map/static_layout.lua:27-65；map/graphnode.lua:340-403 |
| Scenario 只保存 scriptname/hasrunonce | components/scenariorunner.lua:8-61 |
| Widget 时间、Kill、坐标和 Badge 参数 | widgets/widget.lua:1-44,325-346,534-558；badge.lua:127 |
| HUD 构造和 ghost/复活调用链 | screens/playerhud.lua:915-925；widgets/controls.lua:55-57；prefabs/player_classified.lua:815-819；player_common_extensions.lua:430 |
| 玩家工厂包装自定义保存回调 | prefabs/player_common.lua:2936-2950 |
| 动作落点、法术回调与持有关系 | bufferedaction.lua:90-101；components/aoespell.lua:11-67；spellbook.lua:97-104 |
| 相机实际方法与原版音乐播放器 | cameras/followcamera.lua:127-131,207-217,364-370；components/dynamicmusic.lua:817-829 |

审阅线索来自 [既有工程补充目录](../../../engineering/dst-mod-engineering/README.md)。本轮把相关精华提炼进原有专题，未新增第二份同主题流程；不把上游单案例建议升级成普遍事实，也不改写未运行测试。

原始定位、文件指纹和修改前备份存于工作区 .codex/validation/dst-skill-content-20261017；不要求其他机器具备这份任务证据目录。这里确认的是源码/文档合同，未启动游戏或编译新美术/音频。
## 2026-10-18 全库维护与接口纠错

v0.4.0 延续上轮融合，审阅范围为普通可查询文档及 Lua 模板；未读取受限 Mod 笔记或创意工坊代码。仍使用上节记录的本机安装包指纹，不把本地快照声明为线上最新。

| 本轮实际处理 | 源码/合同依据 |
|---|---|
| 32 份组件参考的声明与调用候选筛查；其中 193 个显式签名逐项记录 | 对应 scripts/components/*.lua；正文里的动态别名、私有 API 与原生绑定另辨上下文 |
| 潮湿、腐坏、部署、战斗、类型抗性、温度、睡眠、随从等纠错 | 对应组件本体、Replica、消费者与事件生产端 |
| 武器范围修正、电击湿度附加系数、投射物生成与回调 | components/weapon.lua、components/combat.lua |
| TheInput 句柄清理、TheFrontEnd 屏幕栈、Screen 焦点 | input.lua、frontend.lua、widgets/screen.lua |
| netvar 初始刷新、房主表现、Replica 与持久化边界 | netvars.lua、entityreplica.lua、entityscript.lua、同类 Prefab |
| 私有案例依赖、服务器权限、交付/扣费/保存分离 | 原专题合同与 builder、inventory、player_common 等实际调用链 |
| FX/shader 原生边界、userdata 包装、stategraph 声明 | VFX 原版调用点、debugsounds.lua、stategraph.lua |
| 模板与旧代码块 | 可解析 Lua 和非独立片段分别标注；可解析不等于资源齐全或运行已验收 |

未维护的普通文档执行结构、链接和候选 API 筛查，不声称逐句证明全部内容。对应范围与最终哈希见 [维护记录](../../../knowledge/review-status.json)；正文后续变化会使记录失效。source_signatures 仅标识组件声明复核，content_curated 标识本轮及前轮实际修订，不是新的证据等级。

备份、候选清单、源码指纹、片段分类及修改清单保存在工作区 `.codex/validation/dst-skill-complete-20261018`。历史结构化包继续保留原数据与证据等级，未运行的游戏测试仍未运行。后续任务须按目标版本确认适用性，并独立完成主客机、存档、画面/声音等实际验收。

## 2026-10-18 v0.4.1 检索导航修复

v0.4.1 延续 0.4.0 的正文与源码结论，只修复知识调用链：

- `knowledge docs` 保持原相关度排序，另以顶层 `primary_topic_candidates` 返回被 `--limit` 截掉的主专题；候选不带新的证据等级。
- `knowledge topics` 复用中英文导航别名，并检索主专题及支持页的标题、描述、路径和正文；默认按相关度返回前 10 条，`--limit` 为 0–50。
- 三个工具补充页补入导航归属；`check_skill --strict` 要求所有普通工程细节页可路由，冻结包与维护说明除外。
- `run.ps1 test_knowledge_service` 统一执行 24 项结构化服务回归；`test_service.py` 也可直接运行。

这轮没有重新核验 0.4.0 的全部源码声明，没有提升历史证据等级，也没有启动游戏或完成联机、画面、声音验收。验证范围为知识检索、路由、维护入口、冻结包完整性和静态检查。

## 2026-10-23 游戏更新与知识迁移

本轮以本机安装版本 `759671`、Steam Build `26148036` 为基线。`D:\mods\scripts` 的 4,084 个 Lua 文件与安装包 `scripts.zip` 全量逐文件哈希一致；`scripts.zip` SHA-256 为 `03d745ab0aa78455b38240998c99d14f81e88e68b95320f31de79705f6ae5008`。这与上一轮记录的 `f8d7cff...` 不同，说明本机安装源码已变化；不据此推断线上版本或所有源码变更。

| 已核实契约 | 当前源码锚点 |
|---|---|
| 普通 `DoAttack`、范围攻击和投射物命中直接调用 `GetAttacked_Internal(...,true)`；公开 `GetAttacked` 只转发 | `components/combat.lua:570-730,1212-1235,1320-1333` |
| 受击、格挡、命中、击杀事件含 `from_doattack`；tough 受击只由标签或武器接口放行 | `components/combat.lua:669-730,1252-1270`；`components/weapon.lua:159-165` |
| 投射物偏转只回调并按字段决定是否移除；反弹要另行生成攻击 | `components/projectile.lua:532-541`；`components/complexprojectile.lua:213-220` |
| 物品温度是 inventoryitem 扩展；睡眠补算，启用时机关键 | `components/inventoryitemtemperature.lua:1-220`；`components/inventoryitem.lua:190-280` |
| 局部温度查询依次检查温度覆盖器、喷气孔 Replica 和世界状态 | `components/temperatureoverrider.lua:14-37` |
| 瞬移许可包含竞技场屏障与虚拟房间跨区规则 | `componentutil.lua:1390-1408`；`components/blinkstaff.lua:62-96` |
| 虚拟房间集合仅主机存在，需边界声明与版本化布局 | `prefabs/world.lua:596-600`；`components/virtualroomset.lua:16-105,1209-1245` |
| `rechargeable` 的充能时间 modifier 是加性比例增量；未满时保存基础时长与当前值 | `components/rechargeable.lua:60-166` |
| 即时事件同步调用 SG `HandleEvent`，普通事件受 SG 队列条件约束 | `entityscript.lua:1290-1326` |
| `spellcaster` 目标、点、库存入口与 spelltype 两端 tag 协议 | `components/spellcaster.lua:1-180`；`componentactions.lua:1774-1800,2186-2215,2460-2486,2941-2958` |
| `useabletargeteditem` 的成功/失败、停止、目标 tag 与原版替换物品例子 | `components/useabletargeteditem.lua`；`actions.lua:3317-3365`；`prefabs/security_pulse_cage.lua:128-208` |
| `deflectable` 只回调并按字段决定移除，不自动反伤或生成反弹 | `components/deflectable.lua` |
| 影子 NPC 观察组件的名称分工与 Brain 的候选、距离、去重条件 | `components/stalkerinspectable.lua`；`brains/stalkerbrain.lua:348-411` |
| 被吞状态为 `net_bool`；循环声与 DSP override 在本地客户端执行 | `prefabs/player_classified.lua:1088-1104,1649-1651`；`components/playerhearing.lua:1-100` |
| 地图可见、点到点传送、连接点和集合放置许可是不同函数 | `componentutil.lua:1390-1453`；`simutil.lua:904-923`；`maputil.lua:432-551`；`components/virtualroomteleporter.lua:39-43` |
| 世界状态标签使用 namespace、位域编码、分片同步和 1024 字符服务器标签预算 | `mainfunctions.lua:2238-2453` |
| 远程判定可从 attacker 识别；未防御位面回调要求 `spdamage.planar` | `components/combat.lua:424-430,593,626,1037-1067` |
| 地图目标不归还自身激活物品；TOSS_MAP 装饰读取 `rmb.invobject` | `components/playercontroller.lua:444-460`；`screens/mapscreen.lua:894-908` |
| `old_skin` / `young_skin` 形态覆盖优先于按角色覆盖；皮肤版本改为 `.VERSION` | `components/skinner.lua:113-230`；`versioning_skins.lua`；`versioning.lua:73-75` |
| `haunted` 事件仅在成功回调后推送；失败与 itemmimic 分支另走收尾 | `components/hauntable.lua:82-115` |
| `corruption` 与 King Cane 阈值强绑定，只借鉴通用状态与目标生命周期 | `components/corruption.lua:1-199` |
| 猎犬下一波事件支持时间倍率和选择更短现有计时 | `components/hounded.lua:162-204,696-722` |
| 发射前停用物品优先 mine，其次 Prefab 回调，并返回是否处理 | `componentutil.lua:2370-2378` |
| 虚拟房间批量改地皮会合并即时物理碰撞重建，结束后恢复原设置 | `components/virtualroomset.lua:446-474` |
| 内置小地图图集依次查找 `data1`、`data2`、`data3`，Mod 图集另经 `AddMinimapAtlas` 加入渲染器 | `simutil.lua:707-730`；`prefabs/minimap.lua:44-51` |
| 皮肤外观可分布在父实体、子实体与特效层，必须按同一组 build/symbol 覆盖并恢复 | `prefabskin.lua:1704-1742` |
| 延迟瞬移中的 `DoGemShine` 在最终可通行/许可/Teleport 检查之前调用，不能作为成功通知 | `components/blinkstaff.lua:36-60` |
| `RunAwayFromQueenTorch` 接收实体；原版调用传 `self.inst` | `brains/braincommon.lua:663-674` |
| 剪贴簿自动发现当前只排除 `INLIMBO`；无数据/角色掩码时安全 no-op | `prefabs/player_common_extensions.lua:1127-1141`；`scrapbookpartitions.lua:162-181,262-285` |
| 可拾取火属性物品允许 `lighter` 或 `torch`，菜单与控制器有同类条件 | `components/playercontroller.lua:2032-2038`；`componentactions.lua:470-479` |
| 特殊伤害可累加到已有来源表；只有合并结果含 `planar` 才按位面触发 | `components/spdamageutil.lua:52-60`；`prefabs/slingshotammo_debuffs.lua:140-170` |
| 火把由 Prefab 偏转回调重建反弹弹道，组件负责保留还是移除投射物 | `prefabs/torch.lua:325-342,479-487`；`components/complexprojectile.lua:213-220` |
| 传送结束音效优先级是 `skin_castsound`、`castsound`、默认；`notlightningteleport` 进入 `idle` | `prefabs/staff_common.lua:306-329` |
| FX 可同步拥有物品的皮肤 build 哈希，再由客户端按部件 build 调用 `SetSkin` 或默认 `SetBuild` | `prefabs/armor_voidcloth.lua:218-276`；`prefabs/hats.lua` |
| 临时效果替换 Brain 前检查 `owner.isplayer`，不得无条件覆盖玩家 Brain | `prefabs/hats.lua:5676-5679` |
| 长期定身/控制效果监听逃脱、传送、死亡、移除，以及飞行/隐形状态退出 | `prefabs/wormwood_vined_debuff.lua:25-30`；`prefabs/shadow_pillar.lua:190-210,490-500` |
| 角色只缩放暗影物品的负面精神收益；先取最终 `GetDapperness` 再判断 `<0` | `prefabs/wanda.lua:201-213`；`prefabs/waxwell.lua:179-184` |
| 最近传送台在距离筛选前先检查点对点传送许可 | `prefabs/telebase.lua:84-110` |
| 陆地暗影生物生成使用 `FindWalkableOffset`，找不到合法落点时安全退出 | `components/shadowcreaturespawner.lua:132-140` |
| 腐化目标协议成对推送 chess struggle；Fissure 仅成功后进入冷却 | `components/corruption.lua:84-180` |
| 死亡记录优先读取 `death.afflicter`，以 `isplayer` 验身份；`killed` 使用另一套字段 | `components/health.lua:565-610`；`components/combat.lua:669-686`；`prefabs/alterguardian_phase3.lua:328-334`；`prefabs/stalker.lua:1078-1084` |
| 蜂蜜轨迹服务器权威减速和客户端预测使用不同的排除标签表 | `prefabs/honey_trail.lua:1-29,52-60,132-141` |
| 飞行状态成对维护飞行物理、`notraptrigger` 与地面速度倍率，并覆盖离开路径 | `stategraphs/SGbuzzard.lua:104-115,583-584,624-630,700-705,723-724` |
| 最近地图图标在距离比较前按玩家权限和 VRS 可见性筛掉候选 | `simutil.lua:896-940`；`componentutil.lua:1410-1434`；`prefabs/globalmapicon.lua:198-209,282-341` |
| 剪贴簿类型、依赖补删、代理和发现即检查均为图鉴元数据契约 | `debugcommands.lua:2372-2392,2521-2567,3411-3566`；`scrapbookpartitions.lua:139-145`；`prefabs/player_common_extensions.lua:1127-1141` |

比较区间 `9b021ff..0f51222` 共有 178 个文件变化，通用层实际变化集中在 `actions.lua`、`componentactions.lua`、`componentutil.lua`、`maputil.lua`、`simutil.lua`、虚拟房间、战斗与皮肤相关文件。`entityscript.lua`、`components/projectile.lua`、`components/rechargeable.lua`、`components/map.lua`、`mods.lua` 和 `prefabs/player_common.lua` 在该区间没有实际差异；上表中的这些条目是对当前版本的契约复核，不应误报为本次版本差异。新增组件、Prefab 和官方中文名只作为当前版本契约。详细文件哈希和旧版缓存差异位于工作区 `.codex/validation/dst-source-update-20261023`。

第二轮遗漏复查后，还补写了施法目标/库存协议、定向物品、偏转实体、影子 NPC 观察、DSP 本地表现、地图/传送资格分层、世界状态标签、远程与点燃动作边界、皮肤形态优先级、附身/腐化状态、猎犬重排和发射前停用。验证仍仅限源码、文档、链接与知识检索；没有启动游戏，也没有验证多人、存档、战斗、传送、世界轮换、动作菜单或声音表现。

第三轮遗漏复查补充了延迟瞬移表现回调、Brain 共享节点参数、剪贴簿 FX 发现、火属性拾取、特殊伤害合并、火把反弹、传送音效/状态、多部件皮肤哈希同步、玩家 Brain 保护、定身控制退出、暗影精神收益、最近传送台筛选、酸雨伤害覆写、安全生成落点、腐化目标协议和冷却成功门控。

其中 `components/acidlevel.lua` 的酸雨覆写接口在当前安装版本中已核对，但在 `9b021ff..0f51222` 区间没有实际差异，属于当前契约复核，不计入本次源码变更。当前源码还明确取消了红、蓝法杖攻击回调里的 `Discharge` 调用；不能把这一局部实现扩张成“所有法杖攻击都不再冷却”。`VAULT_KEY_FOUND` 的世界状态写入、瞬时状态语义和 HUD 不应持久化这一结论已复核，没有新增差异需要重复扩写。

第四轮遗漏复查补充了死亡击杀归属、蜂蜜轨迹双端排除标签、飞行状态成对物理清理、最近地图图标的 VRS 可见性筛选，以及剪贴簿元数据语义。剪贴簿这些字段在 `9b021ff` 已存在，只补当前契约文档，不算本次新增 API。地图图标筛选和飞行 helper 等结论仍只经过源码静态核对；尚未运行多人主客机、存档、传送、战斗和真实 UI。
