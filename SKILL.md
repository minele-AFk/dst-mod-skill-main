---
name: dst-mod-skill-main
description: 饥荒联机版（DST）Mod 专业知识按需查询。用于 API、游戏机制、组件、物品代码名、源码契约、历史案例或实现方式不清楚，需要查证时；简单明确且不涉及这些专业知识的编辑、普通游戏攻略和与 DST Mod 无关的任务不使用。
---

# DST Mod 知识库与开发查证

先遵守 [开发边界与验证约定](references/development-contract.md)。用户本次指令与工作区 AGENTS.md 优先；询问或评价请求只读，已授权的修复直接在指定范围实施。第三方 Mod、资料包及原有 Mod 分析笔记只有用户明确点名时读取。

本 skill 定位为 DST Mod 专业知识库和查证入口，不是每个 DST 任务都必须走的固定流程。简单机械编辑、需求与实现均已明确且不需要查 API/机制/代码名时，直接按用户要求和 AGENTS.md 处理；只有存在知识缺口、版本契约不清、需要案例依据或结论可能影响运行行为时，才读取相关专题或检索知识库。AGENTS.md 要求先参考本 skill 的游戏机制或组件文档时，仍从其要求。

本 skill 的源目录为 `.trae/skills/dst-mod-skill-main`；项目调用入口 `.agents/skills/dst-mod-skill-main` 指向同一目录。显式调用 `$dst-mod-skill-main`；不创建另一个同名全局副本。所有嵌套专题均为本 skill 内的参考文档，由此入口按需读取；只有 `dst-mod-skill-main` 是可调用 skill。

## 调用边界

- 直接处理：需求、实现和涉及的专业知识都明确，且不需要核对游戏机制、组件契约或物品代码名。
- 进入查证：API、机制、组件、代码名、版本契约或既有实现不清楚；需要历史案例；结论会影响运行行为。
- `AGENTS.md` 明确要求参考游戏机制或组件文档时，优先执行其要求。
- 查证时只读当前任务最相关的一份专题；命中后再读具体参考和源码，不默认加载全库。

## 工作顺序

先按请求选择工作深度，再进入下方相关专题：

| 请求 | 起点与停止条件 |
|---|---|
| 咨询、解释、评价 | 只读相关文档与目标代码，回答问题；无需套用实现和测试全流程 |
| 设计、方案审查 | 查证关键可行性，列出未定行为、方案取舍及验收方法；要求先审查时等确认再实施 |
| 开发、修复 | 先理解已授权目标与对应专题，再按以下步骤改动和验证 |
| 崩溃、行为异常 | 从用户提供的复现与第一条相关日志开始，按 [任务指南](references/task-playbook.md#调试损坏的功能) 定位运行端和调用链 |
| 贴图、拆件、动画 | 从已确认参考与交付阶段开始；按下方美术路由选择流程，保持已批准设计 |

1. 识别当前目标、源码/运行副本、配置与实际触发端，并判断是否存在 DST Mod 知识缺口。简单明确任务直接执行；不确定 API、机制、组件、物品代码名或实现方式时再进入查证。涉及物品代码名先查 [物品名字.txt](references/prefabs/物品名字.txt)。
2. 需要查证时按任务检索 [本地知识库](references/knowledge/README.md)。已知准确专题或记录 ID 时直接读取；入口不明确或需要跨系统证据时用 `run.ps1 knowledge lookup '任务关键词' --mode debug`（按任务选择模式），同时定位本地文档和结构化记录。简单机械编辑无需重复检索。遇到技能未被使用、附件不完整或本机/云端混用，先查 [加载与资料边界](references/engineering/dst-mod-engineering/environment-tools.md#技能加载知识读取与执行位置)。
3. 查原版定义、调用者、主客机边界、初始化/退出和保存链路。优先用户指定源码或 `DST_SCRIPTS_DIR`；本工作区可读 `D:\mods\scripts`，这是手动维护快照，重要结论核对当前安装的 `data/databundles/scripts.zip`。
4. 建立需求 → 目标实现 → 原版契约 → 验证方法。确定故障按授权修复；未知需求和影响行为的方案取舍交给用户，已明确决策不重复询问。
5. 做最小完整改动，覆盖实际相关的取消、移除、死亡、重连、读档等路径；保留用户已有改动和无关文件。大型项目先规划并取得确认。
6. 用合适的检查器和可用运行环境验证。交付说明改动、实际同步目标、证据与未覆盖项；工具返回不能作为整体正确性的证明。提交、推送和发布另需用户明确授权。

## 按任务读取

| 任务 | 优先阅读：对应专题 | 补充：专题不足或需要跨系统契约时读取 |
|---|---|---|
| 脚手架、Lua 环境、Hook | [脚手架](references/core/dst-mod-scaffolding/GUIDE.md)、[运行时](references/core/dst-lua-runtime/GUIDE.md) | [Lua 环境与 Hook](references/engineering/dst-mod-engineering/core-lua-hooks.md) |
| Prefab、Component、Replica | [Prefab](references/core/dst-prefab-authoring/GUIDE.md)、[Component](references/core/dst-component-authoring/GUIDE.md) | [实体与组件](references/engineering/dst-mod-engineering/entities-components.md) |
| 网络、RPC、预测、输入 | [联机](references/core/dst-networking-rpc/GUIDE.md)、[动作](references/core/dst-action-authoring/GUIDE.md) | [联机契约](references/engineering/dst-mod-engineering/networking-rpc.md)、[UI 与动作](references/engineering/dst-mod-engineering/ui-actions-controls.md) |
| 生命周期、存档、迁移 | [事件任务](references/core/dst-events-tasks-lifecycle/GUIDE.md)、[存档](references/core/dst-persistence-migration/GUIDE.md) | [生命周期与恢复](references/engineering/dst-mod-engineering/lifecycle-save.md) |
| 游戏更新、源码版本变化 | [API 更新差异](references/engineering/dst-api-update-diff/GUIDE.md) | [源码研究](references/core/dst-source-research/GUIDE.md) |
| 食物、料理、物品、植物 | [食物](references/gameplay/dst-food-cooking/GUIDE.md)、[物品](references/gameplay/dst-inventory-equipment-containers/GUIDE.md) | [物品与植物](references/engineering/dst-mod-engineering/items-food-plants.md)、[锅料理完整链路](references/engineering/dst-mod-engineering/cooker-dishes.md) |
| 战斗、法术、自定义属性 | [战斗](references/gameplay/dst-combat-weapons-projectiles/GUIDE.md)、[生存属性](references/gameplay/dst-status-buffs-survival/GUIDE.md) | [战斗与 Buff](references/engineering/dst-mod-engineering/combat-buffs-containers.md)、[法术与 HUD](references/engineering/dst-mod-engineering/spells-and-custom-stats.md) |
| 角色、AI、SG、世界生成 | [角色](references/gameplay/dst-character-authoring/GUIDE.md)、[世界生成](references/gameplay/dst-worldgen-authoring/GUIDE.md) | [角色与状态图](references/engineering/dst-mod-engineering/characters-brains-stategraphs.md)、[世界与空间](references/engineering/dst-mod-engineering/worldgen-spatial.md) |
| 贴图、拆件、动画、音效 | [贴图](references/world-ui-assets/dst-texture-style/GUIDE.md)、[动画流程](references/world-ui-assets/dst-action-create-workflow/GUIDE.md) | [资源检查](references/engineering/dst-mod-engineering/assets-animation.md)、[动画配方](references/engineering/dst-mod-engineering/animation-recipes.md)、[音频](references/engineering/dst-mod-engineering/audio-particles.md) |
| 排错、审查、测试、发布 | [调试](references/core/dst-debugging-testing/GUIDE.md)、[审查](references/engineering/dst-mod-review-refactoring/GUIDE.md) | [证据等级与隔离测试](references/engineering/dst-mod-engineering/testing-release.md) |

每次先选最相关的一份专题；命中后读取有关段落及来源，不把摘要当作完整知识。查询中的 maintenance 只记录本地正文哈希与维护深度，stale/unrecorded 时补查原文和来源；record_current 也不代表源码最新版、结论适用或实机通过。只有涉及补充契约时继续读取；查询不到时用精确 API 名或同义词缩小搜索，再查当前源码。具体步骤查 [任务指南](references/task-playbook.md)，完整目录见 [详细目录](references/topic-index.md)；环境和工具补充见 [融合工程入口](references/engineering/dst-mod-engineering/README.md)。

`lookup` 返回本地文档与结构化证据时，分别选择各自最相关的记录并读完整上下文：本地文档提供当前操作流程，结构化条目补充来源、适用范围、反例和更正。两组结果的分值不可横向比较，结构化记录稀疏或排序靠后也不等于没有证据；没有可复用条目时保留本地流程并明确知识缺口。

命中旧模式页或融合工程细节页时，按结果中的 `primary_topics` 先读主专题，再按实际问题读细节；若主专题被条数截掉，读取顶层 `primary_topic_candidates`。若只需找负责的专题，用 `knowledge topics --query '关键词'` 查当前 50 个专题的结构化路由。该目录是导航元数据，不给文档赋予历史知识包的证据等级。

美术任务有用户例图，或反馈画风/精细度不符时，先走 [参考驱动提示与验收](references/world-ui-assets/dst-texture-style/references/reference-led-prompts.md)：实际选图、区分设计与画法、保留已确认项，并检查原尺寸；不默认把所有 Mod 图套成同一种风格。

## 工具选择

Python 工具要求 3.10+；新增 AST 检查器依赖 `luaparser`，本项目独立解释器为 `.codex/venvs/dst-skill/Scripts/python.exe`。工具的输入、覆盖范围和退出码见 [工具台账](references/tools/README.md)。
需要仓库环境要求或跨平台常见安装目录时读 [项目说明](README.md)；安装工具或启动 Steam 前先取得用户明确授权。

| 场景 | `run.ps1` 子命令 / 工具 | 验证边界 |
|---|---|---|
| 定点源码查证 | `zip_read`：显式指定安装目录或 ZIP，无缓存；原有 `general/dst_zip_tool.py` 用于兼容已有参数 | 本机安装包不是线上最新版本；源码只读 |
| 单文件快速声明扫描 | `check_api_fast`：[快速扫描器](references/tools/general/check_api.py) | 无额外依赖；别名、动态字段和未覆盖项要求核对 |
| 整个 Mod 的 Lua 语法与声明审查 | `check_api_ast`：[AST 检查器](references/tools/engineering/scripts/check_api.py) | AST 解析；自定义组件优先，主组件/Replica 分开；不能证明签名和运行端 |
| Windows 离线隔离单分片测试 | `references/tools/engineering/scripts/dst_modtest.py` | 唯一副本/存档，显式 TEST.Done 与失败观察；不验证真实客户端 UI、预测、听感 |
| 按需知识查询 | `knowledge lookup/docs/read`：[查询入口](references/knowledge/README.md) | 本地专题、组件、模式、名称表与结构化记录；目录剪枝排除受限笔记和素材；原有 `status/call/validate` 保留 |
| skill 维护检查 | `check_skill --strict`；`test_skill` 运行维护回归 | 单入口、旧调用、文档/结构/语法；跳过受限目录，不启动游戏或生成 pyc |

从 skill 根目录用 `references/tools/engineering/run.ps1` 选择项目独立 Python；调用示例见 [融合工具说明](references/engineering/dst-mod-engineering/README.md#执行工具)。旧 macOS 注入桥仍属于待移植工具，不与新的 Windows runner 混为一谈。

## 判断与交付

- Component/Replica 方法与初始化路径分别核对；引擎绑定或注入方法找不到声明时保留待查状态，不虚构契约。
- 知识记录中的事实、单案例观察、更正、建议和未运行测试分别处理；命中结果不是当前项目的根因或测试通过。
- 游戏部署、专服启停、注入、存档修改只作用于当前任务已授权的测试范围；不会因为载入本 skill 自动执行。
- 分别报告文档/语法检查、声明核对、stub 合约、专服行为、真实客户端和资源验收。未亲自执行的项目列为未测。
- 融合来源、固定提交、许可与差异处理见 [工程入口与来源记录](references/engineering/dst-mod-engineering/README.md#来源与融合范围)。
