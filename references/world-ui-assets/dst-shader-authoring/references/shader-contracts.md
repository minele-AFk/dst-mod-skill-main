# DST Shader Contracts

## 目录

- [本地权威参考](#本地权威参考)
- [GLSL 兼容层](#glsl-兼容层)
- [世界 AnimState Bloom Pass](#世界-animstate-bloom-pass)
- [UIAnim AnimState 契约](#uianim-animstate-契约)
- [UI Image 契约](#ui-image-契约)
- [VFXEffect 契约](#vfxeffect-契约)
- [PostProcessor 契约](#postprocessor-契约)
- [编译与问题定位](#编译与问题定位)
- [性能](#性能)

## 本地权威参考

在同一份 DST 安装中优先读取下列文件，而不是凭记忆补全引擎接口：

- `data/scripts/gamelogic.lua`：各 `RENDERPASS` 的默认 effect；bloom 默认是 `anim_bloom.ksh`。
- `data/databundles/shaders/anim.ksh`：世界动画主 pass、图集、时间、颜色变换与光照。
- `data/databundles/shaders/anim_bloom.ksh`：世界 `AnimState` bloom pass 的输入与默认输出。
- `data/databundles/shaders/ui_anim.ksh`、`ui_anim_cc.ksh`：UI `UIAnim` 的 `AnimState` 主 pass。
- `data/databundles/shaders/ui.ksh`：最小 UI `ImageWidget`。
- `data/databundles/shaders/overheat.ksh`：`IMAGE_PARAMS` 与 UV 扭曲。
- `data/databundles/shaders/moonstorm.ksh`：`IMAGE_PARAMS`、`IMAGE_PARAMS2` 和 `ALPHA_RANGE`。
- `data/databundles/shaders/vfx_particle*.ksh`：不同 blend 家族的 GPU 粒子。
- `data/databundles/shaders/postprocess_*.ksh`、`blurh.ksh`、`blurv.ksh`：全屏和多 pass。
- `data/scripts/postprocesseffects.lua`：后处理构建、排序、sampler、uniform。
- `data/scripts/widgets/image.lua`：UI 参数写入 API。
- `data/scripts/prefabs/mistparticle.lua`：`VFXEffect` 资源绑定。

## GLSL 兼容层

使用旧式 GLSL。一个完整的最小顶点阶段是：

```glsl
attribute vec3 POSITION;
attribute vec2 TEXCOORD0;
varying vec2 UV;

void main()
{
    gl_Position = vec4(POSITION, 1.0);
    UV = TEXCOORD0;
}
```

与之匹配的完整片元阶段是：

```glsl
#if defined(GL_ES)
precision mediump float;
#endif

uniform sampler2D SAMPLER[1];
varying vec2 UV;

void main()
{
    gl_FragColor = texture2D(SAMPLER[0], UV);
}
```

避免 `#version`、`layout`、`in/out`、`texture()`、UBO、SSBO。保留 `varying` 的名称和类型；两阶段有一处不一致就会失败或产生未定义画面。

## 世界 AnimState Bloom Pass

`data/scripts/gamelogic.lua` 将 `RENDERPASS.BLOOM` 的默认 effect 设为 `shaders/anim_bloom.ksh`。`AnimState:SetBloomEffectHandle()` 覆盖的是这个 pass，不是世界实体的正常 `anim.ksh` 主 pass。

标准输入包括普通矩阵路径和 `SKINNED` fast-animation 路径：

```glsl
#ifdef SKINNED
uniform mat4 pv;
uniform mat4 fastanim_xform;
uniform vec4 fastanim_bones[64];
#else
uniform mat4 MatrixP;
uniform mat4 MatrixV;
uniform mat4 MatrixW;
#endif

attribute vec4 POS2D_UV;
varying vec3 PS_TEXCOORD;
```

`POS2D_UV.z` 是 `u + samplerIndex * 2`；`SKINNED` 路径还把 bone index 编在 `POS2D_UV.w`。直接从 `assets/templates/anim_effect.vs` 开始，避免只支持普通矩阵路径。

绑定 Mod 自己的 bloom shader：

```lua
local SHADER = "shaders/my_anim_bloom.ksh"

Assets = Assets or {}
table.insert(Assets, Asset("SHADER", SHADER))

inst.AnimState:SetBloomEffectHandle(resolvefilepath(SHADER))
```

这只改变 bloom pass。若需求是任意修改世界实体主 pass，先说明公开 Lua 使用面没有与 UI `SetDefaultEffectHandle()` 等价、已由本地脚本验证的通用路线；不要把 bloom API 冒充主 pass API。

## UIAnim AnimState 契约

`UIAnim:GetAnimState()` 使用与世界动画相似的 atlas 编码，但主 effect 可通过 `SetDefaultEffectHandle()` 替换。本地脚本中的 `ui_anim_cc.ksh` 用法证明了这条 UI 路线。

```lua
local UI_ANIM_SHADER = "shaders/my_ui_anim.ksh"

Assets = Assets or {}
table.insert(Assets, Asset("SHADER", UI_ANIM_SHADER))

local animstate = ui_anim:GetAnimState()
animstate:SetDefaultEffectHandle(resolvefilepath(UI_ANIM_SHADER))
```

片元阶段通常从 `SAMPLER[0]` / `SAMPLER[1]` 选择 atlas，并乘 `COLOUR_XFORM`。使用 `assets/templates/ui_anim_effect.*` 保留 `SKINNED`、双 atlas、`COLOUR_XFORM` 和预乘颜色上限。

不要把这个模板用于 `Image` widget；后者使用 `MatrixPVW`、`POSITION`、`TEXCOORD0`、`DIFFUSE` 的独立输入布局。

## UI Image 契约

共享 UI `ImageWidget` 顶点输入：

```glsl
uniform mat4 MatrixPVW;
attribute vec3 POSITION;
attribute vec2 TEXCOORD0;
attribute vec4 DIFFUSE;
varying vec2 PS_TEXCOORD;
varying vec4 PS_COLOUR;
```

应在顶点阶段预乘：

```glsl
PS_COLOUR = vec4(DIFFUSE.rgb * DIFFUSE.a, DIFFUSE.a);
```

| shader uniform | Lua 写入 | 启用注意事项 |
| --- | --- | --- |
| `IMAGE_PARAMS` (`vec4`) | `Image:SetEffectParams(a, b, c, d)` | 本地 `heatover.lua` 直接写入即可；不要声称始终必须 `EnableEffectParams(true)`。 |
| `IMAGE_PARAMS2` (`vec4`) | `Image:SetEffectParams2(a, b, c, d)` | 本地 `playerhud.lua` 在使用前显式调用 `EnableEffectParams2(true)`；自定义 effect 也按此做。 |
| `ALPHA_RANGE` (`vec2`) | `Image:SetAlphaRange(min, max)` | 仅在 shader 声明并使用该 uniform 时写入。 |
| `SAMPLER[0]` | Image 当前纹理 | 由 `ImageWidget` 绑定。 |

`EnableEffectParams(true)` API 确实存在，但 `IMAGE_PARAMS` 的现有调用并不统一要求它。需要第二组参数时使用：

```lua
image:SetEffect(resolvefilepath("shaders/my_ui_effect.ksh"))
image:EnableEffectParams2(true)
image:SetEffectParams(time, strength, 0, 0)
image:SetEffectParams2(value1, value2, 0, 0)
```

从纹理采样后先乘 `PS_COLOUR`，再改变颜色，避免破坏预乘 alpha。

## VFXEffect 契约

常规 additive 粒子的输入为：

```glsl
uniform mat4 MatrixPVW;
attribute vec3 POSITION;
attribute vec3 TEXCOORD0_LIFE; // xy UV, z normalized life
attribute vec4 DIFFUSE;        // colour envelope result
varying vec3 PS_TEXCOORD_LIFE;
varying vec4 PS_COLOUR;
```

`vfx_particle_add.vs` 把 RGB 乘 alpha，因此片元阶段再应用生命周期淡出时，必须同时缩放 RGB 和 alpha：

```glsl
float fade = 1.0 - PS_TEXCOORD_LIFE.z;
gl_FragColor = vec4(
    texel.rgb * PS_COLOUR.rgb * fade,
    texel.a * PS_COLOUR.a * fade
);
```

`vfx_particle_reveal` 是不同契约：其顶点阶段不预乘 RGB，片元输出也不等同于 additive 模板。先按所需 blend 家族选择参考，不要混合两套公式。

注册并绑定 Mod 资源：

```lua
local TEXTURE = "images/my_particle.tex"
local SHADER = "shaders/my_particle.ksh"

Assets = Assets or {}
table.insert(Assets, Asset("IMAGE", TEXTURE))
table.insert(Assets, Asset("SHADER", SHADER))

effect:InitEmitters(1)
effect:SetRenderResources(0, resolvefilepath(TEXTURE), resolvefilepath(SHADER))
effect:SetMaxNumParticles(0, 64)
effect:SetMaxLifetime(0, 1.5)
effect:SetColourEnvelope(0, "my_colour_envelope")
effect:SetScaleEnvelope(0, "my_scale_envelope")
```

需要世界光照时参考 `vfx_particle.ksh`，并保留 `MatrixW`、世界位置、`LIGHTMAP_WORLD_EXTENTS` 与对应 lightmap sampler。

## PostProcessor 契约

后处理注册通常写在 `modmain.lua`。该入口只注入有限的 Lua 函数和模组 API；先显式局部化没有注入的对象：

```lua
local assert = GLOBAL.assert
local tonumber = GLOBAL.tonumber
local PostProcessorEffects = GLOBAL.PostProcessorEffects
local resolvefilepath = GLOBAL.resolvefilepath
```

`modmain.lua` 执行时 `GLOBAL.PostProcessor` 仍为 nil；引擎稍后创建它，再调用模组 Shader 回调。因此要在回调或实际调用的辅助函数内读取：

```lua
AddModShadersInit(function()
    local PostProcessor = GLOBAL.PostProcessor
    -- Create uniforms and effects here.
end)
```

多 pass 还需要从 `GLOBAL` 局部化 `hash`、`WRAP_MODE`、`FILTER_MODE`、`MIP_FILTER_MODE`、`SamplerSizes`、`SamplerColourMode` 和 `SamplerEffectBase`。不要在 `modmain.lua` 中直接假设这些名称已注入。

基础全屏顶点阶段：

```glsl
attribute vec3 POSITION;
attribute vec2 TEXCOORD0;
varying vec2 PS_TEXCOORD0;

void main()
{
    gl_Position = vec4(POSITION, 1.0);
    PS_TEXCOORD0 = TEXCOORD0;
}
```

`AddPostProcessEffect()` 的 `SAMPLER[0]` 是当前屏幕。额外 sampler 由 `AddSampler()` 的调用次序决定：第一次是 `SAMPLER[1]`，第二次是 `SAMPLER[2]`。

| `AddUniformVariable(name, size)` | GLSL 类型 |
| --- | --- |
| `1` | `float` |
| `2` | `vec2` |
| `3` | `vec3` |
| `4` | `vec4` |

普通自定义 uniform 必须按顺序执行：

```lua
local id = PostProcessor:AddUniformVariable("MY_VALUE", 1)
local effect = PostProcessor:AddPostProcessEffect(resolvefilepath("shaders/my_effect.ksh"))
PostProcessor:SetEffectUniformVariables(effect, id)
PostProcessor:SetUniformVariable(id, 0.5)
```

创建资源写进 `AddModShadersInit()`；排序和启用写进 `AddModShadersSortAndEnable()`：

```lua
PostProcessor:SetPostProcessEffectAfter(effect, PostProcessorEffects.ColourCube)
assert(PostProcessor:EnablePostProcessEffect(effect, true))
```

`SamplerEffectBase` 决定 sampler effect 的 `SAMPLER[0]`：

| 值 | 来源 | 是否需要附加 ID |
| --- | --- | --- |
| `PostProcessSampler` | 当前屏幕 | 否 |
| `BloomSampler` | bloom 缓冲 | 否 |
| `Shader` | 已存在的 sampler effect | 是，传 effect ID |
| `Texture` | `AddTextureSampler()` 创建的纹理 | 是，传 texture ID |
| `Smoke` | 引擎 smoke 缓冲 | 否 |

多 pass、纹理 sampler、尺寸模式、颜色模式和自动 `SAMPLER_PARAMS` 见 `references/postprocess-multipass.md`。

## 编译与问题定位

使用：

```powershell
ShaderCompiler.exe -little name source.vs source.ps name.ksh -oglsl
```

`.ksh` 是二进制容器，绝不手改。若本机 `ShaderCompiler.exe` 退出 `0xC0000135`，先报告 Cg/VC90 运行时缺失；不要产出或声称有编译成功的文件。

| 现象 | 先检查 |
| --- | --- |
| 世界实体正常画面未改变 | 是否误把 bloom pass 当成主 pass。 |
| 黑屏 | 顶点布局是否对应目标渲染器；`SAMPLER[0]` 是否已绑定。 |
| 崩溃 | 多余 sampler/uniform 是否没有来源；Mod 路径是否 `resolvefilepath()`。 |
| UI 参数无效 | uniform 名称和 `SetEffectParams*` 通道是否匹配；Params2 是否启用。 |
| 后处理无法启用 | 最终 effect 是否已经排序；是否在正确回调中调用。 |
| 纹理错位 | `AddSampler` 次序是否和 `SAMPLER[n]` 一致。 |
| 模糊方向或半径错误 | `SAMPLER_PARAMS.zw` 是否作为 texel size，且绑定到 sampler effect。 |
| 边缘发黑/发白 | 是否破坏预乘 alpha；降低 alpha 时是否同步降低 RGB。 |

先写 pass-through：UI 用 `texture2D(SAMPLER[0], PS_TEXCOORD) * PS_COLOUR`，后处理用 `texture2D(SAMPLER[0], PS_TEXCOORD0)`。确认该版本正常后才加数学。

## 性能

- UI/VFX 优先保持 1 到 2 次纹理采样。
- 全屏 pass 每帧覆盖所有像素；避免不必要循环、噪声、多纹理和高精度。
- 中间模糊纹理使用 `SamplerSizes.Relative` 降分辨率；内置 bloom 使用 `0.25 x 0.25`。
- 默认使用 `mediump`，仅在实际需要时改用 `highp`。
