# Widget 契约：构造、布局、输入与生命周期

2026-10-22 对照本机安装 `data/databundles/scripts.zip` 的 widget、screen、frontend、text 等文件；具体指纹保存在本轮审阅证据中。历史行号不再冒充当前定位；没有进行客户端视觉或输入验收。

## 模块定义与扩展

自有控件放 `scripts/widgets/my_mod_widget.lua`，通过 `require("widgets/my_mod_widget")` 加载；模块返回类，不在全局作用域创建实例。Screen 放 `scripts/screens/`，继承 widgets/screen，见 [Screen 示例](../../../widgets/screen.md)。

```lua
local Widget = require("widgets/widget")
local MyModWidget = Class(Widget, function(self, owner)
    Widget._ctor(self, "MyModWidget")
    self.owner = owner
    -- 在这里构造本项目需要的稳定子树；此骨架没有可见内容或业务。
end)
return MyModWidget
```

Image、Text、UIAnim、Button、ImageButton 等各自从 widgets 对应模块引入，不能假定它们的方法都属于 Widget。具体控件从 [Widget 专题](../GUIDE.md) 选择。数据变化通过 Refresh/SetValue 等项目接口更新，不反复重建稳定节点。

现有类使用模组环境 AddClassPostConstruct(package, postfn)，package 为 widgets/controls 等 require 风格路径。它包装 _ctor，在原构造后运行 postfn；这是后续每个实例的构造补丁，不是当前已存在实例的自动迁移。补丁层级选择见 [UI 补丁模式](../../../patterns/ui/ui-patch-patterns.md)。

## 树与生命周期

Widget 构造带 UITransform、uianim 和 UI/widget 标签的 self.inst，并持有 children 集合。children 以子 Widget 为 key；仅保存 Lua 引用不会挂载。`parent:AddChild(child)` 同时建立 Widget 树与实体父级。

- RemoveChild(child) 只断开父子关系，不调用 Kill；缓存池或替换节点自行决定是否销毁。
- Kill 停止更新、递归 KillAllChildren、脱离父树并停止内置 FollowMouse，最后移除 self.inst。当前实现不保证将 self.parent 置 nil，不能据此判断存活。
- Hide 保留实例与子树；Hide/Show 调用 OnHide/OnShow，不能拿隐藏替代关闭、销毁或撤销全局输入。
- self.inst 移除会处理其任务与 EntityScript 事件监听；同一存活 Widget 换绑 owner/item/source 时，先从旧 source 精确 RemoveEventCallback。不要 RemoveAllEventCallbacks 清掉其他功能。
- Widget 默认静态时间任务在暂停时继续；UpdateWhilePaused(false) 切换到模拟时间任务并调整 uianim，亦可按需求用 self.inst.DoSimTaskInTime/DoSimPeriodicTask。挂在 owner 上的任务由 owner 管理，不随 Widget 自动结束。

每个外部注册都有明确拥有者和撤销点；重复注入、提前停用、换绑和最终 Kill 是不同路径。

## 布局与层级

SetPosition 使用父节点局部坐标；GetWorldPosition 用于跨父树定位，不直接等于任意屏幕坐标。

| 目标 | 接口/条件 |
|---|---|
| 固定屏幕边缘或中心 | 根节点 SetHAnchor/SetVAnchor，再以局部偏移 SetPosition |
| 保持内容比例 | SCALEMODE_PROPORTIONAL，按水平/垂直较小缩放 |
| 铺满背景 | 图像 H/V anchor、H/V region point 与 SCALEMODE_FILLSCREEN；会拉伸美术 |
| 固定屏幕比例 | SCALEMODE_FIXEDSCREEN_NONDYNAMIC 以 1280x720 窗口缩放为基准；FIXEDPROPORTIONAL 另考虑控制台安全区 |
| 文本区域对齐 | SetRegionSize 后设置 HAlign/VAlign |
| 图片自身对齐点 | Image:SetHRegPoint/SetVRegPoint |
| 同父级前后次序 | MoveToFront/MoveToBack |

不要让装饰节点抢鼠标：SetClickable(false)。HUD 部件选正确 Controls 缩放根，参见 [HUD 挂载](../../dst-hud-screens-input/references/hud-customization.md)。

GetScale 返回累计父级缩放 Vector3，GetLooseScale 返回本级三个数值。简单同锚点下可按“屏幕点减父原点再除累计缩放”换算；anchor、region 等变换另查，不把这个公式推广到任意树。

FollowMouse 直接使用鼠标屏幕坐标，不保证嵌套缩放后仍适配。拖拽保存按下偏移，并在松键、失焦、关闭与 Kill 时结束，不为一个面板修改所有控件坐标规则。

## 焦点与输入

Widget 的 OnControl、OnRawKey、OnMouseButton 在无焦点时返回，并分发给已获焦点子节点。覆写通常先保留基类消费路径；有意抢占时明确范围，未处理分支交回默认行为。

```lua
-- 放在上面模块的 return MyModWidget 之前；OnActivate 为项目提供的回调。
function MyModWidget:OnControl(control, down)
    if MyModWidget._base.OnControl(self, control, down) then
        return true
    end
    if self.focus and control == CONTROL_ACCEPT and down
        and self.OnActivate ~= nil then
        self:OnActivate()
        return true
    end
    return false
end
```

SetFocusChangeDir(MOVE_UP, target) 等定义方向关系；导航目标需 IsVisible 且 enabled。重建 Grid/List、分页或隐藏条目后重算路径，并让父 Screen/HUD 提供初始焦点。普通 Widget 不伪装为 Screen。

这里的 true 是 UI 责任链的消费结果。**TheInput 全局事件句柄回调不采用同一消费合同**，其参数、分派与清理由 [TheInput 合同](../../../systems/theinput.md) 统一说明；输入方式的选择见 [输入模式](../../../patterns/runtime/input-patterns.md)。

## 更新、事件与清理

StartUpdating/StopUpdating 管理 TheFrontEnd 的 updating_widgets 集合。当前前端只检查 enabled，不检查 shown；隐藏节点仍可能执行 OnUpdate。

- 首选数据事件、Replica dirty 通知和显式 Refresh，只有连续动画、跟随或按住重复等需求才逐帧更新。
- OnHide 停止不再需要的更新，OnShow 按需求恢复；不要假设 Hide 自动暂停更新和静态任务。
- 实体事件用 self.inst:ListenForEvent，保存回调引用；换绑时精确撤销旧 source。
- 全局 TheInput handler 由本功能保存并 handle:Remove，关闭或 Kill 前明确清理；Widget 树不管理任意外部句柄。
- UI 不权威推进资源，按钮的真实游戏意图经 [Action](../../../core/dst-action-authoring/GUIDE.md) 或 [网络入口](../../../core/dst-networking-rpc/GUIDE.md) 在服务器重新验证。

## 文本与集合

可变长文本先定义区域、对齐和换行：SetRegionSize、SetHAlign/SetVAlign、EnableWordWrap。

- 单行 SetTruncatedString 的当前源码注释提示未优化，且与 SetRegionSize 混用可能无限循环；不机械叠加。
- 多行有限区域用 SetMultilineTruncatedString，明确行数、宽度、每行字符限制与是否缩小字体；当前源码建议用它替代 SetAutoSizingString。
- 清空动态 Grid/List 时销毁旧项，再重建数据和方向焦点，不能只覆盖 Lua 引用。
- Badge 基类 SetPercent(val, max, bonusval) 与 HealthBadge:SetPercent(val, max, penaltypercent) 第三参含义不同，参见 [HealthBadge](../../../widgets/healthbadge.md)。

## 查找范例

| 需求 | 当前原版入口 |
|---|---|
| 纯状态展示 | widgets/badge.lua、bloodover.lua |
| 键鼠与手柄按钮 | widgets/button.lua、imagebutton.lua |
| 网格/列表/分页/重复 | widgets/grid.lua、scrollablelist.lua、pagedlist.lua、spinner.lua |
| 响应式根与文本区域 | widgets/scripterrorwidget.lua |
| HUD 根、缩放与玩家绑定 | widgets/controls.lua、screens/playerhud.lua；按 [HUD 生命周期](../../dst-hud-screens-input/references/hud-customization.md) 接入 |

## 提交前检查

创建、隐藏、显示、换绑、销毁和重建后不留输入、任务或旧数据源回调。鼠标/键盘/手柄可完成主操作并离开自定义区域；长文本、窄屏、超宽屏、UI scale 和暂停分别验证。声明与语法检查不能证明这些场景已通过。
