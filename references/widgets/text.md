# `Text` Widget

> 适用版本：API 10+
> 最后更新：2026-07-12

当任务涉及显示文字、文本排版、字体设置时，使用此Widget。

官方源码：

- `scripts/widgets/text.lua`

高频方法：

- `SetString(str)`
- `GetString()`
- `SetFont(font)`
- `SetSize(sz)`
- `GetSize()`
- `SetColour(r, g, b, a)`
- `GetColour()`
- `SetRegionSize(w, h)`
- `SetMultilineTruncatedString(str, maxlines, maxwidth, ...)`
- `SetAutoSizingString(str, max_width, allow_scaling_up)`
- `SetVAlign(anchor)`
- `SetHAlign(anchor)`
- `EnableWordWrap(enable)`

常见搭配：

- `Text` + `Button`（按钮文字）
- `Text` + `Widget`（信息显示）
- `Text` + `Screen`（标题显示）

常见陷阱：

- 字体大小会影响文字的实际显示大小。
- 需要设置RegionSize才能正确换行。

---

## 创建Text

```lua
local text = parent:AddChild(Text(BODYTEXTFONT, 24))
text:SetString("Hello World")
text:SetColour(1, 1, 1, 1)
```

---

## 设置文本

### 设置字符串

```lua
text:SetString("这是一段文字")
```

### 获取字符串

```lua
local str = text:GetString()
```

### 设置多行截断字符串

```lua
text:SetMultilineTruncatedString("这是一段很长很长的文字", 2, 200, 50, true)
```

参数：str, maxlines, maxwidth, maxcharsperline, ellipses

### 设置自动调整大小

```lua
text:SetAutoSizingString("自动调整大小的文字", 300)
```

---

## 设置字体

### 设置字体类型

```lua
text:SetFont(BODYTEXTFONT)
text:SetFont(HEADERFONT)
text:SetFont(DIALOGFONT)
```

### 设置字体大小

```lua
text:SetSize(24)
```

### 获取字体大小

```lua
local sz = text:GetSize()
```

---

## 设置颜色

### 设置文字颜色

```lua
text:SetColour(1, 0, 0, 1)
```

参数：r, g, b, a（0-1）

### 获取文字颜色

```lua
local r, g, b, a = text:GetColour()
```

---

## 设置对齐

### 垂直对齐

```lua
text:SetVAlign(ANCHOR_TOP)
text:SetVAlign(ANCHOR_MIDDLE)
text:SetVAlign(ANCHOR_BOTTOM)
```

### 水平对齐

```lua
text:SetHAlign(ANCHOR_LEFT)
text:SetHAlign(ANCHOR_MIDDLE)
text:SetHAlign(ANCHOR_RIGHT)
```

---

## 设置区域大小

### 设置区域大小

```lua
text:SetRegionSize(200, 100)
```

### 获取区域大小

```lua
local w, h = text:GetRegionSize()
```

### 重置区域大小

```lua
text:ResetRegionSize()
```

---

## 换行

### 启用自动换行

```lua
text:EnableWordWrap(true)
```

### 启用空白换行

```lua
text:EnableWhitespaceWrap(true)
```

---

## 实战示例

### 示例1：创建标题文字

```lua
local title = self.root:AddChild(Text(HEADERFONT, 36))
title:SetString("游戏标题")
title:SetColour(1, 0.8, 0, 1)
title:SetHAlign(ANCHOR_MIDDLE)
title:SetPosition(0, 100)
```

### 示例2：创建多行描述

```lua
local desc = self.root:AddChild(Text(BODYTEXTFONT, 18))
desc:SetString("这是一段很长很长的描述文字，需要自动换行显示")
desc:SetRegionSize(300, 200)
desc:SetVAlign(ANCHOR_TOP)
desc:SetHAlign(ANCHOR_LEFT)
desc:EnableWordWrap(true)
```

---

## 注意事项

1. **字体资源**：字体文件需要正确注册
2. **性能优化**：避免频繁修改文字内容
3. **区域大小**：设置区域大小后文字会自动换行