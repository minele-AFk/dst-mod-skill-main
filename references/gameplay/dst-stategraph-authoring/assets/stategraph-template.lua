-- Save as scripts/stategraphs/SGmod_entity.lua and load with
-- inst:SetStateGraph('SGmod_entity'). Register the action before this module loads.
assert(ACTIONS.MOD_INTERACT ~= nil, 'Register MOD_INTERACT before loading SGmod_entity')

local actionhandlers =
{
    ActionHandler(ACTIONS.MOD_INTERACT, 'act'),
}

local states =
{
    State
    {
        name = 'idle',
        tags = { 'idle', 'canrotate' },

        onenter = function(inst)
            inst.Physics:Stop()
            inst.AnimState:PlayAnimation('idle', true)
        end,
    },

    State
    {
        name = 'act',
        tags = { 'busy' },

        onenter = function(inst)
            inst.Physics:Stop()
            inst.AnimState:PlayAnimation('act')
        end,

        timeline =
        {
            TimeEvent(6 * FRAMES, function(inst)
                inst:PerformBufferedAction()
            end),
        },

        events =
        {
            EventHandler('animover', function(inst)
                inst.sg:GoToState('idle')
            end),
        },

        onexit = function(inst)
            if inst:GetBufferedAction() ~= nil then
                inst:ClearBufferedAction()
            end
        end,
    },
}

local events = {}

return StateGraph('mod_entity', states, events, 'idle', actionhandlers)
