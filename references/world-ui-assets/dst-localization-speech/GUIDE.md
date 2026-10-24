---
name: dst-localization-speech
description: Localize Don't Starve Together mods and author character speech. Use when adding STRINGS names, descriptions, recipe text, action labels, UI strings, character quotes, speech files, PO translations, placeholders, gender-aware text, or fixing missing and overwritten localization keys.
---

# DST 本地化与角色台词

使用稳定、唯一的字符串键，把默认语言、翻译和角色语音分层，并保留格式占位符。

## 工作流

1. 列出 Prefab、Recipe、Action、UI、角色名、检查台词和配置说明所需的字符串键。
2. 为模组使用唯一前缀，只写目标叶子键，不替换整个 STRINGS 子表。
3. 默认字符串在运行入口初始化；大量翻译使用 PO 文件和 LoadPOFile，并明确语言代码。
4. 角色 speech 文件沿原版 speech_* 结构覆盖需要的键，未覆盖项安全回退。
5. 保留 %s、%d、换行、颜色标签和其他格式占位符的数量与顺序。
6. 处理角色性别、复数、专有名词、文本过滤上下文和 UI 宽度。
7. 测试默认语言、中文、缺失翻译、长文本、手柄 UI 和专服无 UI 环境。

## 源码锚点

- strings.lua、strings_pretranslated.lua、translator.lua。
- speech_wilson.lua 与各 speech_*.lua。
- createstringspo.lua、languages/。
- modutil.lua：LoadPOFile 与 AddModCharacter。

## 不变量

- 不要整体覆盖 STRINGS、CHARACTERS 或 ACTIONS 表。
- 翻译键必须稳定，文本内容可变。
- 占位符不匹配会在运行时格式化失败，必须自动或人工核对。
- 服务器逻辑不依赖本地化后的显示文本。

## 验证

- 所有目标语言无缺失键、格式错误或乱码。
- 未翻译键有可接受默认回退。
- 长文本和多行文本在目标 Widget 中不截断关键操作信息。

