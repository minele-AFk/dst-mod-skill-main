---
name: dst-userdata-method-extension
description: 引擎 userdata 的方法定位、共享索引表与兼容包装；不把方法名反射当作签名证据。
---

# userdata：引擎对象的方法查看与扩展

> 复核：2026-10-18。本机 `scripts/debugsounds.lua` 可见 SoundEmitter 方法表的包装调用；原生实现仍不在 Lua 源码包中。

TheNet、TheSim、AnimState 等引擎对象不要直接当普通 table 遍历。先检查实际类型与运行环境；全局名字、实例与方法表是不同对象，前端/世界加载阶段也可能不同。

## 查看可访问的方法表

下面只在元表确实可见且 __index 为 table 时列出名称。受保护的元表或函数型 __index 不适用；不能承诺枚举出全部引擎 API。

```lua
local function InspectMethodTable(object)
    local mt = getmetatable(object)
    local index = type(mt) == "table" and rawget(mt, "__index") or nil
    if type(index) ~= "table" then
        return false
    end
    for name, value in pairs(index) do
        if type(value) == "function" then
            print(name)
        end
    end
    return true
end
```

枚举得到的名称没有说明参数、返回值、网络同步或可调用时机。继续查同类官方 Lua 调用点与上下文，按任务实测；不要通过名字推断未证实的行为。

## 优先使用项目自己的辅助函数

单个项目的动画组合可以作为普通函数，避免污染共享引擎方法表：

```lua
local function PlayAndPush(animstate, first, nextanim, loop)
    animstate:PlayAnimation(first)
    animstate:PushAnimation(nextanim, loop == true)
end
```

这是自定义 helper，first/nextanim 必须存在于当前 bank，不能称为内置 AnimState:PlayAndPush。

## 必须包装时保持合同与所有权

官方 debugsounds.lua 展示 SoundEmitter.PlaySound 的全局包装方式。是否能使用某方法表仍应在目标环境检查。以下为通用结构，只允许实际 table 和已存在的函数；不是让所有 Mod 都包装引擎方法：

```lua
local function WrapMethod(methods, name, before)
    assert(type(methods) == "table")
    local original = methods[name]
    assert(type(original) == "function")
    local wrapper = function(self, ...)
        before(self, ...)
        return original(self, ...)
    end
    methods[name] = wrapper
    return function()
        if methods[name] == wrapper then
            methods[name] = original
            return true
        end
        return false
    end
end
```

- 原函数用相同 self 与全部参数调用，直接 return 保留全部返回值。需要处理调用后的结果时还要保持 nil 和数量，不用普通表长度猜返回个数。
- before 应小而确定；若它抛错，原调用不会执行。不要默认吞掉错误改变原接口的异常语义。
- 恢复只在当前槽位仍指向自己的 wrapper 时进行；若已有别人包装，不覆盖回旧函数。重复加载也要有项目级防重策略。
- 修改共享方法表会影响所有使用者，优先缩小到目标 Prefab/组件的 hook；需考虑其他 Mod 的包装顺序。

相关：`scripts/debugsounds.lua`、`scripts/postprocesseffects.lua` 与 [Hook 专题](../GUIDE.md)。静态看到调用方式不等于证明所有原生绑定支持同样的扩展。
