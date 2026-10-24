# 反伤（阈值超标反弹 / 防套娃）

讲解一种可复用的「受击反伤」实现：单次伤害超过阈值时，把**超出部分**打回攻击者。代表实证：棱镜子圭玄鸟（创意工坊 1392778117 `scripts/prefabs/boss_siving_phoenix.lua`）。

## 适用场景

- Boss / 坦克装：惩罚高伤爆发，低伤、多段更安全  
- 「荆棘」「反震」类被动：有阈值、不是全额百分比  
- 需要避免两个反伤单位互弹死循环时  

## 一、阈值超标反弹（玄鸟式）

### 语义

```text
反伤量 = max(0, 本次伤害 - 阈值)
阈值内不反；只反超出部分
```

### 常量（可按难度配置）

```lua
local ATK_HUTR = 130 --反伤上限/阈值；0 = 关闭反伤
```

### 核心写法

```lua
inst:ListenForEvent("attacked", function(inst, data)
    local atker = data.attacker
    if atker == nil or not atker:IsValid() or atker:HasTag("playerghost") then
        return
    end
    if ATK_HUTR <= 0 or data.damage == nil or atker.components.combat == nil then
        return
    end

    if data.damage > ATK_HUTR then
        -- attacker 传 nil：不把「被打者」标成攻击者，避免触发对方盾反/对攻击者逻辑
        atker.components.combat:GetAttacked(nil, data.damage - ATK_HUTR)
        -- 可选：播荆棘特效
    end
end)
```

### 数值示例（阈值 130）

| 单次伤害 | 反弹 |
| --- | --- |
| 80 | 0 |
| 130 | 0 |
| 200 | 70 |
| 500 | 370 |

### 为何 `GetAttacked` 第一个参数是 `nil`

- 若把 `inst`（玄鸟自己）当 attacker 传入，对方可能再触发「被 XX 攻击时」的反击/盾反  
- 注释原意（棱镜）：**为了不受到盾反伤害，不设定玄鸟为攻击者**  
- 需要「算作被某实体打」时再传实体；只要纯反伤数值，用 `nil` 最安全  

## 二、百分比反伤（对照）

```lua
-- 例：反弹最终伤害的 50%（无阈值）
atker.components.combat:GetAttacked(nil, data.damage * 0.5)
```

| | 阈值超标 | 百分比 |
| --- | --- | --- |
| 低伤 | 不反 | 照样反 |
| 高伤爆发 | 重罚超出部分 | 线性 |
| 设计感 | 防秒、鼓励控伤 | 通用荆棘 |

可组合：`min(percent * damage, damage - threshold)` 等，写清公式即可。

## 三、防死循环（必做）

两个单位都带反伤时，`A 反 B → B 反 A → …` 会无限互弹。

常用约束（择一或组合）：

1. **阈值/上限**：低伤不反（玄鸟）  
2. **限次**：对同一攻击者在一次反击窗口内最多反 N 次（棱镜 `shieldlegion`：举盾期间对同目标只反 1 次）  
3. **attacker = nil**：削弱「对方把这次当成被你攻击」的链路  
4. **单向**：只有 NPC/Boss 有反伤，玩家侧装备不叠同类逻辑  
5. **标记**：反伤造成的伤害打上 `cause`/标记，带标记的伤害不再触发反伤  

```lua
-- 盾思路示意：一次举盾对同对象只反击 1 次
-- if self.atkents[attacker] ~= nil then return end
-- self.atkents[attacker] = 1
-- attacker.components.combat:GetAttacked(doer, dmg, ...)
```

## 四、和其它机制的边界

| 机制 | 区别 |
| --- | --- |
| 真实伤害 | 让**这一次攻击**穿透减伤（见 [custom-damage-settlement-and-rollback.md](../../../core/dst-hooking-compatibility/references/custom-damage-settlement-and-rollback.md)） |
| 反伤 | **被打后**把伤害打回去；本身仍可被对方护甲/抗性结算 |
| 位面/特殊伤害反伤 | 需另带 `spdamage` 表；百分比反伤通常只反普攻数字 |
| 荆棘甲类 | 常挂在玩家护甲：`onhitother` 或护甲被击路径；注意耐久与限次 |

若反伤也要无视护甲：对 `atker` 再套真伤标记，或 `health:DoDelta(..., ignore_absorb=true)`（一般不推荐无脑真伤反伤）。

## 五、使用注意

- `data.damage` 是 **`attacked` 事件里的伤害字段**，通常是结算后的受击值，不是武器面板原始值；以你监听的事件字段为准  
- 幽灵、无效实体、无 `combat` 的目标要先判掉  
- 联机：反伤逻辑应在**服务端**  
- 难度/配置：阈值做成可配（简单档可直接 `0` 关闭）  

## 关键点

- 阈值语义：`只反 (damage - threshold)`  
- `GetAttacked(nil, …)` 优先于传自己，防盾反套娃  
- 必须有阈值/限次/单向之一，避免互弹  
- 与真伤文档互补，不要把反伤写成「强制穿透后再反」除非技能明确要  

官方/实证：DST `components/combat.lua`（`attacked` / `GetAttacked`）；棱镜 `boss_siving_phoenix.lua`（阈值反伤）、`components/shieldlegion.lua`（限次反击）、`prefabs/siving_related.lua`（护甲反伤特效路径，按需查阅）。
