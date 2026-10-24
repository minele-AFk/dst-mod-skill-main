-- modworldgenmain.lua 或由它 modimport 的注册文件。
-- 函数需要已确认的 roomname/prefabname/count；
-- 给现有房间补计数，不覆盖默认任务集或擅自指定新世界。
local function AddMyModRoomContent(roomname, prefabname, count)
    AddRoomPreInit(roomname, function(room)
        room.contents = room.contents or {}
        room.contents.countprefabs = room.contents.countprefabs or {}
        room.contents.countprefabs[prefabname] = count
    end)
end

-- 调用示意（参数由项目配置和设计提供）：
-- AddMyModRoomContent(roomname, prefabname, count)
-- count 按每个生成节点生效，不保证全世界恰好该数量。
--
-- 要新增 Room/Task：用环境 AddRoom/AddTask 注册独立名字；
-- keys_given 不写成 keys，room_choices 表示数量/函数，不是一般权重。
-- 向已有 TaskSet 加任务：核对 taskset ID 后用 AddTaskSetPreInit，
-- 在其 tasks 表追加已注册任务，保留无关字段与重复登记防护。
-- AddTaskSet 注册新对象，不是自动合并/追加 API。
--
-- 静态布局使用 scripts/map/static_layouts 下可 require 的 Tiled Lua 表，
-- StaticLayout.Get -> 唯一 Layouts 项 -> room/taskset 实际放置入口。
-- JSON 先转换。Scenario 持久化见本专题 references/worldgen-scenarios-hooks.md。
-- worldgen 无运行中 TheWorld，不通过 TheWorld.overrides 配置新图。
