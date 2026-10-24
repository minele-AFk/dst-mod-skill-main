# DST PostProcessor Multipass

## 目录

- [API 形状](#api-形状)
- [尺寸与颜色](#尺寸与颜色)
- [自动 SAMPLER_PARAMS](#自动-sampler_params)
- [采样状态与过滤](#采样状态与过滤)
- [构建 pass 链](#构建-pass-链)
- [编译模板](#编译模板)
- [调试顺序](#调试顺序)

## API 形状

以下代码运行在 `modmain.lua` 时，先从 `GLOBAL` 局部化入口阶段已经存在的未注入对象；完整模板已经包含这些声明：

```lua
local assert = GLOBAL.assert
local tonumber = GLOBAL.tonumber
local hash = GLOBAL.hash
local PostProcessorEffects = GLOBAL.PostProcessorEffects
local resolvefilepath = GLOBAL.resolvefilepath
local WRAP_MODE = GLOBAL.WRAP_MODE
local FILTER_MODE = GLOBAL.FILTER_MODE
local MIP_FILTER_MODE = GLOBAL.MIP_FILTER_MODE
local SamplerSizes = GLOBAL.SamplerSizes
local SamplerColourMode = GLOBAL.SamplerColourMode
local SamplerEffectBase = GLOBAL.SamplerEffectBase
```

`PostProcessor` 本身晚于 `modmain.lua` 创建，不能在文件加载时缓存。应在 `AddModShadersInit`、`AddModShadersSortAndEnable` 回调及它们调用的辅助函数内使用 `local PostProcessor = GLOBAL.PostProcessor`。

本地 `scripts/postprocesseffects.lua` 展示了三类对象：

```lua
local texture_id = PostProcessor:AddTextureSampler(resolvefilepath("images/noise.tex"))

local sampler_effect_id = PostProcessor:AddSamplerEffect(
    resolvefilepath("shaders/blur_h.ksh"),
    SamplerSizes.Relative,
    0.5,
    0.5,
    SamplerColourMode.RGBA,
    SamplerEffectBase.PostProcessSampler
)

local final_effect_id = PostProcessor:AddPostProcessEffect(
    resolvefilepath("shaders/composite.ksh")
)
```

`AddTextureSampler()` 返回静态纹理 ID。为 Mod 自己的纹理先注册 `Asset("IMAGE", path)`，运行时参数使用 `resolvefilepath(path)`。

`AddSamplerEffect()` 创建离屏 pass。参数依次为 shader、尺寸模式、宽度或宽度比例、高度或高度比例、颜色模式、基础输入类型，以及基础类型需要时的 ID。

`AddPostProcessEffect()` 创建进入全局后处理排序链的最终 pass。只有最终 effect 需要用 `SetPostProcessEffectBefore/After()` 排序并启用；可达的 sampler-effect 依赖会作为输入执行。

## 尺寸与颜色

| 枚举 | 含义 |
| --- | --- |
| `SamplerSizes.Relative` | 后两个尺寸参数是相对当前缓冲区的比例，例如 `0.5, 0.5`。 |
| `SamplerSizes.Static` | 后两个尺寸参数是固定像素尺寸，例如 `1024, 32`。 |
| `SamplerColourMode.RGB` | 中间目标只需要 RGB。 |
| `SamplerColourMode.RGBA` | 中间目标还要保留 alpha。 |

模糊等高成本 pass 优先用 `Relative` 降采样。若后续计算依赖透明度则使用 `RGBA`；纯 bloom 色彩链通常可用 `RGB`。

## 自动 SAMPLER_PARAMS

sampler effect 可以绑定引擎自动填充的：

```glsl
uniform vec4 SAMPLER_PARAMS;
// xy = buffer width, height
// zw = 1 / width, 1 / height
```

Lua 中使用名字的 hash 绑定它：

```lua
local sampler_params = hash("SAMPLER_PARAMS")
PostProcessor:SetEffectUniformVariables(sampler_effect_id, sampler_params)
```

不要对它调用 `AddUniformVariable()`，也不要调用 `SetUniformVariable()`。它只在 sampler effect 上由引擎按目标尺寸更新。水平 texel offset 使用 `vec2(SAMPLER_PARAMS.z, 0.0)`，垂直 offset 使用 `vec2(0.0, SAMPLER_PARAMS.w)`。

## 采样状态与过滤

静态纹理使用 texture-sampler API：

```lua
PostProcessor:SetTextureSamplerState(texture_id, WRAP_MODE.CLAMP_TO_EDGE)
PostProcessor:SetTextureSamplerFilter(
    texture_id,
    FILTER_MODE.LINEAR,
    FILTER_MODE.LINEAR,
    MIP_FILTER_MODE.NONE
)
```

离屏 sampler effect 使用对应 API：

```lua
PostProcessor:SetSamplerEffectState(sampler_effect_id, WRAP_MODE.CLAMP_TO_EDGE)
PostProcessor:SetSamplerEffectFilter(
    sampler_effect_id,
    FILTER_MODE.LINEAR,
    FILTER_MODE.LINEAR,
    MIP_FILTER_MODE.NONE
)
```

模糊目标通常使用 `CLAMP_TO_EDGE`，避免屏幕边缘绕回另一侧；线性过滤适合降采样和模糊，像素化效果改用 `POINT`。

## 构建 pass 链

以下依赖关系对应 `assets/templates/postprocess_multipass_modmain.lua`：

```text
current screen
    -> blur_h sampler effect (SAMPLER[0])
    -> blur_v sampler effect (SAMPLER[0] = blur_h output)
    -> composite postprocess
         SAMPLER[0] = current screen
         SAMPLER[1] = blur_v output
```

关键调用顺序：

1. 创建普通强度 uniform。
2. 以 `SamplerEffectBase.PostProcessSampler` 创建水平 pass。
3. 以 `SamplerEffectBase.Shader, blur_h_id` 创建垂直 pass。
4. 创建最终 composite postprocess，并用 `AddSampler(composite_id, SamplerEffectBase.Shader, blur_v_id)` 把模糊结果追加为 `SAMPLER[1]`。
5. 给两个 sampler effect 绑定 `hash("SAMPLER_PARAMS")`，给 composite 绑定普通强度 uniform。
6. 在 `AddModShadersSortAndEnable` 中只排序并启用 composite。

## 编译模板

在 Mod 的 shader 源码目录中分别编译三个 `.ksh`：

```powershell
ShaderCompiler.exe -little my_blur_h postprocess_blur.vs postprocess_blur_h.ps my_blur_h.ksh -oglsl
ShaderCompiler.exe -little my_blur_v postprocess_blur.vs postprocess_blur_v.ps my_blur_v.ksh -oglsl
ShaderCompiler.exe -little my_blur_composite postprocess_blur_composite.vs postprocess_blur_composite.ps my_blur_composite.ksh -oglsl
```

把结果放进 Mod 的 `shaders/`，并保持 Lua 模板中的三个路径完全一致。

## 调试顺序

1. 先让 composite 直接输出 `SAMPLER[0]`，确认最终 effect 的排序和启用。
2. 再输出 `texture2D(SAMPLER[1], PS_TEXCOORD0)`，确认依赖链和 `AddSampler()`。
3. 让水平、垂直 pass 分别只采样中心点，确认 `SAMPLER_PARAMS` 绑定。
4. 最后恢复多 tap 权重，并用非零默认强度验证效果可见。

若 `SAMPLER[1]` 为空，先检查 `SamplerEffectBase.Shader` 的 ID 链；若模糊半径随分辨率变化，先检查是否把 `SAMPLER_PARAMS.zw` 误当成尺寸而不是尺寸倒数。
