local ModState = Class(function(self, inst)
    self.inst = inst
    self.enabled = false
end)

function ModState:SetEnabled(enabled)
    enabled = enabled == true
    if self.enabled == enabled then
        return
    end

    self.enabled = enabled

    if self.inst.replica ~= nil and self.inst.replica.mod_state ~= nil then
        self.inst.replica.mod_state:SetEnabled(enabled)
    end

    -- Keep server domain events distinct from replica netvar dirty events.
    self.inst:PushEvent('mod_state_changed', { enabled = enabled })
end

function ModState:IsEnabled()
    return self.enabled
end

function ModState:OnSave()
    return self.enabled and { enabled = true } or nil
end

function ModState:OnLoad(data)
    self:SetEnabled(data ~= nil and data.enabled == true)
end

function ModState:OnRemoveFromEntity()
    -- Cancel tasks and remove cross-entity listeners here.
end

function ModState:GetDebugString()
    return self.enabled and 'enabled' or 'disabled'
end

return ModState
