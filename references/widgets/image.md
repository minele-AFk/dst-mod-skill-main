# `Image` Widget

> 适用版本：API 10+
> 最后更新：2026-07-12

当任务涉及显示图片、图标、纹理时，使用此Widget。

官方源码：

- `scripts/widgets/image.lua`

高频方法：

- `SetTexture(atlas, tex, default_tex)`
- `SetMouseOverTexture(atlas, tex)`
- `SetDisabledTexture(atlas, tex)`
- `SetSize(w, h)`
- `GetSize()`
- `ScaleToSize(w, h)`
- `SetTint(r, g, b, a)`
- `SetFadeAlpha(a, skipChildren)`
- `SetEffect(filename)`

常见搭配：

- `Image` + `Widget`（作为子节点）
- `Image` + `Button`（作为按钮背景）
- `Image` + `Screen`（作为屏幕背景）

常见陷阱：

- 图片路径需要使用TEX文件格式。
- Atlas和Texture参数顺序不能颠倒。

---

## 创建Image

```lua
local image = parent:AddChild(Image("images/hud/my_icon.tex"))
```

使用Atlas：

```lua
local image = parent:AddChild(Image("images/hud/hud.xml", "my_icon.tex"))
```

---

## 设置纹理

### 基础纹理

```lua
image:SetTexture("images/hud/my_icon.tex")
```

### 使用Atlas

```lua
image:SetTexture("images/hud/hud.xml", "my_icon.tex")
```

### 鼠标悬停纹理

```lua
image:SetMouseOverTexture("images/hud/hud.xml", "my_icon_hover.tex")
```

### 禁用纹理

```lua
image:SetDisabledTexture("images/hud/hud.xml", "my_icon_disabled.tex")
```

---

## 尺寸控制

### 设置尺寸

```lua
image:SetSize(64, 64)
```

### 获取尺寸

```lua
local w, h = image:GetSize()
```

### 缩放到指定尺寸

```lua
image:ScaleToSize(100, 100)
```

---

## 颜色和透明度

### 设置颜色

```lua
image:SetTint(1, 1, 1, 1)
```

参数：r, g, b, a（0-1）

### 设置透明度

```lua
image:SetFadeAlpha(0.5)
```

---

## 效果

### 设置效果

```lua
image:SetEffect("shaders/ui_effects.xml", "glow")
```

### 设置效果参数

```lua
image:SetEffectParams(1, 0.5, 0, 0)
```

---

## 实战示例

### 示例1：创建图标

```lua
local icon = self.root:AddChild(Image("images/hud/skill_icon.tex"))
icon:SetSize(48, 48)
icon:SetPosition(0, 0)
icon:SetTint(1, 1, 1, 0.8)
```

### 示例2：创建按钮背景

```lua
local bg = self.button:AddChild(Image("images/hud/button_bg.tex"))
bg:SetSize(200, 50)
bg:SetTint(0.8, 0.8, 0.8, 1)
```

---

## 注意事项

1. **资源路径**：使用相对路径，从mod根目录开始
2. **Atlas优先**：使用Atlas可以减少draw call
3. **内存管理**：不需要的Image应该及时移除