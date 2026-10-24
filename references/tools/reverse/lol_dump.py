# 逆向/混淆破解工具（道诡异仙 DaxSg 三层加密专用）
# 范畴：mod-notes 案例研究，非通用开发工具。仅作逆向过程理解底本，暂未在本环境验证运行。
# 依赖：lupa（pip install lupa）。
# 注意：文件内硬编码作者本机路径（E:/神秘复苏/饥荒大型mod/3155177428/ 等），复用前须改为目标 mod 目录。
# 使用流程（按管线顺序）：lol_dump（提取 LOL! wrapper）→ probe_require（还原 require 链）→ daogui_full（解 modmain）→ daogui_scripts/worldgen/plants（分域解密）。
#
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)
G = lua.globals()
code = open('E:/神秘复苏/饥荒大型mod/3155177428/modworldgenmain.lua','rb').read().decode('utf-8','replace')
m = re.search(r'v15\("LOL!(.*?)",\s*v9\(\)', code, re.S)
payload = 'LOL!' + m.group(1)
print('payload len:', len(payload))
def py_write_byte(b):
    return None
buf = []
def py_push(b):
    buf.append(b)
G['py_push'] = py_push
lua.execute(r'''
payload = ...
local function dec(v16)
  local v19
  v16 = string.gsub(string.sub(v16,5), "..", function(v30)
    if string.byte(v30,2) == 79 then
      v19 = tonumber(string.sub(v30,1,1))
      return ""
    else
      local v81 = string.char(tonumber(v30,16))
      if v19 then local v90 = string.rep(v81,v19); v19 = nil; return v90
      else return v81 end
    end
  end)
  return v16
end
local out = dec(payload)
for i=1,#out do py_push(out:byte(i)) end
''', payload)
data = bytes(buf)
open('E:/神秘复苏/dist/dst-mod-creater/drafts/_wgen_vm_blob.bin','wb').write(data)
print('blob bytes:', len(data))
strs = re.findall(rb'[\x20-\x7e]{4,}', data)
print('strings:')
for s in strs[:120]:
    print('  ', s.decode('utf-8','replace'))
