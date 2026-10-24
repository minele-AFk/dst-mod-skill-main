local POSTPROCESS_SHADER = "shaders/my_postprocess.ksh"
-- modmain.lua has a restricted environment. Localize stable globals explicitly,
-- but fetch PostProcessor only after the engine creates it.
local assert = GLOBAL.assert
local tonumber = GLOBAL.tonumber
local PostProcessorEffects = GLOBAL.PostProcessorEffects
local resolvefilepath = GLOBAL.resolvefilepath

local DEFAULT_INTENSITY = 0.5
local MyPostProcess = {}

Assets = Assets or {}
table.insert(Assets, Asset("SHADER", POSTPROCESS_SHADER))

function SetMyPostProcessIntensity(value)
    local PostProcessor = GLOBAL.PostProcessor
    assert(MyPostProcess.intensity ~= nil, "postprocess shader is not initialized")
    value = math.max(0, math.min(1, tonumber(value) or 0))
    PostProcessor:SetUniformVariable(MyPostProcess.intensity, value)
end

AddModShadersInit(function()
    local PostProcessor = GLOBAL.PostProcessor
    MyPostProcess.intensity = PostProcessor:AddUniformVariable("MY_INTENSITY", 1)
    MyPostProcess.effect = PostProcessor:AddPostProcessEffect(
        resolvefilepath(POSTPROCESS_SHADER)
    )

    PostProcessor:SetEffectUniformVariables(
        MyPostProcess.effect,
        MyPostProcess.intensity
    )
    SetMyPostProcessIntensity(DEFAULT_INTENSITY)
end)

AddModShadersSortAndEnable(function()
    local PostProcessor = GLOBAL.PostProcessor
    assert(PostProcessor:SetPostProcessEffectAfter(
        MyPostProcess.effect,
        PostProcessorEffects.ColourCube
    ))
    assert(PostProcessor:EnablePostProcessEffect(MyPostProcess.effect, true))
end)
