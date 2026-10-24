-- scripts/widgets/my_mod_value.lua
-- UI 模板：读取函数与 eventname 必须连接到项目真实的客户端复制数据。
local Widget = require("widgets/widget")
local Text = require("widgets/text")

local MyModValue = Class(Widget, function(self, owner, readvalue, eventname)
    Widget._ctor(self, "MyModValue")
    self.owner = owner
    self.readvalue = readvalue
    self.label = self:AddChild(Text(BODYTEXTFONT, 22, "--"))

    self.Refresh = function(widget)
        local value = widget.readvalue(widget.owner)
        widget.label:SetString(value ~= nil and tostring(value) or "--")
    end
    if eventname ~= nil then
        self.inst:ListenForEvent(eventname, function()
            self:Refresh()
        end, owner)
    end
    self:Refresh()
end)

-- 挂载示例见 ../references/hud-customization.md：
-- 在 widgets/controls PostConstruct 中使用 self.owner，
-- self.topleft_root:AddChild(MyModValue(owner, readvalue, eventname))。
-- 不用 not ismastersim 排除房主，不直接读取仅服务器存在的状态。
-- Widget:Kill 移除自己的 inst 和监听；提前停用需另撤销自己的外部资源。
return MyModValue
