# 运行时国际化模式

当任务设计或重构 mod 的运行时本地化时，请使用此文件。本页面适用于运行时文本，而非 `modinfo.lua` 元数据。

## 官方运行时基础

在官方文件中验证：

- `scripts/modutil.lua`
  - mod 环境暴露 `LoadPOFile(path, lang)`
- `scripts/translator.lua`
  - `Translator:LoadPOFile(...)`
  - `TranslateStringTable(tbl)`
- `scripts/languages/loc.lua`
  - 官方语言切换调用 `TranslateStringTable(STRINGS)`
- `scripts/stringutil.lua`
  - 运行时查找使用 `GetString(...)`

含义：

- 官方运行时翻译存在
- 基于 `.po` 文件和翻译器
- 运行时文本仍通过 `STRINGS` 解析

已验证的 mod 端辅助函数：

- `scripts/modutil.lua`
  - 在 mod 环境中暴露 `LoadPOFile(path, lang)`

## 推荐的运行时策略

对于大多数 mod，优先使用 Lua 表运行时国际化层，而不是从 `.po` 文件生成完整的 Lua 转储。

推荐方法：

1. 在小型加载器模块中选择一次语言环境
2. 加载一个特定语言环境的公共表，用于 mod 拥有的字符串
3. 将该表合并到 `STRINGS` 中
4. 深拷贝基础语音表用于角色语音
5. 仅对自定义角色应用稀疏的语言环境覆盖

优点：

- 语言环境文件更小
- 更容易审查
- 生成的噪声更少
- 角色 mod 从基础表继承未来的默认行
- 公共字符串和角色语音保持分离

实用规则：

- 当可维护性比匹配官方 `.po` 流程更重要时，使用 Lua 增量表
- 当项目明确需要翻译工具或现有 `.po` 工作流时，使用 `.po`

## 推荐的目录结构

```text
scripts/languages/
├─ i18n.lua
├─ common_en.lua
├─ common_zh.lua
├─ speech_mychar_en.lua
├─ speech_mychar_zh.lua
├─ speech_sidekick_en.lua
└─ speech_sidekick_zh.lua
```

角色：

- `i18n.lua`
  - 语言环境选择和加载编排
- `common_<locale>.lua`
  - mod 拥有的 `STRINGS` 附加项
- `speech_<character>_<locale>.lua`
  - 角色语音表的稀疏覆盖
- 伙伴或同伴语音文件
  - 按语音路径或符号 ID 键控的独立本地化表

## 公共字符串应是 mod 拥有的附加项

```lua
return {
    NAMES = {
        MY_ITEM = "My Item",
    },
    RECIPE_DESC = {
        MY_ITEM = "Craft a thing.",
    },
    ACTIONS = {
        MY_ACTION = "Use",
    },
    UI = {
        TOOLTIP = {
            MY_TOOLTIP = "Drag with RMB.",
        },
    },
    CHARACTERS = {
        GENERIC = {
            DESCRIBE = {
                MY_ITEM = "A custom thing.",
            },
        },
    },
    MYMOD = {
        SKILLS = {
            TITLE = "Skill",
        },
    },
}
```

- `common_<locale>.lua` 应仅描述您的 mod 拥有的字符串
- 当只需要几个分支时，不要镜像整个全局 `STRINGS` 树

## 角色语音应从 `STRINGS.CHARACTERS.GENERIC` 开始

在 `scripts/stringutil.lua` 中验证：

- `GetString(...)` 解析角色字符串
- 缺失的角色特定值回退到 `STRINGS.CHARACTERS.GENERIC`

规则：

- 正确的基础语音表是 `STRINGS.CHARACTERS.GENERIC`
- 当您只需要差异时，不要从头构建完整的复制语音文件
- 不要将基础视为 `WILSON`；默认回退表是 `GENERIC`

推荐模式：

1. 深拷贝 `STRINGS.CHARACTERS.GENERIC`
2. 将稀疏语言环境覆盖合并到该副本中
3. 将合并结果分配给 `STRINGS.CHARACTERS.<YOURCHAR>`

## 稀疏角色语音文件

```lua
return {
    DESCRIBE = {
        MY_ITEM = "This is mine.",
    },
    BATTLECRY = {
        GENERIC = "Let's do this.",
    },
    ANNOUNCE_ENTER_DARK = "Too dark...",
}
```

- 只保留此处更改的行
- 从复制的通用基础继承其他所有内容

## 标准加载器形状

```lua
local supported = {
    en = true,
    zh = true,
}

local function ResolveLocale()
    local lang = GetModConfigData("LANGUAGE")
    if lang == nil or lang == "auto" then
        lang = LOC.GetLocaleCode()
    end
    if not supported[lang] then
        lang = "en"
    end
    return lang
end

local function DeepCopy(value)
    if type(value) ~= "table" then
        return value
    end

    local result = {}
    for k, v in pairs(value) do
        result[k] = DeepCopy(v)
    end
    return result
end

local function DeepMerge(dst, src)
    for k, v in pairs(src) do
        if type(v) == "table" then
            if type(dst[k]) ~= "table" then
                dst[k] = {}
            end
            DeepMerge(dst[k], v)
        else
            dst[k] = v
        end
    end
end

local locale = ResolveLocale()

local common = require("languages/common_" .. locale)
DeepMerge(STRINGS, common)

local speech = DeepCopy(STRINGS.CHARACTERS.GENERIC)
DeepMerge(speech, require("languages/speech_mychar_" .. locale))
STRINGS.CHARACTERS.MYCHAR = speech
```

## 资源、字符串和国际化边界

保持这些系统分离：

- 运行时国际化
  - 语言环境选择、表合并、可选的 `.po` 加载
- 运行时字符串
  - 最终 `STRINGS` 树内容
- 资源
  - 图集、纹理、动画 zip、声音

翻译名称不会注册图标。注册图标不会填充本地化的 `STRINGS.NAMES` 条目。

## 伙伴或代理说话者文本

不要将第二个说话者表按最终翻译的句子文本进行键控。

- 避免使用本地化输出字符串作为查找键，例如 `STRINGS.CHARACTERS.MYCHAR.DESCRIBE.MY_ITEM`
- 行文本更改、语言环境更改和标点符号编辑将破坏查找

优先选择：

- 路径键控表
  - `DESCRIBE.MY_ITEM`
  - `BATTLECRY.GENERIC`
- 符号 ID
  - `MYITEM_DESCRIBE`
  - `GENERIC_BATTLECRY`

```lua
return {
    DESCRIBE = {
        MY_ITEM = "Don't touch that.",
    },
    BATTLECRY = {
        GENERIC = "Go!",
    },
}
```

从当前语言环境表上的相同路径读取，而不是使用翻译文本作为键。

## 可选的官方 `.po` 路由

官方 mod 环境暴露：

```lua
LoadPOFile(path, lang)
```

官方运行时翻译基于：

- `LanguageTranslator:LoadPOFile(...)`
- `TranslateStringTable(STRINGS)`

- 这是真实的官方运行时能力
- 当您明确需要 `.po` 工作流时使用它
- 对于许多游戏玩法 mod，Lua 增量表方法更易于维护

最小官方风格路由：

1. 调用 `LoadPOFile(path, lang)`
2. 确保目标字符串存在于 `STRINGS` 中
3. 在相关流程中调用或依赖 `TranslateStringTable(STRINGS)`

如果项目不想要 `.po`，Lua 表路由通常更简单。

## 意图索引

- "我希望我的 mod 有适当的运行时国际化"
  - 从语言环境选择的公共表加上小型加载器开始
- "我希望避免生成巨大的语音文件"
  - 深拷贝 `STRINGS.CHARACTERS.GENERIC` 并合并稀疏覆盖
- "我正在制作角色 mod"
  - 将 `STRINGS.CHARACTERS.GENERIC` 视为语音基础
- "我的公共字符串和角色语音混合在一起"
  - 将 `common_<locale>.lua` 与 `speech_<character>_<locale>.lua` 分开
- "我有第二个说话者，按翻译行键控"
  - 用路径键控或符号 ID 表替换文本键
- "我想要基于 `.po` 的本地化"
  - 查看 `LoadPOFile(...)` 和 `TranslateStringTable(STRINGS)`

## 常见失败点

- 语言环境文件巨大且难以比较
  - 镜像了太多 `STRINGS`
- 角色语音随时间偏离基础游戏
  - 复制了完整语音表而不是从 `GENERIC` 继承
- 翻译编辑后运行时文本查找中断
  - 按翻译句子值键控伙伴逻辑
- 公共字符串意外覆盖了太多全局状态
  - 合并了完整树而不是稀疏的 mod 拥有分支集
- 运行时国际化和 `modinfo.lua` 国际化混合在一起
  - 两个不同的系统被视为一个
- 运行时语言环境文件试图解决缺失的资源或图集问题
  - 错误的子系统
- 直接字符串写入和语言环境加载器都覆盖同一分支，没有明确的顺序
  - 最终运行时文本变得不可预测

## 快速导航

- "我只需要几个新字符串"
  - 阅读本页“少量字符串与 modinfo 边界”
- "我需要运行时语言环境切换"
  - 留在本页面
- "我需要元数据/配置翻译"
  - 阅读 `references/patterns/startup/modinfo-patterns.md`
- "文本正确但美术缺失"
  - 阅读 `references/patterns/asset/asset-patterns.md`

## 经验法则

- `modinfo.lua` 本地化是一个系统。
- 运行时本地化是另一个系统。
- 保持运行时语言环境文件稀疏。
- 对于角色 mod，复制 `STRINGS.CHARACTERS.GENERIC` 并只覆盖差异。

## 少量字符串与 modinfo 边界

一两个固定文本在 modmain 或 modimport 加载的注册文件写目标叶子键即可，不必为单语言功能建完整 locale 加载器。长字符串表可用 modimport("scripts/my_strings.lua") 拆分；普通 require 模块的环境需另核对。

```lua
local S = GLOBAL.STRINGS -- 模组环境注册文件
S.NAMES.MY_PREFAB = "My Prefab"
S.RECIPE_DESC.MY_PREFAB = "Builds a thing."
S.CHARACTERS.GENERIC.DESCRIBE.MY_PREFAB = "It exists."
S.ACTIONS.MY_ACTION = "Use"
```

Prefab/Action 字符串键按原版使用大写（可对代码名 string.upper）；UI 文本放模组自己的 STRINGS.UI 分支。文本与资源注册分开：缺图查 ATLAS/IMAGE，缺名称查 STRINGS，不能靠翻译注册图标。保留格式占位符与回退，避免覆写整个子表。

modinfo 的 locale/ChooseTranslationTable 在元信息环境选择名称、说明与配置标签；不拿该辅助函数当运行时翻译器。示例为 name = ChooseTranslationTable({ "English Name", ["zh"] = "Localized Name" })。大量运行时多语言再沿本文的稀疏语言表或 PO 路线；元信息细节见 [modinfo 模式](startup/modinfo-patterns.md)。
