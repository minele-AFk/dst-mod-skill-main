-- scripts/prefabs/my_mod_building.lua
-- 项目须提供真实 bank/build/动画；本骨架不附图标、容器或燃烧政策。
local assets = {
    Asset("ANIM", "anim/my_mod_building.zip"),
}

local function OnHammered(inst, worker)
    if inst.components.lootdropper ~= nil then
        inst.components.lootdropper:DropLoot()
    end
    inst:Remove()
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddSoundEmitter()
    inst.entity:AddNetwork()
    MakeObstaclePhysics(inst, 0.5)
    inst.AnimState:SetBank("my_mod_building")
    inst.AnimState:SetBuild("my_mod_building")
    inst.AnimState:PlayAnimation("idle", true)
    inst:AddTag("structure")
    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end
    inst:AddComponent("inspectable")
    inst:AddComponent("lootdropper")
    -- 按设计在此设置真实掉落；不在 onwork 和 onfinish 各掉一次。
    inst:AddComponent("workable")
    inst.components.workable:SetWorkAction(ACTIONS.HAMMER)
    inst.components.workable:SetWorkLeft(5)
    inst.components.workable:SetOnFinishCallback(OnHammered)

    -- 如需燃烧，选择当前标准 helper；不先重复添加 helper 自己会创建的组件。
    -- 容器的 params、Replica 与实际资源在项目内另行完整接入。
    return inst
end

return Prefab("my_mod_building", fn, assets),
    MakePlacer("my_mod_building_placer", "my_mod_building", "my_mod_building", "idle")
