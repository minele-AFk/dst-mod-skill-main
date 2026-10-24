# DST SCML 制作参考

## 目录

- [语料证据](#语料证据)
- [不要过度推断](#不要过度推断)
- [SCML 数据约束](#scml-数据约束)
- [动作组织](#动作组织)
- [动作设计](#动作设计)
- [部件与 pivot](#部件与-pivot)
- [层级、显隐与镜像](#层级显隐与镜像)
- [分类制作建议](#分类制作建议)
- [验证](#验证)

## 语料证据

以下数字来自 2026-08-10 对项目 `anim_unpacked/zip` 的全量 XML 解析：

- 2,247 个 SCML 全部可解析，包含 2,266 个 entity、15,695 个 animation。
- 所有文件标记为 `BrashMonkey Spriter r11`。
- 91,739 条 PNG 声明；文件系统另含未直接声明或重复用途的 PNG。
- PNG 全量检查未发现缺失或无效文件，但有 99 条 SCML 声明尺寸与 PNG IHDR 不同；这些实际文件全部是 100x100 重建占位图，集中在 13 个 SCML。将它们视为解包语料例外，不作为新资产模板。
- 15,605 个动作使用 33ms interval，约占 99.4%。其余为 83、40、37、41ms。
- 动作时长中位数为 396ms。
- 339,278 个 mainline key，6,488,844 个 timeline key。
- 从 0 到 length 的 interval 槽位中有 1,708 个没有 mainline key；静态动作和动作终点边界允许保持稀疏。
- 6,488,844 个 timeline key 全部为 `curve_type="instant"`。
- 6,488,844 个 object_ref，0 个 bone_ref。
- object_ref 到 timeline/key、object 到 folder/file 的闭合检查未发现断链。
- 所有 mainline key 和 timeline key 都落在各自动作的 interval 网格上。
- 1,685,047 个 object key 使用负 scale；10,971 个文件 pivot 坐标超出 0..1。
- 未发现对象 `a` 属性参与 alpha 动画。
- 所有 animation 都省略 `looping` 属性。不要从这一点推断游戏一定循环，运行时代码仍决定 `PlayAnimation` 或 `PushAnimation` 的循环参数。
- 高频名称包括 `idle`、`hit`、`anim`、`place`、`burnt`、`open`、`loop`、`close`、`death`。
- 生物方向动作常见 `walk_pre_side`、`walk_loop_side`、`walk_pst_side`，并配套 `up`、`down`。

从 skill 目录使用以下命令复现该统计：

```powershell
python tools/analyze_scml.py <anim_unpacked>/zip --skip-image-checks
```

## 不要过度推断

当前 SCML 来自解包与重建流程，明显呈现烘焙后的逐帧对象轨道。零 bone_ref 说明最终语料不依赖 SCML 骨骼引用，不证明原始作者工程没有骨骼、约束或补间。允许在源工程使用高效 rig，但最终导出必须通过现有 DST 工具链并与参考输出兼容。

全量语料的共同点可以作为兼容基线；尺寸、部件数量、pivot 范围、动作时长和方向数量必须从同类参考得出，不能取全局平均。

## SCML 数据约束

保持以下引用关系闭合：

1. `folder/file` 定义 PNG 相对路径、像素尺寸和默认 pivot。
2. `entity/animation` 定义动作名、`length` 和 `interval`。
3. `mainline/key/object_ref` 在每个主帧选择 timeline、timeline key 和 z_index。
4. `timeline/key/object` 选择 folder/file，并记录 x、y、scale、angle 与可选 pivot。
5. folder、file、timeline 和 key ID 都以所属父节点为作用域，不把别处 ID 当作全局 ID。

遵循当前语料的稳妥基线：

- 使用 UTF-8 XML 和 `spriter_data scml_version="1.0"`。
- 常规动作采用 33ms interval；只有明确匹配参考或运行时要求时改变。
- 将关键时间落在 interval 网格上。
- 使用 `curve_type="instant"` 保持烘焙帧，不依赖运行时补间猜测。
- 让每个已有 mainline key 显式引用该时刻所需对象；匹配参考时保留有意的稀疏槽位。
- 让目标 SCML 声明尺寸与 PNG IHDR 尺寸一致；审查原版时单独标记已知 100x100 重建占位，不据此改写声明。
- 使用正斜杠的相对 PNG 路径，避免绝对路径和越出资源目录的路径。
- 保持动作名、entity 名和 symbol 名大小写稳定。

最小静态动作也可以保留 33ms 或多个重复帧。是否采用 33ms、99ms 等长度，应优先匹配同类资产的工具链输出，不为“精简 XML”破坏兼容。

## 动作组织

先从运行时代码反推动作表：

- `idle`、`idle1`、`idle2`、`idle_loop`：常驻或变体静止。
- `*_pre`、`*_loop`、`*_pst`：进入、持续、退出三段式状态。
- `open`、`close`、`closed`：容器和机械结构。
- `place`、`build`、`raise`：部署或生成。
- `hit`、`death`、`burnt`、`frozen`：受击和状态终点。
- `walk_*_up/down/side`：多方向移动。side 通常由运行时镜像覆盖左右，但必须核对目标代码。

不要仅因原版有某名称就创建空动作。每个动作都应有代码调用者，或作为兼容占位被明确记录。

## 动作设计

按动作职责设计节奏：

- 快速交互：短预备、清晰接触、快速回收，避免每段平均分配。
- 重击：先压低重心和反向蓄力，在命中帧形成最大轮廓变化，再用较长恢复表达重量。
- 开合：把锁点、盖板、内容物和阴影的层级变化放在明确阶段。
- 行走：先固定落脚节拍，再处理躯干上下、头部延迟和附属物反相摆动。
- 待机：幅度小但周期不完全机械；保持根部稳定，避免整件漂浮。
- FX：先确定生成、扩张或飞散、消退的生命周期，再分配粒子轨道和 z_index。

在 1x 游戏尺寸和邻近对象背景下检查，不只看白底大图。DST 动作依靠夸张姿势、短暂 hold 和轮廓突变传达意图，细腻但不可见的补间没有价值。

## 部件与 pivot

Spriter pivot 通常以归一化贴图坐标记录：x 从左向右，y 从下向上。语义 pivot 应落在关节、接触点、握点或地面锚点，而不是机械地放在图片中心。

换帧时执行以下检查：

- 如果裁切框变化，保持世界中的语义锚点不跳动。
- 同一肢体的多个图形帧保持关节 pivot 一致。
- 武器和工具保留握点；建筑保留地面锚；阴影保留中心或接地锚。
- 超界 pivot 可能用于远离图形的旋转中心，不能仅因数值不在 0..1 就修正。
- PNG 四周保留足够的抗锯齿和外伸线，不让紧裁切断描边。

## 层级、显隐与镜像

每个 mainline key 的 z_index 决定当帧遮挡。角色转向、交叉手脚、开门、武器挥过身体时允许动态改变层级。

当前语料常通过以下方式表达变化：

- 对象在某帧加入或移出 mainline，而不是动画 alpha。
- timeline key 切换 folder/file，形成逐帧换图。
- 负 `scale_x` 或 `scale_y` 处理镜像和坐标系转换。
- 多个同名视觉层使用不同 timeline ID；名称不能代替 ID。

不要统一转正负 scale。先在编辑器和游戏中验证方向、angle 与 pivot 组合，否则容易造成 180 度翻转或锚点跳变。

## 分类制作建议

- 手持物：优先单图或少量状态图，pivot 锁定握点，核对 swap symbol 名称。
- 建筑：拆分基座、活动件、前后遮挡、阴影和状态覆盖，保持地面锚稳定。
- 生物：按方向拆动作族，优先落脚、脸部朝向和攻击接触点；附属物延迟跟随。
- UI：避免沿用世界物体的透视和阴影假设，严格匹配 UI 容器尺寸与 symbol。
- FX：允许多轨复用同一小图，通过位置、scale、angle、z_index 和出现时机形成群体效果。

## 验证

运行：

```powershell
python tools/analyze_scml.py <target.scml>
```

然后逐项确认：

- XML 可解析，根节点版本正确，ID 在各自作用域内存在且不重复。
- folder/file 与 timeline/key 引用存在，object_ref 指向同一时刻的 timeline key。
- PNG 路径使用安全的正斜杠相对路径，不包含绝对路径或 `..` 越界。
- PNG 存在且声明尺寸匹配；原版的 100x100 重建占位作为已知例外单独报告。
- mainline 的稀疏槽位与终点边界是有意设计，不因“补齐帧”改变参考节奏。
- 动作名、方向和 pre/loop/pst 契约与 Lua 一致。
- 时间落在目标 interval 网格，关键游戏事件能对齐明确帧。
- 首帧继承正确，末帧能无跳变进入下一状态。
- 循环首尾在位置、速度、遮挡和图形帧上闭合。
- 镜像后握点、脸、文字性标记和不对称装备方向正确。
- z_index 无穿层，隐藏 symbol 无残帧。
- 游戏实际缩放下轮廓、命中和落脚仍清楚。
- 记录未做的编译、加载或联机验证，不把 XML 通过等同于游戏通过。
