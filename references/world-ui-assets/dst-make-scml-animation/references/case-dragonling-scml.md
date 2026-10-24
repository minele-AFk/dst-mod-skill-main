# Dragonling 伙伴生物 SCML 案例

记录日期：2026-10-20。参考对象是用户提供的
`D:\mods\资料包\dragonling` 工程；用户说明原作者已同意公开引用。本笔记只提炼制作和审计方法，不复制 PNG，也不把整份 SCML 收入 skill。

## 适用范围与证据

这份工程适合用来学习“伙伴生物（critter）动画的完成度判断和续做”，不适合当作敌对生物的全套模板。当前证据分三层：

1. 工程事实：对 `dragonling_build.scml` 和 `dragonling_build.autosave.scml` 做 XML、PNG、时间轴和引用检查。
2. 运行时契约：核对本机安装包 `data/databundles/scripts.zip`（SHA-256：`f8d7cff2e9f86cdab3de08c6e750ecec2986c9bc95b364724f4c77244a798bf1`，仅代表本机快照）中的 `scripts/stategraphs/SGcritter_common.lua`、`scripts/stategraphs/SGcritter_dragonling.lua` 和 `scripts/stategraphs/commonstates.lua`。`SGcritter_common.lua` 使用 `idle_loop`、`walk_pre/loop/pst`、`eat_pre/loop/pst`、`emote_nuzzle`、`emote_pet`、`emote_combat_*`、`interact_active/passive` 与 `distress`，随机表情入口也可到达 `emote_cute`；它本身没有 `sleep_*` 动画调用。`SGcritter_dragonling.lua` 注册 `CommonStates.AddSleepExStates` 并增加睡眠/唤醒事件，具体 `sleep_pre/loop/pst` 播放由 `commonstates.lua` 的该 helper 提供。Dragonling 专属图还为 `emote_bounce`、`emote_yawn`、`emote_flame` 绑定时间事件，并在睡眠、落地和起飞阶段处理飞行状态。
3. 未执行：没有用 Spriter/OpenSpine 打开工程做画面回放，没有用官方 Mod Tools 编译 `anim/*.zip`，没有加载游戏，也没有检查联机两端。下面的结论不能写成实机验收通过。

## 工程快照

| 项目 | 正式版 | 自动保存版 |
|---|---|---|
| 文件 | `dragonling_build.scml` | `dragonling_build.autosave.scml` |
| 最后写入时间 | 2026-01-13 11:29:26 | 2026-03-06 21:02:17 |
| SHA-256 | `3AA7A6C0EEF0283CE98EC93946C1FD407D3AA0AC65316CC473C332441A56F20B` | `D9398FA38AA9D3A48A4F51A57122C05C429EF8375D6A6F89E11F54F5FC38A20B` |
| generator | `BrashMonkey Spriter r11` | 同左 |
| entity | `dragonling` | 同左 |
| folder / file 声明 | 9 / 71 | 9 / 71 |
| animation | 32 | 32 |
| 动作总长 | 32 段均使用 33ms interval | 同左 |
| 时间轴 | 9,843 个 timeline key，全部 `instant` | 数量相同 |
| 骨骼引用 | 0 个 `bone_ref` | 0 个 `bone_ref` |
| 工程引用 | 缺图、断链、越界路径均为 0 | 同左 |
| PNG 声明尺寸 | 5 处与实际 IHDR 不符 | 3 处不符 |

两份文件不能按文件名猜版本。自动保存版的写入时间更晚，`head/head-0.png`、`body/body-0.png` 的声明尺寸与正式版不同且更接近实际 IHDR，但仍有 `wingflap/wingflap-0.png`、`wingflap/wingflap-1.png`、`wingflap/wingflap-2.png` 三处不符。另有少量 pivot 精度变化和动作轨道变化；这些差异是否代表修正或最终稿，尚未用 Spriter 画面确认。在选择续做基线前应重开两份工程并做画面差异审查，不能直接覆盖正式版。

71 张 PNG 按内容哈希分成 12 组重复内容：`head/head-4-0.png` 与 `head/head-4-1.png` 为一组；`tailwhip-2` 到 `tailwhip-20`（偶数编号）的 `-0/-1` 文件各为一组，共 10 组；`tailwhip-0-0.png`、`tailwhip-0-1.png`、`tailwhip-22-0.png`、`tailwhip-22-1.png` 构成一组四文件重复内容。重复不自动等于错误，但必须核对它是刻意的左右配对、循环端点，还是复制后尚未改画。`mouth/mouth-2.png` 在 9,843 个 timeline key 中没有被任何动作引用，应标为未使用候选，而不是直接删除。

## 可复用的动作族

工程的动作按伙伴生物职责组织，而不是按“每段都做成攻击”组织：

| 动作族 | 本工程名称 | 运行时职责 |
|---|---|---|
| 常驻 | `idle_loop_side`、`idle_loop_downside`、`idle_loop_upside` | 待机、转向后的常驻姿势 |
| 行走三段 | `walk_pre_*`、`walk_loop_*`、`walk_pst_*`，每段有 side/downside/upside | 起步、持续移动、停下 |
| 进食三段 | `eat_pre`、`eat_loop`、`eat_pst` | 接到进食事件后播放 |
| 睡眠三段 | `sleep_pre`、`sleep_loop`、`sleep_pst` | 入睡、持续睡眠、醒来 |
| 情绪/表情 | `emote_bounce`、`emote_flame`、`emote_nuzzle`、`emote_yawn`、`emote_cute`、`emote_pet` | 随机表情、互动和专属表现 |
| 警戒/玩耍 | `emote_combat_pre`、`emote_combat_loop`、`emote_combat_pst`、`interact_active`、`interact_passive`、`interact_*_upside` | 伙伴的警戒、主动玩耍、被动回应 |
| 饥饿 | `distress` | 饥饿或不满表现 |

这些动作与运行时调用链的对应关系已按上方列出的本机安装源码核对，不是从 SCML 名称反推。

不能从本工程推出“伙伴生物只需要这些动作”。专属 StateGraph 可能追加动作或事件。更关键的是，本工程没有 `hit`、`death` 或独立攻击段。若目标 prefab 会受伤、死亡或参战，必须按目标 StateGraph 补齐并做状态衔接检查。

## 方向与换图

- 侧向动作使用 `*_side`，正面/背面动作使用 `*_downside` 和 `*_upside`。本工程没有用 `*_down`/`*_up` 命名，说明动作名应以消费代码为准，不能套通用模板。
- 本工程在 32 段中主要用 `side/downside/upside` 三套朝向；`interact_active` 与 `interact_passive` 还各有一个 `*_upside` 变体。不要把 side 的镜像规律直接套到正面/背面。
- 多方向动作大量通过同一 timeline 切换 `folder/file` 换图，例如 head、body、claw 的不同朝向和表情帧。检查时要同时看 `object_ref` 的 timeline/key 和 object 的 folder/file，不能只看文件名。
- 层级不是全程固定。`distress`、`emote_bounce`、`emote_cute`、`interact_active` 等动作出现 2 到 6 种 z_index 排列；转身、抬爪、尾巴扫过身体和落地时需要逐帧检查遮挡。
- 动作中同时出现正负 scale 和接近 ±180° 的 angle。它们是该工程的姿势数据，不能因为“看起来不标准”就统一转正；应先还原到画面确认。

## 半成品审计流程

拿到类似“有 SCML、有 PNG、可能还有 autosave”的工程时，按以下顺序做只读审计：

1. 记录 `.scml`、`.autosave.scml`、PNG 目录的路径、大小、最后写入时间和 SHA-256；先确认要续做的基线。
2. 用 `dst-make-scml-animation/tools/analyze_scml.py` 检查 XML、ID、引用、时间网格、PNG 存在性和声明尺寸。
3. 统计动作名、方向后缀、`length`、`interval`、mainline/timeline key 数量和 `curve_type`；不要只看工程能否打开。
4. 统计每个 `folder/file` 的引用次数和所属动作，找出未使用图片、重复图片和只在单一动作出现的换图。
5. 统计每个动作的 z_index 排列、负 scale、pivot 和轨道数量，定位转身、抬爪、落地等高风险片段。
6. 到目标 StateGraph、prefab 和 common states 中搜索实际动作名、循环参数和 `TimeEvent`，建立“动作名 → 调用点 → 事件帧”表。
7. 用编辑器逐段回放并导出关键姿势，重点看首帧、末帧、循环接缝、接地、层级、镜像和换图；XML 通过不代表画面通过。
8. 只有完成官方编译和隔离加载后，才把结果写成“可交付”或“游戏通过”。

本工程的实际审计命令：

```powershell
& '.\.codex\venvs\dst-skill\Scripts\python.exe' `
  '.trae\skills\dst-mod-skill-main\references\world-ui-assets\dst-make-scml-animation\tools\analyze_scml.py' `
  'D:\mods\资料包\dragonling\dragonling_build.scml'
```

正式版返回 `Validation issues: 5`，全部来自 PNG 声明尺寸；XML 引用、时间网格、ID 和路径检查为 0 问题。自动保存版返回 `Validation issues: 3`，仍不能直接判为可交付。

## 续做顺序

如果要把这份工程补成可运行资源，建议按以下顺序，而不是直接增加新动作：

1. 冻结一个基线副本，保留正式版、自动保存版和全部 PNG；先修复 PNG 声明尺寸或确认工具链为何接受旧尺寸。
2. 用目标代码列出动作清单和方向，标记已有、缺失、未使用和命名不一致项；至少确认 `idle`、`walk_*`、`eat_*`、`sleep_*`、`distress`、`emote_*`、`interact_*` 的调用条件。
3. 先修共用部位和方向换图，再修单段动作。不要先加攻击/死亡，导致基础待机和行走仍无法回放。
4. 为每个动作补关键姿势和事件表，尤其是 `emote_bounce` 的落地、`emote_flame` 的火焰出现、`eat_*` 的咬合、`sleep_*` 的入睡/醒来。
5. 处理未使用和重复图片时先保留原文件，记录它们在哪个动作、哪个时间、哪个方向出现；删除必须有用户明确授权。
6. 在 SCML 检查通过后，用官方 Mod Tools 编译 `anim/*.zip`，再在隔离测试 prefab 和世界加载。编译成功仍不等于动作画面和联机状态通过。

## 常见误判

- “文件更新”不等于“版本更完整”：自动保存版可能只修了尺寸，也可能留下未保存的动作改动。
- “XML 可解析”不等于“动画可播放”：缺图、尺寸错误、层级和 pivot 仍需逐项检查。
- “32 段动作”不等于“生物完成”：缺少受击、死亡、攻击或特定状态时，不能拿伙伴动作表冒充完整战斗动作表。
- “PNG 重复”不等于“无用”：可能是左右配对、循环端点或刻意复用；先查引用和画面。
- “bone_ref 为 0”不等于“没有骨骼”：烘焙后的 SCML 可以是逐帧对象轨道；原始工程是否用骨骼，要看 Spriter/OpenSpine 工程和导出流程。
- “动作里有负 scale”不等于“数据损坏”：先确认方向和 pivot，再做修正。
