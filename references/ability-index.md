# 能力系统索引（Capability Index）

## 用途

统一归口"**角色/装备/玩家可获得的能力**"——即一个实体能做什么（被动或主动增益效果）。所有这类能力的实现虽按领域散落在各子技能，但这里按大类交叉索引，一眼找全入口。

## 概念分层：能力 vs 机制

- **能力（本文索引对象）** = 一个实体能做什么的效果本身，通常按领域实现（吃→food、buff→status、角色特征→character、装备→container）。
- **机制 / 授予方式** = 能力"怎么获得、怎么触发"（投喂升级=买点授予、Buff 模板=临时、tag/开关=常驻）。机制类文档**不归能力索引**，只在同一份能力下方给一条引导链接。

> 与"投喂升级"这类触发器解耦的原则：本索引只收能力，授予机制在其各自的子系统文档维护，能力文档尾部回链到本页。

## 能力一览

### 移动 / 环境

| 能力 | 实现文档 | 归属子技能 |
|------|----------|------------|
| 踏水 / 跨洞穴虚空行走 | [character-walkonwater.md](gameplay/dst-character-authoring/references/character-walkonwater.md) | dst-character-authoring |
| 一键跨世界迁移（回程/穿越） | [portable-cross-world-migration.md](gameplay/dst-world-systems-events-weather/references/portable-cross-world-migration.md) | dst-world-systems-events-weather |

### 生存 / 收益

| 能力 | 实现文档 | 归属子技能 |
|------|----------|------------|
| 夜视 | [buff-nightvision.md](gameplay/dst-status-buffs-survival/references/buff-nightvision.md) | dst-status-buffs-survival |
| 携带被动（暖石恒温 / 喂火把照明） | [carried-passive-buffs.md](gameplay/dst-status-buffs-survival/references/carried-passive-buffs.md) | dst-status-buffs-survival |
| 进食三维改动 | [eating-stat-modification.md](gameplay/dst-status-buffs-survival/references/eating-stat-modification.md) | dst-status-buffs-survival |
| 耐久自动维修 | [auto-repair-maintenance.md](gameplay/dst-inventory-equipment-containers/references/auto-repair-maintenance.md) | dst-inventory-equipment-containers |

### 战斗 / 防御

| 能力 | 实现文档 | 归属子技能 |
|------|----------|------------|
| 防脱手 / 防击退 / 攻击倍率 | [common-abilities.md](patterns/character/common-abilities.md) | patterns/character |
| 专属物品防偷防掉 | [exclusive-item-protection.md](gameplay/dst-inventory-equipment-containers/references/exclusive-item-protection.md) | dst-inventory-equipment-containers |

### 行动 / 行为

| 能力 | 实现文档 | 归属子技能 |
|------|----------|------------|
| 快速进食 / 快速制作 | [character-fast-abilities.md](gameplay/dst-character-authoring/references/character-fast-abilities.md) | dst-character-authoring |
| 伪进食（本不可吃变成可吃） | [pseudo-eating-ability.md](gameplay/dst-food-cooking/references/pseudo-eating-ability.md) | dst-food-cooking |

### 收纳 / 容器合集

| 能力 | 实现文档 | 归属子技能 |
|------|----------|------------|
| 便携厨具容器（保鲜 / 无限堆叠 / 三维补充 / 特效料理） | [portable-chef-container.md](gameplay/dst-inventory-equipment-containers/references/portable-chef-container.md) | dst-inventory-equipment-containers |
| 实体打包收纳 | [entity-to-item-capture.md](gameplay/dst-inventory-equipment-containers/references/entity-to-item-capture.md) | dst-inventory-equipment-containers |

## 授予机制（如何获得 / 触发能力）

| 机制 | 文档 | 归属子技能 |
|------|------|------------|
| 投喂升级（喂物触发解锁/叠加能力） | [feed-to-upgrade.md](core/dst-action-authoring/references/feed-to-upgrade.md) | dst-action-authoring |
| Buff 模板 / 临时增益 | 见 dst-status-buffs-survival 子技能 | dst-status-buffs-survival |

## 回链约定

上述各能力文档的尾部均带一条返指本页的链接（`[能力索引](ability-index.md)`），以实现双向往返。