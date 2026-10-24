# `Button` Widget

> 适用版本：API 10+
> 最后更新：2026-07-12

当任务涉及按钮交互、点击事件、选择状态时，使用此Widget。

官方源码：

- `scripts/widgets/button.lua`

高频方法：

- `SetOnClick(fn)`
- `SetOnSelect(fn)`
- `SetOnUnselect(fn)`
- `SetText(msg, dropShadow, dropShadowOffset)`
- `GetText()`
- `SetFont(font)`
- `SetTextSize(sz)`
- `SetTextColour(r, g, b, a)`
- `Select()`
- `Unselect()`
- `IsSelected()`
- `SetControl(ctrl)`

常见搭配：

- `Button` + `Image`（自定义按钮外观）
- `Button` + `Text`（按钮文字）
- `Button` + `TabGroup`（标签页切换）

常见陷阱：

- 点击回调需要在服务端执行的逻辑要注意网络同步。
- `SetControl()` 需要传入正确的控制键。

---

## 创建Button

```lua
local button = parent:AddChild(Button())
button:SetText("点击我")
button:SetOnClick(function()
    print("按钮被点击")
end)
```

---

## 设置点击回调

### 点击事件

```lua
button:SetOnClick(function()
    -- 点击时执行
end)
```

### 选择事件

```lua
button:SetOnSelect(function()
    -- 选中时执行
end)

button:SetOnUnselect(function()
    -- 取消选中时执行
end)
```

### 按下事件

```lua
button:SetOnDown(function()
    -- 按下时执行
end)

button:SetWhileDown(function(dt)
    -- 按住时持续执行
end)
```

---

## 设置文字

### 设置文本

```lua
button:SetText("确定")
```

### 设置字体

```lua
button:SetFont(BODYTEXTFONT)
```

### 设置文字大小

```lua
button:SetTextSize(24)
```

### 设置文字颜色

```lua
button:SetTextColour(1, 1, 1, 1)
```

---

## 选择状态

### 选中

```lua
button:Select()
```

### 取消选中

```lua
button:Unselect()
```

### 检查是否选中

```lua
if button:IsSelected() then
    -- 已选中
end
```

---

## 设置控制键

```lua
button:SetControl(CONTROL_ACCEPT)
```

---

## 实战示例

### 示例1：创建确认按钮

```lua
local confirm_btn = self.root:AddChild(Button())
confirm_btn:SetText("确认")
confirm_btn:SetFont(BODYTEXTFONT)
confirm_btn:SetTextSize(20)
confirm_btn:SetOnClick(function()
    print("确认按钮被点击")
end)
confirm_btn:SetPosition(0, -50)
```

### 示例2：创建可选择按钮

```lua
local tab_btn = self.root:AddChild(Button())
tab_btn:SetText("标签1")
tab_btn:SetOnSelect(function()
    tab_btn:SetTextColour(1, 0, 0, 1)
end)
tab_btn:SetOnUnselect(function()
    tab_btn:SetTextColour(1, 1, 1, 1)
end)
```

---

## 注意事项

1. **回调优先级**：点击事件会在选择事件之前触发
2. **状态管理**：需要手动管理选中状态
3. **控制键冲突**：避免设置相同的控制键