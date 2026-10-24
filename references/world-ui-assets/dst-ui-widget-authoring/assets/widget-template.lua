local Widget = require("widgets/widget")
local Text = require("widgets/text")

local ModWidget = Class(Widget, function(self)
    Widget._ctor(self, "ModWidget")

    self.label = self:AddChild(Text(BODYTEXTFONT, 24, ""))
    self.label:SetRegionSize(260, 36)
    self.label:SetHAlign(ANCHOR_MIDDLE)
    self.label:SetClickable(false)

    -- Keep the function identity so rebinding can remove the old listener.
    self._onvaluechanged = function()
        self:Refresh()
    end
end)

function ModWidget:SetDataSource(source)
    if self.source == source then
        return
    end

    if self.source ~= nil then
        self.inst:RemoveEventCallback("myvaluedirty", self._onvaluechanged, self.source)
    end

    self.source = source

    if self.source ~= nil then
        -- Replace the event name and value lookup with the replica/local data you own.
        self.inst:ListenForEvent("myvaluedirty", self._onvaluechanged, self.source)
    end

    self:Refresh()
end

function ModWidget:Refresh()
    local value = self.source ~= nil and self.source.value or nil
    self.label:SetString(value ~= nil and tostring(value) or "")
end

function ModWidget:OnControl(control, down)
    if ModWidget._base.OnControl(self, control, down) then
        return true
    end

    return false
end

function ModWidget:Kill()
    -- Remove a replaceable source early; entity removal clears any remaining listeners.
    self:SetDataSource(nil)
    ModWidget._base.Kill(self)
end

return ModWidget