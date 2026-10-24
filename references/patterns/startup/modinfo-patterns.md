# Modinfo 模式

当任务编辑 `modinfo.lua` 时使用此文件。它涵盖元数据、兼容性标志和 `configuration_options`。

## `modinfo.lua` 不是普通的运行时 Lua

- 将 `modinfo.lua` 视为受限的元数据环境
- 不要假设运行时全局变量或 Lua 标准库辅助函数可用
- 优先使用字面表、数值 `for` 循环和直接字符串拼接
- 避免使用 `pairs`、`ipairs`、`tostring`、`type`、`string`、`table` 等假设
- 保持辅助函数小巧且意图清晰

## 尽早读取这些字段

- `name`
- `description`
- `author`
- `version`
- `api_version`
- `dst_compatible`
- `client_only_mod`
- `all_clients_require_mod`
- `mod_dependencies`
- `configuration_options`

如果配置已存在，请在添加新选项之前检查其布局。

## `mod_dependencies`

用法：

```lua
mod_dependencies = {
    { workshop = "workshop-123456", ["ModFancyName"] = true },
}
```

- 用于硬依赖，而非软兼容性提示
- 依赖项按表读取 `v.workshop`，并遍历表中的其他键作为模组名；不要把单个 workshop 字符串直接放进数组
- 当前加载器对 `client_only_mod` 不支持依赖，纯客户端模组不要依赖此字段获得服务器模组
- 当任务提到依赖模组时，首先检查此项

## `modinfo.lua` 中的本地化

为了标准化技能输出，优先使用：

- `MODINFO_TRANSLATIONS`
- `Translate(key)`

```lua
local MODINFO_TRANSLATIONS = {
    en = {
        ModName = "Example Mod",
    },
    zh = {
        ModName = "Example Mod (ZH)",
    },
}

local function Translate(key)
    return (MODINFO_TRANSLATIONS[locale] or MODINFO_TRANSLATIONS.en)[key] or key
end
```

- `modinfo.lua` 本地化与运行时 `STRINGS` 是分开的
- 保持辅助函数最小化
- 在构建本地化配置时不要依赖标准库辅助函数

## `configuration_options`

典型结构：

```lua
configuration_options = {
    {
        name = "EXAMPLE_TOGGLE",
        label = "Example Toggle",
        hover = "Short explanation.",
        options = {
            { description = "Off", data = false },
            { description = "On", data = true },
        },
        default = false,
    },
}
```

高频字段：

- `name`
- `label`
- `hover`
- `options`
- `default`

规则：

- 尽可能在发布后保持选项名称稳定
- 保持 `data` 值简单明确
- 保持 `default` 与其中一个选项的 `data` 值完全相同

## 配置部分标题

当对角色、装备、UI 或调试选项进行分组时，使用一个假的配置条目作为分区标签。

推荐的辅助函数：

```lua
local function MakeConfigSectionHeader(label)
    return {
        name = "",
        label = label,
        options = {
            {
                description = "",
                data = false,
            },
        },
        default = false,
    }
end
```

- `titlefn` 描述的是结构，而非意图
- `MakeConfigSectionHeader` 明确说明了辅助函数返回的内容

这样使用：

```lua
configuration_options = {
    MakeConfigSectionHeader("General"),
    {
        name = "EXAMPLE_TOGGLE",
        label = "Example Toggle",
        options = {
            { description = "Off", data = false },
            { description = "On", data = true },
        },
        default = false,
    },

    MakeConfigSectionHeader("UI"),
    {
        name = "SHOW_EXAMPLE",
        label = "Show Example",
        options = {
            { description = "Yes", data = true },
            { description = "No", data = false },
        },
        default = true,
    },
}
```

## 安全的辅助函数风格

好的辅助函数特点：

- 小巧
- 大量使用表字面量
- 无标准库依赖
- 无隐藏的运行时假设

好的例子：

- 使用直接表访问的本地化查找辅助函数
- 布尔选项构建器
- 配置分区标题构建器
- 在字面量选项列表上使用数值 `for` 循环

不好的例子：

- 使用 `pairs(...)` 构建配置
- 使用 `table.insert(...)`
- 使用 `string.format(...)`
- 使用 `tostring(...)`
- 假设来自 `modmain.lua` 的仅运行时全局变量

## 按键映射选项

如果用户希望在 `configuration_options` 中添加热键配置，请保持辅助函数字面量且保守。

```lua
local default_suffix = " (Default)"

local function MakeKeyOptions(default_value)
    local options = {
        { description = "A", data = 97 },
        { description = "B", data = 98 },
        { description = "C", data = 99 },
        { description = "D", data = 100 },
        { description = "E", data = 101 },
        { description = "F", data = 102 },
        { description = "G", data = 103 },
        { description = "H", data = 104 },
        { description = "I", data = 105 },
        { description = "J", data = 106 },
        { description = "K", data = 107 },
        { description = "L", data = 108 },
        { description = "M", data = 109 },
        { description = "N", data = 110 },
        { description = "O", data = 111 },
        { description = "P", data = 112 },
        { description = "Q", data = 113 },
        { description = "R", data = 114 },
        { description = "S", data = 115 },
        { description = "T", data = 116 },
        { description = "U", data = 117 },
        { description = "V", data = 118 },
        { description = "W", data = 119 },
        { description = "X", data = 120 },
        { description = "Y", data = 121 },
        { description = "Z", data = 122 },
    }

    for i = 1, #options do
        if options[i].data == default_value then
            options[i].description = options[i].description .. default_suffix
            break
        end
    end

    return options
end
```

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
{
    name = "HOTKEY_SKILL",
    label = "Skill Hotkey",
    hover = "Hotkey for the skill.",
    options = MakeKeyOptions(122),
    default = 122,
}
```

规则：

- 在 `modinfo.lua` 中使用显式的键码表
- 通过在数值循环中修改匹配的字面量条目来标记默认选项
- 保持键标签和键码值紧密在一起
- 如果列表变得很大，仍然优先使用字面量表；如果需要，将其拆分为一个小的辅助表
- 避免使用 `string.char(...)`、`table.insert(...)`、`pairs(...)`、`ipairs(...)` 和 `string.format(...)`

## 配置优先级模式（预设与自定义）

当需要提供预设配置等级（如简单/普通/困难）同时允许用户单独调整各项数值时，使用此模式。单独调整项的优先级高于预设等级。

### modinfo.lua 配置示例

```lua
configuration_options = {
    {
        name = "POWER_LEVEL",
        label = "强度等级",
        hover = "选择预设的技能强度等级",
        options = {
            { description = "简单", data = "easy" },
            { description = "普通", data = "normal" },
            { description = "困难", data = "hard" },
        },
        default = "normal",
    },
    {
        name = "ATTACK_DAMAGE",
        label = "攻击伤害",
        hover = "自定义攻击伤害，设置为0则使用强度等级的默认值",
        options = {
            { description = "使用预设值", data = 0 },
            { description = "5", data = 5 },
            { description = "10", data = 10 },
            { description = "15", data = 15 },
            { description = "20", data = 20 },
            { description = "25", data = 25 },
            { description = "30", data = 30 },
        },
        default = 0,
    },
    {
        name = "HEALTH",
        label = "生命值",
        hover = "自定义生命值，设置为0则使用强度等级的默认值",
        options = {
            { description = "使用预设值", data = 0 },
            { description = "100", data = 100 },
            { description = "150", data = 150 },
            { description = "200", data = 200 },
            { description = "250", data = 250 },
            { description = "300", data = 300 },
        },
        default = 0,
    },
}
```

### modmain.lua 数值获取逻辑

```lua
local SKILL_PRESETS = {
    easy = {
        attack_damage = 8,
        health = 120,
    },
    normal = {
        attack_damage = 12,
        health = 150,
    },
    hard = {
        attack_damage = 15,
        health = 100,
    },
}

local function GetSkillValue(power_level, custom_value, preset_key)
    if custom_value ~= nil and custom_value > 0 then
        return custom_value
    end
    return SKILL_PRESETS[power_level] and SKILL_PRESETS[power_level][preset_key] or SKILL_PRESETS.normal[preset_key]
end

AddPrefabPostInit("player", function(inst)
    if not TheWorld.ismastersim then return end
    
    local power_level = GetModConfigData("POWER_LEVEL")
    local custom_damage = GetModConfigData("ATTACK_DAMAGE")
    local custom_health = GetModConfigData("HEALTH")
    
    local final_damage = GetSkillValue(power_level, custom_damage, "attack_damage")
    local final_health = GetSkillValue(power_level, custom_health, "health")
    
    inst.components.health:SetMaxHealth(final_health)
    inst.components.combat:SetDefaultDamage(final_damage)
end)
```

### 规则

- 单独调整项的默认值设为 0，表示"使用预设值"
- 判断条件 `custom_value > 0` 确保只有用户明确设置的值才会覆盖预设
- 如果 0 本身是有效值（如倍率类选项），改用 -1 作为哨兵值，表示"使用预设值"
- 保持预设数值表与配置选项的对应关系清晰
- 在 `modmain.lua` 中实现优先级逻辑，不在 `modinfo.lua` 中做复杂计算

## 意图索引

- "我需要对模组类型进行分类"
  - 检查 `client_only_mod` 和 `all_clients_require_mod`
- "我需要添加依赖的创意工坊模组"
  - 检查 `mod_dependencies`
- "我需要将配置分成多个部分"
  - 使用 `MakeConfigSectionHeader(...)`
- "我需要在 `modinfo.lua` 中添加热键配置"
  - 使用字面量键选项构建器，如 `MakeKeyOptions(...)`
- "我需要本地化模组元数据"
  - 将本地化保持在 `modinfo.lua` 内部
  - 优先使用 `MODINFO_TRANSLATIONS` 和 `Translate(...)`
- "我需要添加配置辅助函数"
  - 保持它们最小化且无标准库依赖
- "我需要提供预设配置等级并允许单独调整"
  - 使用配置优先级模式，单独调整项优先级高于预设等级

## 常见失败点

- 游戏在加载模组元数据时失败
  - `modinfo.lua` 使用了不可用的辅助函数或全局变量
- 配置分区标签破坏了选项解析
  - 假标题条目的结构与正常配置条目的预期不匹配
- 本地化元数据工作正常但配置构建器崩溃
  - 辅助函数使用了不可用的库调用
- 选项默认值行为异常
  - `default` 与其中一个选项的 `data` 值不完全匹配

## 经验法则

- 让 `modinfo.lua` 保持简单。
- 优先使用字面量而非抽象。
- 如果添加辅助函数，请使其小巧且意图清晰。
- 对于配置分组，优先使用 `MakeConfigSectionHeader(...)` 而非模糊的名称如 `titlefn`。
