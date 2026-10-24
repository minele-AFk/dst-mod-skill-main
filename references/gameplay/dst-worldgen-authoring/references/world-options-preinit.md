# 世界设置选项与全局 PreInit 钩子

本页说明建服界面的世界选项、运行时读取位置，以及 `AddLevelPreInitAny` / `AddTaskSetPreInitAny` 的执行时机。依据当前安装版 `modutil.lua`、`map/customize.lua`、`map/level.lua` 和 `map/tasksets.lua`；游戏更新后重新核对。

## 1. 注册世界设置

在 `modworldgenmain.lua` 中注册。建服前端会部分加载该入口，世界生成也会加载它；不要放到只面向游戏内运行的 `modmain.lua`。

```lua
-- modworldgenmain.lua
local freq = GetCustomizeDescription("frequency_descriptions")

AddCustomizeGroup(LEVELCATEGORY.SETTINGS, "mymod_monsters",
    "我的模组生物", nil, "images/mymod_customization.xml", 20)

AddCustomizeItem(LEVELCATEGORY.SETTINGS, "mymod_monsters", "mymod_beast", {
    value = "default",
    desc = freq,
    image = "mymod_beast.tex",
    atlas = "images/mymod_customization.xml",
    world = { "forest", "cave" },
    order = 1,
})
```

| API | 关键点 |
|---|---|
| `AddCustomizeGroup(category, name, text, desc, atlas, order)` | `category` 取 `LEVELCATEGORY.SETTINGS` 或 `LEVELCATEGORY.WORLDGEN`；同名组已存在时直接返回 |
| `AddCustomizeItem(category, group, name, itemsettings)` | 同名选项已存在时直接返回；`group` 为 nil 时只登记为 misc，不出现在界面 |
| `RemoveCustomizeGroup` / `RemoveCustomizeItem` | 删除自己的项；对原版项是按模组记录禁用 |
| `GetCustomizeDescription(name)` | 返回原版描述列表的深拷贝，修改不会污染原版 |

- 选项名是全局键，必须加模组前缀；同名原版或其他模组选项可能让注册静默失败。
- 加入原版组时，原版图集通常没有你的图片，必须在 `itemsettings` 中写 `atlas`。
- 前端图标需在 `modservercreationmain.lua` 的 `FrontEndAssets` 中声明并调用 `ReloadFrontEndAssets()`；普通运行时资源另在 `Assets`/`PreloadAssets` 处理。
- 选项值必须与 `desc` 中某项的 `data` 匹配；`nil` 按默认值处理。

## 2. 读取设置值

| 类型 | 运行时位置 |
|---|---|
| `LEVELCATEGORY.SETTINGS` | 服务器读 `TheWorld.topology.overrides[name]` |
| `LEVELCATEGORY.WORLDGEN` | 世界生成阶段读 `level.overrides[name]` |

两种都要处理 `nil`（旧存档、未开模组创建的世界或没有该选项），把它当作默认值。不要用 `GetModConfigData` 代替世界设置值；两者是不同作用域。

## 3. PreInit 顺序

`Level:ChooseTasks()` 当前顺序：

1. `tasksets.GetGenTasks(task_set)` 取得 TaskSet 数据的深拷贝。
2. `AddTaskSetPreInit(task_set, fn)`。
3. `AddTaskSetPreInitAny(fn)`。
4. 把 TaskSet 数据字段合并到 Level 对象。
5. `AddLevelPreInit(level.id, fn)`。
6. `AddLevelPreInitAny(fn)`。

`AddLevelPreInit` 按 `level.id` 匹配。玩家用自定义预设创建世界时，id 不一定是原版预设 id；要覆盖所有森林或洞穴世界，使用 `AddLevelPreInitAny` 并按 `level.location` 过滤。

```lua
AddLevelPreInitAny(function(level)
    if level.location ~= "forest" then
        return
    end
    if (level.overrides.mymod_beast or "default") == "never" then
        return
    end
    level.set_pieces = level.set_pieces or {}
end)
```

这些回调只在世界生成环境执行，不能访问 `TheWorld`、玩家或运行时组件。参数是本次生成用的拷贝；修改 Level/TaskSet 字段不会污染原版定义，但向共享常量表插入数据前仍要先复制。

## 4. 验证清单

- 新建森林和洞穴世界时，选项出现在预期页签并返回正确值。
- 旧存档或关闭模组后，读取代码对 `nil` 有默认值。
- 自定义预设和原版预设都能触发预期的 `AddLevelPreInitAny` / `AddTaskSetPreInitAny`。
- 前端图标、运行时图集和 `FrontEndAssets` 声明没有混用。
- 世界生成回调没有访问 `TheWorld`、玩家或客户端 UI。

本页于 2026-10-22 对照安装版 `map/customize.lua:1099-1215`、`map/level.lua:89-115` 与 `modutil.lua` 相关注册函数；未执行建服前端或真实世界生成测试。
