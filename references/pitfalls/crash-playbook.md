> 来源：原手册吸收自 Zechariah0121/dst-mod-devkit；2026-10-18 按本库源码合同纠正旧规则，方法与来源见 [纠错索引](old-rule-corrections.md)。

# 崩溃与行为异常：症状、调查入口与验证

本表提供调查顺序，不把同一症状认定为唯一根因。先记录实际副本、运行端、复现步骤和第一条相关错误的完整堆栈；从本轮实际启动日志定位，不把旧日志或另一分片的结果当成本次证据。日志中的 Workshop 路径不授予读取该 Mod 的权限。

## 启动与模块加载

| 症状 | 优先核对 | 下一步 |
|---|---|---|
| Error loading file prefabs/... | PrefabFiles 对应的脚本路径、大小写、语法、加载依赖 | 一个文件可返回多个 Prefab；文件名不必等于注册名。按 [Prefab 合同](../core/dst-prefab-authoring/references/prefab-contract.md) 追注册链 |
| TheWorld / TECH / GLOBAL 等为 nil 或未声明 | 当前脚本环境、模块导入、发生阶段及实际对象 | 世界尚未创建时延后相应逻辑；不以一段 env 元表代理修复所有问题。见 [Lua 环境](../core/dst-lua-runtime/GUIDE.md) |
| 自定义入口变量在组件中不可见 | env 变量是否只存在于入口、require 缓存和依赖传递 | 明确传入配置或使用项目模块，不把 TUNING/STRINGS 当任意跨文件变量仓库 |
| 找不到 XML / TEX / ANIM | 声明路径、实际运行副本、资源依赖和大小写 | 核对目标文件与哈希；不得用整目录覆盖或删除素材来碰运气 |
| modinfo 加载失败或配置值异常 | Lua 语法、配置 default、运行端与本地配置语义 | GetModConfigData 第二参不是默认值；nil 兜底保留 false/0。见 [脚手架](../core/dst-mod-scaffolding/GUIDE.md) |

## 外观、动画、贴图与声音

| 症状 | 优先核对 | 下一步 |
|---|---|---|
| 手持不显示或换形态只房主可见 | 实际 bank/build/symbol、挂载、装备链、客户端初值和后续更新 | 三种名字职责不同，无需统一为同名；按 [角色装备美术](../engineering/dst-mod-engineering/character-and-equipment-art.md) 查真实符号 |
| Could not find anim bank | 动画 bank 与加载依赖、当前动画是否存在 | 不用 buildname 代替 bank；换符号包可能只有 build，按用途核对 ZIP 结构 |
| 原生崩溃、长动画无法加载 | 首个失败资源、编译产物、纹理尺寸/页、引用、动画数据与客户端日志/转储 | 没有 60/149 帧通用硬上限。用隔离的最小资源比较定位，见 [资源合同](../world-ui-assets/dst-assets-animation-atlas/GUIDE.md) |
| 白方块、黑色 FX、透明边缘异常 | 原始 RGBA、图集 Element/sampler、材质、乘色与加色 | 先看原尺寸和每个实际 FX；加色不是所有黑块的修法，不自动重绘或改资产 |
| FX 房主正常、客机无变化 | 公共初始设置、网络状态、dirty 回调、房主刷新与专服分支 | 静态公共设置按同类 Prefab 安排；动态外观由状态驱动各客户端，不把全部设置移到 SetPristine 前 |
| 声音无声或播放即崩 | bank/event 路径、声明、编译格式、触发端与实际听者 | 专服日志不证明声音通过；见 [音频专题](../world-ui-assets/dst-audio-camera-effects/GUIDE.md) |

资源重编译在隔离副本上完成，保留源工程与原输出；按引用重新构建并核对目标，不删除整个 anim 目录。渲染、pivot、帧序、透明边缘和听感各有实际验收记录。

## 组件、状态与事件

| 症状 | 优先核对 | 下一步 |
|---|---|---|
| attempt to call method ... nil | 接收对象、主组件/Replica、动态注入、初始化时机 | 声明查到不代表参数或当前运行端正确。按 [组件合同](../core/dst-component-authoring/references/component-contract.md) 查定义及调用者 |
| stackable_replica 数值编码错误 | maxsize 实际赋值、当前编码表与扩展协议 | 不把历史几种堆叠数写成永久容量白名单，核对当前 stackable 与 Replica |
| HUD 首次为 0、之后更新正常 | 权威初值、netvar 创建、绑定对象、第一次读取和 dirty 源 | 普通字段不跨网，Class setter 不等于网络机制。见 [自定义属性](../cases/case-custom-stat.md) |
| 事件触发却无效 | PushEvent 的实际 data、事件源、监听时序与 SG/Brain 分发 | data 可能是表、实体或其他值；普通监听与 SG 调度分别追踪，不能统一按下一帧理解 |
| 保存/重连后数值丢失或叠加 | 保存层、恢复顺序、派生值、重复任务和 modifier 来源 | 区分组件返回 data 与实体填写 data；组件加载无固定顺序。见 [存档合同](../core/dst-persistence-migration/GUIDE.md) |
| 物品交给别人后效果仍在旧玩家 | 持有者换绑、旧来源撤销、跨实体任务/监听 | 明确 effect owner，按来源清理；恒温共享字段不得盲目恢复。见 [携带被动能力](../gameplay/dst-status-buffs-survival/references/carried-passive-buffs.md) |

## 料理、网络与测试环境

| 症状 | 优先核对 | 下一步 |
|---|---|---|
| 菜能吃却煮不出，调味后图标丢失 | cooker 注册、test/priority/weight 的当前选择合同、产物 Prefab、调味变体、图鉴与台词 | 不用固定 priority 阈值压过所有菜；见 [料理完整链路](../engineering/dst-mod-engineering/cooker-dishes.md) |
| RPC 静默或某端报错 | namespace/name 双方注册、发送方向、参数、当前玩家身份与权限 | namespace 是显式注册值，不必等于目录名；Server/Client/Shard 分别查合同 |
| Widget 挂载或关闭报 nil | 实际控件树、Widget.inst、owner、本机显示阶段与清理 | Widget 可有 inst；不要凭旧示例猜 controls 字段，见 [HUD 与输入](../world-ui-assets/dst-hud-screens-input/GUIDE.md) |
| 房主可以、远端材料不足也成功 | 主机快路径和远端入口是否经过同一权威业务检查 | 确认拥有者、材料、距离、冷却及重复请求；客户端数量仅是视图 |
| 端口占用或测试残留 | 本轮 manifest、进程身份、日志中的实际端口、启动权限 | 只结束自己启动且身份可确认的进程；不按固定 10999 端口杀无关服务 |
| 测试报告互相矛盾 | 运行 ID、完成标记、异步错误、退出码与对应日志 | 记录命令不等于执行，旧 PASS 不是本轮结果；见 [隔离测试](../engineering/dst-mod-engineering/testing-release.md) |

修改后重放原复现，并覆盖受影响的失败、取消、移除、保存和主客机路径。静态声明、专服行为、真实客户端和资源效果分别报告；没有执行能力时写明可确认范围及下一步证据。
