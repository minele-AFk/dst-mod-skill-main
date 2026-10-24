# HealthBadge：生命徽章接口与客户端数据

2026-10-22 对照本机安装 widgets/healthbadge.lua → badge.lua → widget.lua 的继承链，以及 statusdisplays.lua、components/health_replica.lua。它是原版生命表现控件，不是 health 组件，也不会替项目建立网络同步。

## 构造与数值

`HealthBadge(owner, art, iconbuild)` 需要实际 owner；当前构造会访问 owner:HasTag 并监听 owner 事件。不要照抄无 owner 的 HealthBadge()。模块需显式 require("widgets/healthbadge")。

| 接口 | 当前合同 |
|---|---|
| HealthBadge:SetPercent(val, max, penaltypercent) | val 是比例，max 用于显示数值，penaltypercent 是生命上限惩罚比例 |
| Badge:SetPercent(val, max, bonusval) | 基类第三参为 bonusval，与 HealthBadge 第三参不是同一语义 |
| PulseGreen()/PulseRed() | 基类提供的脉冲反馈，不代替真实生命数据 |
| StartWarning(r, g, b, a)/StopWarning() | 基类警告表现 |
| SetPosition/SetScale/Show/Hide/Kill | 继承 Widget 的布局与生命周期 |

当前这条继承链没有可直接调用的 GetPercent、SetMax、SetValue 或通用 SetColour 合同。数据从实际 Replica/读取函数取得，不把显示控件当业务数据源；自定义颜色需要定位具体 Image/Text/UIAnim，不按相似方法名猜调用。

## 显式 owner 与数据读取示例

下面是可视客户端函数片段，parent 是已挂载到正确缩放根的 Widget，owner 是当前有效本地玩家。它只建立一次展示与主动刷新；没有自动注册全部状态事件或提供完整 HUD。

```lua
local HealthBadge = require("widgets/healthbadge")

local function RefreshHealthBadge(badge, owner)
    local health = owner.replica.health
    if health ~= nil then
        badge:SetPercent(health:GetPercent(), health:Max(), health:GetPenaltyPercent())
    end
end

local function CreateHealthBadge(parent, owner)
    local badge = parent:AddChild(HealthBadge(owner))
    badge:SetScale(1)
    RefreshHealthBadge(badge, owner)
    return badge
end
```

项目按实际本地事件继续刷新，初次 Replica 未就绪时沿真实附着链补绑定；不要在客户端回调中改读服务器 inst.components.health。原版 StatusDisplays 会管理惩罚、受伤反馈、幽灵模式和多种角色状态，另造徽章时要明确自己承担哪些部分。

服务端 PushEvent("healthdelta") 不会仅凭同名自动跨网；事件绑定、初值与换角色/幽灵生命周期按 [HUD 合同](../world-ui-assets/dst-hud-screens-input/references/hud-customization.md)。

## 原版扩展点与表现边界

StatusDisplays 构造心形徽章时会检查 owner.CreateHealthBadge(owner)，否则使用原版 HealthBadge；需要替换角色生命徽章时核对此扩展点，不复制整个 Controls/StatusDisplays。

原先“低于 30% 自动变红”的固定规则不作为通用合同。HealthBadge 的箭头、屏蔽、惩罚与动画依赖 owner 状态及原版回调；需要变化时查对应来源，不把 PulseRed、警告色与永久颜色混为一谈。

与 HungerBadge/SanityBadge 组合时分别引入各自模块和核对参数，不假设它们全部共用 HealthBadge 合同。布局、文本、Hide/Kill 与输入清理统一见 [Widget 合同](../world-ui-assets/dst-ui-widget-authoring/references/widget-contract.md)。

## 验证

检查初值/后续刷新、最大值与惩罚变化、缺失 Replica、幽灵/复活、换角色、重建、重连和不同 HUD scale。以上示例未在游戏中运行，不代表原版资源、反馈和主客机行为已通过。
