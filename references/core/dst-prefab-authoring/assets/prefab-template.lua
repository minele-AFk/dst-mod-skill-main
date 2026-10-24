local assets =
{
    Asset('ANIM', 'anim/mod_prefab.zip'),
}

local function OnSave(inst, data)
    data.enabled = inst._enabled == true
end

local function OnLoad(inst, data)
    inst._enabled = data ~= nil and data.enabled == true
end

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()

    inst.AnimState:SetBank('mod_prefab')
    inst.AnimState:SetBuild('mod_prefab')
    inst.AnimState:PlayAnimation('idle', true)

    inst:AddTag('mod_prefab')

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst._enabled = true

    inst:AddComponent('inspectable')

    inst.OnSave = OnSave
    inst.OnLoad = OnLoad

    return inst
end

return Prefab('mod_prefab', fn, assets)

