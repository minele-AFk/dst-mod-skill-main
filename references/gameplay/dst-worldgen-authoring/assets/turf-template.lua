-- 保存为 scripts/my_mod/tile_registration.lua，普通 require 模块返回注册函数。
-- 从模组入口显式传入环境 API 与真实资源定义：
-- require("my_mod/tile_registration")(AddTile, grounddef, minimapdef, turfdef)
-- 这里不附带美术，也不修改默认任务集。
local function RegisterMyModGround(addtile, grounddef, minimapdef, turfdef)
    if WORLD_TILES.MY_MOD_GROUND ~= nil then
        return -- 前端启用/切换存档可能在同进程重入。
    end
    assert(type(addtile) == "function", "missing mod environment AddTile")
    assert(grounddef ~= nil and minimapdef ~= nil, "missing tile definitions")
    addtile("my_mod_ground", "LAND",
        { ground_name = "my_mod_ground" },
        grounddef, minimapdef, turfdef)
end

-- 从 modworldgenmain 调用：当前普通运行时也会先执行此入口。
-- 整个私有 tile 名一起替换为项目命名空间；不要在 modmain 再无条件登记。
-- 注册后使用 WORLD_TILES.MY_MOD_GROUND，不写 GROUND.MY_MOD_GROUND。
-- 房间/任务仅在 modworldgenmain 使用 AddRoom/AddTask 及限定 PreInit。
-- 运行时改地形时显式接收两个坐标：
-- local tx, ty = TheWorld.Map:GetTileCoordsAtPoint(x, 0, z)
-- TheWorld.Map:SetTile(tx, ty, WORLD_TILES.MY_MOD_GROUND)
-- SetTile 不等于 ClearTileUnderneath；完整填海另设计通行、平台、拓扑和保存。
return RegisterMyModGround
