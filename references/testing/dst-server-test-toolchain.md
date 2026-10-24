# DST 无头服务器 Lua 快速测试工具链

> 来源：外部项目 `dst-ai-scripting-main`，本 skill 将其整体能力集成于此分类。
> 源码原样保留在本目录 `dst_test_mod/`（桥接模组），Python 工具链已上收至 `../tools/testing/`（总台账见 `references/tools/README.md`），便于直接使用或对照阅读。

## 定位

### 平台与授权边界

本页说明的是旧 macOS 注入桥；已融合的 Windows 隔离单分片 runner 属于另一条工具链，入口见 [融合工具说明](../engineering/dst-mod-engineering/README.md#执行工具)。不要将新 runner 的接入当作本页 Python 脚本已经完成移植。

- Python 工具链保留 macOS 的目录与进程实现；**Windows 待移植，Linux 待适配和运行验证**，不能仅因 Python 语法检查通过就宣称可用。
- Lua 桥接模组使用游戏 API，具备跨平台设计基础；每个平台仍需实际验证文件权限、mtime、响应路径与生命周期。
- 本文的安装、进程启停和脚本注入只用于用户已授权的独立测试环境。先备份测试配置，不覆盖真实存档，不按名称终止无关服务器。
- 源码、第三方访问和测试结果表述遵守 [共用约定](../development-contract.md)。

让外部程序（例如 AI）向运行中的《饥荒：联机版》**无头专用服务器**（Dedicated Server）注入 Lua 代码、执行并取回返回值，全程不需要玩家进入游戏。可用于：

- 自动化测试 mod 逻辑（生成物品、查状态、模拟事件）
- AI 驱动的游戏内脚本调试（比重启服务器快得多）
- 批量执行游戏内查询（`TheWorld.state.cycles`、玩家数据、全局变量等）

## 核心原理（先理解这个，代码就好读了）

游戏对 Lua 运行时的文件读写限制极严：mod 无法随意读写磁盘。这套工具找到两条合法通道：

| 方向 | 通道 | 说明 |
| --- | --- | --- |
| 读 | `kleiloadlua` / `TheSim:GetFileModificationTime` | 只能读 mod 自己目录（`MODROOT`）下的文件 |
| 写 | `io.open("unsafedata/...", "w")` | 游戏运行时唯一允许的写盘通道，目录扁平、限 .txt 等少量扩展名 |

基于此设计出**"改文件 mtime 即触发"**的通讯协议：

1. 桥接模组 `dst_test_mod` 通过 `AddSimPostInit` 注册 `TheWorld:DoPeriodicTask(1/30)`，每 1/30 秒轮询 `scripts/test_request.lua` 的修改时间（mtime）；
2. `run_script.py` 把要执行的 Lua 代码写入该文件，并用 `os.utime` 保证 mtime 与上次不同；
3. 模组发现 mtime 变化 → `kleiloadlua` 加载代码 → `setfenv` 注入沙箱环境 → `xpcall` 执行；
4. 返回值 + `print` 输出写回 `unsafedata/dst_test_response_<mtime>.txt`；
5. Python 端清理旧响应文件、轮询新响应、解析并打印结果。

> 游戏没有文件删除 API，所以响应文件**按 mtime 命名保证唯一**，旧文件由外部工具负责清理。

## 目录结构与文件说明

```
references/testing/
├── dst-server-test-toolchain.md   # 本文档
└── dst_test_mod/                  # 桥接模组源码（游戏内部分，跨平台通用）
    ├── modinfo.lua                # 模组信息（priority=9999 保证优先加载）
    ├── modmain.lua                # 核心：轮询 + 执行 + 写回
    └── scripts/test_request.lua   # "信箱"：被注入的 Lua 代码写在这里

references/tools/testing/          # Python 工具链（已上收，注意：原版为 macOS 专用）
    ├── game_config.py             # 所有路径的集中配置（可用环境变量覆盖）
    ├── game_process.py            # 启动 / 停止 / 查询服务器进程
    ├── game_log.py                # 读取 server_log.txt，支持 tail / grep / follow
    ├── run_script.py              # 注入 Lua 代码并等待、解析、返回运行结果
    └── setup.py                   # 安装模组进游戏目录 + 幂等配置
```

### 模组加载方式（三道保险）

1. **存档强制加载**：`Cluster/Master/modoverrides.lua` 中 `["dst_test_mod"] = { enabled = true }`；
2. **开发模式强制加载**：游戏 `Contents/mods/modsettings.lua` 追加 `ForceEnableMod("dst_test_mod")`（由 `setup.py` 幂等写入）；
3. **`pause_when_empty = false`**：否则服务器无人连接时暂停模拟，轮询任务不会运行，注入工具永远超时。

## 注入脚本的可用环境（沙箱细节）

脚本运行在 `setmetatable({}, {__index = GLOBAL})` 的环境里：

- 可直接使用 `TheWorld`、`ThePlayer`、`TheSim`、`GLOBAL` 及大部分游戏全局函数；
- `print(...)`：被重定向，输出进响应文件的 `prints:` 节，不污染游戏日志；
- `gameprint(...)`：原版 print，直接写游戏日志（调试用）；
- 返回值可为任意数量，`nil` / 布尔 / 数字 / 字符串 / 表都会被序列化。

## 响应文件格式

```text
--dst-test-response--
status:ok|error
mtime:<触发本次响应的 mtime>
values:
  <序列化值>          # nil / true / false / number:x / string:"..." / table:<DataDumper>
prints:
  <print 输出行>
--dst-test-response-end--
```

## 关键坑点（作者踩过的坑，务必记住）

1. **专用服务器上禁用 `debug.traceback`**：把它作为 `xpcall` 的错误处理函数（或带错误值调用）会污染 Lua 状态并**直接崩溃进程**（"LuaError but no error string"）。必须像 `modmain.lua` 那样用 `debug.getinfo` 手写栈回溯。
2. **`pause_when_empty` 必须为 `false`**：否则空服暂停模拟 → 轮询不运行 → 注入超时。
3. **mtime 可能是 16 位十六进制**（如 `000000006a71e141`），Python 端 `_parse_mtime` 做了兼容。
4. **轮询竞态**：模组可能错过第一次写入，所以 `run_script.py` 每 3 秒重新 touch 一次请求文件。
5. **脚本必须快速返回**：注入代码跑在服务器主线程，死循环会卡死整个服务器。

## 使用流程（macOS 布局示例，其他平台不得直接套用）

```bash
# 工具链位于 references/tools/testing/，以下路径均为相对 references/tools/testing/ 运行

# 初始化（首次）：安装模组进游戏目录 + ForceEnableMod + pause 修复
python3 setup.py

# 启动服务器（--wait-ready 等待启动完成；--lan 适合无公网环境；--unpaused 保证空服不暂停）
game_process.py start --wait-ready --lan --unpaused

# 注入测试
run_script.py --ping
run_script.py --code 'return TheWorld.state.cycles'
run_script.py --code 'local p = GLOBAL.ThePlayer; print("player", p and p.name or "none"); return p ~= nil' --json

# 停止
game_process.py stop
```

`run_script.py` 退出码：`0` 成功，`1` 脚本报错，`2` 等待响应超时，`3` 服务器未运行。

## Windows 移植注意（原工具链为 macOS 专用）

模组部分（`dst_test_mod/`）是 Lua + 游戏 API，跨平台行为仍需实测。Python 工具链至少有以下适配项；只改配置路径不足以完成 Windows 支持：

| 文件 | macOS 写法 | Windows 需要 |
| --- | --- | --- |
| `game_config.py` | 二进制路径 `.../dontstarve_dedicated_server_nullrenderer.app/Contents/MacOS/...` | Windows 版专用服务器是 `bin/dontstarve_dedicated_server_nullrenderer.exe`，无 `.app` 结构 |
| `game_process.py` | `ps` / `pgrep` 查进程、`os.kill(pid, 0)` 探活、`SIGTERM` / `SIGKILL` | 用 `tasklist` / `taskkill` 或 `psutil`，进程结束用 `proc.terminate()` / `taskkill /F` |
| `run_script.py` | `import fcntl`（文件锁） | Windows 无 `fcntl`，`import` 直接崩溃，需换 `msvcrt.locking` 或去掉锁 |

另外需要先准备 Windows 版 DST 专用服务器：用 steamcmd 下载 app 343050（约 4~5GB），不能用客户端版代替（客户端无法无头运行，也没有 `-conf_dir` 等参数）。
