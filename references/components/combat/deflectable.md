# `deflectable`：可偏转实体

> 源码复核：2026-10-23，本机安装 `759671` 的 `components/deflectable.lua`。未运行偏转、反弹或多人战斗测试。

当某个实体本身可以作为可偏转对象，并且偏转后需要执行自定义回调或按规则移除时，使用此组件。它只负责“可偏转”的资格标记、拥有者与偏转回调；投射物的弹道和命中仍由 `projectile` 或 `complexprojectile` 管理。

## 接口

| 接口 | 合同 |
|---|---|
| 构造 | 自动添加 `deflectable` tag；移除组件时撤销 |
| `SetOwner(owner)` / `GetOwner()` | 记录偏转对象归属者，通常用于回调中的攻击来源或生成反弹 |
| `SetOnDeflectFn(fn)` | 回调签名 `fn(inst, owner, deflector)` |
| `SetKeepOnDeflect(keep)` | 非真时，`Deflect` 在回调后移除自身 |
| `Deflect(deflector)` | 调用偏转回调，再按 `keepondeflect` 决定是否移除 |

`Deflect` 不自动扣血、不反伤、不改变归属、不选择反弹目标，也不生成后续投射物。回调中的 `deflector` 是执行偏转的实体或组件调用者；项目若需要反弹，必须另建合法的攻击或投射物，并处理阵营、来源、重复偏转、伤害结算与清理。

`projectile` 和 `complexprojectile` 的 `Deflect(deflector)` 处理投射物自身的偏转状态与可选移除；`deflectable` 则描述可偏转的普通实体。不要用其中一个组件的存在推断另一条路径已经完成，也不要同时移除投射物又在回调里重复生成命中。

标准火把展示了投射物侧的自定义反弹：`complexprojectile:SetOnDeflect` 先停止旧运动，以偏转者为参照向相对方向外推约 3 格，使用短距离、低弧线重新发射，再恢复常规速度与高弧线；`SetKeepOnDeflect(true)` 让组件保留这个投射物。复用时必须重置运动状态、限制重复偏转和递归，并检查目标在回调中失效；组件的 `Deflect` 本身仍不负责反弹伤害或归属。

## 验证

检查无回调、有回调、保留与移除、owner 失效、偏转后再次命中、双方阵营、客户端表现和投射物所有权。需要反弹时另验证反弹来源、伤害只结算一次、递归偏转终止和目标被删除。静态合同与源码顺序通过不代表游戏内弹道已验证。
