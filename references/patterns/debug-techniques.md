# Debug Techniques：闭包与 upvalue 定点修补

需要修改一个闭包捕获的内部 helper，且普通 Hook/PostInit 不足时读取。本页只处理 Lua debug 库边界；日志和官方控制台检查统一见 [调试专题](../core/dst-debugging-testing/GUIDE.md) 与 [控制台命令](../core/dst-debugging-testing/references/console-commands.md)。

## 选择暴露点

先从已授权的目标源码理解运行端、调用者和闭包归属，检查常规 mod API、post-init 或较小覆写点。比如 onxxxfn 捕获局部 bar，外部无法直接替换 bar 时，可调查 upvalue。不是所有同名函数都来自同一个闭包；确认实际被调用的函数对象。

- `debug.getupvalue(f, index)` / `debug.setupvalue(f, index, value)`：访问捕获的外层变量。
- `debug.getlocal` / `debug.setlocal`：访问调用栈帧的局部变量；需要正确线程、栈层和存活调用帧，不是任意捕获变量的替代入口。

upvalue 名称/索引不是稳定公共 API；不存在目标时停止并报告，不循环猜索引。

## 有限查找、类型检查与有条件回退

下面为 Lua 辅助函数，不自动寻找任何官方目标，也不自动执行 patch。调用者传入已经核实的 target 函数、upvalue 名称与 replacement。返回 undo 或 nil/error。

```lua
local function ReplaceFunctionUpvalue(target, wanted, replacement)
    if type(target) ~= "function" or type(wanted) ~= "string"
        or type(replacement) ~= "function" then
        return nil, "invalid patch arguments"
    end
    local index = 1
    while true do
        local name, original = debug.getupvalue(target, index)
        if name == nil then
            return nil, "upvalue not found: " .. wanted
        end
        if name == wanted then
            if type(original) ~= "function" then
                return nil, "upvalue is not a function: " .. wanted
            end
            debug.setupvalue(target, index, replacement)
            local patched_index = index
            local function undo()
                local current_name, current = debug.getupvalue(target, patched_index)
                if current_name ~= wanted or current ~= replacement then
                    return false, "upvalue changed after patch"
                end
                debug.setupvalue(target, patched_index, original)
                return true
            end
            return undo
        end
        index = index + 1
    end
end
```

replacement 自己维护参数与返回值合同；需要包装原函数时，在确认其值后构造包装器，不因拿到名字就吞掉原返回值。

## 兼容性与退出

多个闭包可能共享同一个 upvalue cell，更改可能影响不止一个入口。逐个核对使用者和加载时机，防止重复包裹。undo 仅在当前值仍是本次 replacement 时恢复，避免覆盖后来其他修改。

记录目标模块/函数、upvalue 名、来源版本、运行端、替换责任与撤销条件。游戏更新后重新定位；语法通过不证明 closure 布局和实际行为。验证目标存在、缺失、类型不符、重复 patch、他人后续修改与撤销路径；本次未运行游戏中的闭包 patch。
