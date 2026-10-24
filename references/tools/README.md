# 通用工具总台账（references/tools/）

> 集中收口跨子技能复用的**通用工具**，按用途分子目录。各子技能的**专属工具**仍放在就近的 `<子技能>/tools/`（见「就近工具」节）。
> 本目录是统一入口：需要某个工具时先查这里，找不到再查就近子技能。

## 子目录一览

| 子目录 | 内容 | 说明 |
|---|---|---|
| `general/` | 全技能通用构建/资源工具（自技能根 `scripts/` 上收） | 打包、初始化 mod、tex 图集、scml 动画、zip 检索、PNG 缩放、PDF 读取等 |
| `testing/` | 无头服务器运行时测试工具链（自 `testing/tools/` 上收，原为 macOS 专属，Windows 需移植） | game_config / game_process / game_log / run_script / setup |
| `reverse/` | 旧目标专用的静态分析底本 | 复用前按静态分析专题核对授权、输入格式与实现，不能按魔数自动选工具 |
| `engineering/` | AST 语法/API 声明检查、显式 ZIP 查询、Windows 隔离专服 runner 与合成回归 | `run.ps1` 选择项目独立 Python；与旧 macOS 桥不同 |
| `knowledge/` | 本地文档与结构化证据的统一查询 CLI / 可选结构化 stdio 协议 | 文档无缓存；排除受限目录；结构化索引在项目 `.codex/cache` |

另：`dst-wiki-scrape.md` 是维基抓取说明文档，非脚本，保留在本目录根部。

## 明确的命令入口

从 skill 根目录执行 `& ./references/tools/engineering/run.ps1 <命令> <参数>`。入口优先使用工作区 `.codex/venvs/dst-skill`，缺失时使用 PATH 中的 Python；实际解释器和脚本路径写到 stderr，工具正文与退出码保持原样。不自动安装依赖，不改变当前目录或相对路径含义。

| 命令 | 实际脚本 | 来源参数 / 退出码 |
|---|---|---|
| `check_api_fast` | `general/check_api.py` | `--scripts-dir` / `--zip` / `--dst`；0匹配、1未找到声明、2输入错误、3人工核对 |
| `check_api_ast` | `engineering/scripts/check_api.py` | `--scripts-dir` / `--zip` / `--dst` 三选一；需 luaparser；0直接声明匹配、1语法错、2待核对或输入/依赖错误 |
| `zip_read` | `engineering/scripts/dst_zip_tool.py` | `--dst` / `--zip` 放在子命令前；无缓存；0成功、1搜索无结果、2错误 |
| `check_skill` | `general/check_skill.py` | `--strict` 将警告视为失败；0通过、1失败 |
| `test_skill` | `references/testing/test_skill_maintenance.py` | 维护检查、缓存和 PowerShell 入口的合成回归；不启动游戏 |
| `test_api` | `references/testing/test_check_api.py` | 原有快速扫描器回归 |
| `test_tools` | `engineering/tests/test_tools.py` | AST、ZIP与模拟专服子进程回归；不启动饥荒 |
| `dst_modtest` | `engineering/scripts/dst_modtest.py` | 仅已授权的隔离专服测试使用，见融合入口 |
| `knowledge` | `knowledge/dst_kb_cli.py` | `lookup/docs/read/catalog/topics` 查询本地知识与专题路由；原 `call/status/validate` 等命令兼容；0查询完成（可含显式缺口/partial）、1错误，参数错误2 |
| `test_knowledge` | `knowledge/tests/test_skill_knowledge.py` | 本地检索相关性、受限目录剪枝、路径读取和回退的合成/文档回归 |
| `test_knowledge_service` | `knowledge/tests/test_service.py` | 结构化知识包服务、冻结包密封、MCP 接口与索引失效回归；不启动游戏 |

旧命令 `check_api` 仍指向 AST 检查器，`dst_zip_tool` 仍指向显式来源的无缓存版本；旧脚本路径、参数和退出码保留。直接运行 `general/dst_zip_tool.py` 时使用原有 `--zip-path`、`show --end`、`stats` 等参数，不能套用 `zip_read` 的 `--zip`、`show --count`、`info`。

```powershell
& ./references/tools/engineering/run.ps1 check_api_fast path/to/target.lua --scripts-dir "D:\mods\scripts"
& ./references/tools/engineering/run.ps1 check_api_ast path/to/mod --scripts-dir "D:\mods\scripts"
& ./references/tools/engineering/run.ps1 zip_read --dst "E:\SteamLibrary\steamapps\common\Don't Starve Together" info
& ./references/tools/engineering/run.ps1 check_skill --strict
& ./references/tools/engineering/run.ps1 test_skill
& ./references/tools/engineering/run.ps1 test_knowledge
& ./references/tools/engineering/run.ps1 test_knowledge_service
```

### 缓存与维护范围

`zip_read` 不生成缓存。原有 `general/dst_zip_tool.py` 的缓存默认写入工作区 `.codex/cache/dst-zip`；独立安装无法识别工作区时回退至系统临时目录 `dst-mod-skill-main/zip-cache`。显式 `DST_ZIP_CACHE_DIR` 仍优先；不迁移或清理旧缓存。

`check_skill` 在遍历前排除第三方 `mod-notes`、冻结知识包、`.git`、缓存、虚拟环境和链接目录，校验唯一根入口及文档/元数据中的旧调用；仅编译 Python 文本，不执行工具。检查通过不代表被排除资料或游戏行为已验证。维护回归使用系统临时目录，不创建第二个真实 skill。

`knowledge` 在进入目录前排除 `mod-notes`、素材、历史包、测试夹具和链接，只检索根入口、普通 Markdown 参考和指定物品名表；不会沿文档链接读取外部 Mod。结构化包通过原服务另行检索。范围、读取步骤与维护规则见 [知识查询入口](../knowledge/README.md)。

---

## general/（13 个）

| 工具 | 用途 |
|---|---|
| `bundle_release.py` | 打包 mod 发布 |
| `init_dst_mod.py` | 初始化新 DST mod 项目 |
| `dst_zip_tool.py` | 读取官方 scripts.zip（工作区不可用时搜索源码） |
| `dst_zip_cache.py` | 缓存 scripts.zip 内容 |
| `tex_atlas_tool.py` | 处理纹理图集 / TextureConverter |
| `anim_scml_tool.py` | 处理 SCML 动画 |
| `scml_build_tool.py` | 构建 SCML 动画 |
| `resize_png.py` | 调整 PNG 尺寸 |
| `read_pdf.py` | 读取 PDF 内容 |
| `check_skill.py` | 单入口、旧调用、文档路径及扫描范围内 Python 工具的内存语法自检，不生成 pyc |
| `check_api.py` | 分开核对主组件/Replica 的直接调用声明；未知、动态和未覆盖项要求人工核对，不等于运行验证 |
| `check_missing_anim.lua` | 检测丢失动画文件（调试动画不显示） |
| `dst-mod-tool.md` | DST Mod Tool（动画工具 CLI/Lua API）调用指南——AI 驱动动画导入/编辑/预览/导出 |

> 用法示例散见模式文档：`references/patterns/asset/`（tex/scml）、`references/mod-bootstrap.md`、`references/official-files.md`、`references/task-playbook.md`。
> DST Mod Tool 完整 API 见 `references/tools/general/dst-mod-tool.md`；工具内置指南用 `DST Mod Tool.exe script --help --lang zh-CN` 随时查看。

### API 声明检查

从 skill 根目录运行，显式路径优先；无显式来源时使用 `DST_SCRIPTS_DIR`，否则按 `dst_zip_tool.py` 定位官方 scripts.zip。解包目录可直接传 `D:\mods\scripts`，也接受含 `scripts/` 的父目录。

```powershell
python -B references/tools/general/check_api.py path/to/target.lua --scripts-dir "D:\mods\scripts"
python -B references/tools/general/check_api.py path/to/target.lua --dst "E:\SteamLibrary\steamapps\common\Don't Starve Together"
python -B references/tools/general/check_skill.py --strict
python -B references/testing/test_check_api.py
```

| 退出码 | 结果 | 后续动作 |
|---|---|---|
| `0` | MATCHED：扫描到的直接调用与对应端源码声明匹配 | 继续核对签名、执行端、生命周期并做运行测试 |
| `1` | FAIL：官方组件对应端未找到方法声明 | 检查拼写、主组件/Replica 区分及动态注入 |
| `2` | ERROR：输入不存在、目录无 Lua 或源码索引无效 | 修正路径/来源后重跑，不当作通过 |
| `3` | REVIEW：别名、动态字段、计算索引、未知方法或零直接调用 | 人工追踪源码；未核对完不能宣称 API 已通过 |

词法检查只覆盖 `components.name:Method(...)`、`replica.name:Method(...)` 与 `inst:Method(...)` 等直接形式。别名与计算索引会提示核对；它不做完整 Lua 类型/控制流分析，也不证明所有间接调用都已覆盖。注释和字符串不作为调用扫描；普通字段不作为已确认的方法。

源码目录与权限统一见 [开发边界与验证约定](../development-contract.md)。

### 融合工具

整个 Mod 的 Lua 语法和自定义组件核对用 `engineering/scripts/check_api.py`；已有快速文件扫描器保留原退出码。新增工具的 `DECLARED` 仅表示对应端声明存在，`NEEDS_REVIEW` 需追踪继承/注入等路径；退出 `1` 为语法错误，`2` 为待查、无直接调用或输入/依赖错误。别名与动态调用仍须人工覆盖。

用法、依赖、许可与回归命令见 [融合工程入口](../engineering/dst-mod-engineering/README.md#执行工具)。工程知识的默认配置与查询命令见 [知识入口](../knowledge/README.md)。新增 runner 只用于已授权的 Windows 离线单分片测试；工具回归不代替饥荒实机测试。

---

## testing/（5 个，macOS 原版）

平台状态：配置仍采用 `.app/Contents/MacOS`，进程工具使用 `ps/pgrep`，注入工具依赖 `fcntl`。Windows 尚未适配，Linux 也不能直接套用 macOS 路径；本次结构/语法检查不是跨平台运行验证。不要在未授权的游戏目录或真实存档上运行 setup、start、stop 或 Lua 注入。

| 工具 | 用途 |
|---|---|
| `game_config.py` | 路径集中配置（env 覆盖） |
| `game_process.py` | 启停/查询专用服务器进程 |
| `game_log.py` | 读 server_log.txt（tail/grep/follow） |
| `run_script.py` | 向运行中服务器注入 Lua 并取回结果 |
| `setup.py` | 安装测试 mod 进游戏目录 + 幂等配置 |

> 流程、坑点与 Windows 移植见 `references/testing/dst-server-test-toolchain.md`（文档仍留在 testing/，工具已上收此处）。

---

## reverse/（5 个）— 目标专用的静态分析底本

| 工具 | 已记录的用途 |
|---|---|
| lol_dump.py | 分析特定 LOL! wrapper 的 VM 数据与常量 |
| daogui_full.py | 特定旧目标的主入口恢复实验 |
| daogui_scripts.py | 特定旧目标的脚本恢复实验 |
| daogui_worldgen.py | 特定旧目标的世界生成恢复实验 |
| daogui_plants.py | 特定旧目标的植物/生物恢复实验 |

这些工具可能硬编码旧目标、路径、字母表和 VM 映射。复用前先读实现与依赖，用本任务已授权输入在独立输出目录验证；不能仅因存在 LOL! 或 daxsg_tn 标记就运行。工具名字与旧结果不证明新目标使用相同算法，也不保证能恢复完整源码。

分析流程按 [静态分析专题](../reverse-engineering/GUIDE.md) 执行：辨识外层变换、Lua chunk/字节码/VM 数据、加载链与各脚本的差异，保存每层指纹并对可逆变换做反向检查。仅凭魔数无法断言“新版必不可恢复”。需要比较历史案例时读 [解密案例与保护形态](../reverse-engineering/decryption-case-patterns.md)，其中的工具、参数、映射和结论都只适用于各自记录的目标快照。命名与目录只支持模块划分推测，不支持具体行为结论。

本条目不触发读取对应 Workshop Mod 或历史笔记。需要用户明确点名授权目标；启动 loader、专服或注入运行环境按相应授权与隔离方案处理。静态无法恢复时写清所卡层与缺少证据，再整理实际读到的内容，不把运行未知脚本作为默认回退。

---

## 就近工具（各子技能 tools/，非本目录）

### dst-assets-animation-atlas/tools/ — KTEX 解码族（4 个）

| 工具 | 用途 |
|---|---|
| `ktex_decode.py` | 单文件 tex → PNG 快速解码 |
| `ktex_batch.py` | 目录批量解码 + 像素统计（色板/饱和度/明暗/alpha） |
| `ktex_ascii.py` | 小纹理 ASCII 预览（无需 Pillow，快速目检图标/UI） |
| `dst_tex_analyze.py` | 全量分析：KTEX 解析 + DXT1/DXT5 解码 + PNG 写出 + 格式/尺寸统计（研究主工具） |

- 用途：KTEX 是 DST 纹理容器（magic `"KTEX"`）。格式判定：低 16 位 `0x2220` 族=DXT5、`0x2200` 族=DXT1；数据区 `== w*h*4`=8-bit RGBA 无压缩（官方人物模板 esctemplate 全 tex 皆此格式，`ktex_decode.py` 自动识别）。
- 文件间存在 `from ktex_decode import ...` 依赖，须同目录使用。
- 格式细节见 `references/world-ui-assets/dst-assets-animation-atlas/references/ktex-format.md`。

### 其他就近工具

- `references/gameplay/dst-worldgen-authoring/tools/`：世界生成（dump_options.lua 重生成 overrides 合法值词表、save_inspect.lua 存档只读检查）
- `references/world-ui-assets/dst-character-parts/tools/`：人物部位（scml_analyze/char_sheet_gen/audit_parts/scml_parts_plan + esc_parts.json）
  - `scml_analyze.py`：解析 Spriter SCML → 部位规范表（folder 帧数/尺寸/pivot/z 区间/动画清单）→ Markdown 与 `-j` JSON；`char_sheet_gen.py`：`--parts-json` 生成空白 1024x512 RGBA 动画贴图模板，`--check` 核验贴图尺寸与 SCML 标准一致。
- `references/core/dst-source-research/tools/`：源码检索（scan-dst-source.ps1）＋逆向探查（probe_require.py）
- `references/engineering/dst-api-update-diff/tools/`：源码快照对比（snapshot-dst-source/compare-dst-snapshots）
- `references/world-ui-assets/dst-make-scml-animation/tools/`：analyze_scml.py
- `references/world-ui-assets/dst-texture-style/tools/`：analyze_textures.py

> 通用约定：多数工具输出默认当前目录 `out/`，可用参数覆盖；中文路径 OK（os.walk 处理非 ASCII）。

### 知识正文维护标记

knowledge docs/lookup/read 增加 maintenance 元数据；catalog 汇报 review_registry 的匹配、失效和未登记数量。其来源为 references/knowledge/review-status.json，按文档 SHA256 匹配；记录缺失或失效不阻断原文检索。

record_current 只表示本轮记录对应当前正文，不自动表示当前安装源码相同、API 对本任务有效或游戏运行通过。工具不跟随登记文件的目录联接，不扫描受限笔记/素材，不因登记项新增读取路径；历史结构化包的来源与证据等级保持原服务语义。
