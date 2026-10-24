-- 最小普通运行入口。按实际项目加入 PrefabFiles/Assets 和注册文件。
local G = GLOBAL
local enabled = GetModConfigData("enabled")
if enabled == nil then
    enabled = true
end

-- 显式 false 保留；不无条件设置 env 代理或覆盖全局方法。
if not enabled then
    return
end

-- 例如自己的注册文件：modimport("scripts/my_mod/setup.lua")
-- 普通 require 模块返回接口；所需环境 API 通过参数显式传入。
-- 世界生成数据放 modworldgenmain；该入口普通运行也会先加载，地皮登记需防重入。
-- 新内容自行提供真实 Prefab/资源；最小模板不注册不存在的配方、命令或世界组件。
