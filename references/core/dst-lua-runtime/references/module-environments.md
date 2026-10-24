# Lua 加载环境与配置

文件所在目录不能决定可见全局；先确认是谁、用哪个 loader、在哪个阶段执行。

| 入口 | 加载合同 | 实现选择 |
|---|---|---|
| modmain / modworldgenmain | mods 创建模组环境，modutil 注入对应阶段 API | 入口 API 直接用；游戏全局通过 GLOBAL 明确引用 |
| modimport(path) | 在当前模组环境执行脚本，每次调用都会执行 | 适合注册文件；不是 require 缓存模块 |
| 通常的 require(name) | loader 执行并按模块名缓存返回值 | 返回表/函数，使用私有命名空间，防止不同 Mod 共用缓存键 |
| PrefabFiles 模块 | LoadPrefabFile 收集 chunk 的多个返回值 | 一个文件可返回多个 Prefab；不要假设拥有 modmain 私有变量 |
| modinfo | 独立的元信息环境 | 不访问世界、玩家或玩法组件 |

modmain 可以 require 普通模块；原有“只允许 require Prefab”的限制错误。普通模块不自动获得 modmain 的 modname、配置值或注册函数；需要时以参数传入，避免为了跨模块传值污染全局。

## 初始化阶段

modmain 顶层适合注册回调，不适合立即访问尚未创建的 TheWorld.components。顶层捕获当时为 nil 的 TheWorld/ThePlayer，后续不会自动更新这个局部变量。服务端的 ThePlayer 不能作为请求者或施法者；从回调参数获得对应玩家。

模组环境版 GetModConfigData(optionname, get_local_config) 第二参表示强制本地配置，不是默认值。缺省处理显式比较 nil，保留 false 和 0。普通模块优先接收入口读取的配置；不猜全局三参数版本所需的 modname。

裸名 pcall 不可见不能推导“游戏禁用了 pcall”。先核对实际环境；保护调用用于可恢复边界，不能吞掉错误后谎报操作成功。require 可返回接口也可执行注册副作用，先读被加载模块。

## 复核

来源提炼自 [环境与 Hook 参考](../../../engineering/dst-mod-engineering/core-lua-hooks.md)；本轮对照 modutil 的配置包装与注册接口。其他 loader 细节按 [源码研究](../../dst-source-research/references/source-research.md) 查 mods.lua、main.lua、mainfunctions.lua。验证显式 false、重复 modimport、缓存模块与世界创建前后，保留版本边界。

## 运行端、全局对象与安装模型

安装标志决定谁需要安装 Mod，执行入口决定加载阶段，运行端决定谁能修改当前玩法状态。安装类型与入口表见 [入口与标志](../../dst-mod-scaffolding/references/entrypoints.md)。

| 对象或检查 | 含义与使用边界 |
|---|---|
| TheWorld.ismastersim | 当前世界的权威模拟；组件、库存、伤害和保存写入按实际业务入口检查 |
| TheNet:IsDedicated() | 无本地玩家 UI 的专服进程；不等于玩法权威检查 |
| TheNet:GetIsServer() | 网络进程角色；不能替代实体的主模拟判断 |
| ThePlayer | 本地玩家，专服或尚未创建玩家时可为 nil；业务执行者用 doer/owner/giver/attacker 参数 |
| TheFrontEnd / TheInput | 本地屏幕与输入；检查实际可用性，房主也会运行本地显示路径 |
| TheWorld.state / TheWorld.Map | 当前分片的世界状态、地图与放置查询；前端/worldgen 另查对应环境 |
| TheSim / TheShard | 引擎和分片接口；按已核实的方法调用，不改成临时存储表 |

监听服务器同时运行主模拟与本地显示。联网 Prefab 的公共实体、网络字段与必要标签按原版在 SetPristine 前建立；服务端组件放主模拟分支。纯本地表现可另用 not TheNet:IsDedicated()，该分支仍须允许 ThePlayer/HUD 尚未就绪。不能用 not ismastersim 排除房主的 UI。

引擎管理的 GLOBAL、TheSim、TheNet、TheShard、TheInput、TheFrontEnd、TheMixer、TheCamera、TheFocalPoint、TheWorld、ThePlayer、AllPlayers 不重新绑定。TUNING、STRINGS、ACTIONS、CUSTOM_RECIPETABS、MOD_RPC/CLIENT_MOD_RPC/SHARD_MOD_RPC 只扩展所需项；Action、Recipe 和 RPC 优先用对应注册 API，不替换整个表，也不把自定义 ID 填入核心 RPC 表。userdata 扩展另见 [专门合同](../../dst-hooking-compatibility/references/userdata-method-extension.md)。

高频函数按用途查：实体搜索 FindEntity、FindPlayersInRange/FindPlayersInRangeSq/FindPlayersInRangeSortedByDistance、TheSim:FindEntities 见 [实体查询](../../../patterns/runtime/entity-query-patterns.md)；SpawnPrefab 与 GetValidRecipe 核对实际目标；GetTime 为游戏时间，Vector3、GetRandomMinMax、GetDistSq 按参数与坐标单位使用。HUD/屏幕见 [HUD 挂载](../../../world-ui-assets/dst-hud-screens-input/references/hud-customization.md)，热键见 [输入](../../../patterns/runtime/input-patterns.md)，跨存档本地配置见 [持久字符串](../../../patterns/persistence/persistent-string-patterns.md)。
