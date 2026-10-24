--[[
Dumps every DST worldgen / worldsettings override option, with its legal values,
straight out of the game's own map/customize.lua.

This is the source of truth for references/worldgen-overrides.md and
references/worldsettings-overrides.md. Re-run it after a game patch.

Usage:
    cd <path to DST data/scripts>
    luajit /path/to/dump_options.lua [--format=md|tsv]

It stubs out the parts of the game customize.lua touches (STRINGS, TUNING,
platform checks, worldsettings_overrides) so the file can be loaded outside
the game. The option tables themselves are the real ones.
]]

local FORMAT = "md"
for _, a in ipairs({...}) do
    local f = a:match("^%-%-format=(%w+)$")
    if f then FORMAT = f end
end

local SCRIPTS = os.getenv("DST_SCRIPTS") or "."
package.path = SCRIPTS .. "/?.lua;" .. package.path

------------------------------------------------------------------
-- stub environment
------------------------------------------------------------------

-- Any nested access returns a stringable placeholder; customize.lua only ever
-- uses STRINGS for display text, which we discard.
local function magic(name)
    return setmetatable({}, {
        __index = function(t, k) local v = magic(name .. "." .. tostring(k)); t[k] = v; return v end,
        __tostring = function() return name end,
        __concat = function(a, b) return tostring(a) .. tostring(b) end,
    })
end

STRINGS = magic("S")
TUNING  = magic("TUNING")

function IsNotConsole() return true end   -- console trims the value lists; PC is the superset
function IsPS4() return false end
function IsConsole() return false end
function IsXB1() return false end
function IsRail() return false end
function IsSteam() return true end
function IsWin32() return false end

LEVELCATEGORY = { SETTINGS = "settings", WORLDGEN = "worldgen", COMBINED = "combined" }
LEVELTYPE = { SURVIVAL = "survival", CAVE = "cave", ADVENTURE = "adventure", CUSTOM = "custom" }

SPECIAL_EVENTS = {
    NONE = "none", HALLOWED_NIGHTS = "hallowed_nights", WINTERS_FEAST = "winters_feast",
    CARNIVAL = "crow_carnival", YOTG = "year_of_the_gobbler", YOTV = "year_of_the_varg",
    YOTP = "year_of_the_pig", YOTC = "year_of_the_carrat", YOTB = "year_of_the_beefalo",
    YOT_CATCOON = "year_of_the_catcoon", YOTR = "year_of_the_bunnyman",
    YOTD = "year_of_the_dragonfly", YOTS = "year_of_the_snake",
}

function table.contains(t, v)
    if type(t) ~= "table" then return false end
    for _, x in pairs(t) do if x == v then return true end end
    return false
end
function FunctionOrValue(v, ...) if type(v) == "function" then return v(...) end return v end
function deepcopy(o) if type(o) ~= "table" then return o end local r = {} for k, v in pairs(o) do r[k] = deepcopy(v) end return r end
function shallowcopy(o) if type(o) ~= "table" then return o end local r = {} for k, v in pairs(o) do r[k] = v end return r end
function GetTableSize(t) local n = 0 for _ in pairs(t or {}) do n = n + 1 end return n end
function IsTableEmpty(t) return next(t or {}) == nil end
function stringidsorter(a, b) return tostring(a) < tostring(b) end

-- map/tasksets and map/startlocations are loaded for real: task_set and
-- start_location are the only two options whose vocabulary is not a static
-- list in customize.lua, and both modules already filter per location (a
-- forest world only offers forest task sets). They pull in nothing heavier
-- than STRINGS, so they load fine outside the game.
ModManager = { currentlyloadingmod = nil, GetPostInitFns = function() return {} end }
function moderror(msg) error(msg, 0) end

local stubs = {
    ["map/tasks"]  = {},
    ["map/levels"] = { GetDataForLocation = function() return nil end },
    -- customize.lua only asserts that a Pre or Post handler exists per option.
    ["worldsettings_overrides"] = {
        Pre  = setmetatable({}, { __index = function() return function() end end }),
        Post = setmetatable({}, { __index = function() return function() end end }),
    },
}

local real_require = require
require = function(m) return stubs[m] or real_require(m) end

local customize = require("map/customize")

-- map/locations.lua holds the per-world override defaults (task_set,
-- start_location, world_size, roads, layout_mode, ...). These WIN over an
-- item's own `value`, so they are the real default a mod inherits. AddLocation
-- normally lives in map/levels.lua; defining it here lets us load the data
-- file on its own.
local LOCATION_DEFAULTS = {}
function AddLocation(data)
    LOCATION_DEFAULTS[data.location] = data.overrides or {}
end
real_require("map/locations")

------------------------------------------------------------------
-- collect
------------------------------------------------------------------

-- task_set and start_location build their lists by iterating a hash table with
-- pairs(), so their order varies run to run. Sort just those two; every other
-- vocabulary is an ordered list (never -> insane) whose order is meaningful.
local UNORDERED = { task_set = true, start_location = true }

local function values_of(opt)
    local out = {}
    if type(opt.options) == "table" then
        for _, o in ipairs(opt.options) do out[#out + 1] = tostring(o.data) end
    end
    if UNORDERED[opt.name] then table.sort(out) end
    return out
end

--- Markdown table cells cannot contain a raw pipe; season_start values do
--- (e.g. "autumn|spring").
local function md_cell(v) return (v:gsub("|", "\\|")) end

--- @return table  rows sorted by group then name
local function collect(getopts, location)
    local rows = {}
    for _, o in ipairs(getopts(location, true)) do
        local locdefault = (LOCATION_DEFAULTS[location] or {})[o.name]
        rows[#rows + 1] = {
            name    = o.name,
            group   = o.group,
            -- the location default, where there is one, is what a level
            -- actually starts from; fall back to the item's own value
            default = tostring(locdefault ~= nil and locdefault or o.default),
            values  = values_of(o),
        }
    end
    table.sort(rows, function(a, b)
        if a.group ~= b.group then return a.group < b.group end
        return a.name < b.name
    end)
    return rows
end

local CATEGORIES = {
    { key = "WORLDGEN",      get = customize.GetWorldGenOptions },
    { key = "WORLDSETTINGS", get = customize.GetWorldSettingsOptions },
}

------------------------------------------------------------------
-- emit
------------------------------------------------------------------

local out = {}
local function emit(s) out[#out + 1] = s end

if FORMAT == "tsv" then
    emit("location\tcategory\tgroup\toption\tdefault\tvalues")
    for _, loc in ipairs({ "forest", "cave" }) do
        for _, cat in ipairs(CATEGORIES) do
            for _, r in ipairs(collect(cat.get, loc)) do
                emit(table.concat({ loc, cat.key, r.group, r.name, r.default,
                                    table.concat(r.values, ",") }, "\t"))
            end
        end
    end
else
    -- Merge forest+cave so each option appears once, tagged with the worlds it
    -- applies to. An option's value list can differ per world, so key on both.
    for _, cat in ipairs(CATEGORIES) do
        emit("# " .. cat.key)
        local seen, order = {}, {}
        for _, loc in ipairs({ "forest", "cave" }) do
            for _, r in ipairs(collect(cat.get, loc)) do
                local k = r.group .. "\0" .. r.name .. "\0" .. table.concat(r.values, ",")
                if not seen[k] then
                    seen[k] = { group = r.group, name = r.name, default = r.default,
                                values = r.values, worlds = {} }
                    order[#order + 1] = k
                end
                table.insert(seen[k].worlds, loc)
            end
        end
        table.sort(order, function(a, b)
            local x, y = seen[a], seen[b]
            if x.group ~= y.group then return x.group < y.group end
            return x.name < y.name
        end)

        local group = nil
        for _, k in ipairs(order) do
            local r = seen[k]
            if r.group ~= group then
                group = r.group
                emit("")
                emit("## " .. group)
                emit("")
                emit("| option | worlds | default | values |")
                emit("|---|---|---|---|")
            end
            emit(string.format("| `%s` | %s | `%s` | %s |",
                r.name,
                table.concat(r.worlds, " + "),
                r.default,
                table.concat((function()
                    local t = {}
                    for _, v in ipairs(r.values) do t[#t + 1] = "`" .. md_cell(v) .. "`" end
                    return t
                end)(), " ")))
        end
        emit("")
    end
end

print(table.concat(out, "\n"))
