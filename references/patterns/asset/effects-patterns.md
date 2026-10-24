# FX、光与声音的组合模式

先区分动画 FX、真实 Light、粒子和 UI 覆盖，再选择网络载体/本地表现。以下原版名称是查证入口；读取它们时仍按目标安装版本核对，不继承项目私有资源或固定参数。

## 模式选择

| 需求 | 优先形态 |
|---|---|
| 一次性动画 | 已有 FX Prefab 或自己的网络/本地动画实体，明确 animover/timeout |
| 循环光环 | 所属效果管理生命周期，结束撤销自己的 FX 和循环声音 |
| 真实照明 | entity:AddLight，光源可见状态和玩法查询分别核对 |
| 粒子 | entity:AddVFXEffect 与 Envelope/EmitterManager，限制数量和寿命 |
| 仅本地提示 | 非联网客户端实体或短命网络代理触发本地表现 |

房主也有可视客户端；用 TheNet:IsDedicated 区分是否创建本地渲染，不能断言主机没有 AnimState。Network、公共标签与所需复制状态按当前实体骨架创建，SetPristine 不自动同步任意 Lua 字段。

资源文件、bank、build、animation、symbol 分开核对，不拼 build 名推导所有 Asset ZIP；合法包可 build-only/animation-only。Mod 的 SetRenderResources 等路径按实际接口 resolvefilepath，声明 Asset 不等于所有消费函数都会定位 Mod 根。

## 生命周期

一次性完成、提前取消、目标删除和重施共用幂等收尾。删除旧任务/旧 FX 前核对它仍属于该轮效果，旧回调不能清掉新句柄。persists=false 只表示不保存，不会自动定时删除。

工厂数据适合相近变体，但 fn、颜色与动画字段是本项目接口，不自动成为原版注册 API。需要新 FX 时按真实资源与任务授权创建，不从参考文件私有 prefab 名推导已注册。

原有拼装模板已移除重复且不成立的资源/端别假设；完整构造步骤统一查 [FX 专题](../../world-ui-assets/dst-fx-vfx-authoring/GUIDE.md)、[动画资源](../../world-ui-assets/dst-assets-animation-atlas/GUIDE.md) 和 [粒子细节](vfx-particle-practical-guide.md)。下列模式保留各自原版检索入口。

## 模式：生成本地专属特效的网络代理

观察到的官方参考：

- `scripts/prefabs/moose_nest_fx.lua`

观察到的流程：

1. 生成一个小型网络代理预制件
2. 在非专用客户端上，延迟一帧并生成本地特效实体
3. 在服务器上，保持代理短暂且非持久化

用于同步演示触发器，客户端只需要本地视觉效果。

## 模式：仅声音代理

观察到的官方参考：

- `scripts/prefabs/atrium_gate_pulsesfx.lua`

观察到的流程：

- 生成一个带有 `FX` 的小型网络代理
- 在非专用客户端上，生成本地非网络声音发射器实体
- 当声音应该是听众相对的时，将其父级相对于 `TheFocalPoint`
- 播放声音
- 立即移除本地声音实体

用于警告提示、区域本地化提示和其他没有持久世界对象的客户端听到的声音事件。

## 模式：组合动画特效（可选声音和灯光）

观察到的官方参考：

- `scripts/prefabs/deer_fx.lua`

观察到的形态：

- `AddAnimState()`
- 可选 `AddSoundEmitter()`
- 可选 `AddLight()`
- `AddNetwork()`
- `FX` 标签
- 可选的 netvar 驱动灯光淡入淡出更新
- 服务器上的 `inst.persists = false`
- 根据数据，一次性移除或循环动画

规则：

- 用于元素法术特效、充能圈、循环光环和其他共享特效系列
- 如果有许多相似变体，使用一个工厂函数加数据表

## 模式：使用 `AddVFXEffect` 的粒子特效

观察到的官方参考：

- `scripts/prefabs/torchfire_barber.lua`

观察到的形态：

- 将粒子纹理和着色器注册为资源
- 通过 `EnvelopeManager` 添加颜色和缩放包络
- 调用 `inst.entity:AddVFXEffect()`
- 初始化一个或多个发射器
- 配置渲染资源、粒子计数、生命周期、混合模式、UV 帧大小、光晕和排序偏移
- 从任务或更新逻辑驱动粒子生成

在以下情况下使用：

- `AnimState` 精灵动画表现力不够
- 效果实际上是一个粒子系统
- 需要烟雾、余烬、火花、火焰羽流或类似的分层粒子

规则：

- 使用 `AnimState` 处理普通精灵动画
- 仅当效果真正以粒子为导向时才使用 `VFXEffect`

## 声音播放模式

观察到的官方用法：

- `inst.SoundEmitter:PlaySound("event/path")`
- `inst.SoundEmitter:PlaySound("event/path", "loop")`
- `inst.SoundEmitter:KillSound("loop")`
- `inst.SoundEmitter:PlayingSound("loop")`
- `inst.SoundEmitter:SetParameter("loop", "intensity", value)`

典型用途：

- 一次性提示音
  - `PlaySound("event/path")`
- 循环环境音或机器嗡嗡声
  - `PlaySound("event/path", "loop")` 稍后 `KillSound("loop")`
- 参数驱动循环
  - 重用命名循环并用 `SetParameter(...)` 调整

观察到的官方参考：

- `winona_battery_low.lua`
- `moon_altar.lua`
- `spiderden.lua`

## SG 定时声音

在 `scripts/stategraph.lua` 中验证，并在 SG 文件如 `SGhound.lua` 中观察到：

- `SoundTimeEvent(time, "event/path")`
- `SoundFrameEvent(frame, "event/path")`

规则：

- 当声音必须与击中帧或动画状态对齐时使用
- 如果时序属于表演者动画，将其放在 SG 时间轴中
- 除非官方模式这样做，否则不要用临时延迟任务替换帧精确的 SG 时序

## 标签索引

围绕灯光、特效和声音的高频标签：

- `FX`
  - 视觉或演示辅助实体
- `NOCLICK`
  - 辅助不应成为鼠标目标
- `NOBLOCK`
  - 辅助不应阻挡放置或移动

观察到的官方示例：

- 许多辅助和特效预制件使用 `FX` + `NOCLICK`
- 放置安全辅助经常添加 `NOBLOCK`

规则：

- 根据交互需求选择这些标签，而不是习惯
- 玩家应该检查或点击的世界对象通常不应该标记为 `NOCLICK`

## 模式：烘焙动画 + 代码拼装的投射物弹幕

当任务是「飞行弹 / 自动索敌弹 / 多彩拖尾」，或用户说「动画是代码生成的」时，用本模式。资源侧反编译与分层判断见 `references/patterns/asset/animation-build-patterns.md`。

完整参考样例（用户提供的源文件，非游戏本体；未点名不要擅自打开）：

- `C:\Users\李博\Downloads\hatred_star_projectile\`（`anim.bin` + `build.bin` + `atlas-0.tex`）
- `C:\Users\李博\Downloads\hatred_homingbullet.lua`

### 分层

1. **烘焙层**：`Asset("ANIM", "anim/....zip")`，只负责部件绕心自转等局部循环（如 `attack`，40fps 约 0.6s 一圈）。
2. **代码层**：染色、相位、拖尾克隆、飞行与索敌全部在 prefab Lua。

### 烘焙层接入

```lua
inst.AnimState:SetBank("hatred_star_projectile")
inst.AnimState:SetBuild("hatred_star_projectile")
inst.AnimState:PlayAnimation("attack", true)
inst.AnimState:SetTime(math.random() * inst.AnimState:GetCurrentAnimationLength())
```

要点：`SetTime` 随机起点让多发不同相位；不要为「看起来转得不一样」去重做多套 anim。

### 运行时染色与发光

```lua
inst.AnimState:SetBloomEffectHandle("shaders/anim.ksh")
inst.AnimState:SetMultColour(r, g, b, alpha) -- 参考文件中为红/白/紫/蓝四选一
inst.AnimState:SetLightOverride(0.3)
```

贴图常为白色蒙版；**最终颜色以代码为准**，反编译 atlas 只会看到白星。

### 尾迹残影（代码生成拖尾）

观察到的形态：

- 非专用服务器侧 `DoPeriodicTask(TAIL_PERIOD, UpdateTail)`（如 `5 * FRAMES`）
- 每次 `CreateEntity` + 同 bank/build/anim + 再随机 `SetTime` / 四色 + 更低 alpha
- `DoTaskInTime(.25, Remove)` 短命销毁；`persists = false`
- 按瞬时速度 `SetScale`（速度越大拖尾越长）
- 朝向用两帧位置 `atan2` 估计，不用 `Transform:GetRotation()`（避免朝向断续）
- 出生前短时间打 `NoTail` tag，避免首帧自激拖尾
- 标签：`FX` + `NOCLICK` + `NOBLOCK`

### 飞行与索敌（不在 anim 里）

- `Physics:SetVel` 每帧写速度；y 给小升力常数（如 `1.5`）
- free：正弦侧摆 `sin(elapsed * ω) * 振幅` 叠在前进方向上
- track：期望角 + `NormalizeAngle` 差速插值，限每帧转角
- 伤害结算与索敌权重属于 combat 逻辑，与 AnimState 解耦

### 常见失败点

- 只交付 anim zip 却期望有多色拖尾
- 客机用 `Physics` 取速度导致拖尾密度不一致 → 应用位置差分
- 尾迹 FX 未去 `NOCLICK`/`NOBLOCK` 或未定时 Remove → 残留实体
- 主体与拖尾共用同一 `SetTime` 初值 → 看起来是「厚块」而非残影链

## 意图索引

- "我想添加一个发光结构"
  - 从发光世界结构模式开始
  - 检查 `moon_altar.lua`
- "我想添加一个手持或附加灯光"
  - 从子灯光辅助模式开始
  - 检查 `lighterfire_common.lua`
- "我想添加一个一次性视觉效果预制件"
  - 从一次性动画特效预制件模式开始
  - 检查 `moose_nest_fx.lua`
- "我想让服务器触发特效但客户端本地生成"
  - 从网络代理特效模式开始
  - 检查 `moose_nest_fx.lua`
- "我想要一个仅声音的提示或警告"
  - 从仅声音代理模式开始
  - 检查 `atrium_gate_pulsesfx.lua`
- "我想要一个循环光环或法术效果（可选灯光和声音）"
  - 从共享特效工厂模式开始
  - 检查 `deer_fx.lua`
- "我想要烟雾、火花或火焰粒子"
  - 从 `AddVFXEffect` 开始
  - 检查 `torchfire_barber.lua`
- "我想要声音完全在动画帧上"
  - 从 `SoundFrameEvent(...)` 开始
  - 检查最接近的已经这样做的官方 SG
- "我想要飞行弹多色拖尾 / 自动索敌弹幕"
  - 从「烘焙动画 + 代码拼装的投射物弹幕」模式开始
  - 反编译 anim 用 `anim_scml_tool.py`；拖尾与染色读参考 Lua，不要只看 atlas

## 常见失败点

- 效果永久存在
  - 忘记 `animover` 移除、定时移除或 `persists = false`
- 辅助捕获鼠标悬停或阻挡放置
  - 缺少 `NOCLICK` 或 `NOBLOCK`
- 灯光在服务器上存在但在客户端上不存在
  - 错误的复制形态或缺少客户端侧辅助创建
- 使用 `VFXEffect` 处理简单 `AnimState` 预制件可以处理的事情
  - 不必要的复杂性
- 声音循环永不停止
  - 关闭或移除时缺少 `KillSound(...)` 路径
- 将声音或灯光逻辑添加到错误的运行时侧
  - 检查官方模式是否使用代理、子实体或 SG 时间轴

## 实用阅读顺序

1. 阅读最接近效果形态的官方预制件。
2. 如果任务也改变交互，检查 `references/patterns/prefab/tag-patterns.md`。
3. 如果任务也改变燃烧、燃料或放置逻辑，检查匹配的世界系统或组件页面。
4. 如果时序属于动画状态，检查 `references/gameplay/dst-stategraph-authoring/references/stategraph-contract.md`。
5. 如果效果需要自定义资源，还请阅读 `references/patterns/asset/asset-patterns.md`。

## 经验法则

- 使用 `AnimState` 特效处理普通精灵效果。
- 使用 `VFXEffect` 处理真正的粒子系统。
- 当客户端只需要本地演示时使用代理模式。
- 根据交互需求选择 `FX`、`NOCLICK` 和 `NOBLOCK`，而不是默认使用。