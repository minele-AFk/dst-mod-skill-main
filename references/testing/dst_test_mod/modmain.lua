--[[
    dst_test_mod - Test script bridge for the DST dedicated server.

    The game does not expose arbitrary filesystem reads/writes to Lua at
    runtime, so the bridge uses the only two file channels that are allowed:

      * reading  -> kleiloadlua / TheSim:GetFileModificationTime on files
                    inside the mod's own directory (MODROOT)
      * writing  -> io.open("unsafedata/...", "w"), the only runtime file
                    write the game allows (data/unsafedata/, flat, .txt ok)

    Every sim tick (POLL_PERIOD = 1/30 s) the mod checks the modification
    time of MODROOT/scripts/test_request.lua.  When it changes, the file is
    loaded with kleiloadlua and executed through xpcall in a sandboxed
    environment.  The return value(s) and anything the script prints are
    written back to data/unsafedata/dst_test_response_<mtime>.txt.
    The game has no file-deletion API, so the external tool
    (tools/testing/run_script.py) is responsible for removing old response files.

    Response file format (plain text):
        --dst-test-response--
        status:ok|error
        mtime:<mtime of the request that produced this response>
        values:
          <serialized value>
          ...
        prints:
          <line emitted by the script's print()>
          ...
        --dst-test-response-end--

    Serialized values:
        nil
        true | false
        number:<number>
        string:"<json escaped text>"
        table:<DataDumper output with newlines flattened>
        <type>:<tostring fallback>
]]

local GLOBAL = GLOBAL

local REQUEST_RELATIVE_PATH = "scripts/test_request.lua"
local RESPONSE_REL_DIR = "unsafedata/"
local RESPONSE_PREFIX = "dst_test_response_"
local POLL_PERIOD = 1 / 30

local request_path = MODROOT .. REQUEST_RELATIVE_PATH
local last_seen_mtime = nil
local last_run_mtime = nil
local bridge_task = nil

-- Best-effort stack walk for error reports.  NOTE: never use
-- debug.traceback on this dedicated-server build: passing it as an xpcall
-- handler (or calling it with an error value) poisons the Lua state and
-- crashes the process with "LuaError but no error string".
local function safe_traceback(start_level)
    local parts = {}
    local i = start_level or 2
    while i < 40 do
        local info = GLOBAL.debug.getinfo(i, "Sl")
        if info == nil then
            break
        end
        parts[#parts + 1] = string.format(
            "%s:%d in %s",
            tostring(info.source),
            info.currentline or 0,
            tostring(info.name or "?")
        )
        i = i + 1
    end
    return table.concat(parts, "\n")
end

local function escape_json_string(s)
    s = s:gsub("\\", "\\\\")
    s = s:gsub('"', '\\"')
    s = s:gsub("\n", "\\n")
    s = s:gsub("\r", "\\r")
    s = s:gsub("\t", "\\t")
    s = s:gsub("[%c]", function(c)
        return string.format("\\u%04X", c:byte())
    end)
    return s
end

local function serialize_value(v)
    local tv = type(v)
    if v == nil then
        return "nil"
    elseif tv == "boolean" then
        return tostring(v)
    elseif tv == "number" then
        if v ~= v then return "number:nan" end
        if v == math.huge then return "number:inf" end
        if v == -math.huge then return "number:-inf" end
        return "number:" .. tostring(v)
    elseif tv == "string" then
        return "string:\"" .. escape_json_string(v) .. "\""
    elseif tv == "table" then
        local ok, dumped = GLOBAL.pcall(GLOBAL.DataDumper, v, nil, false)
        if ok and type(dumped) == "string" then
            dumped = dumped:gsub("\r\n", "\n"):gsub("\n", "\\n")
            return "table:" .. dumped
        end
        return "table:<" .. tostring(v) .. ">"
    end
    return tv .. ":" .. tostring(v)
end

local function write_response(status, values, print_lines, mtime)
    local parts = {}
    parts[#parts + 1] = "--dst-test-response--"
    parts[#parts + 1] = "status:" .. tostring(status)
    parts[#parts + 1] = "mtime:" .. tostring(mtime)
    parts[#parts + 1] = "values:"
    for i, v in ipairs(values) do
        parts[#parts + 1] = "  " .. serialize_value(v)
    end
    parts[#parts + 1] = "prints:"
    for i, line in ipairs(print_lines) do
        parts[#parts + 1] = line
    end
    parts[#parts + 1] = "--dst-test-response-end--"
    local text = table.concat(parts, "\n") .. "\n"
    -- A unique filename per run so stale responses stay unambiguous.
    local response_rel = RESPONSE_REL_DIR .. RESPONSE_PREFIX .. tostring(mtime) .. ".txt"
    local ok, err = GLOBAL.pcall(function()
        local f, ferr = GLOBAL.io.open(response_rel, "w")
        if f == nil then
            error(tostring(ferr))
        end
        f:write(text)
        f:close()
    end)
    if not ok then
        -- Last resort: keep the message in the game log so it is not lost.
        print("[dst_test_mod] failed to write " .. response_rel .. ": " .. tostring(err))
    end
end

local function run_request(mtime)
    local print_lines = {}

    local fn = GLOBAL.kleiloadlua(request_path)
    if type(fn) == "string" then
        write_response("error", { "failed to load request: " .. fn }, print_lines, mtime)
        return
    elseif type(fn) ~= "function" then
        write_response("error", { "request file not found: " .. request_path }, print_lines, mtime)
        return
    end

    -- Sandboxed environment for the injected script.  GLOBAL is not a real
    -- global in the game's _G, so it is provided explicitly; the __index
    -- fallback inherits everything else (including the game's strict mode,
    -- which turns typos into proper errors).
    local script_env = GLOBAL.setmetatable({}, { __index = GLOBAL })
    script_env.GLOBAL = GLOBAL
    script_env.print = function(...)
        local n = GLOBAL.select("#", ...)
        local parts = {}
        for i = 1, n do
            parts[i] = tostring(GLOBAL.select(i, ...))
        end
        table.insert(print_lines, table.concat(parts, "\t"))
    end
    -- Escape hatch: the original game print (goes to the server log).
    script_env.gameprint = GLOBAL.print
    script_env.TheWorld = GLOBAL.TheWorld
    script_env.ThePlayer = GLOBAL.ThePlayer
    script_env.TheSim = GLOBAL.TheSim
    GLOBAL.setfenv(fn, script_env)

    local ok, results_or_err = GLOBAL.xpcall(
        function()
            return { fn() }
        end,
        function(e)
            local msg = "error: " .. tostring(e)
            local frames = safe_traceback(3)
            if frames ~= "" then
                msg = msg .. "\nstack traceback:\n" .. frames
            end
            return msg
        end
    )

    if ok then
        write_response("ok", results_or_err, print_lines, mtime)
    else
        table.insert(print_lines, tostring(results_or_err))
        write_response("error", {}, print_lines, mtime)
    end
end

local function poll()
    if GLOBAL.TheWorld == nil or GLOBAL.TheWorld.ismastersim ~= true then
        return
    end

    local ok, mtime = GLOBAL.pcall(
        GLOBAL.TheSim.GetFileModificationTime,
        GLOBAL.TheSim,
        request_path
    )
    if not ok or mtime == nil or mtime == 0 then
        -- File does not exist (yet); wait for it to appear.
        last_seen_mtime = nil
        return
    end

    if last_seen_mtime ~= nil and mtime ~= last_seen_mtime then
        -- Ignore a transient nil-lookup glitch: only run once per unique
        -- modification time, never re-run the same mtime.
        if last_run_mtime == nil or mtime ~= last_run_mtime then
            print("[dst_test_mod] mtime change " .. tostring(last_seen_mtime) .. " -> " .. tostring(mtime))
            run_request(mtime)
            last_run_mtime = mtime
        end
    end
    last_seen_mtime = mtime
end

local function poll_safe()
    local ok, err = GLOBAL.pcall(poll)
    if not ok then
        print("[dst_test_mod] poll error: " .. tostring(err))
    end
end

AddSimPostInit(function()
    if bridge_task == nil and GLOBAL.TheWorld ~= nil then
        bridge_task = GLOBAL.TheWorld:DoPeriodicTask(POLL_PERIOD, poll_safe)
        print("[dst_test_mod] bridge started, watching " .. request_path)
    end
end)
