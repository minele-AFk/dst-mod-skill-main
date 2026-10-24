# 设计案例：动态立绘的 UI 与资源合同

用于选人/皮肤搭配界面。保留“动画节点与静态肖像按角色切换”的做法，不把某一版控件的字段层级当作所有版本固定 API。

## 最小动画节点

```lua
local UIAnim = require("widgets/uianim")

local function AddAnimatedPortrait(parent, bank, build, animation)
    local node = parent:AddChild(UIAnim())
    node:SetClickable(false)
    local anim = node:GetAnimState()
    anim:SetBank(bank)
    anim:SetBuild(build)
    anim:PlayAnimation(animation, true)
    return node
end
```

parent 是调用者确认的布局容器，不能把可能被 Hide 的静态图片当作必定合适的父级。资源、动画名、缩放和位置来自本角色真实编译产物；上面没有提供它们，也没有验证客户端画面。

## 薄适配层

先读当前 widgets/redux/characterselect、loadoutselect 及其实际 portrait 控件，确认角色/皮肤更新由哪个方法完成、参数与初次构造顺序。PostConstruct 中创建一次节点，再窄包装真正更新方法；保留 self、参数、全部返回值和原副作用。

首次安装后主动按当前角色刷新，不只等下一次 SetPortrait。普通角色、目标角色、稻草人、返回主菜单和界面重建分别决定显隐。专服不加载 UI 功能，前端不假设有 TheWorld/ThePlayer。

## 皮肤、图层与清理

皮肤 build 不自动等于动画 bank；多皮肤使用明确映射与缺失回退，不能把 base 名直接同时喂 SetBank/SetBuild。UIAnim 的资源与世界 AnimState 的某些渲染合同不同。

隐藏静态图可选自身 owned 的显隐/alpha 策略，保存并恢复自己改变的状态；固定重置为全白可能覆盖其他 tint。布局容器、裁剪与缩放影响实际尺寸，位置数值不从旧案例冻结。

关闭/重建依靠 Widget 树销毁本节点，外部监听/输入仍按所属生命周期清理。重复更新不反复 new UIAnim，循环动画不永久额外挂全局任务。

## 验收

静态链核对 Asset、bank/build/animation、atlas 与引用；客户端检查首次进入、角色切换、皮肤切换、缺失资源、稻草人、窗口比例与多次开关。没有真实客户端时记录未测，不能把 Lua 可解析称为立绘完成。

[资源合同](../world-ui-assets/dst-assets-animation-atlas/GUIDE.md) · [Widget](../world-ui-assets/dst-ui-widget-authoring/references/widget-contract.md) · [角色资源](../world-ui-assets/dst-character-parts/GUIDE.md)
