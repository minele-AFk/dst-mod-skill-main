# 珂朵莉（chtholly）mod 架构学习笔记

> 范畴：mod-notes。目标 mod：创意工坊 3440394425「珂朵莉」v5.7（作者：寒枫 / 深海水母灯）。
> 解密状态（2026-10-16 复核）：`modmain.lua` / `modmain0.lua` 是分层混淆加载器与中间容器；`modmain1.lua` 和 `scripts/` 下 30 个 Lua 载荷已通过静态流程完整恢复。`modinfo.lua`、`scripts/speech_chtholly.lua`、资源为明文。
> 先前将本 Mod 归为与 `mod-mythwords.md`、`mod-dengxian.md` 完全相同的 DaxSg 解密方案，证据不足；外层结构相似不能证明各层字母表、VM 序列化和字节映射相同。不要跨 Mod 复用映射表，须从目标加载器重新提取并验证。

---

## 1. 概览

- **性质**：单角色 mod（可玩角色"珂朵莉"），重度"魔法战斗 + 自愈/生存强化"风格，带一只可召唤/分身的宠物系。
- **全文件规模**（顶层）：anim 12 zip、bigportraits 4、images 70、scripts 31。
- **无 PrefabFiles**（modinfo 不含）→ 原始加载器负责动态加载/注册 prefab；旧笔记记录过服务器注册日志，此次静态解密没有复测运行行为。
- **原始包中的明文脚本**：`scripts/speech_chtholly.lua`（327KB）——完整的珂朵莉版 `STRINGS` 覆盖表；其他 30 个脚本现已另行静态恢复。

---

## 2. 加载架构与分层混淆

### 2.1 文件分层

| 文件 | 大小 | 角色 |
|---|---|---|
| `modinfo.lua` | 13.5KB | 明文；无 PrefabFiles，137 行按键表 + 26 个 configuration_options |
| `modmain.lua` | 49KB | **入口 loader**；扁平化状态机，包含外层自定义字母表及取出内层解码器所需逻辑 |
| `modmain0.lua` | 96KB | 自定义字母表编码的中间载荷；正确解码后为 72,226 字节 Lua 容器/虚拟机加载器 |
| `modmain1.lua` | 84,673 字节 | 主业务逻辑载荷；与 `scripts/` 下脚本使用同一字节替换与文件逆序变换 |
| `scripts/*.lua` 30 个 | — | 同一字节替换与文件逆序变换；已完整恢复，可按原相对路径阅读 |
| `scripts/speech_chtholly.lua` | 327KB | **明文 STRINGS**（未加密） |

### 2.2 实际解码层

- 这是**分层混淆/编码**，不是 AES 等现代密码学加密。`modmain.lua` 的外层状态机有 818 项常量和 181 个分派块；从目标加载器提取真实自定义 Base64 字母表后，`modmain0.lua` 才能正确解出 72,226 字节中间容器。不同层的字母表不能混用。
- 中间容器不是标准 `\x1bLua` 字节码，而是自定义序列化的虚拟机载荷。主原型含 1,094 条指令和 9 个嵌套原型；对其静态反序列化、翻译为 Lua 5.1 字节码并辅助反编译后，在嵌套原型中找到真实载荷解码器。
- 内层解码器使用 316 项常量构造一张 255 项字节置换表，覆盖字节 1–255（不含 NUL）。对目标载荷逐字节替换，再将整个文件逆序，即得明文：`plain = reverse(substitute(cipher))`。这是可逆替换混淆，不具备现代加密的密钥安全性。
- `modmain1.lua` 开头的 `0xD3` 是载荷内容的一部分；正确解码后它对应末尾注释内容。不能把它当填充字节剥掉。
- 解码器只在隔离的 Lua 5.1 环境中单独执行；环境仅提供纯字符串/表函数及 `pairs`、`ipairs`。没有运行原加载器、反篡改逻辑、文件/网络钩子或 Mod 业务代码。

### 2.3 旧笔记为何失败，以及本次如何恢复

- **外层字母表取错**：旧流程用错了 `modmain0.lua` 的自定义 Base64 映射，输出自然呈现高熵乱码；这不能证明载荷是强加密，也不能由此判断无法恢复。
- **把不同层混成一种算法**：旧笔记把外层 VM、序列化容器和内层脚本载荷看成同一层，并尝试用词典/Re-Pair 等词组编码解释 `scripts/`；实际脚本使用的是固定单字节置换加文件逆序。
- **已知明文猜错且忽略逆序**：旧猜测 `7a8754e8 = self` 不成立。真实映射先得到 `tsni`，文件级逆序后才对应 `inst`。只凭少数词猜替换表会制造互相矛盾的映射；已知明文必须能在整文件位置和逆序关系下成立。
- **没有走到藏表的嵌套原型**：只分析外层 `modmain.lua` 或把中间结果直接当源码，会错过真正生成 255 项映射表的内层函数。成功路径是静态提取外层常量/分派、解出中间容器、反序列化 VM，再提取纯解码函数和映射表。
- 此前 `decrypted_scripts/` 中旧版 30 个输出在 Lua 5.1 语法检查中 **30 个全部失败**；这些词表猜测结果不能当作源码。

### 2.4 完整性验证与边界

- 30/30 个脚本与主逻辑 1/1 均已恢复；Lua 5.1 原生编译检查 33/33 通过（只编译，不执行）。
- 31/31 个载荷重新编码后与原密文逐字节一致；提取的 Lua 解码器与独立 Python 解码结果 31/31 逐字节一致。88 个资源 SHA-256 匹配，124 个原始目录文件哈希未变，独立目录复现的 121 个交付文件哈希一致。
- **未做游戏内运行测试**：语法、往返和独立解码器对照证明的是源码恢复完整性，不证明角色、联机或技能的实机行为。
- 详细过程、工具和结果：`D:\mods\资料包\chtholly_3440394425\recovery_verified\README.md`、`verification.json`；完整源码副本在同目录 `decrypted_mod/` 与 `chtholly_3440394425_完整解密.zip`。

---

## 3. 角色与数值系统（modinfo 明文还原）

珂朵莉是可配置的强生存魔法角色，26 项配置分 6 组：

### 3.1 按键体系（4 个自定义快捷键）
| 配置 | 默认键 | 用途（由 label 推断） |
|---|---|---|
| `key1` | C(99) | 魔力释放按键 |
| `key2` | Z(122) | 魔力聚集按键 |
| `key3` | V(118) | 快捷切换武器状态按键 |
| `keybuff` | O(111) | 状态免疫按键 |

按键表覆盖完整键盘（字母/数字/F 区/小键盘/修饰键），`keylist` 结构 `{description=键名, data=键码}`。

### 3.2 属性上限（200~1000 可选）
- `health` 生命最大值 / `sanity` 理智最大值 / `hunger` 饥饿最大值 / `maxmagic` **魔力最大值**（默认均 200）→ 角色带独立"魔力"资源条。

### 3.3 乘区调整
- `speed` 移速倍率、`hungerrate` 饥饿消耗、`workrate` 工作效率、`cookrate` 烹饪速度（均 100%~500%）；
- `damagerate` 攻击倍率、`damagecishu` 攻击触发伤害次数（1~5）。

### 3.4 魔力系统（核心特色）
- `magicregen` 魔力回复/秒（默认 2）
- `molidelta` 魔力聚集消耗/秒（默认 10）
- `molidelta2` 魔力释放消耗/次（默认 100，100~200）→ "聚集(charge) + 释放(burst)"双阶段魔法手感。

### 3.5 生存/防御强化
- `healthabsorb` 人物减伤 0~99%、`limithealth1` 单次最大受伤害限制（默认 20）、`limithealth2` 10s 内扣血上限（默认 10%）、`shanbi` 人物闪避率（默认 90%）、`healthregen` 回血/分钟、`sanitydelta` 理智损失/分钟（默认 10）。
- `redmode` 特殊机制（理智为 0 触发，默认开）→ 低理智变"红模式"强化。

### 3.6 被动便利 + 召唤
- `yeshi` 夜视（默认开）、`hengwen` 恒温（默认开）、`tashui` 踏水（默认开）；
- `chongwu` **分身数量**（1~5，默认 1）→ 与 summon 组件/分身系统对应。

---

## 4. 系统划分（解密源码与资源索引）

> 以下按已恢复源码路径、明文配置/台词、资源命名和注册信息整理模块边界。要确认具体机制仍应定位并阅读对应源码；文件名或图标本身不能证明运行行为。

### 4.1 角色本体
- `prefabs/chtholly.lua`（37KB，最大 prefab）——主角色；`prefabs/chtholly_none.lua`（0.5KB）——无服装形态（_none 惯例）。
- 资产命名佐证：`chtholly.zip` 主动画、`chtholly_red.zip`（红模式变体）、`chtholly_bundle.zip`/`chtholly_packbox`（打包/送礼）、`ghost_chtholly_build.zip`、`status_chtholly.zip`（状态条）、`names_chtholly`（名称牌）。

### 4.2 魔力/魔法武器（key1~key3 驱动）
- `prefabs/chtholly_sword.lua`（36KB）+ `chtholly_sword.zip` → 主武器，注册日志含 `chtholly_sword_shadow`（暗影派生）。
- `prefabs/chtholly_amulet.lua`（15KB）+ `chtholly_amulet.zip` + `ui_chtholly_amulet_5x5.zip` → 护符（5x5 UI 网格，功能面板）。
- `prefabs/chtholly_stafflight.lua`（9KB）→ 法杖。
- `prefabs/chtholly_hat.lua`（28KB）+ `chtholly_hat.zip` → 头盔。
- `chtholly_sword.lua` 注册含 **多武器形态**：sword_shadow 等，配合 `key3`"切换武器状态"。

### 4.3 Buff/状态系统（keybuff + redmode）
- `prefabs/chtholly_buffs.lua`（5KB）→ 注册日志含 `chtholly_buff1`、`chtholly_zhenshi_buff`（"真视"buff）；`chtholly_hat` 注册 `chtholly_packbox/packbox_placer`。
- `widgets/chtholly_bd.lua`（5KB）、`widgets/chthollymagic.lua`（1.4KB）→ 状态 buff 指示 widget；images 根 `chthollymagic.tex/xml`。

### 4.4 分身/召唤（chongwu 配置）
- `components/chtholly_summon.lua`、`chtholly_summon_new.lua`、`chtholly_summon_controller.lua`（19KB）、`chtholly_summon_new.lua`、`components/chtholly_petleash.lua`（8KB）→ 分身/宠物召唤与牵绳。
- `prefabs/chtholly_shadow.lua`（19KB）注册 `chtholly_shadow`、`chtholly_shadow_tele`（传送）、`chtholly_shadow_builder`（建造者）→ 分身=影子系。
- `brains/chtholly_shadowbrain.lua`、`stategraphs/SGchthollypet.lua`（21KB）→ 影子宠物 AI 与状态机。

### 4.5 战斗/敌人交互
- `components/chtyolly_enemyselect.lua`（注意拼写 chtyolly，作者笔误）→ 敌人选中（索敌/锁定）。
- `components/chtholly_give.lua`、`chtholly_packer.lua` → 给予/打包交互。
- `components/chtholly_controller.lua`/`_new.lua`、`chtholly_backlevelup_item.lua` → 控制器与"后退/升级"物品。

### 4.6 护盾/领域（Dome）
- `prefabs/chthllydome.lua`（21KB）注册：`chthllydome`、`chthllylrxhent`、`chtholly_molifx`、`chtholly_star_cold`、`chtholly_star_cold_new`、`chtholly_workent`、`chtholly_shadowfirefx`、`chtholly_fuhuo`（复活）→ **领域/结界/冷星/复活 FX 家族**。
- `widgets/chthollydomeover.lua`、`chthollylrxheover.lua`、images 根 `chtholly_dome_over.*`、`chthllylrxh_over.*` → dome 覆盖层 HUD。
- 资产：`chtholly_molifx.zip`、`chtholly_star_cold.zip`、`chthllylrxhent.zip`。

### 4.7 农具
- `prefabs/chtholly_farm_plow.lua`（12KB）→ `chtholly_farm_plow` + `_item` + `_item_placer` + inventoryimages `chtholly_farm_plow_item`。

### 4.8 配方/物品系统（inventoryimages 拼音缩写，22 图标）
`chtholly_recipes.lua`（41KB）注册 20+ 合成物，图标名即拼音缩写：

```
chtholly_crbn  chtholly_yxsx  chtholly_rjjdq  chtholly_ldjz
chtholly_fymrl chtholly_lyssy chtholly_lssjl  chtholly_fhym
chtholly_ly    chtholly_csdp  chtholly_lrxh   chtholly_hsjh
chtholly_sw    chtholly_fsjm  chtholly_zhenshi
chtholly_lcmjnht chtholly_mhqccjg
chtholly_ly_aoeent chtholly_fhym_aoeent chtholly_ly_fire
```

（拼音首字缩写为作者命名习惯；具体中文名可在已恢复的配方与字符串源码中查证。）

---

## 5. 语音/文案系统（明文 speech_chtholly.lua）

326KB 明文 `return { ... }`，**139 个顶层 STRINGS 块**（标准 DST speech 结构，全量覆盖）：
- `ACTIONFAIL`、`ANNOUNCE_*`（约 100 项：环境/战斗/季节/幽灵/海洋钓鱼/Klaus/Moon Altar/Ticoon 追踪 等）
- `BATTLECRY` / `COMBAT_QUIT` / `DESCRIBE` / `EAT_FOOD` 等标准段
- 证据点：含 `ANNOUNCE_SHADOWLEVEL_ITEM`、`ANNOUNCE_EQUIP_SHADOWLEVEL_T1~T4`（**暗影等级装备四阶**台词）、`ANNOUNCE_SACREDCHEST_YES/NO`、`ANNOUNCE_TICOON_*`（蒂贡宠物追踪台词）。

→ 可确认命名线索：**ShadowLevel 暗影等级装备（T1~T4）** + **SacredChest 圣匣** + **Ticoon（kitcoon 系宠物追踪）**。已恢复业务源码可用于核对其注册和行为；这份架构索引不代替对应源码审查。

---

## 6. 资产命名规律（可复用规范）

### 6.1 anim zip（12）
- 角色主包 `chtholly.zip`；配色变体 `chtholly_red.zip`（红模式）；装备 `chtholly_sword/amulet/hat/bundle`；状态 `status_chtholly`；特效 `chtholly_molifx/star_cold`；UI `ui_chtholly_amulet_5x5`；伙伴 `chthllylrxhent`；幽灵 `ghost_chtholly_build`。

### 6.2 images（70）
- `inventoryimages/`：22 个 xml 图标（一物一 atlas，XML 单 Element 满幅 UV）→ **物品 = inventoryimages 名**。
- `map_icons/chtholly`；`avatars/`（头像/幽灵/自检）；`saveslot_portraits`、`selectscreen_portraits`（+`_silho` 剪影）——角色标准五件套目录。
- 覆盖层 HUD：根目录 `chtholly_dome_over` / `chthllylrxh_over` / `chthollymagic`。

### 6.3 bigportraits（4）
`chtholly` + `chtholly_none`（tex+xml）——完整角色大图含无服装态。

---

## 7. 技术亮点 / 设计模式（可借鉴）

1. **明文 STRINGS 可辅助建立模块索引**：327KB 台词表能暴露 ShadowLevel（四阶）/SacredChest/Ticoon 等命名线索；现在业务源码也已恢复，应交叉检查代码，不再把台词推测当成唯一证据。
2. **魔力 charge/burst 双阶段资源**：魔力聚集(消耗/秒)+释放(消耗/次)的按键手感设计，`maxmagic/magicregen` 完整成长线。
3. **多层防御兜底**：减伤 / 单次伤害上限 / 10s 扣血上限 / 闪避率 四层叠加，配合 90% 闪避默认值——强生存角色数值设计范例。
4. **红模式（redmode）**：低理智(0)触发形态切换，配合 `chtholly_red.zip` 独立配色动画 = 低成本"二阶段角色"实现。
5. **拼音缩写图标命名**：22 个配方物品用拼音首字命名（crbn/yxsx/rjjdq…），适合快速批量注册 inventory 图标；缺点是辨识度低（学习反向案例）。
6. **分身=shadow 家族**：主 prefab 一个文件注册多个 prefab（shadow/tele/builder），共享动画 `chtholly_shadow`，是批量实体注册的最小单位范例。

---

## 8. 后续复核指引

- 先对原始文件做哈希和清单，再在独立输出目录运行恢复流程；不要覆盖创意工坊原件或旧进度。
- 每个目标 Mod 都要单独提取其字母表和映射表。相同的 loader 标记或外观相似，不代表内层解码器可复用。
- 保留原始字节，不随意剥离前缀/后缀；用反向编码逐文件还原密文，并用独立提取的纯解码器做第二路逐字节比对。
- 将 Lua 5.1 语法检查与执行、游戏内验证分开报告。不要为了提取源码运行未知加载器或反篡改分支；本案例的源码恢复不需要启动 DST 或执行原 Mod。
- 本案例产物和复现命令见 `D:\mods\资料包\chtholly_3440394425\recovery_verified\README.md`。恢复副本的编译和字节一致性检查通过，但游戏内运行尚未验证。
