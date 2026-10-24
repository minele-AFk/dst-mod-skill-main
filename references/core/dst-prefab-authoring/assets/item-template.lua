-- scripts/prefabs/my_mod_item.lua
-- 骨架依赖真实动画/图集；不是附带资源的完整物品。
local assets = {
    Asset("ANIM", "anim/my_mod_item.zip"),
    Asset("ATLAS", "images/inventoryimages/my_mod_item.xml"),
    Asset("IMAGE", "images/inventoryimages/my_mod_item.tex"),
}

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank("my_mod_item")
    inst.AnimState:SetBuild("my_mod_item")
    inst.AnimState:PlayAnimation("idle")
    inst:AddTag("my_mod_item")
    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.atlasname = "images/inventoryimages/my_mod_item.xml"
    inst.components.inventoryitem.imagename = "my_mod_item"
    inst:AddComponent("stackable")
    inst.components.stackable.maxsize = TUNING.STACK_SIZE_SMALLITEM

    -- 装备/武器/工具/腐烂/耐久按实际设计添加，不默认同时启用。
    -- 自定义库存图若还用于静态菜单/图鉴，在入口注册对应 Atlas 查询键。
    return inst
end

return Prefab("my_mod_item", fn, assets)
