# UI 补丁层级与生命周期选择

当难点是由 controls、playerhud、临时 Widget、Screen 还是 frontend 拥有功能时读取。本页负责选择扩展点；[Widget 合同](../../world-ui-assets/dst-ui-widget-authoring/references/widget-contract.md) 负责控件本身，[HUD 合同](../../world-ui-assets/dst-hud-screens-input/references/hud-customization.md) 负责玩家绑定与初值。

## 层级模型

FrontEnd 管理屏幕栈及顶层前端根；Screen 提供激活/焦点/销毁基础；PlayerHud 编排世界内 HUD 根和弹窗；Controls 构造持久 HUD 子树；ContainerWidget 等功能控件管理每次打开的状态。它们是所有权边界，不是每个功能都要改五层。

## 快速路由

| 需求 | 优先入口 | 下一份材料 |
|---|---|---|
| 自有可复用控件 | scripts/widgets/<name>.lua | [Widget 专题](../../world-ui-assets/dst-ui-widget-authoring/GUIDE.md) |
| 持久仪表、状态栏邻接或布局 | widgets/controls | [HUD 挂载](../../world-ui-assets/dst-hud-screens-input/references/hud-customization.md) |
| HUD 覆盖层、弹窗编排、世界内屏幕生命周期 | screens/playerhud | 同上 |
| 容器打开时按钮/槽位/临时反馈 | widgets/containerwidget 等具体类 | 当前 Open/Close 与数据源 |
| 临时确认、通知或模态弹窗 | 自有 Screen 或 screens/redux/popupdialog | [Screen 模板](../../widgets/screen.md) |
| 共享屏幕焦点/激活/销毁 | widgets/screen | [Screen 合同](../../widgets/screen.md) |
| 屏幕栈/全局淡入淡出/前端声音/顶层文本管道 | scripts/frontend.lua | [TheFrontEnd](../../systems/thefrontend.md) |

选择实际拥有行为的最窄类。只打开自有 Screen 时调用 PushScreen，不需要为此覆写整个 frontend。

## `widgets/controls`：持久 HUD 子元素所有权

Controls(owner) 构造持久 HUD 子树并提供多组缩放根；在 ClassPostConstruct 中使用 self.owner，缓存放当前 Controls 实例。适合计数器、徽章、物品栏邻接或布局；不代替某个容器每次打开的状态，也不负责所有弹窗的堆栈。

完整 modmain 挂载示意见 HUD 合同，所需 Widget 的读取函数和事件应接项目真实 Replica；新 Controls 跟随新树重建，不复用旧的已 Kill 节点。

## `screens/playerhud`：屏幕拥有的 HUD 生命周期

PlayerHud 拥有 overlayroot、under_root、root、over_root、popupstats_root 等分支，并编排多种弹出界面。CreateOverlays 等路径可能重建分支，先确认自己节点的生命周期；构造时创建、分支重建时恢复和最终销毁分别处理。

单个状态控件通常先看 Controls；只有覆盖层排序、HUD 事件或弹窗编排确实归 PlayerHud 时才补丁此处。暂停屏幕与模组焦点的实际接口见 HUD 合同，不把 InsertScreenUnderTop 当成自动暂停 API。

## `widgets/containerwidget`：临时打开或关闭小部件

Open 创建/绑定当前容器的子节点、按钮和回调，Close 移除临时资源；同一实例可能为不同容器再次打开。按钮属于“本次打开”还是长期节点先明确，换容器前撤销旧数据源监听。

这类功能不应仅在构造时按第一次容器永久绑定，也不应在 Close 后留下全局输入响应。完整容器复制/slot 合同见 [container](../../components/storage/container.md)。

## `screens/redux/popupdialog`：干净的临时屏幕形状

模态确认与通知使用真正 Screen；配置 default_focus，保留 OnControl 的确认/取消和未消费返回值，Close 走 PopScreen。不要用一个没有焦点入口的普通 Widget 冒充屏幕。

自有模块在 scripts/screens 下，require 路径为 screens/<name>。可解析基础类见 Screen 模板；原版 popupdialog 提供按钮与默认焦点的具体例子。

## `widgets/screen`：共享屏幕生命周期

OnBecomeInactive 保存 last_focus，OnBecomeActive 尝试恢复有效 last_focus/default_focus。OnDestroy 默认 Kill 子树；覆写要先清自己的外部资源并保留基类销毁。

OnControl、OnRawKey、OnMouseButton 等仍沿 Widget/Screen 的焦点责任链；并非每个屏幕都必须覆写全部方法。焦点方向和控件输入实现回到 Widget 合同。

## `scripts/frontend.lua`：屏幕堆栈和前端根

FrontEnd 持有 screenstack/screenroot/overlayroot；PushScreen 令原栈顶失活并激活新屏，PopScreen 走移除/销毁并在栈顶变化时恢复当前屏。前端声音可从 GetSound 获取，不依赖世界实体 SoundEmitter。

只在要更改全局栈或前端根行为时补丁本类；普通 HUD、容器按钮、自有弹窗优先使用其自身扩展点。屏幕插入、获取活动屏和关闭细节统一见 TheFrontEnd 合同。

## 构造函数与活动/非活动与销毁

| 阶段 | 适合处理 |
|---|---|
| AddClassPostConstruct | 后续实例的稳定结构；包路径为 require 风格，原 _ctor 后执行 |
| OnBecomeActive/Inactive | 顶部覆盖与恢复、焦点和当前活动行为 |
| Open/Close | 功能级每次打开的数据绑定和撤销 |
| OnDestroy/Kill | 最终销毁与本功能外部资源清理 |

判断重复注入时区分：多个不同实例正常重建、同一实例被多次安装、模组注册本身重复。self.mychild 非 nil 只能保护该实例，不能解决长寿命全局 handler 的累加。

## 清理清单

分别登记输入 handle、EntityScript 回调、Screen 自有事件表、任务、临时子树和缓存引用；它们不使用同一套 Remove API。自己注册 TheInput 句柄用 handle:Remove；Screen:AddEventHandler 与 EntityScript:ListenForEvent 按各自合同撤销。

HUD/Screen 关闭时清缓存并停止拖拽，换绑时清旧 source，最终销毁保留基类行为。具体签名见 [TheInput](../../systems/theinput.md)、[Screen](../../widgets/screen.md) 和 Widget 合同。

## 焦点和控制器规则

给交互屏幕可达 default_focus，集合重建后重算方向路径；不能只验证鼠标。聊天、暂停、焦点禁用与控制器状态分别约束输入，不无条件吞掉取消或原版分支。

## 最小模式

- 自定义 Widget 定义与模块路径：[Widget 合同](../../world-ui-assets/dst-ui-widget-authoring/references/widget-contract.md#模块定义与扩展)。
- 带 owner/读取函数/事件的 HUD 挂载：[HUD 合同](../../world-ui-assets/dst-hud-screens-input/references/hud-customization.md#选择稳定入口)。
- Screen 继承、基类 OnControl、取消与栈关闭：[Screen](../../widgets/screen.md)。
- 全局输入与 Widget 输入的选择：[输入模式](../runtime/input-patterns.md)。
- UI 请求真实玩法：[Action 链](../../core/dst-action-authoring/references/action-pipeline.md) 或 [网络合同](../../core/dst-networking-rpc/references/network-contract.md)，客户端只发送意图。

2026-10-22 对照本机安装的 controls、playerhud、containerwidget、screen、frontend 与 modutil。声明与结构整理不证明 UI 层级、焦点、暂停、重连或真实输入已经验收。
