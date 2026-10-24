# Mod 引导

当缺少 `modinfo.lua` 或 `modmain.lua` 且任务看起来是创建新 mod 时使用此文件。
如果脚手架需要包含依赖项或非平凡的 `configuration_options`，也请阅读 `references/patterns/startup/modinfo-patterns.md`。

## 何时提供脚手架

在以下情况下提供 mod 脚手架：

- 目标文件夹没有 `modinfo.lua`
- 目标文件夹没有 `modmain.lua`
- 用户描述的是一个新 mod 想法，而不是对现有 mod 的编辑

如果 `modinfo.lua` 已存在，不要直接跳到脚手架。
先读取现有标志，推断 mod 是客户端/服务端共用游戏玩法、仅客户端还是仅服务端。

## 首先要问什么

只问最小必要的阻塞性问题：

1. 如果缺少 `modinfo.lua`，这是什么类型的 mod：
   - 客户端/服务端共用游戏玩法 (all-clients gameplay)
   - 仅客户端 (client-only)
   - 仅服务端 (server-only)
2. `modinfo.lua` 中应显示什么显示名称？
3. 应该使用什么简短描述？
4. 脚手架是否应包含配置选项？

仅在用户关心或任务明确要求时才询问作者或版本。

如果 `modinfo.lua` 存在但标志不完整或矛盾，只需询问缺失的分类问题，而不是重新询问所有内容。

## 要生成什么

至少：

- `modinfo.lua`
- `modmain.lua`

可选的后续添加：

- prefab 文件夹
- 图片或图标
- 配置选项条目
- `scripts/`、`widgets/`、`stategraphs/` 或 `prefabs/` 的辅助目录

## 按 Mod 类型划分的最小文件集

- 仅客户端 UI 或 QoL mod
  - `modinfo.lua`
  - `modmain.lua`
  - 可选的 `scripts/` 用于 widgets、screens 或 helpers
- 仅服务端世界或自动化 mod
  - `modinfo.lua`
  - `modmain.lua`
  - 如果涉及预设、房间、任务或起始位置，则可选 `modworldgenmain.lua` 或 `modservercreationmain.lua`
- 客户端/服务端共用游戏玩法/内容 mod
  - `modinfo.lua`
  - `modmain.lua`
  - 通常需要 `prefabs/`
  - 可选的 `scripts/components/`、`scripts/replicas/`、`scripts/widgets/`、`scripts/stategraphs/`、`scripts/brains/`

实用规则：

- 不要习惯性创建 `modworldgenmain.lua`
- 仅当功能确实属于世界生成或主机设置流程时才添加它

## 推荐默认值

- `api_version = 10`
- `dst_compatible = true`
- 版本字符串如 `0.1.0`
- 空的 `PrefabFiles` 和 `Assets` 列表
- `modmain.lua` 具有只读 `GLOBAL` 环境传递和清晰的服务端/客户端分离

## 使用脚手架脚本

当用户想要确定性的引导输出时，使用 `references/tools/general/init_dst_mod.py`。

示例：

```bash
python references/tools/general/init_dst_mod.py .\MyNewMod --display-name "My New Mod" --description "Short summary" --mod-type all-clients
```

如果用户想要初始的 `configuration_options`，添加 `--with-config`。

## 脚手架之后

下一个文件取决于第一个实际功能：

- 入口点布局、`PrefabFiles`、`Assets` 或 `modimport(...)`
  - 阅读 `references/patterns/startup/modmain-patterns.md`
- 物品、生物、结构或 FX prefab
  - 阅读 `references/templates/template-patterns.md`
- 元数据、依赖项或关键配置
  - 阅读 `references/patterns/startup/modinfo-patterns.md`
- 世界生成或预设
  - 阅读 `references/patterns/world/worldgen-patterns.md`
- 运行时字符串或区域设置加载器
  - 阅读 `references/patterns/runtime-i18n-patterns.md`
  - 如有需要，然后阅读 `references/patterns/runtime-i18n-patterns.md`

## 常见失败点

- 搭建了错误的 mod 类型
  - 首先修复 `client_only_mod` 和 `all_clients_require_mod`
- 为普通运行时 mod 生成了世界生成文件
  - 不必要的文件面使路由更差
- 在 `modmain.lua` 中存在 `PrefabFiles` 之前就开始编写 prefabs
  - 注册路径稍后会中断
- 在 `modmain.lua` 的顶层保留了太多实际游戏玩法逻辑
  - 将实例行为移回到 prefab、component、brain、SG 或 post-init 代码中
- 重新分配了引擎全局变量，如 `GLOBAL`、`TheSim`、`TheWorld` 或 `ThePlayer`
  - 保持引擎全局变量只读，仅将它们用作查找句柄
