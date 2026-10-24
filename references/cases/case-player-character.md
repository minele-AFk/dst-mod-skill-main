# 设计案例：联机人物的装配与生命周期

普通角色使用 prefabs/player_common 返回的 MakePlayerCharacter 工厂。示例只说明接入职责，不包含角色美术、平衡数值、初始物品与完整机制。

## 模块骨架

```lua
local MakePlayerCharacter = require("prefabs/player_common")

local function common_postinit(inst)
    inst:AddTag("my_mod_character")
    -- 双端所需状态在此建立；普通 Lua 字段不会自动复制。
end

local function master_postinit(inst)
    inst.soundsname = "wilson"
    -- 按已确认设计设置组件数值和权威事件。
end

return MakePlayerCharacter("my_mod_character", nil, nil,
    common_postinit, master_postinit)
```

注册所需 PrefabFiles 与 AddModCharacter，配套资源与字符串沿 [角色专题](../gameplay/dst-character-authoring/GUIDE.md) 核对。文件名、角色名、build 可以显式映射，不以“全部同名”代替消费者检查。

## 特殊能力应挂在哪条链

| 能力 | 合同 |
|---|---|
| 夜间视野 | 本地玩家 playervision/复制状态及来源栈；不是 playercontroller:SetOverrideVisionRadius |
| 受到攻击后回复理智 | 服务端 attacked 生产端与实际 data；验证是否每次命中/格挡都触发 |
| 速度修饰 | locomotor 私有来源键 Apply/Remove，死亡/复活/读档策略一致 |
| 状态条 | Controls/StatusDisplays 的客户端生命周期，绑定时读初值 |
| 小地图图标 | 确认 MiniMapEntity、图集和 Element，再设置真实资源 |
| 攻击或技能 | Action/SG/权威组件链，不在 UI 直接改组件 |

不向已经由工厂装配的玩家重复 AddComponent("playercontroller")；温度组件没有可凭名字假定的 Reset()。当前世界用 TheWorld，不继承旧单机 GetWorld/GetPlayer 调用。

## 存档、幽灵与复活

工厂包装 master 内提供的 OnSave/OnLoad；后续 PostInit 不可直接覆盖并丢掉玩家原逻辑。专属进度保存到自定义组件，恢复逻辑幂等。

服务端成功复活链与请求、进入幽灵及本地 HUD 显示分别处理；不能把“监听复活”当作新建与幽灵入场都会初始化。以已复制 ghost 状态驱动本地表现，不能期待服务端事件自动传到客机。

## 检查顺序

新建角色 → 主机可玩 → 真实远端选择与进入 → 幽灵进入/复活 → 重连/换洞穴 → 旧档缺字段。语法/组件声明检查和游戏画面分别报告。

延伸：[能力值案例](case-custom-stat.md)、[HUD 合同](../world-ui-assets/dst-hud-screens-input/references/hud-customization.md)、[Buff 与夜视](../gameplay/dst-status-buffs-survival/GUIDE.md)。
