---
name: dst-character-authoring
description: Create and maintain playable Don't Starve Together characters. Use when adding a mod character, player prefab, stats, starting inventory, character strings and speech, portraits and minimap assets, custom actions, stategraph hooks, skill trees, character-specific UI, save data, or multiplayer spawn behavior.
---

# DST 可玩角色编排

围绕玩家 Prefab 的公共初始化、主机初始化、客户端表现和角色专属系统分层实现。

## 工作流

1. 定义角色规格：基础属性、优势、弱点、初始物品、专属动作、制作、技能树、语音、资源和存档状态。
2. 对照 prefabs/player_common.lua 与至少一个机制相近的原版角色，使用玩家构造助手创建 Prefab。
3. 在所有端初始化 AnimState、标签、网络变量、地图图标和客户端表现；在主机初始化组件数值、物品、监听和保存状态。
4. 只调用一次 AddModCharacter(name, gender, modes) 注册角色；显式传入 'FEMALE'、'MALE'、'ROBOT'、'NEUTRAL' 或 'PLURAL' 字符串之一，避免 nil 的警告和默认 'NEUTRAL'。补齐 STRINGS.CHARACTER_NAMES[name]、STRINGS.CHARACTER_DESCRIPTIONS[name]、STRINGS.CHARACTER_QUOTES[name] 与角色 speech 文件；只有实际提供皮肤时才添加相应 STRINGS.SKIN_NAMES 键。
5. 优先向 SGwilson 和客户端 SG 添加状态、事件或 ActionHandler，不复制整份玩家 SG。
6. 专属制作使用角色过滤器、builder_tag 或 builder_skill；技能树按 skilltree Skill 的数据和同步流程接入。
7. 测试新建角色、重选角色、死亡复活、换洞穴、断线重连、保存重载、不同客户端资源和手柄 UI。

## 源码锚点

- prefabs/player_common.lua、characterutil.lua：玩家 Prefab 与公共行为。
- 各原版角色 Prefab、speech_*.lua 和 skilltree_*.lua。
- stategraphs/SGwilson.lua 与客户端玩家 SG。
- widgets/、screens/redux/：角色选择、HUD 和技能树 UI。
- modutil.lua：AddModCharacter、AddCharacterRecipe 与技能树图集注册。

## 按需参考

- [character-assets.md](references/character-assets.md) - 模组角色资源：选人大立绘、名字图、头像、制作栏图标、讣告、小地图固定路径，以及 `ExcludeClothingSymbolForModCharacter` / `RemoveDefaultCharacter`。
- [character-fast-abilities.md](references/character-fast-abilities.md) - 角色被动快速能力：吃得快/造得快（内建 `fastbuilder` 标签、自定义快速进食 SG 状态 + EAT 动作重定向）。
- [character-fast-work.md](references/character-fast-work.md) - 快速采集/制造/交互：覆写 `dolongaction` 共享状态统一缩短动作时长、`pickable:Pick` 双倍采集、按键+RPC 一键范围收获。
- [character-swim-ocean.md](references/character-swim-ocean.md) - 海上游泳：复用官方 `amphibiouscreature` 组件管理进海/上岸状态、自建跳跃状态清碰撞层、自动探测水陆边界触发跳入/跳出。
- [character-walkonwater.md](references/character-walkonwater.md) - 踏水/跨洞穴虚空行走：物理碰撞层切换（`COLLISION.WORLD`→`COLLISION.GROUND`）、关溺水、穿墙虚影模式与配套特效。

## 不变量

- 主机属性和客户端视觉初始化分开，不能在客户端访问服务器组件。
- 不要整文件覆盖 SGwilson、字符串表或玩家公共函数。
- 角色资源名、Prefab 名和字符串键保持一致并使用唯一前缀。
- 重生或换角色时清理旧角色拥有的世界监听、子实体和 UI。
- 角色资源路径和元素名必须按当前消费者核对；缺失头像、名字图或小地图图标通常只显示回退或空白，不会在加载阶段明确报错。

## 验证

- 角色在主机、专服客户端和洞穴中均能选择、生成和重连。
- 死亡、复活、换人、保存重载后专属状态不重复或丢失。
- 缺少可选皮肤、技能或配置时仍能使用基础角色。

## 玩家工厂、存档与表现的独立链

MakePlayerCharacter 的 common 与 master 回调分别用于公共构造和权威逻辑；公共初始化不代表所有普通 Lua 字段都会同步。master 内提供的保存回调由工厂包装，后续 PostInit 替换玩家 OnSave/OnLoad 时要保留已存在的工厂链。

角色选择菜单三维与出生后组件值是两条数据链；需要菜单数值时检查对应 TUNING 键及当前菜单消费者。死亡/复活/重连的 HUD 读取已复制 ghost 状态，并在初次绑定主动刷新；不能期待服务端 PushEvent 自动到客机。

玩家通常复用 SGwilson/SGwilson_client；资源 build、注册名和文件名可以显式映射，唯一命名与引用一致即可。台词 GENERIC/随机候选等结构按 GetString 消费者核对；应为 GENERIC 的键不能误写成普通字符串数组或反向嵌套。

来源 [角色与 AI 参考](../../engineering/dst-mod-engineering/characters-brains-stategraphs.md)；当前玩家生命周期具体接法按 [HUD 合同](../../world-ui-assets/dst-hud-screens-input/references/hud-customization.md)。角色新机制仍需新建、幽灵进入、复活、换洞穴与旧档验证。
