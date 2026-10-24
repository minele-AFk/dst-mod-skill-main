# 动画构建模式

当任务涉及编译 `.scml`、重新构建 `anim/*.zip`、将已编译的动画 zip 恢复为 `.scml`，或理解 Don't Starve Mod Tools 生成的 `exported/<name>/` 动画工作区时，请阅读本页面。

## 工具选型

| 场景 | 推荐 |
|---|---|
| 交互式动画创作、预览、批量编辑、AI 驱动 | **DST Mod Tool**（Lua IPC），见 [dst-mod-tool.md](../../tools/general/dst-mod-tool.md) |
| `.scml` → `anim zip` 最终编译 | 官方 `Don't Starve Mod Tools`（`scml.exe`） |
| 反编译已编译 zip | `anim_scml_tool.py` |

## 优先使用官方 Mod Tools（编译链）

使用本地安装的 `Don't Starve Mod Tools` 作为动画编译的权威来源。

高价值文件：

- `mod_tools\scml.exe`
- `mod_tools\tools\scripts\buildanimation.py`
- `mod_tools\compiler_scripts\zipanim.py`
- `mod_tools\exported\export.py`

实践规则：

- 优先使用官方 Mod Tools，而非第三方动画打包工具
- 将 `build.bin`、`anim.bin` 和 `atlas-*.tex` 视为编译输出，而非手动编辑的源文件
- 当任务仅是"重新构建动画"时，先进行编译，仅在用户明确要求修改资源时才编辑 `.scml`
- 当原始源文件 `.scml` 缺失且用户需要检查或恢复时，使用 `references/tools/general/anim_scml_tool.py` 反编译已编译的 zip

## 官方构建链

本地 Mod Tools 链分为两个阶段工作。

1. `scml.exe` 读取一个 `.scml` 文件及其同级的 PNG 文件夹。
2. 它重新生成同文件夹下的中间文件 `<name>.zip`。
3. 然后驱动正常的编译器流程，并写入最终的 `anim/<name>.zip`。

观察到的本地行为：

- 输入：`exported/huohuo/huohuo.scml`
- 重新生成的中间文件：`exported/huohuo/huohuo.zip`
- 最终编译输出：`<output_dir>/anim/huohuo.zip`

实践规则：

- 重新生成的同文件夹 zip 是构建中间产物，而非主要的用户创作源文件
- 当用户说"编译这个 `.scml`"时，从 `.scml` 开始，而非要求他们指向中间 zip
- 如果该同文件夹 zip 在另一个程序中打开，且构建因权限或锁定错误而失败，请解释工具正在尝试覆盖其自身的中间输出

最终编译的 zip 包含以下文件：

- `anim.bin`
- `build.bin`
- `atlas-0.tex`
- `atlas-1.tex`

## 恢复已编译的动画 Zip / 已解包目录

当用户有一个已编译的 `anim/<name>.zip`，或已解包目录（`anim.bin` + `build.bin` + `atlas-*.tex`），并希望检查动画内容时，请使用 `references/tools/general/anim_scml_tool.py`。

示例：

```bash
python references/tools/general/anim_scml_tool.py decompile anim/huohuo.zip --output-dir .tmp/exported/huohuo_recovered --force
python references/tools/general/anim_scml_tool.py decompile path/to/extracted_dir --output-dir .tmp/exported/preview --force
```

该脚本读取：

- `build.bin`
- `anim.bin`
- `atlas-*.tex`

它写入：

- `<buildname>.scml`
- SCML 引用的符号 PNG 文件夹

实践规则：

- 这是恢复/反编译工作流，而非首选的源工作流
- 输入 zip/目录必须同时包含 `build.bin` 和 `anim.bin`；某些角色构建包仅包含 `build.bin` 加图集，不是独立的动画
- 恢复的 SCML 可能会丢失保真度，因为 Spriter 无法表达所有 DST 原生变换（如剪切）
- 当用户的原始导出 `.scml` 和 PNG 文件夹存在时，优先使用它们
- 使用恢复的输出进行检查、小范围编辑或重建丢失的源工作区
- 编辑恢复的 SCML 后，通过 `references/tools/general/scml_build_tool.py build` 进行编译，而非编辑 `anim.bin` 或 `build.bin`
- **不要把预览当作游戏内最终观感**：颜色、相位、拖尾、飞行轨迹常由运行时 Lua 叠加（见下一节）

### 离线读动画元数据（不解 SCML 也可）

`anim_scml_tool.py` 的 `parse_build` / `parse_anim` 可直接二进制解析，用于快速回答「有哪些动画、多少帧、fps、符号帧数」：

```python
from anim_scml_tool import parse_build, parse_anim
build = parse_build(open("build.bin", "rb").read_bytes(), "build.bin")
anims = parse_anim(open("anim.bin", "rb").read_bytes(), "anim.bin")
# anim.name / anim.frame_rate / len(anims[0].frames)
# build.symbols[hash].frames / frame.atlas_bbox
```

实测结构要点（ANIM v4 / BILD v6，与 `official-esctemplate-spec.md` 一致）：

- 动画名、bank 名在 v4 末尾字符串表；元素含 `hash | build_frame | layer_hash | matrix(4×f32) | tx | ty | z`
- `build_frame` 选择符号的哪一帧贴图；多数投射物动画**只引用 frame 0**，用 matrix 做旋转/位移
- 符号多帧（如 8 个预烘焙旋转星）可以存在但本动画不用——不要假设「有 N 帧就一定逐帧播」

### 离线动画预览（GIF / 胶片条）

反编译得到 SCML + 符号 PNG 后，可按 timeline 的 `x/y/angle` 用 Pillow 合成循环预览（不进游戏）：

1. 读 SCML `animation/timeline/key`（或直接用 `parse_anim` 的 matrix）
2. Spriter 坐标 y 向上、角度逆时针；贴到画布时 `screen_y = cy - y`，PIL `rotate(angle)` 需以 pivot 为 `center`
3. 输出：循环 GIF（建议 25ms/帧对齐 40fps）+ 全帧缩略胶片条，便于不依赖 GIF 播放也能看节奏
4. 可选：中心点 + 轨道半径参考圈，便于辨认「绕心自转 / 局部摆动 / 位移」

## 烘焙动画 + 代码拼装表现

分析投射物 / 弹幕类资源时，先分清两层，避免只反编译 anim 就以为「动画效果齐了」。

| 层 | 负责什么 | 典型落点 |
|---|---|---|
| 烘焙 anim zip | 部件绕心自转、形变、局部 idle/attack 循环 | `anim.bin` + `build.bin` + atlas |
| 运行时 Lua | 随机相位、染色、发光、拖尾残影、飞行/索敌 | prefab `AnimState` + `DoPeriodicTask` + `Physics` |

判断口诀：

1. 用户说「这动画是代码生成的」时，先反编译看**烘焙**做了什么，再读 prefab 看**运行时**叠了什么
2. 纯白 sprite + 代码里 `SetMultColour` → 视觉颜色以代码为准
3. 单动画却出现多色拖尾 → 几乎一定是 `CreateTailFx` 类克隆，不是 build 里的多符号
4. 预览 GIF 只能证明「部件运动」，不能证明「飞行路径/拖尾」

完整模式、接入代码与失败点见 `effects-patterns.md` 的「烘焙动画 + 代码拼装的投射物弹幕」。

已验证样例：

- 解包目录与 Lua 路径见 `effects-patterns.md` 样例节
- 银行/构建 `hatred_star_projectile`；动画 `attack`（40fps，24 帧，~0.6s 绕心公转+自转）
- 符号 `image` 有 8 个预旋转帧，但 `attack` 只用 frame 0 + matrix

## 重要的 CLI 细节

`scml.exe` 将输出目录作为其第二个参数。不要将第二个参数当作目标 zip 文件名。

示例：

```bash
python references/tools/general/scml_build_tool.py build .tmp/exported/huohuo/huohuo.scml --output-dir .tmp/exported/compiled
```

这会生成：

- 更新的中间 zip：`.tmp/exported/huohuo/huohuo.zip`
- 最终编译的 zip：`.tmp/exported/compiled/anim/huohuo.zip`

如果输出参数看起来像 `something.zip`，Mod Tools 仍会将其视为文件夹，并创建 `something.zip/anim/...`。

## 中间 Zip 已存在时的快速路径

如果导出文件夹已包含 `<name>.zip`，可以跳过 `.scml` 步骤，直接通过 `buildanimation.py` 编译该 zip。

示例：

```bash
python references/tools/general/scml_build_tool.py compile .tmp/exported/huohuo/huohuo.zip --output-dir .tmp/exported/compiled --force
```

在以下情况下使用此快速路径：

- 用户已经有一个最新的导出 zip
- 任务仅是重新构建 `anim/<name>.zip`
- 需要围绕纹理格式或图集输出进行更窄范围的调试循环

不要仅仅因为导出文件夹恰好包含 `<name>.zip` 就默认切换到此路径。该 zip 通常存在是因为官方 `.scml` 构建路径之前生成了它。

## 文件布局要求

`.scml` 文件应位于一个导出动画文件夹的根目录，其引用的 PNG 文件夹应与其并排。

典型结构：

```text
exported/huohuo/
  huohuo.scml
  huohuo.zip
  face/
  torso/
  hand/
  ...
```

实践规则：

- 将图像文件夹放在 `.scml` 旁边
- 不要将 PNG 文件夹移离 `.scml`，然后期望相对路径继续工作
- 不要假设 `bigportraits/` 或其他 UI 纹理属于已编译的 `anim/*.zip`；动画编译仅消耗导出构建引用的内容

## 验证检查清单

- 在承诺编译支持之前，确认本地安装了 `Don't Starve Mod Tools`
- 在使用 `.scml` 构建路径之前，确认 `scml.exe` 存在
- 在使用 zip 快速路径之前，确认 `buildanimation.py` 和捆绑的 Python 2.7 存在
- 编译后，确认最终的 zip 存在于 `anim/` 下
- 如果编译的 zip 异常小或缺少 `build.bin` 或 `anim.bin`，则视为编译失败