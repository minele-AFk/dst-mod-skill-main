# `sanity`

> 适用版本：API 10+
> 方法签名复核：2026-10-18，本机安装快照；不代表游戏行为验收。

当任务涉及修改理智值增减、月相疯狂、光环免疫或惩罚调整的理智限制时，使用此文件。

官方源码：

- `scripts/components/sanity.lua`

相关官方预制件示例：

- `scripts/prefabs/player_common.lua`
- `scripts/prefabs/wathgrithr.lua`

高频方法：

- `GetPercent()`
- `GetRealPercent()`
- `SetPercent(per, overtime)`
- `DoDelta(delta, overtime)`
- `SetMax(amount)`
- `EnableLunacy(enable, source)`
- `AddSanityPenalty(key, mod)`
- `RemoveSanityPenalty(key)`
- `SetFullAuraImmunity(immunity, source)`
- `SetNegativeAuraImmunity(immunity, source)`
- `SetPlayerGhostImmunity(immunity, source)`
常见组件搭配：

- `sanity` + 玩家副本或分类流程
- `sanity` + `talker`

常见陷阱：

- `GetPercent()` 可能反映惩罚调整后的值；调试时与 `GetRealPercent()` 比较。
- 月相疯狂和精神错乱是模式逻辑，不仅仅是负增量。
- 持续的光环或模式重新计算可能会覆盖一次性的理智写入。

---

## 理智增减机制

基于源码 `sanity.lua:73-124`：

### 核心属性

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `max` | number | 100 | 最大理智值 |
| `current` | number | 100 | 当前理智值 |
| `rate` | number | 0 | 当前理智变化速率 |
| `rate_modifier` | number | 1 | 速率倍率 |
| `dapperness` | number | 0 | 精神恢复值 |
| `dapperness_mult` | number | 1 | 精神恢复倍率 |
| `penalty` | number | 0 | 最大理智惩罚百分比 |
| `externalmodifiers` | SourceModifierList | 0 | 外部速率修改（加法） |
| `custom_rate_fn` | function | nil | 自定义速率函数 |
| `mode` | number | SANITY_MODE_INSANITY | 理智模式（0=疯狂, 1=月相） |

### 模式系统

```lua
SANITY_MODE_INSANITY = 0  -- 普通模式：低理智=疯狂
SANITY_MODE_LUNACY = 1    -- 月相模式：低理智=月相觉醒

function Sanity:IsSane()
    if self.mode == SANITY_MODE_INSANITY then
        return self.sane and not self.inducedinsanity or self.inducedlunacy or false
    else
        return self.sane and not self.inducedlunacy or self.inducedinsanity or false
    end
end

-- 切换模式
function Sanity:EnableLunacy(enable, source)
    self._lunacy_sources:SetModifier(self.inst, enable, source)
    self:UpdateMode_Internal()
end
```

---

## 理智百分比计算

```lua
-- 真实百分比（不考虑惩罚和诱导状态）
function Sanity:GetRealPercent()
    return self.current / self.max
end

-- 显示百分比（受惩罚和诱导状态影响）
function Sanity:GetPercent()
    return (self.inducedinsanity and 0)
        or (self.inducedlunacy and 1 - self.penalty)
        or self:GetRealPercent()
end

-- 考虑惩罚后的百分比
function Sanity:GetPercentWithPenalty()
    return (self.inducedinsanity and 0)
        or (self.inducedlunacy and 1)
        or self.current / (self.max - (self.max * self.penalty))
end

-- 惩罚后的最大理智
function Sanity:GetMaxWithPenalty()
    return self.max - (self.max * self.penalty)
end
```

---

## 光环系统

### 光环免疫类型

```lua
-- 完全免疫所有光环
function Sanity:SetFullAuraImmunity(immunity, source)
    self.sanity_aura_immune_sources:SetModifier(source or self.inst, immunity)
end

-- 仅免疫负面光环
function Sanity:SetNegativeAuraImmunity(immunity, source)
    self.neg_aura_immune_sources:SetModifier(source or self.inst, immunity)
end

-- 免疫特定标签的光环（如Wendy对幽灵的免疫）
function Sanity:AddSanityAuraImmunity(tag, source)
    if self.sanity_aura_immunities == nil then
        self.sanity_aura_immunities = {}
    end
    local sources = self.sanity_aura_immunities[tag]
    if sources == nil then
        sources = SourceModifierList(self.inst, false, SourceModifierList.boolean)
        self.sanity_aura_immunities[tag] = sources
    end
    sources:SetModifier(source or self.inst, true)
end
```

### 其他免疫

```lua
-- 免疫玩家幽灵
function Sanity:SetPlayerGhostImmunity(immunity, source)
    self.player_ghost_immune_sources:SetModifier(source or self.inst, immunity)
end

-- 免疫黑暗/夜晚理智消耗
function Sanity:SetLightDrainImmune(immunity, source)
    self.light_drain_immune_sources:SetModifier(source or self.inst, immunity)
end
```

---

## 惩罚系统

```lua
-- 添加惩罚（减少最大理智）
function Sanity:AddSanityPenalty(key, mod)
    self.sanity_penalties[key] = mod
    self:RecalculatePenalty()
end

-- 移除惩罚
function Sanity:RemoveSanityPenalty(key)
    self.sanity_penalties[key] = nil
    self:RecalculatePenalty()
end

-- 惩罚上限：最大理智不低于5点
function Sanity:RecalculatePenalty()
    local penalty = 0
    for k, v in pairs(self.sanity_penalties) do
        penalty = penalty + v
    end
    self.penalty = math.min(penalty, 1 - (5 / self.max))
    self:DoDelta(0)
end
```

---

## 实战示例

### 理智增减

```lua
-- 增加50点理智
inst.components.sanity:DoDelta(50)

-- 减少20点理智
inst.components.sanity:DoDelta(-20)

-- 渐变增减（overtime模式）
inst.components.sanity:DoDelta(50, true)
```

### 添加惩罚

```lua
-- 添加20%最大理智惩罚
inst.components.sanity:AddSanityPenalty("my_skill", 0.2)

-- 移除惩罚
inst.components.sanity:RemoveSanityPenalty("my_skill")
```

### 免疫光环

```lua
-- 完全免疫光环
inst.components.sanity:SetFullAuraImmunity(true, "my_skill")

-- 移除免疫
inst.components.sanity:SetFullAuraImmunity(false, "my_skill")

-- 免疫特定光环
inst.components.sanity:AddSanityAuraImmunity("ghost", "my_skill")
```

### 切换月相模式

```lua
-- 切换到月相模式（低理智=觉醒）
inst.components.sanity:EnableLunacy(true, "my_skill")

-- 切换回普通模式
inst.components.sanity:EnableLunacy(false, "my_skill")
```

后续阅读：

- [player-network-patterns.md](../../patterns/network/player-network-patterns.md)
- [talker.md](../behavior/talker.md)
