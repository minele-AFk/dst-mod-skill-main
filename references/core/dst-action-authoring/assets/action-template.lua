-- This is a registration file. Load it from modmain.lua with modimport,
-- because AddAction and AddComponentAction belong to the mod environment.
-- Replace mod_interactable with a server component and client replica supplied by the mod.
local ActionHandler = GLOBAL.ActionHandler

local MOD_INTERACT = AddAction(
    'MOD_INTERACT',
    'Interact',
    function(act)
        local target = act.target
        local doer = act.doer

        if target == nil or not target:IsValid() or doer == nil or not doer:IsValid() then
            return false
        end

        local component = target.components.mod_interactable
        if component == nil or not component:CanInteract(doer) then
            return false
        end

        return component:Interact(doer)
    end
)

AddComponentAction(
    'SCENE',
    'mod_interactable',
    function(inst, doer, actions, right)
        local replica = inst.replica.mod_interactable
        if right and replica ~= nil and replica:CanInteract(doer) then
            table.insert(actions, MOD_INTERACT)
        end
    end
)

AddStategraphActionHandler('wilson', ActionHandler(MOD_INTERACT, 'doshortaction'))
AddStategraphActionHandler('wilson_client', ActionHandler(MOD_INTERACT, 'doshortaction'))
