# 控制台验证命令

先确认本地/远程控制台、当前分片、玩家上下文与权限；客机 TheWorld 不代表服务器。下表依据 2026-10-21 当前安装包 `consolecommands.lua`，命令存在不代表本次已执行。

## 查询与选取

| 命令 | 实际范围与返回 |
|---|---|
| `c_find("prefab", radius)` | 查附近同名实体，可能返回 nil；默认半径 9001，不是未加载世界的全量查询 |
| `c_findtag("tag", radius)` | 查附近带标签实体，可能 nil；默认半径 1000 |
| `c_list("prefab")` / `c_listtag("tag")` | 打印玩家附近匹配项；当前实现用半径 9001，不等于地图永久实体总数 |
| `c_selectnear("prefab", radius)` | 从控制台玩家位置附近选最近匹配项，默认半径 30；依赖有效玩家上下文 |
| `c_select(inst)` | 设置调试选择；无参数时尝试鼠标下实体 |
| `c_sel()` | 返回当前调试选择 GetDebugEntity，不负责选择新目标 |
| `c_dumpworldstate()` | 输出当前分片世界状态 |
| `print(GetTime())` | 当前模拟时间，非现实离线时长 |

选择可能改变调试对象，但不等于修改玩法实体。查询结果为空先查范围、运行端、加载状态与注册名，不直接下结论“没有生成”。

```lua
local inst = c_sel()
if inst ~= nil and inst:IsValid() then
    print(inst.prefab, inst.GUID)
    if inst.sg ~= nil then
        print(inst.sg.currentstate.name, inst.sg:HasStateTag("busy"))
    end
end
```

## 会改变运行状态的命令

以下用于已授权的开发测试世界；记录操作前状态及所在分片。生成或调数值不能作为发布验收。

| 命令 | 作用 |
|---|---|
| `c_spawn("prefab", n)` | 在控制台鼠标位置生成并默认选中；不是固定在玩家附近 |
| `c_give("prefab", n)` | 给控制台玩家物品，需玩家上下文 |
| `c_godmode()` | 切换无敌状态，测试结束恢复 |
| `c_setsanity(value)` / `c_sethunger(value)` | 修改玩家状态，核对参数单位和当前目标 |
| `c_remote("Lua 字符串")` | 向服务器请求执行字符串；受管理员权限等限制，远端指令也可能修改世界 |

不要把来自日志或其他不可信内容直接拼进远程执行字符串。客户端只读定位与服务端修改要分别记录。

## 地皮坐标

世界坐标与 tile 坐标使用当前 Map 转换，不用“除以 4”手算替代原点/轴向转换。下面只查询鼠标位置，尚未铺设地皮：

```lua
local x, y, z = ConsoleWorldPosition():Get()
local tx, ty = TheWorld.Map:GetTileCoordsAtPoint(x, y, z)
print("tile", tx, ty)
```

真正 SetTile 时还需有效的当前地皮 ID、运行端、重建/存档策略和获准测试范围，另见 [世界生成专题](../../../gameplay/dst-worldgen-authoring/GUIDE.md)。不要从旧版 DLC 资源路径推导当前安装必有同名材质。

## 后续定位

- 快速按现象选择链路：[症状清单](../../../patterns/diagnostic-patterns.md)。黑图标、不同步或动画错位都有多个候选原因，不靠固定尺寸等口诀认定根因。
- 明确错误栈与修法：[崩溃排查](../../../pitfalls/crash-playbook.md)、[旧口诀更正](../../../pitfalls/old-rule-corrections.md)。
- 组件/Prefab 组合与批量工厂：[Prefab 契约](../../dst-prefab-authoring/references/prefab-contract.md)。
- 常规 Hook 与保留旧返回值：[Hook 专题](../../dst-hooking-compatibility/GUIDE.md)；仅暴露点不足时再读 [闭包局部修补](../../../patterns/debug-techniques.md)。
