require('behaviours/wander')

local ModBrain = Class(Brain, function(self, inst)
    Brain._ctor(self, inst)
end)

function ModBrain:OnStart()
    local root = PriorityNode(
    {
        Wander(self.inst, nil, 8),
    }, 0.5)

    self.bt = BT(self.inst, root)
end

return ModBrain
