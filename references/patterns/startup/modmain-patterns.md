# Modmain 模式

当任务主要涉及 `modmain.lua` 本身时使用本文件：

- 游戏玩法侧入口文件负责什么
- `PrefabFiles` 或顶级 `Assets`
- `modimport(...)` 与 `require(...)` 的区别
- 共享启动代码、小地图 atlas 或角色注册
- 将大型 `modmain.lua` 拆分为更小的注册文件

如果任务主要涉及预制物构造函数或组件类（在注册已经确定之后），也请阅读 `references/core/dst-prefab-authoring/references/prefab-contract.md`。

## `modmain.lua` 实际上是什么

官方加载器将 `modmain.lua` 作为普通游戏玩法侧模组入口文件运行。

在 `scripts/mods.lua` 中观察到的加载器流程：

- 首先准备模组环境
- 模组的 `scripts/?.lua` 路径被添加到 `package.path`
- `modimport(...)` 被安装到模组环境中
- `ModWrangler:InitializeModMain(modname, mod, "modmain.lua")` 运行该文件
- 之后，`PrefabFiles` 中列出的预制物文件被单独加载

实际影响：

- `modmain.lua` 是注册中心，而不是创建预制物实例的地方
- 世界生成和服务端创建逻辑属于 `modworldgenmain.lua` 或 `modservercreationmain.lua`，而不是这里

如果 `modmain.lua` 缺失，加载器会跳过它而不是因此崩溃。

## 通常属于 `modmain.lua` 的内容

高价值的 `modmain.lua` 工作通常是以下之一：

- 声明 `PrefabFiles`
- 声明顶级共享 `Assets`
- 可选声明 `FrontEndAssets` 或 `PreloadAssets`
- 注册钩子，如预制物、组件、状态机、窗口部件或类的 post-init
- 注册动作、组件动作、配方、RPC 处理器或可复制组件
- 加载共享字符串、调整和配置代码
- 注册小地图 atlas 和模组角色
- 使用 `modimport(...)` 将启动工作拆分为更小的文件

好规则：

- 如果代码主要说"注册这个"、"加载这个"或"连接这些系统"，它可能属于 `modmain.lua`
- 如果代码主要说"创建这个实体实例"或"每次运行这个实体行为"，它可能属于 `prefabs/*.lua`、组件、大脑或状态机

## 通常不属于这里的内容

- 世界生成或主机设置逻辑
- 每个实例的预制物构造
- 假设 `TheWorld`、`ThePlayer` 或已生成实体已存在的重型顶级运行时逻辑
- 假设 `TheWorld` 在模组加载时已存在的保护代码
- 应该从 `require(...)` 返回的大型可重用模块

顶级 `modmain.lua` 代码在模组加载期间运行，因此优先选择注册和设置而不是普通游戏玩法执行。

## 常见环境传递

许多模组使用小型传递，以便无前缀的全局变量针对 `GLOBAL` 解析：

```lua
local GLOBAL = GLOBAL
GLOBAL.setmetatable(env, {
    __index = function(_, key)
        return GLOBAL.rawget(GLOBAL, key)
    end,
})
```

这是一个便利模式，不是必需的。

实践规则：

- 当模组经常接触全局 DST API 时使用它
- 将其放在 `modmain.lua` 的顶部附近
- 不要将其与注册混淆；它只改变名称查找行为
- 在 DST 的模组环境中，优先使用 `GLOBAL.setmetatable(...)` 而不是裸 `setmetatable(...)`，因为在严格模组加载下普通全局可能不可用

只读规则：

- 将 `GLOBAL`、`TheSim`、`TheNet`、`TheShard`、`TheInput`、`TheFrontEnd`、`TheMixer`、`TheCamera`、`TheFocalPoint`、`TheWorld`、`ThePlayer` 和 `AllPlayers` 视为引擎拥有的全局变量
- 不要在正常模组代码期间分配它们、将它们设为 nil 或用模拟表替换它们
- 局部自别名如 `local GLOBAL = GLOBAL` 是可以的，因为它保留了同一个对象
- `TheWorld` 和 `ThePlayer` 是实体引用，因此将世界或玩家拥有的字段附加到实体可能是有效的；替换全局绑定则无效
- 共享注册表如 `TUNING`、`STRINGS`、`ACTIONS`、`CUSTOM_RECIPETABS` 和模组 RPC 注册表可以狭窄扩展，但不要替换整个表

错误形状：

```lua
GLOBAL = {}
TheNet = nil
TheWorld = nil
ThePlayer = inst
TUNING = {}
ACTIONS = {}
MOD_RPC = {}
RPC = {}
```

更安全的形状：

```lua
local GLOBAL = GLOBAL

TUNING.MYMOD_DAMAGE_MULT = 1.25
STRINGS.ACTIONS.MYMOD_ACTION = "做某事"

if ThePlayer ~= nil and ThePlayer.HUD ~= nil then
    -- 在不重新绑定引擎全局的情况下读取本地玩家状态
end
```

优先使用官方辅助函数（如果存在）：

- 使用 `AddAction(...)` 而不是手动构建 `ACTIONS` 和 `STRINGS.ACTIONS`
- 使用 `AddRecipe2(...)` 和 `AddRecipeToFilter(...)` 而不是替换配方注册表
- 使用 `AddModRPCHandler(...)`、`AddClientModRPCHandler(...)` 和 `AddShardModRPCHandler(...)` 而不是触摸核心 `RPC` 表

## `modimport(...)` 与 `require(...)`

这些是不同的工具。

在 `scripts/mods.lua` 中观察到的 `modimport(...)` 行为：

- 从 `env.MODROOT .. modulename` 加载
- 如果缺少则追加 `.lua`
- 在模组环境中执行

实践规则：

- 使用 `modimport("scripts/modmain/init")` 或类似方式处理主要执行副作用注册的有序启动文件
- 使用 `require("widgets/foo")`、`require("brains/foo")` 或类似方式处理应该返回表、类或构造函数的可重用模块

好启发式：

- `modimport(...)` 用于"现在运行这个文件"
- `require(...)` 用于"加载这个模块并使用其返回值"

## `PrefabFiles` 仅注册预制物文件

`PrefabFiles` 本身不会创建预制物实例。

在 `scripts/mods.lua` 中观察到的流程：

- `modmain.lua` 首先完成
- `RegisterPrefabs()` 迭代 `mod.PrefabFiles`
- 每个条目从 `prefabs/<name>.lua` 加载
- 返回的 `Prefab(...)` 对象被复制到全局预制物表中

实际影响：

- `PrefabFiles = { "my_item" }` 意味着加载器应该查找 `prefabs/my_item.lua`
- 如果新预制物"不存在"，在调试其构造函数之前检查 `PrefabFiles`
- 字符串应该是不带 `.lua` 的预制物文件路径

## 顶级 `Assets` 是共享模组资源

`modmain.lua` 中的顶级 `Assets` 不绑定到一个游戏玩法预制物文件。

在 `scripts/mods.lua` 中观察到的流程：

- 预制物注册后，加载器创建 `Prefab("MOD_"..modname, nil, mod.Assets, prefabnames, true)`
- 该默认模组预制物携带模组级别的资源表

实际影响：

- 使用顶级 `Assets` 存放共享 atlas、肖像、角色艺术、技能 atlas 或共享动画压缩包
- 将一次性游戏玩法预制物资源放在实际拥有它们的预制物文件中
- 从 `modmain.lua` 用 `AddMinimapAtlas(...)` 注册全局小地图 atlas

从 `scripts/modutil.lua` 暴露的相关辅助函数：

- `AddMinimapAtlas(...)`
- `ReloadFrontEndAssets()`
- `ReloadPreloadAssets()`

如果任务主要涉及资源声明或纹理路径，也请阅读 `references/patterns/asset/asset-patterns.md`。

## 有意拆分大型 `modmain.lua` 文件

当 `modmain.lua` 开始变成一个巨大的混合文件时，将其拆分为小的注册文件，并将根文件保留为中心。

一个清晰的模式是：

1. 设置环境传递
2. 声明 `PrefabFiles` 和共享 `Assets`
3. `modimport("scripts/modmain/init.lua")`
4. 在导入后只保留小的启动代码

在 `scripts/modmain/init.lua` 内部，按关注点分组：

- 配置
- 字符串或国际化引导
- 配方和动作
- UI
- 副本或 RPC
- 钩子
- 状态机注册
- 链接或兼容性代码

因为 `modimport(...)` 立即执行，所以保持加载顺序明确，而不是将其视为无序模块列表。

## 角色模组代码通常从这里开始

角色模组通常将此注册保存在 `modmain.lua` 中：

- 顶级 `Assets` 中的角色肖像和选择界面资源
- `AddMinimapAtlas("images/map_icons/<name>.xml")`
- `AddModCharacter("<name>", "FEMALE")` 或匹配的性别
- 通过调整表进行启动物品代码
- 当自定义启动物品需要正确图标时使用 `TUNING.STARTING_ITEM_IMAGE_OVERRIDE[...]`

将仅元数据的本地化保存在 `modinfo.lua` 中。
将运行时语音和游戏玩法字符串保留在运行时字符串文件中。

## `modmain.lua` 中的运行时保护

不要将 `modmain.lua` 视为预制物构造函数。

有用的保护规则：

- 本地输入或 HUD 代码通常应该放在 `if not TheNet:IsDedicated() then` 后面
- 权威实体行为通常属于预制物构造函数、组件或由 `TheWorld.ismastersim` 保护的 post-init 回调
- 不要假设 `TheWorld` 在 `modmain.lua` 加载时已存在
- 除非确定模组完全没有客户端注册，否则避免 blanket 顶级 `if not TheWorld.ismastersim then return end`

最后一个错误很常见，因为它可能会意外跳过：

- 本地 UI patch
- 输入处理器
- 副本设置辅助函数
- 客户端可见的字符串或资源

## 快速路由

- "为什么我的预制物文件没有加载？"
  - 检查 `PrefabFiles`
- "共享肖像、atlas 或动画压缩包应该在哪里声明？"
  - 检查顶级 `Assets`
- "我的 `modmain.lua` 太大了。"
  - 使用 `modimport("scripts/modmain/...")` 拆分
- "为什么我的角色没有正确显示？"
  - 检查 `AddModCharacter(...)`、顶级角色资源和 `modinfo.lua`
- "配置驱动的启动调整应该放在哪里？"
  - 将代码保存在 `modmain.lua` 中，然后将实际行为移到预制物或组件代码中