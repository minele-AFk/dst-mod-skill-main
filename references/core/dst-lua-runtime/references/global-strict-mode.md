---
name: dst-global-strict-mode
description: 饥荒 GLOBAL 严格模式（strict.lua）的全局变量读写规则与报错规避。处理 "variable not declared" / "assign to undeclared variable" 报错时使用。
---

# GLOBAL 严格模式：全局变量的读写规则

饥荒在全局表 `_G` 上挂了严格模式（[strict.lua](file:///d:/mods/scripts/strict.lua)），行为与普通 Lua 不同：普通 Lua 读未声明全局返回 `nil`，饥荒里**直接报错**。这是 mod 开发最常见的报错来源之一。

## 两条硬规则

**1. 读未声明的全局变量 → 报错**

```lua
print(foo)   -- variable 'foo' is not declared
```

注意：如果访问来自 C 代码则不受限（`debug.getinfo(2, "S").what ~= "C"` 才报错），所以很多引擎内部访问没问题。

**2. 函数内给未声明全局赋值 → 报错**

```lua
function init()
    foo = 1   -- assign to undeclared variable 'foo'
end
```

例外：**顶层（main chunk）赋值会自动声明**，不报错。

```lua
foo = 1  -- 顶层声明，合法
```

## 三种正确写法

**写法 A：先判断是否存在（用 rawget 绕过报错）**

```lua
if rawget(GLOBAL, "MakeInventoryFloatable") ~= nil then
    -- 该全局存在时才执行
end
```

**写法 B：函数内先声明再赋值（global()）**

```lua
function init()
    global("foo")   -- 声明，之后可正常读写
    foo = 1
end
```

**写法 C：顶层先置 nil 声明**

```lua
foo = nil  -- 顶层声明
function init()
    foo = 1
end
```

## 注意点

- mod 的入口环境（modmain 等）里 `GLOBAL` 就是 `_G`，严格模式同样生效；不要以为"用了 GLOBAL 就豁免"。
- 判断某个全局是否存在时，务必用 `rawget(GLOBAL, name)` 而非 `GLOBAL.name`（后者未声明会直接报错）。
- 局部变量不受严格模式影响，能用局部就用局部。
