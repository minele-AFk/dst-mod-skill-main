# damagetyperesist：按攻击者/武器标签匹配的倍率

源码复核：2026-10-18，components/damagetyperesist.lua。它不是一张引擎通用的火/冰/毒伤害枚举表，也不直接改变护甲吸收。

## 方法与数值

| 方法 | 合同 |
|---|---|
| AddResist(tag, src, pct, key) | 给指定 tag 添加来源倍率 |
| RemoveResist(tag, src, key) | 撤销相同来源/键 |
| GetResistForTag(tag) | 查询这个 tag 的来源乘积，缺省为 1 |
| GetResist(attacker, weapon) | 攻击者非 nil 时，匹配攻击者或武器 tag，乘入对应来源列表 |

pct 虽名为百分比，实际是伤害乘数：1 不变，0.5 为该路径一半，2 为两倍。对不同来源乘入 0.5 与 0.8，合成为 0.4；再乘一个 0.5 会进一步减伤，不是“减少抗性/穿甲”。

## 标签必须从实际实体获得

攻击者/武器是否具有某 tag 要查 Prefab 和消费者。fire、ice、melee、projectile、poison 不能凭英文名假定所有对应攻击都带有它。特殊伤害、防火、护甲和无敌另有自己的链路，不能用这一个组件承诺全部覆盖。

```lua
-- tag 是已确认会出现在目标攻击者/武器上的真实标签。
local function ApplyResist(target, tag, source, multiplier)
    target.components.damagetyperesist:AddResist(tag, source, multiplier, "my_mod_resist")
end

local function RemoveResist(target, tag, source)
    if target ~= nil and target.components.damagetyperesist ~= nil then
        target.components.damagetyperesist:RemoveResist(tag, source, "my_mod_resist")
    end
end
```

0 倍率只影响匹配且走此消费者的伤害，不等于所有伤害无敌；attacker=nil 的路径不执行该标签遍历。source/key 保持私有并对称撤销，不修改目标所有来源的总值当“穿甲”。

## 验证

分别用确有/无该 tag 的攻击者、武器带 tag、attacker=nil、两个来源结束、普通/位面与不同伤害管线测试。当前仅源码/示例检查，未运行战斗。

[combat](combat.md) · [武器与位面](../../gameplay/dst-combat-weapons-projectiles/GUIDE.md)
