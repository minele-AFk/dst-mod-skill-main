# 逆向/混淆破解工具（道诡异仙 DaxSg 三层加密专用）
# 范畴：mod-notes 案例研究，非通用开发工具。仅作逆向过程理解底本，暂未在本环境验证运行。
# 依赖：lupa（pip install lupa）。
# 注意：文件内硬编码作者本机路径（E:/神秘复苏/饥荒大型mod/3155177428/ 等），复用前须改为目标 mod 目录。
# 使用流程（按管线顺序）：lol_dump（提取 LOL! wrapper）→ probe_require（还原 require 链）→ daogui_full（解 modmain）→ daogui_scripts/worldgen/plants（分域解密）。
#
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)
G = lua.globals()
MODROOT = 'E:/神秘复苏/饥荒大型mod/3155177428/'
DRAFTS = 'E:/神秘复苏/dist/dst-mod-creater/drafts/'
read_log = []

lua.execute(r'''
-- 万能表工厂
local function make_mt()
  local mt = {}
  mt.__index = function(t, k) local v = {}; setmetatable(v, mt); return v end
  mt.__call = function() return setmetatable({}, mt) end
  return mt
end
local mt = make_mt()
local data_mt = {}
data_mt.__index = function(t, k) local v = {}; setmetatable(v, data_mt); return v end
STRINGS = setmetatable({}, data_mt)
-- 万能算术表：未知 TUNING 键返回可索引可算术的表（如 GAMEMODE_STARTING_ITEMS）
local utmt = {__index = function() return ut end, __call = function() return ut end,
  __add=function() return 1 end, __sub=function() return 1 end, __mul=function() return 1 end,
  __div=function() return 1 end, __mod=function() return 1 end, __pow=function() return 1 end,
  __unm=function() return 1 end, __lt=function() return true end, __le=function() return true end,
  __eq=function() return false end, __len=function() return 0 end, __concat=function() return "UT" end,
  __tostring=function() return "UT" end}
ut = setmetatable({}, utmt)
TUNING = setmetatable({}, {__index = function(t,k)
  local known = {TOTAL_DAY_TIME=480, PERISH_MED=4800, PERISH_SUPERFAST=480,
    SEED_CHANCE_RARE=0.5, SEED_CHANCE_COMMON=0.8, SEED_CHANCE_MED=0.6, SEED_CHANCE_UNCOMMON=0.3}
  if known[k] ~= nil then return known[k] end
  return ut
end})
DAOGUI = setmetatable({}, mt)
VEGGIES = setmetatable({}, mt)
PLANT_DEFS = setmetatable({}, mt)
PREFAB_SKINS = setmetatable({}, mt)
SKIN_AFFINITY_INFO = setmetatable({}, mt)
SKIN_RARITY_COLORS = setmetatable({}, mt)
RARITY_ORDER = setmetatable({}, mt)
KNOWN_STRINGS = setmetatable({}, mt)
-- 赋值记录：STRINGS 的 __newindex 记录 key/value hex
str_assigns = {}
setmetatable(STRINGS, {__index = function(t,k)
  local v = {}; setmetatable(v, {__index=function(t2,k2)
    local v2 = {}; setmetatable(v2, {__index=function(t3,k3)
      local v3 = {}; setmetatable(v3, {__index=function(t4,k4)
        local v4 = {}; setmetatable(v4, {__index=function() return "" end})
        return v4
      end})
      return v3
    end, __newindex=function(t3,k3,v3)
      if type(v3)=="string" then
        local h = ''
        local n = math.min(#v3, 24)
        for i=1,n do h = h .. string.format('%02x', v3:byte(i)) end
        table.insert(str_assigns, {tostring(k), tostring(k2), tostring(k3), h, #v3})
      end
      rawset(t3, k3, v3)
    end})
    return v2
  end, __newindex=function(t2,k2,v2)
    if type(v2)=="string" then
      local h = ''
      local n = math.min(#v2, 24)
      for i=1,n do h = h .. string.format('%02x', v2:byte(i)) end
      table.insert(str_assigns, {tostring(k), tostring(k2), h, #v2})
    end
    rawset(t2, k2, v2)
  end})
  return v
end, __newindex=function(t,k,v) rawset(t,k,v) end})
local noop = function() end
setup_log = {}
local API = {'AddString','AddPrefabPostInit','AddPrefabPostInitAny','AddComponentPostInit','AddRecipe','AddRecipe2','AddBrainPostInit','AddStategraphPostInit','AddSimAction','AddComponentAction','AddGlobalClassPostConstruct','AddModRPCHandler','AddClientModRPCHandler','AddPlayerPostInit','AddMinimapAtlas','RegisterInventoryItemAtlas','RegisterGlobalClassPostConstruct','RegisterPrefabs','AddCharacterCommonPrefabPostInit','AddClassPostConstruct','AddReplicableComponent','AddComponentPhysicsCollision','AddWorldGenPostInit','AddTaskSetPreInit','AddLevelPreInit','AddLevel','AddTask','AddRoom','AddRoomPreInit','AddLocation','AddTurf','AddWall','AddPrefab','AddVegetation','AddPrototyperRecipe','AddEntityToWorld','AddDlcRecipe','AddSimPostInit','AddInventoryItem','AddOnPlayerSpawn','AddSeason','AddGameMode','AddGameModePostInit','AddModCharacter','AddSimpleRecipe','AddToAllPlayers','AddSkin','RemoveRecipe','RemoveRecipeByName','RemovePrototyperRecipe','RemovePrefab','AddResource','AddOptionalResource','AddBuff','AddDebuff','AddServerRecipe','AddClientRecipe','MakeRecipe','MakeIngredient','MakeInventoryItem','MakeItemSkin','AddItemSkin','AddCharacterSkin','CreatePrefabSkin','MakeCharacterSkin','AddPrototyperRecipe','AddExperiment','AddResearch','AddXRay','AddCameraShaker','AddScreenFlash','RegisterPrefabSkin','RegisterEntitySkin','AddLevelPreInitAny','AddRoomPreInitAny','AddTaskSetPreInitAny','AddGameModePostInitAny'}
for _, n in ipairs(API) do _G[n] = noop end
_G['TimeEvent'] = noop
_G['ActionHandler'] = noop
_G['State'] = noop
_G['EventHandler'] = noop
-- 类构造函数：返回万能表（可调用、可索引、可链式）
local CLASS = {'Action','Ingredient','Recipe','TechTree','Container','CraftingStation','Builder','FoodProcessor','SpicedFood','StringBuffer','EntityScript','Class','Event','Vector3','Point','Angle','FxHandle','HealthBar','OnUpdate','Widget','Text','Image','Button','Menu','GridLayout','UIPanels','AddBuff','Debuff','Prefab','Entity','PersistentPrefab','ItemSkin','PlayerSkin','CompoundIngredient','RecipeSorter','CraftingTab','Tab','Group','Panel','AnimState','AnimAction','Buff','SpawnPrefabAtPoint'}
for _, n in ipairs(CLASS) do _G[n] = function(...) return setmetatable({}, mt) end end
-- require：已知模块给真实形状，其余返回万能表
_G['require'] = function(name)
  if name == 'containers' then return {MAXITEMSLOTS = 0, params = {}} end
  if name == 'cooking' then return {} end
  if name == 'components/spdamageutil' then return {} end
  if name == 'prefabs/farm_plant_defs' then return {PLANT_DEFS = setmetatable({}, mt)} end
  if name == 'skin_affinity_info' then return {} end
  if name == 'skin_namemaps' then return {} end
  if name == 'actions' then return {} end
  if name == 'brains/brain_common' then return {} end
  if name == 'stategraphs/sg_common' then return {} end
  if name == 'components/health' then return {} end
  return setmetatable({}, mt)
end
_G['GetModConfigData'] = function(k) return nil end
_G['GetModConfigNumber'] = function(k) return nil end
_G['GetModConfigBool'] = function(k) return nil end
KnownModIndex = setmetatable({}, mt)
getfenv = function(fn) if fn == nil then return _ENV end; return debug.getupvalue(fn,1) end
setfenv = function(fn, env) if fn == nil then return nil end; return debug.setupvalue(fn,1,env) end
unpack = table.unpack
math.random = function(a,b) if a==nil then return 0.5 end if b==nil then return a end return a end
math.randomseed = function() end
os.time = function() return 0 end; os.clock = function() return 0 end
os.data = function() return 0 end
-- 对象 metatable：__index 是空表（可被 mod 赋值方法）
local obj_mt = {__index = {}}
TheWorld = setmetatable({}, obj_mt)
TheSim = {LoadPrefabs = noop, LoadPrefabFile = noop, SetPrefabs = noop, GetRegionGrid = noop, SetRegionGrid = noop}
TheInventory = setmetatable({}, obj_mt)
ThePlayer = setmetatable({}, obj_mt)
TheFrontEnd = setmetatable({}, obj_mt)
TheInput = setmetatable({}, obj_mt)
TheCamera = setmetatable({}, obj_mt)
TheNet = setmetatable({}, obj_mt)
TheShard = setmetatable({}, obj_mt)
TheWorldEventBroadcaster = setmetatable({}, obj_mt)
TheDungeon = setmetatable({}, obj_mt)
TheHUD = setmetatable({}, obj_mt)
TheHud = setmetatable({}, obj_mt)
TheScreenManager = setmetatable({}, obj_mt)
TheMiniMap = setmetatable({}, obj_mt)
GetWorld = function() return TheWorld end
GetPlayer = function() return ThePlayer end
GetInventoryItem = function() return nil end
GetClock = function() return setmetatable({}, mt) end
GetSeasonManager = function() return setmetatable({}, mt) end
GetTime = function() return 0 end
GetModName = function() return 'daogui' end
GetHUD = function() return TheHUD end
GetHud = function() return TheHUD end
GetFrontEnd = function() return TheFrontEnd end
GetScreenManager = function() return TheScreenManager end
GetCamera = function() return TheCamera end
GetTask = function() return setmetatable({}, mt) end
Sim = setmetatable({}, mt)
Profile = setmetatable({}, mt)
ModManager = setmetatable({}, mt)
EventMaster = setmetatable({}, mt)
ClassTuning = setmetatable({}, mt)
KnownWorldModifiers = {}
ServerLog = noop
ExecuteConsoleCommand = noop
GetTimeInFrames = function() return 0 end
IsServer = function() return true end
IsClient = function() return false end
IsMasterSim = function() return true end
IsDedicatedServer = function() return false end
IsConsole = function() return false end
IsPaused = function() return false end
IsGamePaused = function() return false end
IsMultiplayer = function() return false end
-- C_ API
local cname = {'C_GetTime','C_GetSeasonManager','C_IsRaining','C_GetCamera','C_GetHUD','C_GetPlayerHUD','C_GetPlayer','C_GetClock','C_GetWorld','C_GetInventory','C_GetMultiplier','C_GetTask','C_GetGameMode','C_GetMap','C_GetMinimap','C_GetFrontEnd','C_GetScreenManager','C_GetInput','C_GetNet','C_GetShard','C_IsDLCEnabled','C_IsRLCEnabled','C_GetPrefabSkin'}
for _, n in ipairs(cname) do _G[n] = function() return setmetatable({}, mt) end end
__loaded = {}
''')
lua.execute(r'''
local __real_getinfo = debug.getinfo
debug.getinfo = function(fn, opt)
  if type(fn) == 'function' and fn == loadstring then return {source='=[C]',short_src='=[C]',what='C',currentline=-1} end
  return __real_getinfo(fn, opt)
end
local __real_setupvalue = debug.setupvalue
debug.setupvalue = function(fn, n, v)
  table.insert(setup_log, {n, type(v), tostring(v):sub(1, 40)})
  return __real_setupvalue(fn, n, v)
end
loadstring = function(s, name)
  local fn, err = load(s, name)
  local bytes = {s:byte(1, -1)}
  __loaded[#__loaded+1] = {bytes, name, fn, err, #s}
  return fn, err
end
-- 自引用万能表：任何索引/调用/算术都安全
local UNIV = {}
local univ_meta = {__index = function() return UNIV end, __call = function() return UNIV end,
  __add=function() return 1 end, __sub=function() return 1 end, __mul=function() return 1 end,
  __div=function() return 1 end, __mod=function() return 1 end, __pow=function() return 1 end,
  __unm=function() return 1 end, __lt=function() return true end, __le=function() return true end,
  __eq=function() return false end, __len=function() return 0 end, __concat=function() return "UNIV" end,
  __tostring=function() return "UNIV" end}
setmetatable(UNIV, univ_meta)
FRAMES = setmetatable({}, univ_meta)
DEGREES = setmetatable({}, univ_meta)
RADIANS = setmetatable({}, univ_meta)
GLOBAL = {}; for k,v in pairs(_G) do GLOBAL[k]=v end
GLOBAL.rawget = function(t,k)
  local v = rawget(t,k); if v~=nil then return v end
  v = rawget(_G,k); if v~=nil then return v end
  return UNIV
end
setmetatable(GLOBAL, {__index = function(t,k) return UNIV end, __call = function() return UNIV end})
env = {}; for k,v in pairs(_G) do env[k]=v end
setmetatable(env, {__index = function(t,k)
  local v = rawget(_G,k)
  if v ~= nil then return v end
  return UNIV
end})
''')

def py_io_open(name, mode=None):
    name = str(name)
    read_log.append(('open', name, mode))
    full = os.path.join(MODROOT.rstrip('/').replace('/', os.sep), name)
    if not os.path.exists(full):
        read_log.append(('open_fail', name))
        return None
    data = open(full, 'rb').read().decode('utf-8', 'replace')
    read_log.append(('open_data_len', name, len(data)))
    return lua.eval('''
        (function(content)
            local f = {}
            f.content = content
            f.read = function(self, fmt) return self.content end
            f.lines = function(self) return function() return nil end end
            f.close = function(self) end
            return f
        end)(...)''', data)

def py_dump(t, name):
    out = os.path.join(DRAFTS, name)
    with open(out, 'wb') as f:
        for i in range(1, len(t) + 1):
            f.write(bytes([int(t[i])]))
    print('  dumped ->', name, os.path.getsize(out))

G['io'] = lua.table(open=py_io_open)
G['loadfile'] = lambda n: read_log.append(('loadfile', str(n))) or None
G['modimport'] = lambda n: read_log.append(('modimport', str(n))) or None
G['LoadPrefabFile'] = lambda n: read_log.append(('LoadPrefabFile', str(n))) or None
G['MODROOT'] = MODROOT
G['py_dump'] = py_dump

def py_log(k, k2, h, n):
    print('  SA', k, k2, h, n)

G['py_log'] = py_log

code = open(os.path.join(MODROOT, 'modmain.lua'), 'rb').read().decode('utf-8', 'replace')
idx = code.rfind('v15("LOL!')
code2 = code[:idx] + 'local __ok, __msg = xpcall(v15, function(e) local __m = tostring(e) .. "\\n" .. tostring(debug.traceback("", 2)); local __h=""; for __i=1,#__m do __h=__h..string.format("%02x",__m:byte(__i)) end; return __h end,' + code[idx+4:]
code2 = code2 + ' if not __ok then return "VMERR:" .. tostring(__msg) end return __ok'
try:
    ok = lua.execute(code2)
    print('EXEC ok=', ok)
    if isinstance(ok, str) and ok.startswith('VMERR:'):
        try:
            print('VMERR:', bytes.fromhex(ok[6:]).decode('utf-8', 'replace'))
        except Exception:
            print('VMERR raw:', ok)
except Exception as e:
    print('EXEC ERROR:', type(e).__name__, str(e)[:400])

loaded = G['__loaded']
print('loaded chunks:', len(loaded))
for i in range(1, len(loaded)+1):
    e = loaded[i]
    lua.execute('py_dump(__loaded[%d][1], %r)' % (i, '_dec_%d.bin' % i))
print('--- read log ---')
for item in read_log:
    print(item)
print('--- STRING assigns (top 40) ---')
lua.execute('local n = math.min(#str_assigns, 40); for i=1,n do local a = str_assigns[i]; py_log(a[1], a[2], a[3], a[4]) end')
print('total str assigns:', len(lua.eval('#str_assigns')))
