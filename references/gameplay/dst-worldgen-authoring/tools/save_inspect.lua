--[[
Read-only inspector for DST world session saves.

Session saves are plain Lua (`local savedata = {} ... return savedata`) with a
trailing NUL byte, so they can be loaded directly once that is stripped. The
file is loaded into an empty environment and never written.

Usage:
    luajit save_inspect.lua <save file> <command> [args]

Commands:
    summary                 map size, node count, the 25 most common prefabs
    count <p1,p2,...>       instance count per prefab (0 when absent)
    find <lua pattern>      every saved prefab whose name matches, with counts
    pos <prefab>            world x/z of each instance
    data <prefab> [depth]   saved component data of each instance
    nodes [lua pattern]     topology nodes: index, id, tags, tile under the centre
    tile <x> <z>            tile name at a world point
    network                 shard_network / world_network persistdata

Save files live at
    <Klei>/DoNotStarveTogether/<account>/Cluster_<n>/<Master|Caves>/save/session/<id>/<nnnnnnnnnn>
the highest number being the latest.
]]

local path, command = arg[1], arg[2]
if not path or not command then
    io.stderr:write("usage: luajit save_inspect.lua <save file> <command> [args]\n")
    os.exit(2)
end

local function load_save(file)
    local f = assert(io.open(file, "rb"))
    local text = f:read("*a")
    f:close()

    local last
    local from = 1
    while true do
        local s, e = text:find("return savedata", from, true)
        if not s then break end
        last, from = e, e + 1
    end
    assert(last, "not a session save: no 'return savedata'")

    local chunk = assert(loadstring(text:sub(1, last), "@" .. file))
    setfenv(chunk, {})
    return chunk()
end

local save = load_save(path)
local map = save.map or {}

local B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local function base64_decode(s)
    local lookup = {}
    for i = 1, #B64 do lookup[B64:byte(i)] = i - 1 end
    local out, bits, nbits = {}, 0, 0
    for i = 1, #s do
        local v = lookup[s:byte(i)]
        if v then
            bits = bits * 64 + v
            nbits = nbits + 6
            if nbits >= 8 then
                nbits = nbits - 8
                local byte = math.floor(bits / 2 ^ nbits) % 256
                out[#out + 1] = string.char(byte)
                bits = bits % 2 ^ nbits
            end
        end
    end
    return table.concat(out)
end

local tile_names, tile_bytes, tile_header
local function tile_at(x, z)
    if not tile_bytes then
        tile_bytes = base64_decode(map.tiles)
        -- The payload is a small header followed by one little-endian uint16 per tile.
        tile_header = #tile_bytes - 2 * map.width * map.height
        tile_names = {}
        for name, id in pairs(map.world_tile_map or {}) do tile_names[id] = name end
    end
    local tx = math.floor(x / 4 + map.width / 2)
    local tz = math.floor(z / 4 + map.height / 2)
    if tx < 0 or tz < 0 or tx >= map.width or tz >= map.height then
        return "OUT_OF_MAP"
    end
    local i = tile_header + 2 * (tz * map.width + tx) + 1
    local id = tile_bytes:byte(i) + 256 * tile_bytes:byte(i + 1)
    return tile_names[id] or tostring(id)
end

local function dump(v, depth, level)
    level = level or 0
    if type(v) ~= "table" then
        return type(v) == "string" and string.format("%q", v) or tostring(v)
    end
    if level >= depth then return "{...}" end
    local keys = {}
    for k in pairs(v) do keys[#keys + 1] = k end
    table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)
    local parts = {}
    for _, k in ipairs(keys) do
        parts[#parts + 1] = tostring(k) .. "=" .. dump(v[k], depth, level + 1)
    end
    return "{" .. table.concat(parts, ", ") .. "}"
end

local function sorted_prefabs(filter)
    local rows = {}
    for prefab, list in pairs(save.ents or {}) do
        if not filter or prefab:find(filter) then
            rows[#rows + 1] = { prefab = prefab, n = #list }
        end
    end
    return rows
end

local commands = {}

function commands.summary()
    print(string.format("map %dx%d tiles, prefab %s, topology nodes %d",
        map.width or 0, map.height or 0, tostring(map.prefab),
        map.topology and #map.topology.nodes or 0))
    local rows = sorted_prefabs()
    table.sort(rows, function(a, b) return a.n > b.n end)
    print(string.format("%d distinct saved prefabs; most common:", #rows))
    for i = 1, math.min(25, #rows) do
        print(string.format("  %-36s %d", rows[i].prefab, rows[i].n))
    end
end

function commands.count(list)
    assert(list, "count needs a comma-separated prefab list")
    for prefab in list:gmatch("[^,%s]+") do
        local ents = save.ents[prefab]
        print(string.format("  %-36s %d", prefab, ents and #ents or 0))
    end
end

function commands.find(pattern)
    assert(pattern, "find needs a Lua pattern")
    local rows = sorted_prefabs(pattern)
    table.sort(rows, function(a, b) return a.prefab < b.prefab end)
    for _, r in ipairs(rows) do print(string.format("  %-36s %d", r.prefab, r.n)) end
    if #rows == 0 then print("  (none)") end
end

function commands.pos(prefab)
    assert(prefab, "pos needs a prefab")
    for i, e in ipairs(save.ents[prefab] or {}) do
        print(string.format("  %s #%d  x=%.2f z=%.2f  tile=%s", prefab, i, e.x, e.z, tile_at(e.x, e.z)))
    end
end

function commands.data(prefab, depth)
    assert(prefab, "data needs a prefab")
    depth = tonumber(depth) or 4
    for i, e in ipairs(save.ents[prefab] or {}) do
        print(string.format("  %s #%d  x=%.2f z=%.2f  %s", prefab, i, e.x, e.z, dump(e.data, depth)))
    end
end

function commands.nodes(pattern)
    local topo = assert(map.topology, "save has no topology")
    for i, node in ipairs(topo.nodes) do
        local id = topo.ids[i]
        if not pattern or id:find(pattern) then
            print(string.format("  %3d  %-48s tile=%-18s tags=%s", i, id,
                tile_at(node.cent[1], node.cent[2]), table.concat(node.tags or {}, ",")))
        end
    end
end

function commands.tile(x, z)
    x, z = assert(tonumber(x), "tile needs x"), assert(tonumber(z), "tile needs z")
    print(tile_at(x, z))
end

function commands.network()
    print("shard_network: " .. dump(save.shard_network, 6))
    print("world_network: " .. dump(save.world_network, 3))
end

local fn = commands[command]
if not fn then
    io.stderr:write("unknown command: " .. command .. "\n")
    os.exit(2)
end
fn(select(3, ...))
