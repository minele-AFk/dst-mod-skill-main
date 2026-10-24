# `useabletargeteditem`：定向使用与停止使用物品

> 源码复核：2026-10-23，本机安装 `759671` 的 `components/useabletargeteditem.lua`、`componentactions.lua`、`actions.lua` 与 `prefabs/security_pulse_cage.lua`。未运行游戏动作测试。

当库存物品需要对世界目标执行一次 `USEITEMON`、可停止的持续使用，或需要禁止在库存中直接切换时，使用此组件。它负责“开始/停止使用”的物品状态与目标动作 tag；具体效果、成功条件和资源变化由 Prefab 的 `SetOnUseFn` 实现。

## 接口

| 接口 | 合同 |
|---|---|
| `SetOnUseFn(fn)` | `fn(inst, target, doer)` 返回 `success, failreason`；没有回调时视为成功 |
| `SetOnStopUseFn(fn)` | `fn(inst)`，停止使用时调用 |
| `StartUsingItem(target, doer)` | 执行使用回调；成功且实体仍有效时，按设置切换 `inuse_targeted` |
| `StopUsingItem()` | 清除 `inuse_targeted` 并调用停止回调 |
| `CanInteract()` | 当前未处于使用中时为 true |
| `SetInventoryDisable(value)` | 使用中是否禁用库存操作；维持 `useabletargeteditem_inventorydisable` tag |
| `SetCanSelfTarget(value)` | 是否允许物品以使用者为目标；tag 名保留源码拼写 `useabletargateditem_canselftarget` |
| `SetUsingItemDoesNotToggleUseability(value)` | 成功使用后是否仍保持可再次交互，不进入使用中状态 |
| `SetTargetPrefab(prefab_name)` | 维护 `<prefab>_targeter` tag，供动作收集筛选目标 |
| `SetUseableMounted(enable)` | 是否允许骑乘时使用；维护 `useabletargeteditem_mounted` tag |

客户端可配置 `inst.UseableTargetedItem_ValidTarget = function(inst, target, doer)` 来缩小候选目标；这个查询用于动作收集，服务器执行时仍必须由 `SetOnUseFn` 重新校验。组件当前没有同名 `SetValidTarget` 方法，不要猜一个不存在的服务端接口。

## 动作链

物品处于使用中时，库存动作会收集 `STOPUSINGITEM`；未使用时，对合法目标收集 `USEITEMON`。`USEITEMON.fn` 在服务端调用 `StartUsingItem`。若回调返回 false，动作失败并返回原因，不会把物品置为使用中。`SetInventoryDisable(true)` 只在进入使用中后阻止库存交互；回调执行期间仍需 Prefab 自己防止重复调用或提前移除实体。

`SetOnUseFn` 返回成功只表示动作可以继续；若 Prefab 随后移除或替换物品，调用方仍须检查实体是否有效，并明确新物品进入哪个库存或地面位置。`StopUsingItem` 不自动撤销已经发生的世界效果、资源消耗或生成实体。

## 原版完整例子

`security_pulse_cage_full` 是可装守卫的笼子：

1. 公共区设置 `UseableTargetedItem_ValidTarget`，只允许空的 `vault_key_activator` 或已制作的守卫。
2. 服务端添加组件并设置 `SetOnUseFn`。
3. 对脉冲基座推送 `ms_depositspark`；对守卫先拒绝金库房间内的目标，再生成脉冲并激活守卫。
4. 成功后生成新的空笼，把旧物品的 `prevcontainer` 与 `prevslot` 交给新笼，再优先交给玩家库存，失败时落在地上；最后移除满笼。

这个例子展示了“目标筛选 → 服务端重验 → 世界效果 → 返还/替换物品 → 保留容器位置”的完整边界。它不是通用成功模板：空笼、守卫和脉冲的数值、资源及房间规则都属于原版玩法。

## 验证

检查合法/非法目标、成功与失败返回、使用中再次点击、停止使用、库存禁用、骑乘、自身目标、重复请求、目标消失、物品在动作中途转移，以及成功替换后的容器槽位和远端客户端菜单。源码与静态动作链通过不代表真实输入、预测或服务器拒绝路径已验证。
