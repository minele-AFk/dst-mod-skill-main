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
TUNING = setmetatable({}, {__index = function(t,k) return 1 end})
DAOGUI = setmetatable({}, mt)
VEGGIES = setmetatable({}, mt)
PLANT_DEFS = setmetatable({}, mt)
PREFAB_SKINS = setmetatable({}, mt)
SKIN_AFFINITY_INFO = setmetatable({}, mt)
SKIN_RARITY_COLORS = setmetatable({}, mt)
RARITY_ORDER = setmetatable({}, mt)
KNOWN_STRINGS = setmetatable({}, mt)
local noop = function() end
local API = {'AddString','AddPrefabPostInit','AddPrefabPostInitAny','AddComponentPostInit','AddRecipe','AddRecipe2','AddBrainPostInit','AddStategraphPostInit','AddSimAction','AddComponentAction','AddGlobalClassPostConstruct','AddModRPCHandler','AddClientModRPCHandler','AddPlayerPostInit','AddMinimapAtlas','RegisterInventoryItemAtlas','RegisterGlobalClassPostConstruct','RegisterPrefabs','AddCharacterCommonPrefabPostInit','AddClassPostConstruct','AddReplicableComponent','AddComponentPhysicsCollision','AddWorldGenPostInit','AddTaskSetPreInit','AddLevelPreInit','AddLevel','AddTask','AddRoom','AddRoomPreInit','AddLocation','AddTurf','AddWall','AddPrefab','AddVegetation','AddPrototyperRecipe','AddEntityToWorld','AddDlcRecipe','AddSimPostInit','AddInventoryItem','AddOnPlayerSpawn','AddSeason','AddGameMode','AddGameModePostInit','AddModCharacter','AddSimpleRecipe','AddToAllPlayers','AddSkin','RemoveRecipe','RemoveRecipeByName','RemovePrototyperRecipe','RemovePrefab','AddResource','AddOptionalResource','AddBuff','AddDebuff','AddServerRecipe','AddClientRecipe','MakeRecipe','MakeIngredient','MakeInventoryItem','MakeItemSkin','AddItemSkin','AddCharacterSkin','CreatePrefabSkin','MakeCharacterSkin','AddPrototyperRecipe','AddExperiment','AddResearch','AddXRay','AddCameraShaker','AddScreenFlash','RegisterPrefabSkin','RegisterEntitySkin','AddLevelPreInitAny','AddRoomPreInitAny','AddTaskSetPreInitAny','AddGameModePostInitAny'}
for _, n in ipairs(API) do _G[n] = noop end
_G['TimeEvent'] = noop
_G['ActionHandler'] = noop
_G['State'] = noop
_G['EventHandler'] = noop
local CLASS = {'Action','Ingredient','Recipe','TechTree','Container','CraftingStation','Builder','FoodProcessor','SpicedFood','StringBuffer','EntityScript','Class','Event','Vector3','Point','Angle','FxHandle','HealthBar','OnUpdate','Widget','Text','Image','Button','Menu','GridLayout','UIPanels','AddBuff','Debuff','Prefab','Entity','PersistentPrefab','ItemSkin','PlayerSkin','CompoundIngredient','RecipeSorter','CraftingTab','Tab','Group','Panel','AnimState','AnimAction','Buff','SpawnPrefabAtPoint','Level','Room','TaskSet','Location','StaticLayout','RoomType','LevelType','Task','Layer','NodeType','LayoutSettings','LevelLayoutSettings','StartLayout','RoomLayout','StaticLayoutTemplate','GroundNode','RoomGroup','RoomLayouts','LevelEntries'}
for _, n in ipairs(CLASS) do _G[n] = function(...) return setmetatable({}, mt) end end
_G['require'] = function(name)
  print('PYREQ:', name)
  return setmetatable({}, mt)
end
_G['GetModConfigData'] = function(k) return nil end
KnownModIndex = setmetatable({}, mt)
getfenv = function(fn) if fn == nil then return _ENV end; return debug.getupvalue(fn,1) end
setfenv = function(fn, env) if fn == nil then return nil end; return debug.setupvalue(fn,1,env) end
unpack = table.unpack
math.random = function(a,b) if a==nil then return 0.5 end if b==nil then return a end return a end
math.randomseed = function() end
os.time = function() return 0 end; os.clock = function() return 0 end
os.data = function() return 0 end
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
local cname = {'C_GetTime','C_GetSeasonManager','C_IsRaining','C_GetCamera','C_GetHUD','C_GetPlayerHUD','C_GetPlayer','C_GetClock','C_GetWorld','C_GetInventory','C_GetMultiplier','C_GetTask','C_GetGameMode','C_GetMap','C_GetMinimap','C_GetFrontEnd','C_GetScreenManager','C_GetInput','C_GetNet','C_GetShard','C_IsDLCEnabled','C_IsRLCEnabled','C_GetPrefabSkin'}
for _, n in ipairs(cname) do _G[n] = function() return setmetatable({}, mt) end end
__loaded = {}
''')
lua.execute(r'''
loadstring = function(s, n)
  local fn, err = load(s, n)
  local bytes = {s:byte(1, -1)}
  __loaded[#__loaded+1] = {bytes, n, fn, err, #s}
  return fn, err
end
package = {loaded = {}}
local __real_getinfo = debug.getinfo
debug.getinfo = function(fn, opt)
  if type(fn) == 'function' and fn == loadstring then return {source='=[C]',short_src='=[C]',what='C',currentline=-1} end
  return __real_getinfo(fn, opt)
end
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
    full = name if name.startswith('E:/') else os.path.join(MODROOT.rstrip('/').replace('/', os.sep), name)
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
            f.seek = function(self) return 0 end
            f.write = function(self) end
            f.flush = function(self) end
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

code = open(os.path.join(MODROOT, 'modworldgenmain.lua'), 'rb').read().decode('utf-8', 'replace')
idx = code.rfind('v15("LOL!')
code = code[:idx] + 'local __ok, __msg = xpcall(v15, function(e) local __m = tostring(e) .. "\\n" .. tostring(debug.traceback("", 2)); local __h=""; for __i=1,#__m do __h=__h..string.format("%02x",__m:byte(__i)) end; return __h end,' + code[idx+4:] + ' if not __ok then return "VMERR:" .. tostring(__msg) end return __ok'
try:
    ok = lua.execute(code)
    print('EXEC ok=', ok)
except Exception as e:
    print('EXEC ERROR:', type(e).__name__, str(e)[:400])

# call shim for plant/food/component files
lua.execute(r'''
local function callshim(name)
  local ok, r = pcall(function() return require(name) end)
  if not ok then print("SHIM ERR", name, tostring(r)) end
end
callshim("prefabs/daogui_farm_plants")
callshim("prefabs/daogui_farm_plants_herbs")
callshim("prefabs/daogui_eyefruit")
callshim("prefabs/daogui_corpse_flower")
callshim("prefabs/daogui_demonflower")
callshim("prefabs/daogui_wheat")
callshim("prefabs/daogui_sharp_berrybush")
callshim("prefabs/daogui_sharp_berries")
callshim("prefabs/daogui_red_webtree")
callshim("prefabs/daogui_qingtitree")
callshim("prefabs/daogui_skulltree")
callshim("prefabs/daogui_corpse_tree")
callshim("prefabs/daogui_planted_tree")
callshim("prefabs/daogui_byg")
callshim("prefabs/daogui_dioptase")
callshim("prefabs/daogui_dioptase_rock")
callshim("components/daogui_regrowthmanager")
callshim("components/daogui_plantpotseed")
callshim("components/daogui_pickable")
callshim("components/daogui_forestresourcespawner")
callshim("daogui_food_defs")
callshim("daogui_abbess_items")
''')
loaded = G['__loaded']
print('total captured chunks:', len(loaded))
names = ['_p_%d.bin' % i for i in range(1, len(loaded)+1)]
for i in range(1, len(loaded)+1):
    lua.execute('py_dump(__loaded[%d][1], %r)' % (i, '_p_%d.bin' % i))
