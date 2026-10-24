# 饥荒联机版 Mod 开发工具包

面向《饥荒：联机版》（DST）Mod 开发的 AI Skill，集成开发知识、源码查证、代码检查与美术资源制作流程。

从角色、装备和技能，到联机同步、世界生成、界面与动画制作，按任务定位需要的知识，再结合原版源码完成设计、实现与验证。既可以作为 AI 助手的开发知识库，也可以直接阅读文档、使用命令行工具。

**50 个专题入口 · 35 份组件参考 · 3,000 余条物品代码名与中文名称映射**

[快速开始](#快速开始) · [知识分类](#知识分类) · [工具能力](#工具能力) · [完整文档目录](references/topic-index.md)

## 可以用它做什么

| 开发需求 | 提供的支持 |
|---|---|
| 制作角色、生物与 Boss | 角色结构、属性与技能、Brain 行为树、状态图、攻击时序、形态切换和生命周期 |
| 制作物品、装备与料理 | 武器护甲、装备效果、背包容器、合成科技、食谱调味、植物生长与物品交互 |
| 实现联机功能 | 主客机职责、网络变量、Replica、RPC、动作预测、后加入同步与跨分片交互 |
| 制作界面与操作 | HUD、Widget、Screen、快捷键、手柄输入、拖拽、法术轮盘和自定义属性显示 |
| 制作贴图与动画 | 参考风格分析、透明贴图、图集、人物拆件、骨骼绑定、SCML 工程与官方资源编译 |
| 排查问题与适配更新 | 日志定位、源码调用链追踪、API 声明检查、存档迁移、兼容性分析和版本差异评估 |

## 知识分类

### 一、核心开发基础

覆盖 Mod 从入口到运行时的基础结构，以及容易影响联机与存档的底层契约。

| 方向 | 主要内容 | 文档入口 |
|---|---|---|
| 项目结构与 Lua | modinfo、modmain、模块环境、GLOBAL、Class 与脚手架 | [项目脚手架](references/core/dst-mod-scaffolding/GUIDE.md) · [Lua 运行时](references/core/dst-lua-runtime/GUIDE.md) |
| 实体与组件 | Prefab 构造、Component、Replica、初始化与移除 | [Prefab](references/core/dst-prefab-authoring/GUIDE.md) · [组件](references/core/dst-component-authoring/GUIDE.md) |
| 联机与动作 | 网络变量、RPC、权威执行、BufferedAction、动作收集与预测 | [联机同步](references/core/dst-networking-rpc/GUIDE.md) · [动作系统](references/core/dst-action-authoring/GUIDE.md) |
| 生命周期与存档 | 事件监听、定时任务、清理、保存加载、引用恢复与数据迁移 | [事件与任务](references/core/dst-events-tasks-lifecycle/GUIDE.md) · [持久化](references/core/dst-persistence-migration/GUIDE.md) |
| 查证、调试与兼容 | 原版调用链、Hook、函数包装、日志分析与最小复现 | [源码研究](references/core/dst-source-research/GUIDE.md) · [兼容性](references/core/dst-hooking-compatibility/GUIDE.md) · [调试测试](references/core/dst-debugging-testing/GUIDE.md) |

### 二、角色、战斗与玩法系统

| 方向 | 主要内容 | 文档入口 |
|---|---|---|
| 人物与技能 | 角色创建、技能树、专属能力、形态与跨系统组织 | [角色开发](references/gameplay/dst-character-authoring/GUIDE.md) · [技能树](references/gameplay/dst-skilltree-authoring/GUIDE.md) |
| 生物与 AI | 生物和 Boss、Brain、行为树节点、状态图与动画事件 | [生物与 Boss](references/gameplay/dst-creature-boss-authoring/GUIDE.md) · [Brain](references/gameplay/dst-brain-authoring/GUIDE.md) · [状态图](references/gameplay/dst-stategraph-authoring/GUIDE.md) |
| 战斗与生存 | 武器、护甲、投射物、范围攻击、位面伤害、生存属性、Buff 与 Debuff | [战斗系统](references/gameplay/dst-combat-weapons-projectiles/GUIDE.md) · [属性与效果](references/gameplay/dst-status-buffs-survival/GUIDE.md) |
| 物品与生产 | 库存装备、容器、配方科技、食物料理、调味与植物再生 | [物品与容器](references/gameplay/dst-inventory-equipment-containers/GUIDE.md) · [合成科技](references/gameplay/dst-crafting-tech-prototypers/GUIDE.md) · [料理](references/gameplay/dst-food-cooking/GUIDE.md) · [植物](references/gameplay/dst-plants-farming-regrowth/GUIDE.md) |
| 随从与场景交互 | 宠物坐骑、建筑部署、Placer、物理、海洋、船与海钓 | [随从坐骑](references/gameplay/dst-followers-mounts-pets/GUIDE.md) · [建筑部署](references/gameplay/dst-building-deployment-physics/GUIDE.md) · [海洋系统](references/gameplay/dst-ocean-boats-fishing/GUIDE.md) |

### 三、世界生成与地图系统

| 方向 | 主要内容 | 文档入口 |
|---|---|---|
| 世界生成 | Location、Level、TaskSet、Task、Room、地形布局与生成规则 | [世界生成](references/gameplay/dst-worldgen-authoring/GUIDE.md) |
| 世界事件 | 天气、世界组件、周期事件与运行时世界逻辑 | [世界系统](references/gameplay/dst-world-systems-events-weather/GUIDE.md) |
| 布局与旧世界接入 | 静态布局、Setpiece、场景布置与 Retrofit | [布局与补丁](references/world-ui-assets/dst-worldgen-layouts-retrofit/GUIDE.md) · [场景与演出](references/world-ui-assets/dst-scenarios-setpieces-cutscenes/GUIDE.md) |
| 地图与分片 | 地皮、小地图图标、地图可见性、洞穴、传送与跨分片迁移 | [地皮与地图](references/world-ui-assets/dst-tiles-map-minimap/GUIDE.md) · [分片与传送](references/world-ui-assets/dst-shards-caves-portals/GUIDE.md) |

### 四、界面、输入与客户端扩展

| 方向 | 主要内容 | 文档入口 |
|---|---|---|
| 界面制作 | Widget、Screen、HUD、状态徽章、面板与界面生命周期 | [控件开发](references/world-ui-assets/dst-ui-widget-authoring/GUIDE.md) · [HUD 与输入](references/world-ui-assets/dst-hud-screens-input/GUIDE.md) |
| 客户端功能 | 纯客户端 Mod、建服前端与界面扩展 | [客户端与前端](references/world-ui-assets/dst-client-frontend-mods/GUIDE.md) |
| 文本与本地化 | 字符串组织、语言适配、人物检查台词与显示文本 | [本地化与台词](references/world-ui-assets/dst-localization-speech/GUIDE.md) |

### 五、美术资源、动画与表现

| 方向 | 主要内容 | 文档入口 |
|---|---|---|
| 贴图与图集 | 参考驱动的画风匹配、透明背景、原尺寸检查、XML/TEX 图集与资源注册 | [贴图制作](references/world-ui-assets/dst-texture-style/GUIDE.md) · [动画与图集](references/world-ui-assets/dst-assets-animation-atlas/GUIDE.md) |
| 人物拆件 | 部位清单、命名、尺寸、轴点、图层与静态拼合 | [人物拆件](references/world-ui-assets/dst-character-parts/GUIDE.md) |
| 动作与骨骼 | 三视图、拆件、OpenSpine 绑定、四方向动作、SCML 导出与官方编译接入 | [动作制作流程](references/world-ui-assets/dst-action-create-workflow/GUIDE.md) · [SCML 制作与审计](references/world-ui-assets/dst-make-scml-animation/GUIDE.md) |
| 外观变体 | Build、Symbol、皮肤切换、多部件覆盖与恢复 | [外观与符号覆盖](references/world-ui-assets/dst-skins-symbol-overrides/GUIDE.md) |
| 特效与听感 | FX、粒子、Shader、后处理、音效、音乐与相机表现 | [视觉特效](references/world-ui-assets/dst-fx-vfx-authoring/GUIDE.md) · [Shader](references/world-ui-assets/dst-shader-authoring/GUIDE.md) · [音频与相机](references/world-ui-assets/dst-audio-camera-effects/GUIDE.md) |

### 六、工程实践与专项分析

| 方向 | 主要内容 | 文档入口 |
|---|---|---|
| 质量与性能 | 性能热点、审查重构、最小修复与兼容边界 | [性能分析](references/engineering/dst-performance-profiling/GUIDE.md) · [代码审查](references/engineering/dst-mod-review-refactoring/GUIDE.md) |
| 测试与发布 | 独立专服测试、分片测试、资源核验与创意工坊发布准备 | [专服测试](references/engineering/dst-dedicated-server-testing/GUIDE.md) · [发布准备](references/engineering/dst-workshop-release/GUIDE.md) |
| 更新适配 | 源码快照对比、API 变化、受影响功能与回归范围 | [版本差异评估](references/engineering/dst-api-update-diff/GUIDE.md) |
| 授权静态分析 | 指定 Mod 的加载链、混淆层、字节码与架构分析方法 | [静态分析](references/reverse-engineering/GUIDE.md) |

## 查询与参考资料

- **组件参考**：按生存、战斗、存储、物品与系统分类，说明常用接口、调用条件及相关机制。[查看组件目录](references/components/)
- **物品名称表**：通过中文名定位代码名，或反查名称，减少凭印象填写 Prefab 的错误。[查看名称表](references/prefabs/物品名字.txt)
- **模式、案例与模板**：提供人物、装备、技能、UI、传送及自定义组件等实现线索。[查看详细目录](references/topic-index.md)
- **知识检索**：同时定位专题正文和有来源的结构化记录，支持中文描述、API 名、专题路由与原文行号读取。[查看查询方法](references/knowledge/README.md)

## 工具能力

| 工具类别 | 能做什么 |
|---|---|
| 源码读取与比较 | 定点查询安装版 scripts.zip，检索定义与调用，生成和比较源码快照 |
| Lua 与 API 检查 | 快速扫描直接调用，或使用 AST 检查整个 Mod 的 Lua 语法与组件声明 |
| 贴图与资源处理 | PNG 缩放、TEX 解码、图集处理、SCML 分析与编译辅助 |
| 工程辅助 | 创建 Mod 脚手架、检查动画资源、整理发布包 |
| 知识查询 | 查询本地文档、组件与物品名称，定位主专题和相关证据 |
| 测试与自检 | Windows 隔离专服测试，以及知识检索、工具与文档结构的回归检查 |

各工具的依赖、平台支持、参数和使用方法见 [工具台账](references/tools/README.md)。Windows 隔离测试与旧版 macOS 测试桥有各自的运行要求；源码与声明检查通过后，仍需按具体功能验证联机、存档、画面和声音。

## 快速开始

### 1. 获取项目

```bash
git clone https://github.com/minele-AFk/dst-mod-skill-main.git
```

将仓库放入所用 AI 工具支持的 Skill 目录，保持文件夹名为 dst-mod-skill-main，并确保 [SKILL.md](SKILL.md) 位于该文件夹根目录。统一通过这个入口调用，内部专题按需读取。

### 2. 描述你的任务

在支持该 Skill 的 AI 工具中，可以这样提出需求：

```text
使用 $dst-mod-skill-main，帮我制作一把带命中特效的武器，
先核对原版伤害与耐久接口，再实现装备、攻击与移除逻辑。
```

```text
使用 $dst-mod-skill-main，排查远端客户端技能按钮不显示的问题，
重点检查 Replica、网络变量初始同步和 HUD 创建时机。
```

```text
使用 $dst-mod-skill-main，根据参考图规划角色拆件与四方向动作，
明确 SCML 源工程、贴图和官方编译资源的交付要求。
```

也可以从 [完整目录](references/topic-index.md) 直接阅读需要的文档。

### 3. 按需使用命令行工具

Python 工具需要 **Python 3.10 或更新版本**；AST 检查需要 luaparser。资源处理按具体工具安装相应依赖，官方动画编译需要《Don't Starve Mod Tools》。涉及游戏源码时，提供自己的游戏安装目录或解包源码路径。

以下 PowerShell 命令在仓库根目录执行：

```powershell
# 查找相关文档
& ./references/tools/engineering/run.ps1 knowledge docs '物品温度' --limit 3

# 按任务同时查询本地文档与结构化知识
& ./references/tools/engineering/run.ps1 knowledge lookup '重连 效果残留 任务清理' --mode debug --limit 4

# 定位专题入口
& ./references/tools/engineering/run.ps1 knowledge topics --query '联机 RPC'

# 检查 Skill 文档与工具结构
& ./references/tools/engineering/run.ps1 check_skill --strict
```

## 项目结构

```text
dst-mod-skill-main/
├── SKILL.md                 统一调用入口
├── agents/                  Skill 展示与调用配置
└── references/
    ├── core/                核心开发与运行时
    ├── gameplay/            角色、战斗与玩法
    ├── world-ui-assets/     世界、界面与美术资源
    ├── engineering/         工程实践与版本适配
    ├── components/          组件接口参考
    ├── prefabs/             物品名称与代码名
    ├── patterns/            开发模式
    ├── cases/               实现案例
    ├── knowledge/           知识检索与专题路由
    ├── tools/               命令行工具
    └── reverse-engineering/ 授权静态分析
```

## 来源与使用

本项目包含持续整理的 DST 开发文档、工具与实践资料；部分工程参考和知识记录融合自 [dst-mod-engineering](https://github.com/Zechariah0121/dst-mod-engineering)，保留对应的 [来源说明](references/engineering/dst-mod-engineering/README.md#来源与融合范围) 与 [MIT 许可](references/engineering/dst-mod-engineering/LICENSE)。游戏及第三方内容的权利归各自权利人所有，使用相关材料时遵守其来源与许可。
