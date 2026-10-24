# 融合工程入口

本目录是现有 DST 工具包的按需补充，统一入口仍是 `$dst-mod-skill-main`。先遵守 [开发边界与验证约定](../../development-contract.md)，再读对应专题；不同时加载全部资料。

## 专题补充

| 目标 | 文档 |
|---|---|
| Lua 环境、配置、Hook | [core-lua-hooks](core-lua-hooks.md) |
| 实体、主组件与 Replica | [entities-components](entities-components.md)、[networking-rpc](networking-rpc.md) |
| 生命周期与存档 | [lifecycle-save](lifecycle-save.md) |
| 角色、Brain、StateGraph | [characters-brains-stategraphs](characters-brains-stategraphs.md) |
| 武器、食物、植物、锅料理 | [items-food-plants](items-food-plants.md)、[cooker-dishes](cooker-dishes.md) |
| 战斗、Buff、容器、法术与数值 | [combat-buffs-containers](combat-buffs-containers.md)、[spells-and-custom-stats](spells-and-custom-stats.md) |
| HUD、输入与动作 | [ui-actions-controls](ui-actions-controls.md) |
| 世界生成与空间 | [worldgen-spatial](worldgen-spatial.md) |
| 贴图、人物拆件、帧序列与声音 | [assets-animation](assets-animation.md)、[character-and-equipment-art](character-and-equipment-art.md)、[animation-recipes](animation-recipes.md)、[audio-particles](audio-particles.md) |
| 环境、工具发现、DMT 操作 | [environment-tools](environment-tools.md)、[tool-bootstrap](tool-bootstrap.md)、[dst-mod-tool](dst-mod-tool.md) |
| 测试、发布与证据等级 | [testing-release](testing-release.md)、[本机验证记录模板](../../testing/local-validation.md) |
| 旧教程纠错 | [sources-and-corrections](sources-and-corrections.md)，与原有 [纠错索引](../../pitfalls/old-rule-corrections.md) 交叉核对 |
| 工程知识与更正关系 | [知识库入口](../../knowledge/README.md)、[检索策略](kb-retrieval.md)、[知识应用例子](knowledge-integration.md) |

## 执行工具

以下命令从 **skill 源目录** 执行。`run.ps1` 优先选用本项目 `.codex/venvs/dst-skill` 的解释器；环境缺失时不自动安装依赖。路径变量必须由当前任务明确定位。完整命令、旧命令兼容关系与退出码以 [工具台账](../../tools/README.md#明确的命令入口) 为准。

```powershell
# 只查语法和直接调用声明，不启动游戏；JSON 输出目录需已存在
& ./references/tools/engineering/run.ps1 check_api_ast $mod --dst $dst --out $report

# 定点读安装版源码，无目录缓存，不覆盖单文件导出目标
& ./references/tools/engineering/run.ps1 zip_read --dst $dst info

# 只执行合成夹具/子进程回归，不运行饥荒
& ./references/tools/engineering/run.ps1 test_tools
```

需要整个 Mod 的语法与自定义组件检查时用 `check_api_ast`；只快速核对单文件直接调用时用无额外依赖的 `check_api_fast`。两者退出码不同：AST 工具 `1` 表示语法错，`2` 表示待核对/输入或依赖问题；快速工具的 `1/2/3` 定义见 [台账](../../tools/README.md#api-声明检查)。两种声明匹配均不等于游戏通过。

仅在用户已授权隔离游戏测试、确认目标 Mod 与二进制后执行：

```powershell
& references/tools/engineering/run.ps1 dst_modtest $mod --dst $dst --out $evidence --script $behaviorTest --quiet
```

新增 Windows runner 使用唯一 Mod 快照、独立存档与带本轮 ID 的完成标记。行为脚本的全部断言完成后必须调用 `TEST.Done()`；它只终止自己启动的进程，保留证据与自己创建的快照路径。旧 macOS 注入桥仍未适配 Windows；两个工具的用途和验证范围不可混用。真实客户端 UI、预测、视觉和听感另做验收。

## 来源与融合范围

- 来源：[Zechariah0121/dst-mod-engineering](https://github.com/Zechariah0121/dst-mod-engineering)，固定提交 `ef682cb95f4b4e2171f3c2c634c88ddecefe75de`。
- 首次融合前的 skill 快照为 Git 提交 `0f56a6f34603490c66be79c920adc1fe36e5ddf8`；后续维护按各轮证据目录保留当前工作内容的前态与差异。
- 融合 21 篇技术专题、3 个开发工具及其合成回归、64 条公开知识记录与只读检索代码。保留本地规则、原有 50 个专题、物品名表、资源和快速检查器。
- 上游主 SKILL、跨产品安装指南、网页包构建器及 dist 产物不作为第二套技能安装；普通开发只从本工具包路由。
- 路径适配、目录归属与源文件 SHA-256 见 [provenance.json](provenance.json)。知识包数据保持冻结，不自动写回。
- 文档与脚本的上游 MIT 许可保留在 [LICENSE](LICENSE)。该许可不重新授权原游戏和第三方 Mod 的源码或素材。
- [上游历史验证](upstream-validation.md) 属于作者的记录，不能当成本机已运行结果。本机验证记录另放在项目 `.codex/validation/dst-skill-integration`。

本地后续维护（2026-10-17）：统一查询入口现同时发现本地专题和结构化知识，见 [知识入口](../../knowledge/README.md)。同主题补充回原专题，已有覆盖复用，缺主题才引入普通参考；不再复制一套上游入口。原 `provenance.json` 是导入时快照，不是后续文件现状校验表；本地纠错与调用适配以当前文件和本轮维护证据为准。下载目录中上游后续许可/发布说明的变化须按具体版本另核对，本轮未替换固定知识包。
## 来源覆盖复核与使用价值

2026-10-18 对用户提供目录的 129 个文件逐项登记用途。23 篇参考中，21 篇技术正文与本地对应文档逐差异比较，保留的内容及路径、措辞适配都有记录；另两篇 agent-setup/web-chat 的可复用加载、资料读取、局部代码和远端交付原则补入 [环境与技能加载](environment-tools.md#技能加载知识读取与执行位置)。具体产品菜单和分发包安装方式不变成本项目的固定调用要求。

64 条规范记录及相关关系与提供目录的数据一致；冻结包的版本、证据与未执行测试继续独立保存。新增维护原则回到 [知识入口](../../knowledge/README.md#知识维护时的源文件与派生产物)。源仓库的网页阅读版和 ZIP 是这些原文的生成物，按输入/输出指纹确认来源，避免把相同正文再建一个知识副本；维护脚本和 CI 的用途与本地游戏能力分别判断。

来源覆盖回答“材料去向和取舍是否有依据”；任务检索、读原文与适用性判断回答“能否使用”；源码或实际运行回答“本任务是否成立”。三者不能靠导入数量或文件哈希互相替代。普通开发沿现有专题使用，维护时再读取本节。