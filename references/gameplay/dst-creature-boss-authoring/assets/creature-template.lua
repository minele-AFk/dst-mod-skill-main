-- 仅为 scripts/prefabs/my_mod_creature.lua 的 Prefab 骨架。
-- 项目须提供真实 anim/my_mod_creature.zip、对应 Brain 与 SG。
-- SG 需要与实际动画和攻击/死亡合同匹配；本文件不是三文件拼在一起的成品。
local assets = {
    Asset("ANIM", "anim/my_mod_creature.zip"),
}
local brain = require("brains/my_mod_creaturebrain")

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddSoundEmitter()
    inst.entity:AddDynamicShadow()
    inst.entity:AddNetwork()
    MakeCharacterPhysics(inst, 50, 0.5)
    inst.AnimState:SetBank("my_mod_creature")
    inst.AnimState:SetBuild("my_mod_creature")
    inst.AnimState:PlayAnimation("idle", true)
    inst:AddTag("my_mod_creature")
    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end
    inst:AddComponent("locomotor")
    inst.components.locomotor.walkspeed = 3
    inst.components.locomotor.runspeed = 5
    inst:AddComponent("health")
    inst.components.health:SetMaxHealth(300)
    inst:AddComponent("combat")
    inst.components.combat:SetDefaultDamage(20)
    inst.components.combat:SetAttackPeriod(2)
    inst:AddComponent("inspectable")
    inst:AddComponent("lootdropper")

    -- 数值仅示例，仇恨、掉落、关系与持久状态由项目设计提供。
    inst:SetBrain(brain)
    inst:SetStateGraph("SGmy_mod_creature")
    return inst
end

return Prefab("my_mod_creature", fn, assets)
