# DST Mod Tool（动画工具 CLI/Lua API）

> 本机 GUI 动画工具，带完整 Lua IPC 脚本接口。适合 AI Agent 驱动做动画资源的导入、编辑、预览与导出。
> 与官方 `Don't Starve Mod Tools`（scml.exe 编译链）互补：DST Mod Tool 侧重交互式动画创作与预览，官方 Mod Tools 侧重最终编译打包。

## 定位与选型

| 场景 | 推荐工具 |
|---|---|
| 交互式动画创作、预览、批量编辑 | **DST Mod Tool**（本工具） |
| `.scml` → `anim zip` 最终编译 | 官方 `Don't Starve Mod Tools`（`scml.exe` / `buildanimation.py`） |
| 反编译已编译 zip | `references/tools/general/anim_scml_tool.py` |
| 纯贴图处理（缩放/抠图） | Python + Pillow，或本工具的导入/导出能力 |

## 安装与路径

- Windows 可执行文件：`DST Mod Tool.exe`（通常位于 `D:\mods\` 或用户自定义路径）
- 版本示例：1.0.5（`FileDescription: dst-app`）
- 日志目录：`C:\Users\<用户>\AppData\Local\aether\dst-mod-tool\data\logs`

首次使用前确认 exe 存在；若用户未告知路径，先在常见位置探测（`D:\mods\`、桌面、Steam 库等）。

## CLI 入口

```powershell
# 帮助（不启动应用）
& "D:\mods\DST Mod Tool.exe" --help
& "D:\mods\DST Mod Tool.exe" script --help --lang zh-CN

# 执行 Lua（三选一）
& "D:\mods\DST Mod Tool.exe" script --file "C:\absolute\path\task.lua"
& "D:\mods\DST Mod Tool.exe" script --text 'print(tool.document_revision)'
Get-Content -Raw "C:\path\task.lua" | & "D:\mods\DST Mod Tool.exe" script --stdin
```

### CLI 行为

- 若应用已在运行：脚本在该实例当前工作区执行；标题栏显示「远程执行中」，不抢占前台焦点
- 若应用未运行：自动启动主应用（可见窗口）；工作区通常为空，可用 `doc:import_resources` 导入
- 输出：固定向 stdout 写一行 JSON（envelope + report）
- 退出码：成功 `0`，协议/脚本失败 `1`
- 并发：同一时刻只执行一个脚本；收到 `busy` 时等待重试，不要并发重放
- 超时：服务端 60s，CLI 客户端 65s

## JSON 响应结构

```json
{
  "version": 1,
  "request_id": 42,
  "response": {
    "type": "script",
    "report": {
      "ok": true,
      "origin": "external_ipc",
      "output": ["print 输出行"],
      "error": null,
      "document": {
        "changed": false,
        "before_revision": 7,
        "after_revision": 7,
        "history_label": null
      },
      "tool_results": [],
      "stats": { "elapsed_micros": 120, "instructions": 8 }
    }
  }
}
```

### 检查清单（调用方必读）

1. `response.type == "script"`（`"error"` 表示 IPC envelope 错误）
2. `report.ok == true`；失败详情在 `report.error`
3. `report.output` 中的 `print(...)` 各行
4. `report.document` 的 revision 变化
5. 每个 `report.tool_results[i].ok`（延迟命令：选择/播放/导出/保存等）
6. `report.ok == false` 不一定表示 Document 没变——Lua+提交成功但后续 tool 命令失败时，已提交的修改会保留

### 稳定错误码

| 层级 | 码 | 含义 |
|---|---|---|
| envelope | `invalid_request` | framing/JSON/请求大小无效 |
| envelope | `unsupported_version` | 协议版本不支持 |
| envelope | `timeout` | 服务端超时 |
| envelope | `internal` | endpoint/通道不可用 |
| script | `busy` | 已有脚本或互斥任务在执行 |
| script | `invalid_source` / `read_source` | 来源参数无效或文件读取失败 |
| script | `lua_syntax` / `lua_runtime` | Lua 语法/运行错误 |
| script | `document_edit` | Document 操作校验失败 |
| script | `resource` | 图片/动画资源加载失败 |
| script | `limit_exceeded` | 源码/时间/指令/内存/输出/图片预算超限 |
| script | `commit_failed` | Document transaction 无法提交 |
| script | `tool_command_failed` | 选择/播放/History/预览/导出命令失败 |
| script | `cancelled` | 请求被取消 |

`error.stage`：`request` | `read_source` | `lua` | `commit` | `tool_command` | `cancelled`

## Lua 环境限制

| 项目 | 限制 |
|---|---|
| 脚本大小 | 1 MiB |
| Lua 内存 | 64 MiB |
| 指令数 | 10,000,000 |
| 运行时间 | 5 秒 |
| 修改操作数 | 10,000 |
| 输出行数 | 1,000 |
| 单行输出 | 4 KiB |
| 单次运行累计解码图片 | 4 GiB |

可用：Lua 基础 + `table` / `string` / `math` / `utf8`。
**不可用**：`io` / `os` / `package` / `debug`；脚本不能任意读写文件或启动外部程序。
受控文件访问仅限：`doc:import_resources`、`frame:replace_image`、图片导出 API、`tool` 的 DMT 工作区命令。

## 文档结构

```
doc
├── builds → Build → symbols → Symbol → frames → SymbolFrame
└── banks  → Bank → animations → Animation → frames → AnimFrame → elements → Element
```

所有集合 1-based，只读视图，用 `ipairs` 遍历（不支持 `pairs`）。名称 `find` 不区分大小写。

## 核心 API 速查

### tool（会话状态 + 非 Document 操作）

| 字段 | 说明 |
|---|---|
| `tool.document_revision` | 当前 revision |
| `tool.document_is_empty` | 是否无 Build/Bank |
| `tool.document_path` | 绑定的 `.dmt` 绝对路径或 nil |
| `tool.selection` | 主选择（bank/animation/frame/element） |
| `tool.playback` | 播放状态 |
| `tool.history` | 撤销历史 |
| `tool.hide_layers` | 隐藏图层数组 |
| `tool.override_symbols` | Symbol 替换映射 |

| 方法 | 说明 |
|---|---|
| `tool:select_animation(anim)` | 排他选中 Animation |
| `tool:select_frame(frame)` | 选中 AnimFrame 并跳转（自动暂停） |
| `tool:play()` / `tool:pause()` | 播放/暂停 |
| `tool:undo(steps?)` / `tool:redo(steps?)` | 撤销/重做（不能与同轮 Document 修改混用） |
| `tool:set_hide_layer(name, enabled)` | 隐藏/显示图层 |
| `tool:set_override_symbol(src, tgt?)` | Symbol 替换预览 |
| `tool:save_document()` | 保存到当前绑定 `.dmt` |
| `tool:save_document_as(abs_path)` | 另存为并绑定 |
| `tool:open_document(abs_path)` | 打开工作区（终止型，不能与其他操作混用） |

### Build 树

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
-- Build 集合
#doc.builds
doc.builds:find(name)
local build = doc.builds:add("mybuild")
build.name = "newname"
build:remove_unused_symbols()
build:remove()

-- Symbol
local symbol = build.symbols:add("swap_object")
symbol:find(name) -- 在 build.symbols 上
symbol:remove()

-- SymbolFrame
local frame = symbol.frames:add(0)  -- num = 0
frame:find(0) -- 精确按 num 查找
frame:replace_image([[C:\abs\path\image.png]])
frame:set_pivot(x, y)
frame:export_png([[C:\abs\out.png]])
frame.width  -- 只读，replace_image 后更新
frame.height
```

### Bank 树

```lua
local bank = doc.banks:add("gungnir")
local anim = bank.animations:add("idle")
anim.frame_rate = 30

local af = anim.frames:add()  -- AnimFrame
af:set_bounds(x, y, w, h)
af:export_png([[C:\abs\frame.png]], { max_dimension = 1024 })

-- Element
local el = af.elements:add({
    symbol = "swap_object",
    frame = 0,
    layer = "swap_object",
    tx = 0, ty = 0,
})
el:set_transform(a, b, c, d, tx, ty)
```

### 导入与导出

```lua
-- 导入（ZIP/DYN/BIN/SCML/GIF/PNG/Spine JSON/PSD；路径必须绝对）
local imported = doc:import_resources({
    [[C:\assets\gungnir.png]],
    [[C:\assets\character.zip]],
}, {
    spine_colors = "bake",       -- 或 "ignore"
    spine_color_tolerance = 0.1,
})

-- 导出动画预览
animation:export_png_sequence([[C:\out\seq-dir]], {  -- 目录必须不存在
    max_dimension = 1024,
    override_symbols = { swap_object = "swap_gungnir" },
    hide_layers = { "shadow" },
    background = { r = 48, g = 48, b = 48 },  -- 省略则透明
    canvas = { center_x = 0, center_y = -40, width = 1024, height = 1024 },
})
animation:export_gif([[C:\out\anim.gif]])
animation:export_apng([[C:\out\anim.png]])
```

### 通用变换

```lua
node:transform({ type = "translate", x = 10, y = -5 })
node:transform({ type = "rotate", degrees = 15 })
node:transform({ type = "scale", x = 1.2, y = 0.8 })
node:transform({ type = "affine", a = 1, b = 0, c = 0, d = 1, tx = 10, ty = -5 })
```

适用：Bank / Animation / AnimFrame / Element。
`scale` 后如需重算碰撞区域：`doc:recalculate_collision(scope, options)`。

## AI Agent 推荐工作流

1. **先读后写**：第一个请求用只读脚本确认 revision、Build、Bank、Animation
2. **精确定位**：`find` + `assert`，不猜名称/下标/Frame num
3. **小步修改**：`doc:set_label("...")` 设 History 标签；一次请求只做一组相关修改
4. **分离 History**：`undo`/`redo` 单独发，不与 Document 修改同轮
5. **检查报告**：`ok` + `error` + `document` + 全部 `tool_results`
6. **视觉验证**：先导出限制尺寸 PNG，用 Agent 图像查看能力检查内容；不要仅凭退出码声称视觉正确

### 只读检查模板

```lua
print("revision", tool.document_revision)
print("builds", #doc.builds)
print("banks", #doc.banks)
for _, bank in ipairs(doc.banks) do
    print("bank", bank.name, "animations", #bank.animations)
end
local sel = tool.selection.animation
if sel then
    print("selected", sel.name, #sel.frames)
end
```

### 修改模板

```lua
doc:set_label("Rename idle animation")
local bank = assert(doc.banks:find("wilson"), "Bank not found")
local animation = assert(bank.animations:find("idle"), "Animation not found")
animation.name = "idle_loop"
```

### 预览渲染模板

```lua
local animation = assert(tool.selection.animation, "Select an Animation first")
local frame = assert(animation.frames[1], "Animation has no frames")
frame:export_png([[C:\tmp\dst-preview.png]], { max_dimension = 1024 })
```

## 路径约定

- 所有路径必须**绝对路径**
- Windows 推荐 Lua 长字符串：`[[C:\assets\file.png]]`（避免反斜杠转义）
- PNG 导出路径必须以 `.png` 结尾
- 序列导出目标目录必须**尚不存在**（宿主原子创建）
- `.dmt` 不能通过 `import_resources` 打开，须用 `tool:open_document`

## 常见陷阱

| 陷阱 | 说明 |
|---|---|
| 点号调方法 | 方法用冒号：`build:set_name(...)` |
| 改只读字段 | `build.version` / 集合直接赋值不允许 |
| Frame num vs 下标 | `symbol.frames[1]` 是第一项；`find(1)` 查 `num==1` |
| 删除后继续用 | `remove()` 后对象失效 |
| 正向遍历中删除 | 倒序遍历或先存列表 |
| undo 混 Document 修改 | 同轮混用直接整轮失败 |
| 相对路径 | 全部 API 只接受绝对路径 |
| 序列目录已存在 | 必须用新目录名 |

## 与 Prefab 代码的衔接

DST Mod Tool 产出的资源最终要落到 mod 目录，被 prefab 引用：

```lua
-- prefab 中引用
local assets = {
    Asset("ANIM", "anim/gungnir.zip"),
    Asset("ANIM", "anim/swap_gungnir.zip"),
    Asset("ATLAS", "images/inventoryimages/gungnir.xml"),
    Asset("IMAGE", "images/inventoryimages/gungnir.tex"),
}

-- 装备时替换手持符号
local function onequip(inst, owner)
    owner.AnimState:OverrideSymbol("swap_object", "swap_gungnir", "swap_gungnir")
    owner.AnimState:Show("ARM_carry")
    owner.AnimState:Hide("ARM_normal")
end
```

工作流建议：
1. DST Mod Tool 中创作/编辑动画，导出预览自检
2. 导出/整理为 mod 目录下的 `anim/*.zip` 与 `images/inventoryimages/*`
3. 编写 prefab Lua 引用
4. 进游戏验收

## 完整 API 文档

工具内置完整指南，随时可查：

```powershell
& "D:\mods\DST Mod Tool.exe" script --help --lang zh-CN
```

内容覆盖：集合语义、Build/Bank 全 API、Element 仿射、Anti-Follow/Follow Symbol、查找替换、碰撞重算、裁剪比较、协议 v1 细节。
