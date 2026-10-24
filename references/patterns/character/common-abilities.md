# 常用能力添加

当任务需要为玩家或角色添加常见的防御能力，如防止武器脱手、免疫击退/击飞等效果时，使用此文件。

典型触发场景：

- "让武器不会脱手"
- "人物不会被击飞"
- "免疫击退效果"
- "防止武器掉落"

---

## 一、武器不会脱手

### 实现原理

游戏没有直接的"disarm"实现，武器脱手通常与**击退事件**（`knockbackdropped`）和**眩晕机制**（`stunned`）相关。防止脱手的核心方法是使用 `equippable` 组件的 `SetPreventUnequipping` 方法。

### 核心方法

```lua
-- 阻止装备被强制卸下
equippable:SetPreventUnequipping(shouldprevent)
```

### 实现示例

#### 方式1：防止所有武器脱手（推荐）

```lua
AddPlayerPostInit(function(inst)
    if not TheWorld.ismastersim then return end

    -- 监听装备变化，自动给武器添加防脱手
    inst:ListenForEvent("equip", function(inst, data)
        if data.item and data.item.components.equippable then
            data.item.components.equippable:SetPreventUnequipping(true)
        end
    end)
end)
```

#### 方式2：针对特定武器

```lua
AddPrefabPostInit("your_weapon_prefab", function(inst)
    if inst.components.equippable then
        inst.components.equippable:SetPreventUnequipping(true)
    end
end)
```

#### 方式3：给所有手持物品添加保护

```lua
AddComponentPostInit("equippable", function(self, inst)
    -- 阻止装备被强制卸下
    self:SetPreventUnequipping(true)
end)
```

#### 方式4：官方 stronggrip 标签（防止被打击脱手，推荐组合）

`SetPreventUnequipping` 防的是"卸下/摘除"；而战斗中被特定攻击**震落/击飞/甩落**手中武器，是另一条路径。游戏原生有一个"强力握持"标签 `stronggrip`，凡是这类判定都会先检查它，命中则跳过脱手，是官方认可、无需额外 hook 的写法。

```lua
-- 角色常驻不脱手
AddPrefabPostInit("your_character", function(inst)
    if not TheWorld.ismastersim then return end
    inst:AddTag("stronggrip")
end)
```

做成**可开关能力**（如"超频/强握"类技能）时，开启打标签、关闭移除，可叠加霸体免疫控制：

```lua
-- 开启：不脱手
inst:AddTag("stronggrip")
inst.noa_ignorecontrol = true      -- 顺带免疫击退/眩晕等控制（可选）
-- 关闭
inst:RemoveTag("stronggrip")
inst.noa_ignorecontrol = nil
```

**原生会因 `stronggrip` 而不再让武器脱手**的判定点：

| 触发源 | 判定位置 | 脱离类型 |
|--------|----------|----------|
| 熊怪武器投掷 | prefabs/bearger.lua（weapontoss） | 震落武器 |
| 麋鹿/鹅跺地 | stategraphs/SGmoose.lua | 击飞武器 |
| 凝胶块悬浮玩家 | prefabs/gelblob.lua | 甩落手持物 |
| 湿滑/下雨失手 | prefabs/player_common.lua | 滑落物品 |
| 溺水 | components/drownable.lua | 落水掉物 |

`stronggrip` 在游戏内本来就是原生用法（gelblob、wurt 自带），是官方认可、无需额外 hook 的写法。官方参考：`prefabs/bearger.lua`、`stategraphs/SGmoose.lua`、`prefabs/gelblob.lua`、`prefabs/player_common.lua`、`components/drownable.lua`。

### 相关机制说明

| 事件名 | 触发时机 | 说明 |
|--------|----------|------|
| `knockbackdropped` | 受到强力击退时 | 同时触发武器脱落 |
| `stunned` | 进入眩晕状态时 | 可能被强制卸下装备 |
| `dropitem` | inventory组件掉落物品时 | 物品掉落事件 |

### 注意事项

- `SetPreventUnequipping(true)` 会阻止**所有**强制卸下操作，包括死亡时的装备掉落
- 如果只需要在特定情况下防止脱手，可以使用条件判断

---

## 二、人物不会被击飞/击退

### 实现原理

击飞/击退（knockback）是通过事件系统实现的，有多种防止方式：

1. **添加重甲标签**：将击退替换为摔倒状态（速度更低）
2. **修改击退力度**：监听击退事件降低力度
3. **自定义后坐力逻辑**：修改combat组件的判定
4. **弹反状态**：抵挡击退并反击

### 实现示例

#### 方式1：添加重甲标签（推荐）

```lua
-- 添加heavyarmor标签，将击退替换为摔倒状态（速度更低）
AddPlayerPostInit(function(inst)
    inst:AddTag("heavyarmor")
end)
```

**效果**：被击退时进入 `knockbacklanded` 状态（摔倒），而不是普通击飞，大幅降低击退速度。

#### 方式2：完全免疫击退

```lua
-- 监听击退事件并取消
AddPlayerPostInit(function(inst)
    inst:ListenForEvent("knockback", function(inst, data)
        -- 取消击退效果
        if inst.Physics then
            inst.Physics:SetMotorVel(0, 0, 0)
        end
        -- 强制返回空闲状态
        if inst.sg and not inst.sg:HasStateTag("dead") then
            inst.sg:GoToState("idle")
        end
    end)
end)
```

#### 方式3：降低击退力度

```lua
-- 监听击退事件，降低力度
AddPlayerPostInit(function(inst)
    inst:ListenForEvent("knockback", function(inst, data)
        if data and data.strengthmult then
            data.strengthmult = data.strengthmult * 0.3  -- 降低70%击退力度
        end
    end)
end)
```

#### 方式4：自定义后坐力逻辑

```lua
-- 修改combat组件的后坐力判定
AddComponentPostInit("combat", function(self, inst)
    self:SetShouldRecoilFn(function(inst, attacker, weapon, damage)
        return false, damage  -- 完全免疫后坐力
    end)
end)
```

### 击退事件数据结构

```lua
knockback_data = {
    knocker = entity,           -- 造成击退的实体
    radius = number,            -- 击退半径
    strengthmult = number,      -- 力度倍率（默认1）
    forcelanded = bool,         -- 是否强制进入"knockbacklanded"状态
    propsmashed = bool,         -- 是否击飞手中物品
    disablecollision = bool,    -- 是否临时关闭碰撞
    starthigh = bool,           -- 是否从高处开始击退动画
}
```

### 相关标签

| 标签名 | 作用 |
|--------|------|
| `heavyarmor` | 重甲标签，将击退替换为摔倒状态 |
| `heavybody` | 重身体标签（某些角色自带） |
| `parrying` | 弹反状态，可抵挡击退 |

---

## 三、攻击倍率修正

### 实现原理

角色的攻击倍率（`damagemultiplier`）直接影响所有攻击伤害。当需要修正角色的初始攻击倍率时，可以直接修改 `combat` 组件的 `damagemultiplier` 属性。

### 核心方法

```lua
inst.components.combat.damagemultiplier = value
```

### 实现示例

#### 方式1：直接修改（推荐）

```lua
AddPlayerPostInit(function(inst)
    if not TheWorld.ismastersim then return end

    inst:DoTaskInTime(0, function()
        if inst.components.combat then
            inst.components.combat.damagemultiplier = 1.2
        end
    end)
end)
```

#### 方式2：针对特定角色

```lua
AddPrefabPostInit("your_character_prefab", function(inst)
    if not TheWorld.ismastersim then return end

    inst:DoTaskInTime(0, function()
        if inst.components.combat then
            inst.components.combat.damagemultiplier = 1.2
        end
    end)
end)
```

#### 方式3：根据条件动态调整

```lua
AddPlayerPostInit(function(inst)
    if not TheWorld.ismastersim then return end

    -- 基础倍率修正
    inst:DoTaskInTime(0, function()
        if inst.components.combat then
            inst.components.combat.damagemultiplier = 1.2
        end
    end)

    -- 等级系统后续加成（基于修正后的值）
    inst:ListenForEvent("level_up", function(inst, data)
        if inst.components.combat then
            -- 读取修正后的基础值
            local base_mult = inst.components.combat.damagemultiplier
            -- 等级加成
            inst.components.combat.damagemultiplier = base_mult + 0.1 * data.level
        end
    end)
end)
```

### 伤害计算公式

```
最终伤害 = 基础伤害 × damagemultiplier × externaldamagemultipliers × ... + damagebonus
```

### 应用场景

| 场景 | 说明 |
|------|------|
| 角色初始倍率修正 | 将角色的初始攻击倍率从低值修正为正常值 |
| 等级系统加成 | 基于修正后的倍率进行等级加成 |
| 装备/技能加成 | 通过 `externaldamagemultipliers` 叠加额外加成 |
| Debuff修正 | 修正负面状态导致的倍率降低 |

### 注意事项

- **直接修改原始值**：修改后所有系统读取到的都是修正后的值
- **与 externaldamagemultipliers 的区别**：`damagemultiplier` 是基础倍率，`externaldamagemultipliers` 是额外叠加倍率
- **等级系统兼容**：等级系统可以基于修正后的值继续加成，无需特殊处理
- **优先级**：在角色初始化后尽早修改，避免其他系统读取到未修正的值

### 与其他倍率的区别

| 属性 | 说明 | 叠加方式 |
|------|------|----------|
| `damagemultiplier` | 基础攻击倍率 | 直接覆盖 |
| `externaldamagemultipliers` | 外部攻击倍率 | 加法叠加 |
| `damagebonus` | 固定伤害加成 | 最后加法 |
| `customdamagemultfn` | 自定义倍率计算 | 乘法叠加 |

---

## 四、组合使用示例

### 完整的防御能力

```lua
AddPlayerPostInit(function(inst)
    if not TheWorld.ismastersim then return end

    -- 1. 防止武器脱手
    inst:ListenForEvent("equip", function(inst, data)
        if data.item and data.item.components.equippable then
            data.item.components.equippable:SetPreventUnequipping(true)
        end
    end)

    -- 2. 添加重甲标签，减少击飞效果
    inst:AddTag("heavyarmor")

    -- 3. 可选：进一步降低击退力度
    inst:ListenForEvent("knockback", function(inst, data)
        if data and data.strengthmult then
            data.strengthmult = data.strengthmult * 0.5
        end
    end)
end)
```

### 针对特定角色

```lua
AddPrefabPostInit("your_character_prefab", function(inst)
    if not TheWorld.ismastersim then return end

    -- 防止武器脱手
    inst:ListenForEvent("equip", function(inst, data)
        if data.item and data.item.components.equippable then
            data.item.components.equippable:SetPreventUnequipping(true)
        end
    end)

    -- 免疫击飞
    inst:AddTag("heavyarmor")
end)
```

---

## 四、相关组件和事件

### 相关组件

| 组件 | 说明 | 文档 |
|------|------|------|
| `equippable` | 可装备组件 | [equippable.md](../../components/combat/equippable.md) |
| `combat` | 战斗组件 | [combat.md](../../components/combat/combat.md) |
| `inventory` | 背包组件 | [inventory.md](../../components/storage/inventory.md) |
| `stunnable` | 眩晕组件 | - |

### 相关事件

| 事件名 | 触发时机 |
|--------|----------|
| `knockback` | 受到击退时 |
| `knockbackdropped` | 受到击退并掉落物品时 |
| `stunned` | 进入眩晕状态时 |
| `equip` | 装备物品时 |
| `unequip` | 卸下装备时 |

---

后续阅读：

- [character-patterns.md](character-patterns.md) - 角色模式
- [player-patterns.md](../player-patterns.md) - 玩家模式
- [combat.md](../../components/combat/combat.md) - 战斗系统
- [equippable.md](../../components/combat/equippable.md) - 可装备组件

---

## 相关枢纽

- [能力索引](../../ability-index.md) - 返回能力系统索引，查看同主题下其他能力的统一归口。
