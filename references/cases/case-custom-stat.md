# 自定义能量与法力：存档、Replica 与 HUD 初始同步

基础数值的可保存主组件与真正 netvar Replica 见 [最小组件案例](case-custom-component.md)，本页只补充可变上限、消耗与界面合同，避免再维护一份分叉实现。

用于能量条、魔力/法力等自定义资源。房主正常但客机首次显示零，先查初始同步与 HUD 绑定；退出重进后丢值，另查保存与恢复，两条链不能互相代验。普通 Lua 字段不产生网络同步，周期读取也不能修复字段从未复制的问题。

## 值模型

先定义 current/max 的范围、精度、上限变化时保持比例还是绝对值、死亡/离线/重选行为。max=0 时定义百分比与可用性，不直接 current/max 产生无效值。

所有权威写入汇合到 setter；它负责范围、网络写入和本地业务通知。Class 属性代理可作入口，但不是同步本身，也不是必须方案。组件构造中不要从 inst.components 取回尚未挂入的自己。

## 可变上限的复制

max 和 current 都需客户端读取时，两者分别建立真实网络值或选择明确编码结构；普通 self.max/current 表无法跨网。多个 netvar 的 dirty 不构成业务事务，显示层要容忍初始化/变化中的暂缺，读取当前完整可见值再刷新。

Replica 提供 GetCurrent/GetMax/GetPercent 等项目自己实现的只读接口。命名与注册使用私有前缀；没有原版“自动复制任意字段”的通用方法。

## 消耗与恢复

请求表达动作意图，由服务器确认当前值、冷却、拥有者和目标，再结算一次。UI 百分比只是展示，不能提交余额或“资源足够”的客户端断言。失败不扣费、不启动新冷却。

在线恢复按模拟时间和当前上下限计算；是否离线追赶由设计决定。保存当前值与必要上限依据，不把运行时任务句柄放进存档。恢复 max/current 与 modifier 使用可重复计算公式，避免加载顺序导致满血/叠乘。

## 客机首次进入：HUD 绑定与初值

- 显式 require Widget/Text/Badge 等依赖，使用实际存在的图集或纯文本起步。
- 在 Controls 或目标状态栏构造完成后 AddChild；房主也显示，不用 not ismastersim 过滤。
- 先读取初值，再监听约定 dirty；source 与事件生产端一致。
- 暂缺显示占位或隐藏，不永久当作 0 掩盖同步失效。
- 关闭/换绑时移除旧监听、长寿命 owner 任务及输入句柄。
- ghost 显示沿真实复制状态处理初次入场、死亡、复活和重连，不只包装后续一次 SetGhostMode。

## 验收

验证小数/边界/max=0、上限改变、服务端拒绝、重复请求、旧档缺字段、真实客机初值和重连。数值正确、网络到达与状态条实际显示分别验收。

[组件合同](../core/dst-component-authoring/references/component-contract.md) · [HUD 实例](../world-ui-assets/dst-hud-screens-input/references/hud-customization.md) · [法术与数值线索](../engineering/dst-mod-engineering/spells-and-custom-stats.md)
