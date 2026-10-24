local BLUR_H_SHADER = "shaders/my_blur_h.ksh"
local BLUR_V_SHADER = "shaders/my_blur_v.ksh"
local COMPOSITE_SHADER = "shaders/my_blur_composite.ksh"
-- modmain.lua has a restricted environment. Localize stable globals explicitly,
-- but fetch PostProcessor only after the engine creates it.
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

local DEFAULT_BLUR_STRENGTH = 0.5
local MultiPass = {}

Assets = Assets or {}
table.insert(Assets, Asset("SHADER", BLUR_H_SHADER))
table.insert(Assets, Asset("SHADER", BLUR_V_SHADER))
table.insert(Assets, Asset("SHADER", COMPOSITE_SHADER))

function SetMyPostProcessBlurStrength(value)
    local PostProcessor = GLOBAL.PostProcessor
    assert(MultiPass.strength ~= nil, "multipass shader is not initialized")
    value = math.max(0, math.min(1, tonumber(value) or 0))
    PostProcessor:SetUniformVariable(MultiPass.strength, value)
end

local function ConfigureSamplerEffect(effect)
    local PostProcessor = GLOBAL.PostProcessor
    PostProcessor:SetSamplerEffectState(effect, WRAP_MODE.CLAMP_TO_EDGE)
    PostProcessor:SetSamplerEffectFilter(
        effect,
        FILTER_MODE.LINEAR,
        FILTER_MODE.LINEAR,
        MIP_FILTER_MODE.NONE
    )
end

AddModShadersInit(function()
    local PostProcessor = GLOBAL.PostProcessor
    local sampler_params = hash("SAMPLER_PARAMS")

    MultiPass.strength = PostProcessor:AddUniformVariable("MY_BLUR_STRENGTH", 1)

    MultiPass.blur_h = PostProcessor:AddSamplerEffect(
        resolvefilepath(BLUR_H_SHADER),
        SamplerSizes.Relative,
        0.5,
        0.5,
        SamplerColourMode.RGBA,
        SamplerEffectBase.PostProcessSampler
    )
    PostProcessor:SetEffectUniformVariables(MultiPass.blur_h, sampler_params)
    ConfigureSamplerEffect(MultiPass.blur_h)

    MultiPass.blur_v = PostProcessor:AddSamplerEffect(
        resolvefilepath(BLUR_V_SHADER),
        SamplerSizes.Relative,
        0.5,
        0.5,
        SamplerColourMode.RGBA,
        SamplerEffectBase.Shader,
        MultiPass.blur_h
    )
    PostProcessor:SetEffectUniformVariables(MultiPass.blur_v, sampler_params)
    ConfigureSamplerEffect(MultiPass.blur_v)

    MultiPass.composite = PostProcessor:AddPostProcessEffect(
        resolvefilepath(COMPOSITE_SHADER)
    )
    PostProcessor:AddSampler(
        MultiPass.composite,
        SamplerEffectBase.Shader,
        MultiPass.blur_v
    )
    PostProcessor:SetEffectUniformVariables(MultiPass.composite, MultiPass.strength)
    SetMyPostProcessBlurStrength(DEFAULT_BLUR_STRENGTH)
end)

AddModShadersSortAndEnable(function()
    local PostProcessor = GLOBAL.PostProcessor
    assert(PostProcessor:SetPostProcessEffectAfter(
        MultiPass.composite,
        PostProcessorEffects.ColourCube
    ))
    assert(PostProcessor:EnablePostProcessEffect(MultiPass.composite, true))
end)
