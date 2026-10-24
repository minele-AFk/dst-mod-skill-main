
# 逆向探查工具：在 Lua 运行时内探测 require 链，还原加载顺序（配合 lol_dump / daogui_* 解密管线）。
# 依赖：lupa（pip install lupa）。硬编码作者本机 MODROOT 路径，复用前须改为目标 mod 目录。暂未验证运行。
#
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)
G = lua.globals()
MODROOT = 'E:/神秘复苏/饥荒大型mod/3155177428/'
def py_open(name, mode=None):
    full = str(name) if str(name).startswith('E:/') else MODROOT + str(name)
    print('IOOPEN:', full)
    if not os.path.exists(full):
        print('  MISSING')
        return None
    data = open(full,'rb').read().decode('utf-8','replace')
    print('  content len:', len(data))
    return lua.eval('(function(content) local f = {} f.read = function(self, fmt) return content end f.close = function(self) end f.lines = function(self) return function() return nil end end f.seek = function(self) return 0 end f.write = function(self) end f.flush = function(self) end return f end)(...)', data)
G['MODROOT'] = MODROOT
G['io'] = lua.table(open=py_open)
G['require'] = lambda n: (print('REQ:', n), {})[1]
G['modimport'] = lambda n: print('MODIMPORT:', n)
G['os'] = lua.table(time=lambda: 0, data=lambda: 0)
G['package'] = lua.table(loaded=lua.table())
G['getfenv'] = lambda: lua.eval('_ENV')
G['setfenv'] = lambda fn, e: None
lua.execute(r'''
loadstring = function(s) print("LOADSTRING len:", #s, "head:", s:sub(1,40)) return function() end end
GLOBAL = {setmetatable=setmetatable, rawget=rawget, getinfo=debug.getinfo}
env = {}
''')
code = open(MODROOT + 'modworldgenmain.lua','rb').read().decode('utf-8','replace')
try:
    ok = lua.execute(code)
    print('EXEC:', ok)
except Exception as e:
    print('ERR:', type(e).__name__, str(e)[:400])
print('--- after run ---')
print('_G.require type:', lua.eval('type(rawget(_G,"require"))'))
print('env.require type:', lua.eval('type(env.require)'))
print('env keys:', lua.eval('(function() local t={} for k in pairs(env) do t[#t+1]=tostring(k) end return table.concat(t,",") end)()'))

print('=== now call the shim ===')
G['py_dump'] = lambda t, name: (open('E:/神秘复苏/dist/dst-mod-creater/drafts/'+name,'wb').write(bytes([int(t[i]) for i in range(1,len(t)+1)])), print('dumped', name))[1]
lua.execute(r'''
local function callshim(name)
  print("calling require shim:", name)
  local ok, r = pcall(function() return require(name) end)
  print("  result:", ok, type(r))
end
-- hook loadstring to capture decrypted scripts sources
local real_loadstring = loadstring
loadstring = function(s, n)
  print("LOADSTRING:", #s, s:sub(1, 60))
  return real_loadstring(s, n)
end
callshim("daogui_turf_defs")
callshim("map/daogui_qingfengtemple")
callshim("map/static_layouts/daogui_dangerland")
''')
print('done')
