# 设计案例：技能树注册、效果与旧档

节点图、客户端选择、服务器生效和保存是四条协作链。当前字段/限制以 [技能树专题](../gameplay/dst-skilltree-authoring/GUIDE.md) 及 prefabs/skilltree_defs.lua、components/skilltreeupdater.lua 为准，不维护第二份依赖私有角色的“完整模板”。

## 注册数据

按现有公共模块 CreateSkillTreeFor 注册稳定角色名与 SKILLS；随后设置该角色的 SKILLTREE_ORDERS、BACKGROUND_SETTINGS，必要时设置 CUSTOM_FUNCTIONS。默认背景路径、图标和描述必须真正存在，不从旧 esctemplate 文件名推导本机已安装这份资源。

图标/背景先选择当前公开注册接口；仅缺少公开扩展点且源码可证时包装 GetSkilltreeBG 等函数，保留其他角色原返回值，避免无条件全局覆盖。

## 节点与图

每个节点使用唯一稳定 ID、pos、图标及当前要求的 title/desc。普通节点按 root/connects/locks 接入，defaultfocus 明确且不冲突；检查官方注册诊断和控制器默认焦点。

锁、隐藏/显示、点数、阵营和互斥分别读消费者，不以 UI 看不见作为服务器禁止。网络节点数按当前原版编码与诊断限制验证，不凭“Lua 表能放更多”绕过。

## 可逆效果

onactivate/ondeactivate 在权威链幂等应用/撤销；增益使用私有 source/key，不在 repeated load 再累乘当前值。客户端表现监听相应实际事件或复制状态，UI 不直接授予技能。

击杀 Boss 解锁等条件由真实权威事件与稳定进度计算；不信任客户端提交计数。改节点定义时，旧存档已选节点的删除、重命名和前置变化要迁移。

## 布局调试

可在独立开发工具中拖拽并记录坐标，但鼠标屏幕位置、父级局部坐标、HUD scale、offset 分开转换。聊天/控制器与关闭时清输入句柄，普通点击保留原行为。

print 输出日志与 ChatHistory 系统消息都是不同的观察方式，不规定“必须聊天输出”。不要把调试热键和全局函数无条件带入发布版。

## 验收

检查零点数/满点、互斥、锁图可达、旧档迁移、死亡复活、跨分片与真实远端同步；多分辨率和手柄另外验收。当前只核对合同，不代表任何角色技能树已经实际可玩。
