local function GetUpValueImpl(fn, upvalueName, level)
    level = level or 5
    local i = 1
    local fns = {}

    while true do
        local name, value = debug.getupvalue(fn, i)
        if not name then break end
        if name == upvalueName then
            return value, i
        end
        if level > 0 and type(value) == "function" then
            table.insert(fns, value)
        end
        i = i + 1
    end

    for _, f in ipairs(fns) do
        local value, index = GetUpValueImpl(f, upvalueName, level - 1)
        if value then
            return value, index
        end
    end

    return nil, nil
end

function GetUpValue(fn, ...)
    if type(fn) ~= "function" then
        return nil, nil, nil
    end

    local val, i, current_fn
    val = fn
    for _, name in ipairs({ ... }) do
        current_fn = val
        val, i = GetUpValueImpl(current_fn, name)
        if i == nil then
            return nil, nil, nil
        end
    end
    return val, current_fn, i
end

local Links = {}
local function _GetEntity(anim)
    return anim ~= nil and Links[anim]
end

local function _NewLink(anim, inst)
    if inst:IsValid() then
        Links[anim] = inst
        inst:ListenForEvent("onremove", function() Links[anim] = nil end)
    end
end

local old_add = Entity.AddAnimState
Entity.AddAnimState = function(ent, ...)
    local inst = Ents[ent:GetGUID()]
    if _GetEntity(inst and inst.AnimState) then
        Links[inst.AnimState] = nil
    end
    local anim = old_add(ent, ...)
    _NewLink(anim, inst)
    return anim
end

TUNING.TEST_CHECK_ANIM_HAS_BUILD = true
local memoizedFilePaths = Hooks.GetUpValue(resolvefilepath, "memoizedFilePaths")
local OldSetBuild = AnimState.SetBuild
function AnimState:SetBuild(build, ...)
    local inst = _GetEntity(self)
    if inst and
        not memoizedFilePaths["anim/" .. build .. ".zip"]
        and TUNING.TEST_CHECK_ANIM_HAS_BUILD
    then
        print(tostring(inst) .. " 调用了SetBuild但是没有 " .. tostring(build) .. ".zip 动画文件，注意检查动画是否正常显示")
    end
    return OldSetBuild(self, build, ...)
end