# `Grid` Widget

> 适用版本：API 10+
> 最后更新：2026-07-12

当任务涉及网格布局、物品排列、表格显示时，使用此Widget。

官方源码：

- `scripts/widgets/grid.lua`

高频方法：

- `SetSize(w, h)`
- `SetGridSize(cols, rows)`
- `GetGridSize()`
- `AddItem(item)`
- `RemoveItem(item)`
- `Clear()`
- `SetOnTileSelected(fn)`
- `SetTileSize(size)`

常见搭配：

- `Grid` + `Widget`（作为网格项）
- `Grid` + `Button`（可点击网格）
- `Grid` + `Image`（图标网格）

常见陷阱：

- 需要设置Grid大小和Tile大小才能正确显示。
- Grid项需要实现特定的接口。

---

## 创建Grid

```lua
local grid = parent:AddChild(Grid())
grid:SetSize(300, 200)
grid:SetGridSize(3, 2)
grid:SetTileSize(80)
```

---

## 设置网格

### 设置网格大小

```lua
grid:SetGridSize(3, 2)
```

参数：cols, rows

### 获取网格大小

```lua
local cols, rows = grid:GetGridSize()
```

### 设置Tile大小

```lua
grid:SetTileSize(80)
```

### 设置Grid尺寸

```lua
grid:SetSize(300, 200)
```

---

## 添加和移除项

### 添加项

```lua
local item = Widget("grid_item")
local icon = item:AddChild(Image("images/hud/item_icon.tex"))
icon:SetSize(64, 64)

grid:AddItem(item)
```

### 移除项

```lua
grid:RemoveItem(item)
```

### 清空网格

```lua
grid:Clear()
```

---

## 设置选中回调

```lua
grid:SetOnTileSelected(function(tile)
    print("选中了:", tile)
end)
```

---

## 实战示例

### 示例1：创建物品网格

```lua
local item_grid = self.root:AddChild(Grid())
item_grid:SetSize(400, 300)
item_grid:SetGridSize(4, 3)
item_grid:SetTileSize(80)

for i = 1, 12 do
    local item = Widget("item_" .. i)
    local icon = item:AddChild(Image("images/hud/item_" .. i .. ".tex"))
    icon:SetSize(64, 64)
    item_grid:AddItem(item)
end
```

---

## 注意事项

1. **Tile接口**：Grid项需要实现特定的接口才能被正确管理
2. **尺寸匹配**：Grid尺寸需要与Tile数量和大小匹配
3. **性能优化**：避免在Grid中添加过多项