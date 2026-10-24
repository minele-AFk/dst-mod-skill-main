# 官方文件映射

使用本地 DST 安装作为真实来源。

## 本地路径

- Windows 常用游戏根目录：`C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Windows 常用脚本包：`C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip`
- Windows 常用创意工坊 mod 根目录：`C:\Program Files (x86)\Steam\steamapps\workshop\content\322330`
- Linux 常用游戏根目录：`~/.local/share/Steam/steamapps/common/Don't Starve Together`
- Linux 常用脚本包：`~/.local/share/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- Linux 常用创意工坊 mod 根目录：`~/.local/share/Steam/steamapps/workshop/content/322330`
- macOS 常用游戏根目录：`~/Library/Application Support/Steam/steamapps/common/Don't Starve Together`
- macOS 常用脚本包：`~/Library/Application Support/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`
- macOS 常用创意工坊 mod 根目录：`~/Library/Application Support/Steam/steamapps/workshop/content/322330`
- 版本文件：`version.txt`
- 官方 mod 说明：`mods\MAKING_MODS.txt`

当已知真实本地安装路径时，使用该路径。不要假设常用 Windows 路径在每台机器上都正确。

## PowerShell 路径引用

在 Windows 上，DST 路径通常包含 `Don't Starve Together`，其中包含撇号。不要生成简单的单引号 PowerShell 字面量，例如 `'D:\...\Don't Starve Together\...'`，因为它们在开始实际工作之前就会在解析时出错。这些引用规则专门适用于 PowerShell，包括在 Linux 或 macOS 上运行的 PowerShell。不要将它们视为通用的 `bash` 或 `zsh` 引用规则。

优先使用这些安全模式：

- 双引号字面量：
  - `"D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\mods\toolbox"`
- 撇号加倍的单引号字面量：
  - `'D:\Program Files (x86)\Steam\steamapps\common\Don''t Starve Together\mods\toolbox'`
- 变量加上 `-LiteralPath`：
  - `$modPath = "D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\mods\toolbox"`
  - `Get-Content -LiteralPath $modPath`

这也适用于数组。例如，优先使用 `$mods=@("D:\...\Don't Starve Together\mods\toolbox","D:\...\3383078008")`，而不是撇号未转义的单引号数组项。

如果活动 shell 不是 PowerShell，请切换到该 shell 自己的引用规则，而不是复制撇号加倍的单引号模式。

## PowerShell 正则表达式参数

在 PowerShell 中将正则表达式模式传递给 `references/tools/general/dst_zip_tool.py` 的 `grep` 子命令时，优先使用单引号参数：

```powershell
python "C:\Users\Kitsune\Projects\AgentSkill\dst-mod\scripts\dst_zip_tool.py" grep 'PushEvent\("equip"' --path-glob 'scripts/components/*.lua'
python "C:\Users\Kitsune\Projects\AgentSkill\dst-mod\scripts\dst_zip_tool.py" grep 'ListenForEvent\("equip"' --path-glob 'scripts/**/*.lua'
```

这些模式中的反斜杠是 Python 正则表达式转义，不是 PowerShell 转义。不要在 PowerShell 中编写 Bash 风格的转义双引号，例如 `"PushEvent(\"equip\""`。因为 `grep` 使用 Python 正则表达式，字面元字符必须转义；例如，使用 `\(` 表示字面左括号。

当崩溃跟踪指向 `../mods/workshop-<id>/...` 时，将该 id 视为指向创意工坊源目录的直接指针，并在猜测原因之前检查 `steamapps/workshop/content/322330/<id>`。

## 首先从工作区推断游戏根目录

如果当前工作区已经位于 DST 安装树的某处，在询问用户或扫描磁盘之前，直接从该路径推断游戏根目录。

示例：

- 工作区：`D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\mods\Huohuo`
- 推断的游戏根目录：`D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`

实用规则：

- 如果工作区路径包含 `Don't Starve Together\mods\...`，将祖先 `Don't Starve Together` 目录视为可能的游戏根目录
- 从该根目录，将脚本包派生为 `data\databundles\scripts.zip`
- 当工作区路径已经指向安装树时，不要递归扫描无关目录

## 创意工坊源路径优先级

当堆栈或 `modimport` 路径已经包含 `workshop-<id>` 时，将该 id 视为创意工坊源路径的最高优先级定位符。

实用规则：

- 将 `workshop-<id>` 直接映射到 `steamapps/workshop/content/322330/<id>`
- 在探测 `common/Don't Starve Together/mods/workshop-<id>` 之前检查该创意工坊源目录
- 除非用户明确要求下一步，否则不要将其变成更广泛的代码分析或 bug 修复任务
- 仅当创意工坊源目录本身缺失时才向用户询问另一个路径

## 检查游戏安装旁边的 Mod 工具

当游戏根目录已知时，还要在同级 Steam `common` 目录中探测 `Don't Starve Mod Tools`。

Windows 常用路径：

- `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Mod Tools`
- `D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Mod Tools`

图集工作流的高价值文件：

- `mod_tools\compiler_scripts\image_build.py`
- `mod_tools\tools\bin\TextureConverter.exe`
- `mod_tools\buildtools\windows\Python27\Lib\site-packages\klei\atlas.py`
- `mod_tools\buildtools\windows\Python27\Lib\site-packages\klei\textureconverter.py`

动画工作流的高价值文件：

- `mod_tools\scml.exe`
- `mod_tools\tools\scripts\buildanimation.py`
- `mod_tools\compiler_scripts\zipanim.py`
- `mod_tools\exported\export.py`

实用规则：

- 如果用户需要 PNG 到 `tex+xml` 打包，优先使用本地 Mod Tools 路径而不是临时编码器
- 如果用户需要 `.scml` 到 `anim/*.zip` 编译，优先使用本地 Mod Tools 的 `scml.exe` 和 `buildanimation.py`
- 如果 Mod Tools 未安装在通常的 Steam 位置，询问是否存在于其他位置
- 如果根本没有安装，推荐 Steam App ID `245850`
- 在 Windows 上，`start steam://install/245850` 打开 Steam 安装提示

## 短期 Zip 缓存

辅助脚本 `references/tools/general/dst_zip_tool.py` 可能对 `scripts.zip` 条目名称和最近读取的文本条目使用短期本地缓存。

实用规则：

- 缓存以绝对 zip 路径加上文件大小和 `mtime_ns` 作为键
- 如果游戏更新且 `scripts.zip` 更改，缓存命名空间会自动更改
- 缓存有意设计为短期，应视为请求上下文，而不是长期提取的副本
- 如果广泛的 `grep` 在 `.tmp\zip_cache` 下报告缓存错误，切换到 `show` 查看已知文件，或使用 `extract` 提取相关官方文件并使用 `rg` 在本地搜索

## 确认的 Mod 入口点

官方加载器代码确认这些根级入口文件：

- `modinfo.lua`
- `modmain.lua`
- `modworldgenmain.lua`
- `modservercreationmain.lua`

使用 `modinfo.lua` 存储元数据和配置选项。使用 `modmain.lua` 作为常规游戏端 mod 引导。仅在任务特定于这些阶段时使用世界生成或服务器创建入口文件。

## 高价值官方文件

- `scripts/modutil.lua`
  - Mod 环境辅助函数和大多数注册 API。
  - 从这里开始了解钩子，如预制件、组件、状态机、配方、RPC 和部件补丁。
- `scripts/mods.lua`
  - `modmain.lua`、`modworldgenmain.lua`、`PrefabFiles` 和 `Assets` 的加载器流程。
  - 当行为依赖于加载顺序或资源注册时很有用。
- `scripts/prefabutil.lua`
  - 辅助构造函数，如 `MakePlacer(...)`。
  - 当 mod 添加可放置结构或可部署预览逻辑时阅读此文件。
- `scripts/modindex.lua`
  - `modinfo.lua` 解析、API 版本检查、兼容性标志和配置选项处理。
  - 对验证元数据假设很有用。
- `scripts/networkclientrpc.lua`
  - Mod RPC 注册表、发送辅助函数和命名空间/ID 路由。
  - 当任务需要自定义 RPC 流程时阅读此文件。
- `scripts/brain.lua`
  - 基础大脑生命周期和行为树所有权。
  - 当 mod 添加或修补 NPC 大脑时阅读此文件。
- `scripts/entityscript.lua`
  - 标签、组件、任务、事件、缓冲动作、子实体、SG 和大脑分配的核心实例方法。
  - 当预制件方法或生命周期细节不明确时阅读。
- `scripts/entityreplica.lua`
  - Replica 组件设置和 `AddReplicableComponent` 行为。
  - 当自定义组件需要客户端可读的 replica 状态时阅读此文件。
- `scripts/standardcomponents.lua`
  - 可重用的辅助构造函数，如可燃、可冻结、物理、可作祟、可漂浮以及其他常见设置辅助函数。
  - 在手动编写低级设置之前阅读。
- `scripts/componentactions.lua`
  - 官方动作收集器定义和动作类型路由，如 `SCENE`、`USEITEM` 和 `POINT`。
  - 在发明自定义动作收集逻辑之前阅读此文件。
- `scripts/stategraph.lua`
  - 核心 SG 对象模型：`State`、`ActionHandler`、`EventHandler`、`TimeEvent` 和时间线行为。
  - 当 SG 对象形状或预测端字段不明确时阅读此文件。
- `scripts/stategraphs/commonstates.lua`
  - 运动、战斗、睡眠、冻结、受击和死亡状态族的可重用辅助构造函数。
  - 在手动编写整个通用状态族之前阅读此文件。
- `scripts/componentutil.lua`
  - 游戏中使用的共享组件端辅助函数和实用逻辑。
  - 当行为似乎依赖于实用包装器而不是单个组件方法时阅读。
- `scripts/components/`
  - 高频官方组件实现，如 `health.lua`、`hunger.lua`、`sanity.lua`、`combat.lua`、`equippable.lua`、`armor.lua`、`weapon.lua` 和 `container.lua`。
  - 当任务以属性、战斗、装备或存储为中心时首先阅读这些文件。
- `scripts/prefabs/`
  - 也是验证预制件标签的主要位置，如 `structure`、`backpack`、`NOCLICK`、`FX` 或 `hostile`。
- `scripts/mainfunctions.lua`
  - 预制件加载和资源解析细节。
  - 当资源路径或预制件注册行为异常时很有用。
- `scripts/input.lua`
  - 键盘、鼠标、移动、文本和映射控件的本地输入处理程序注册。
  - 当 mod 需要热键、鼠标钩子或本地输入拦截时阅读此文件。
- `scripts/frontend.lua`
  - 前端屏幕堆栈和前端声音访问，如 `PushScreen(...)`、`PopScreen(...)` 和 `GetSound()`。
  - 当任务依赖于本地屏幕流程而不是游戏权限时阅读此文件。
- `scripts/map/rooms.lua`
  - 核心房间注册和重复名称行为。
  - 当任务添加或修补房间定义时阅读此文件。
- `scripts/map/tasks.lua`
  - 核心任务注册和重复名称行为。
  - 当任务添加或修补任务定义时阅读此文件。
- `scripts/map/tasksets.lua`
  - 世界预设使用的任务集定义。
  - 当任务修改预设组合或任务集路由时阅读此文件。
- `scripts/map/startlocations.lua`
  - 起始位置定义和世界入口路由。
  - 当任务更改生成起点或自定义起始位置时阅读此文件。
- `scripts/map/customize.lua`
  - 世界自定义选项定义、类别以及 mod 添加的自定义组或项目。
  - 当任务添加或移除主机可见的世界设置或世界生成选项时阅读此文件。
- `scripts/map/levels.lua`
  - 预设列表、按 `LEVELCATEGORY` 查找预设，以及设置/世界生成预设组合。
  - 当任务依赖于预设 ID、预设描述或组合预设行为时阅读此文件。
- `scripts/constants.lua`
  - 整个代码库中使用的核心常量、枚举和标识符。
- `scripts/tuning.lua`
  - 调优值和平衡常量。
  - 首先在这里阅读平衡更改。
- `scripts/strings.lua`
  - 核心 `STRINGS` 树和命名模式。
  - 当 mod 添加或路由运行时文本时阅读此文件。
- `scripts/consolecommands.lua`
  - 高价值调试控制台辅助函数，如 `c_spawn`、`c_find`、`c_findtag` 和 `c_dumpworldstate`。
  - 当任务需要实用的游戏内验证或调试快捷方式时阅读此文件。
- `scripts/recipe.lua`
  - `AddRecipe2` 背后的配方对象行为。
  - 当配方配置行为不明确时阅读此文件。

## 模式目录

- `scripts/prefabs/`
  - 官方预制件实现。添加或修改游戏对象时首先阅读。
- `scripts/components/`
  - 官方组件逻辑。当行为由组件驱动时首先阅读。
- `scripts/stategraphs/`
  - 状态转换、动作处理和动画逻辑。
- `scripts/prefabs/*fx*.lua`
  - 一次性特效、声音代理、灯光辅助函数和仅展示预制件的高价值参考。
- `scripts/prefabs/lighterfire_common.lua`
  - 实用的灯光辅助函数和网络变量驱动的便携式灯光模式。
- `scripts/prefabs/torchfire_barber.lua`
  - 实用的 `AddVFXEffect()` 粒子系统参考。
- `scripts/brains/`
  - AI 决策逻辑。
- `scripts/map/levels/*.lua`
  - 森林、洞穴、事件和特殊模式的具体关卡定义。
- `scripts/map/customize.lua`
  - 世界设置和世界生成自定义屏幕的类别和选项连接。
- `scripts/map/rooms/**`
  - 按生物群系或内容族分组的具体房间定义。
- `scripts/map/tasks/*.lua`
  - 按世界族分组的具体任务定义。
- `scripts/widgets/`
  - UI 补丁使用的部件类。
- `scripts/screens/`
  - 屏幕级 UI 流程。

## `AnimState` 现实检查

`AnimState` 是引擎端的。你不会在 `scripts.zip` 中找到像 `animstate.lua` 这样的普通 Lua 实现。

对于动画工作，改为检查脚本级用法：

- `scripts/prefabs/`
  - 预制件启动动画、符号交换、构建覆盖
- `scripts/stategraphs/`
  - 角色驱动的动画流程和过渡排序
- `scripts/widgets/`
  - 进度条和 UI `SetPercent(...)` 用法
- `scripts/screens/`
  - 屏幕本地动画状态更新

## 实用阅读顺序

1. 阅读 `scripts/modutil.lua` 了解你计划使用的钩子系列。
2. 当任务涉及 `modmain.lua`、`PrefabFiles` 或资源如何加载时，阅读 `scripts/mods.lua` 和 `scripts/mainfunctions.lua`。
3. 当任务添加自定义动作收集或输入到动作行为时，阅读 `scripts/componentactions.lua`。
4. 当任务添加或修补 SG 流程时，阅读 `scripts/stategraph.lua` 和 `scripts/stategraphs/commonstates.lua`。
5. 当任务需要 RPC 或 replica/网络变量流程时，阅读 `scripts/networkclientrpc.lua` 和 `scripts/entityreplica.lua`。
6. 当任务添加 NPC AI 时，阅读 `scripts/brain.lua` 和 `scripts/brains/` 下的匹配文件。
7. 当任务添加放置器或配方时，阅读 `scripts/prefabutil.lua` 和 `scripts/recipe.lua`。
8. 当任务主要是文本或本地化连接时，阅读 `scripts/strings.lua`。
9. 阅读已经做过类似事情的具体官方文件。
10. 如果具体文件调用更深层的辅助函数，阅读 `scripts/entityscript.lua` 或 `scripts/standardcomponents.lua`。
11. 仅当任务主要是数据或常量时，阅读 `scripts/tuning.lua` 或 `scripts/constants.lua`。