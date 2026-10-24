# 自定义动作系统实战指南

六种收集签名、注册分层与故障路由统一见 [Action 完整链路](../../core/dst-action-authoring/references/action-pipeline.md)。本页保留可改造示例、BufferedAction 回调与技能设计边界。

## 一、注册一个右键世界动作

下面放在 **modmain.lua 模组环境**。示例只投递项目事件：目标需有 inspectable，并在公共初始化区加入 `my_mod_action_target` 标签；项目另行监听 `my_mod_action` 实现业务。没有提供目标 Prefab、资源和业务消费者，不是完整 Mod，也未实机运行。

```lua
local G = GLOBAL
local MY_ACTION = AddAction("MY_MOD_ACTION", "执行操作", function(act)
    if not G.TheWorld.ismastersim then
        return false
    end
    local doer, target = act.doer, act.target
    if doer == nil or not doer:IsValid()
        or target == nil or not target:IsValid()
        or not target:HasTag("my_mod_action_target")
        or doer:GetDistanceSqToInst(target) > 9 then
        return false
    end
    -- 实际业务应在此再次核对权限、资源、冷却与目标状态。
    target:PushEvent("my_mod_action", { doer = doer })
    return true -- 表示投递成功，不表示未知事件消费者已完成玩法。
end)
MY_ACTION.priority = 2
MY_ACTION.distance = 3
MY_ACTION.rmb = true

AddComponentAction("SCENE", "inspectable", function(inst, doer, actions, right)
    if right and inst:HasTag("my_mod_action_target") then
        table.insert(actions, MY_ACTION)
    end
end)

AddStategraphActionHandler("wilson", G.ActionHandler(MY_ACTION, "dolongaction"))
AddStategraphActionHandler("wilson_client", G.ActionHandler(MY_ACTION, "dolongaction"))
```

`AddAction` 已写默认动作字符串；本地化可再设置对应 STRINGS.ACTIONS 键。EQUIPPED/USEITEM 等入口按合同更换签名与资格，不照抄 SCENE 参数。

自有组件 collector 还要提供客户端动作组件注册/Replica；上例借已有 inspectable，不能据此省掉其他组件的网络接入。自定义生物使用其内部 SG 名和真实存在的执行状态，不假设所有 SG 都有 doaction 状态。

## 二、Action 属性的边界

| 属性 | 用途与注意点 |
|---|---|
| priority / rmb | 候选优先级与按钮语义，collector 同时按 right 筛选 |
| instant | 即时执行路径；非 instant 通常需要 SG 表演 |
| distance / mindistance / arrivedist | 距离与接近策略，最终服务器业务仍核对可达性 |
| canforce / rangecheckfn | 按具体调用链处理强制动作/范围，不是绕过全部限制或同步坐标 |
| mount_valid / encumbered_valid / ghost_valid | 骑乘、负重、幽灵资格；按实际玩法开放 |
| paused_valid / floating_valid | 对应环境资格，需核对调用者与状态支持 |
| invalid_hold_action | 影响按住按钮后的动作续用，playercontroller 不把它保存为 lastheldaction；不是“手持物品时无效” |
| actionmeter | 动作计量表现的标记；不自动扣除某种资源或动作条 |
| do_not_locomote / skip_locomotor_facing | 移动/朝向策略，不代替执行校验 |
| pre_action_cb | 客户端和服务器都可能调用，不能放一次性权威扣费 |

不需要时保持默认值。字段存在不代表任意状态、载具或输入设备都支持其组合。

## 三、BufferedAction 回调与执行

构造签名：`BufferedAction(doer, target, action, invobject, pos, recipe, distance, forced, rotation, arrivedist)`。

下面为 **服务器端、实例已具备 locomotor 和目标动作 SG 映射** 的辅助函数。action 是上节 AddAction 返回值；这是可复用片段，不重新注册全局动作。

```lua
local function QueueAction(doer, target, action)
    if not TheWorld.ismastersim or doer == nil or not doer:IsValid()
        or doer.components.locomotor == nil
        or target == nil or not target:IsValid() then
        return false
    end
    local ba = BufferedAction(doer, target, action)
    ba.validfn = function(buffered)
        return buffered.target ~= nil and buffered.target:IsValid()
            and buffered.target:HasTag("my_mod_action_target")
    end
    ba:AddSuccessAction(function()
        if doer:IsValid() then doer:PushEvent("my_mod_action_success") end
    end)
    ba:AddFailAction(function()
        if doer:IsValid() then doer:PushEvent("my_mod_action_fail") end
    end)
    doer.components.locomotor:PushAction(ba, true)
    return true -- 已提交，不表示未来一定执行成功。
end
```

`validfn` 接 BufferedAction，success/fail 回调无参数。`ba:IsValid()` 检查当前资格；`ba:Do()` 在执行 Action.fn 后调用成功/失败，通常交 SG 的 PerformBufferedAction 触发。`ba:Succeed()/Fail()` 是完成操作，不在 Do 之后重复手动完成。`doer:PushBufferedAction(ba)` 可走直接开始路径，不等于替你完成寻路接近。

普通字段 `pos` 包装为 DynamicPosition；用 `GetActionPoint()` 获取可为空的世界坐标，`GetDynamicActionPoint()` 获取动态位置对象。最终执行还要验证持有物所有权与目标状态，队列开始时的资格不能代替执行帧验证。

## 四、技能动作与投射物

技能用 SCENE 还是 POINT 取决于目标是实体还是落点，不因“火球”名称决定。自有技能组件、CanCast 方法、projectile Prefab 都是项目依赖，不能当成原生 API。

实施顺序：客户端显示资格 → 玩家预测/预览 → 服务器重新验证施法者、目标/落点、距离、冷却、资源、持有物 → 创建有效载体并确认其组件/发射合同 → 按明确成功点扣费与记冷却 → 命中时由约定组件结算伤害。生成失败和中断要有失败策略；不要先扣费再无条件使用可能为 nil 的 SpawnPrefab 结果。

没有通用 EntityScript:Consume() 消耗物品合同。按 stackable、finiteuses、消耗整件等实际语义选择组件路径并处理移除；不要用未知方法替代。投射物 Throw 的攻击者/武器参数、命中和归属见 [战斗专题](../../gameplay/dst-combat-weapons-projectiles/GUIDE.md)。法术载体和自定义属性见 [法术参考](../../engineering/dst-mod-engineering/spells-and-custom-stats.md)。

复用玩家已有状态前核对装备、动画和数据依赖；自定义法术不能仅把 ActionHandler 指到 shoot 就视为完整预测实现。

## 五、官方动作选择

| 行为 | 官方 ID（还需匹配组件与资格） |
|---|---|
| 攻击/进食 | ATTACK、EAT |
| 砍/挖矿/挖掘/采集/收获/敲击 | CHOP、MINE、DIG、PICK、HARVEST、HAMMER |
| 建造/部署/存入/给予 | BUILD、DEPLOY、STORE、GIVE |
| 物品/装备使用 | USEITEM、USEEQUIPPEDITEM |
| 法术/闪烁 | CASTSPELL、BLINK |

这些 ID 取自 ACTIONS。USEITEM 与 USEEQUIPPEDITEM 在当前 actions.lua 均存在；复用时读其执行函数，不把 ID 本身当作自定义技能业务。

2026-10-21 对照本机安装包 actions.lua、bufferedaction.lua、componentactions.lua、modutil.lua、playercontroller.lua 和 SGwilson/SGwilson_client；未完成游戏内输入、预测、扣费和投射物验收。
