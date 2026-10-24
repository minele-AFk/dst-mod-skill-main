local ModState = Class(function(self, inst)
    self.inst = inst
    self._enabled = net_bool(inst.GUID, 'mod_state.enabled', 'mod_state_dirty')
end)

function ModState:SetEnabled(enabled)
    if TheWorld.ismastersim then
        self._enabled:set(enabled == true)
    end
end

function ModState:IsEnabled()
    return self._enabled:value()
end

return ModState
