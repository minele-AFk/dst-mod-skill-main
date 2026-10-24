# HUD 挂载、初值与角色生命周期

## 本地玩家与屏幕入口

ThePlayer 是本地玩家引用，通常在客机和房主存在，专服及初始化阶段可为 nil。直接访问 HUD 前同时检查 ThePlayer 与 ThePlayer.HUD；inst == ThePlayer 仅用于本地玩家判断，服务端业务执行者仍从 doer、owner、giver、attacker 等参数取得。

TheFrontEnd 管理 PushScreen、PopScreen、GetActiveScreen 和 GetSound():PlaySound 等本地界面行为。它不代表服务器权限，not TheNet:IsDedicated() 也不保证某个玩家 HUD 已构造。屏幕栈低层接口见 [TheFrontEnd](../../../systems/thefrontend.md)，控件树、坐标、暂停计时与清理统一见 [Widget 合同](../../dst-ui-widget-authoring/references/widget-contract.md)。

## 选择稳定入口

当前 PlayerHud:SetMainCharacter 设置玩家 HUD 引用并构造 Controls(owner)。Controls 构造完成后，ClassPostConstruct 可使用 self.owner 与已存在的缩放锚点；不依赖猜测的 player Prefab、一次零延迟任务或未查证的 hud_ready 事件。

以下为 modmain 的纯 UI 接入示意，MyModValue 是本专题模板对应的自定义 Widget；事件名和读值函数必须接入项目的真实复制数据：

```lua
local G = GLOBAL
if not G.TheNet:IsDedicated() then
    AddClassPostConstruct("widgets/controls", function(self)
        local owner = self.owner
        if owner == nil or self.my_mod_value ~= nil then
            return
        end
        local MyModValue = require("widgets/my_mod_value")
        self.my_mod_value = self.topleft_root:AddChild(
            MyModValue(owner, function(player)
                -- 示例接口，须由项目的 Replica 实现。
                local replica = player.replica.my_mod_energy
                return replica ~= nil and replica:GetCurrent() or nil
            end, "my_mod_energy_dirty"))
        self.my_mod_value:SetPosition(10, -40, 0)
    end)
end
```

这个示意不替你实现 my_mod_energy Replica。值未就绪显示占位，复制数据/引用就绪后按真实事件补绑定；不能靠永久显示 0 掩盖缺少同步。dirty 通知应由实际 netvar/本地转发产生并发到约定 source，任意服务端 PushEvent 不会自动到客机。

Controls 重建时新 Widget 跟随新树生成；缓存放对应 Controls，不能在玩家上保留已 Kill Widget 引用。房主也运行该路径，不能用 not ismastersim 过滤。

## 初次同步与幽灵

主动初次读取，再订阅变化；这是数据绑定合同，不是每个 HUD 都必须每帧轮询。StatusDisplays 初始构造可能暂用 SetGhostMode(false)，PostConstruct 后不能把临时 false 当真实角色状态。

本地玩家 ghost 显示沿 player_classified.isghostmode → OnGhostModeDirty → SetGhostMode → HUD/StatusDisplays。classified 尚未附着时等实际就绪链再绑定；已是幽灵进入世界也要正确刷新。其他玩家的私有 classified 未必对观察者可读。

respawnfromghost 是请求/流程入口，需要“复活完成”时跟踪服务端成功路径如 ms_respawnedfromghost；这类事件仍不自动跨网。自定义按钮在执行端校验状态、次数和消耗，界面隐藏不构成权限。

## 缩放、焦点与关闭

Controls 有多组 root/scale root；按目标位置选择锚点，用 AddChild 真正接入树。挂在父级缩放树后避免额外叠加一次全屏缩放；窗口比例、HUD scale 和边缘布局需实际检查。

Screen/Widget 输入方法保持原版返回值，true 表示该 UI 责任链已消费；TheInput 全局句柄回调返回值不会以同样方式消费事件，详见 [TheInput 合同](../../../systems/theinput.md)。聊天输入、暂停、控制禁用与手柄焦点分别决定是否处理。面板重复打开复用或聚焦，关闭清空所属 HUD 引用并撤销输入 handle/拖拽。

自定义 Widget 监听挂 self.inst，不是 Widget 本身直接调用 EntityScript 方法。Kill 会移除它的 inst，但外部注册的输入 handler 仍需自己 Remove；Hide 只隐藏，不能当作任务结束。

## OpenScreenUnderPause 与 SetModFocus

PlayerHud:OpenScreenUnderPause(screen) 在暂停屏已打开时用 InsertScreenUnderTop，否则 PushScreen；该方法编排屏幕，不自动开启游戏暂停。PlayerHud:SetModFocus(modname, focusid, hasfocus) 用命名空间标记模组焦点，打开和关闭使用同一 modname/focusid 释放自己的贡献；不替代 Widget:SetFocus 或全局输入消费合同。

## 资源与查证

- [可复用 Widget 模板](../assets/hud-widget-template.lua)：返回 Class，接收 owner、读值函数和本地事件。
- [Widget 合同](../../dst-ui-widget-authoring/references/widget-contract.md)：时间、坐标与清理。
- [HUD 与输入来源](../../../engineering/dst-mod-engineering/ui-actions-controls.md)。
- 2026-10-22 补查当前 playerhud 的挂载、OpenScreenUnderPause/SetModFocus，controls 构造与模板读取合同；ghost 细节仍沿目标版本完整调用链确认。

示例未运行游戏；验收主机/远端、初次入场、幽灵入场、复活、Controls 重建、重连与多分辨率。
