# UI 图集注册

本页说明库存图、小地图、剪贴簿、技能树图标和角色技能树背景的注册方式。依据当前安装版 `simutil.lua`、`modutil.lua`、`prefabs/minimap.lua` 与相关 Widget 消费者；游戏更新后重新核对。

## 1. 库存物品图集

```lua
-- modmain.lua
RegisterInventoryItemAtlas("images/mymod_inventory.xml", "mymod_item")
```

- 第二参是查询键，通常使用 Prefab 名；图片元素名也建议与 Prefab 名一致，例如 `mymod_item.tex`。
- 当前查找缓存按图片名保存；同一个图片名重复注册到不同图集时会打印警告，但不会自动替换。
- 注册前确保 XML 和 `.tex` 已在 `Assets` 中声明，且路径能被当前加载阶段解析。
- 配方和库存 UI 通常通过 `GetInventoryItemAtlas(image)` 查找；如果元素名不是 Prefab 名，必须在配方或消费者中显式提供 `atlas`/`image`。

## 2. 小地图图集

小地图图标使用 `AddMinimapAtlas(atlaspath)` 注册，Prefab 侧通过 `MiniMapEntity:SetIcon("name.png")` 选择元素。当前 `prefabs/minimap.lua` 会遍历 `MinimapAtlases` 后逐个 `AddAtlas`。

- 元素名通常以 `.png` 结尾，不是 `.tex`。
- 角色小地图图标固定使用 `<character>.png`；可在 XML 中使用该名字，或改 `SetIcon`。
- 注册的是 Atlas 路径，不是单张图片；每个元素仍要存在于对应 XML/TEX 中。
- 当前内置小地图查找顺序是 `minimap/minimap_data1.xml` → `data2.xml` → `data3.xml`，之后才把 Mod 注册的 `MinimapAtlases` 添加到小地图渲染器。不要硬编码“原版只有两张图集”，也不要认为 `GetMinimapAtlas` 的内置查找会遍历 Mod 图集；Mod 图标仍通过 `AddMinimapAtlas` 注册，并由 `prefabs/minimap.lua` 加入渲染层。

## 3. 剪贴簿图标

```lua
RegisterScrapbookIconAtlas("images/mymod_scrapbook.xml", "mymod_item.tex")
```

- 第二参是图片元素名，通常带 `.tex`。
- 剪贴簿先查注册缓存，再查内置图集；未命中时可能回退到通用图标。
- 同一个图片名不要注册到多个图集；冲突时当前实现只打印警告并保留先注册值。
- 玩家附近的自动发现由 `player_common_extensions.lua` 查询 `TUNING.SCRAPBOOK_UPDATERADIUS` 内实体。当前查询只排除 `INLIMBO`，不再统一排除 `FX`，因此附近特效实体也可能进入发现流程；需要长期排除时使用实体字段 `scrapbook_ignore = true`，隐藏入口等原版对象会在需要时动态设置它。
- 没有剪贴簿数据、角色不在原版角色掩码或目标是未登记 Prefab 时，分区写入会安全 no-op，而不是抛错。图集注册成功也不代表该 Prefab 已有剪贴簿内容；资源、数据条目和发现行为要分别验证。

### 剪贴簿元数据字段

以下字段是当前版本的图鉴数据契约，旧提交中已经存在，不应误报成这次游戏更新新增的 API：

- `scrapbook_thingtype` 只在生成图鉴条目时覆盖自动分类，且 `pointofinterest` 组件优先。它属于图鉴分类元数据，不改变实体运行时 tag。
- `scrapbook_adddeps` / `scrapbook_removedeps` 只作用于 `d_createscrapbookdata` 生成的依赖列表，先补加、后删除，最后移除条目自身。它们不是配方、掉落或运行时依赖。
- `scrapbook_proxy` 让 `ScrapbookPartitions:RedirectThing` 把实体重定向到代理 Prefab 字符串，发现、查询和查看状态都走这个重定向。代理目标仍须已有登记数据，否则分区写入会安全 no-op。
- `scrapbook_inspectonseen` 只影响附近发现时的记录方式：当前发现循环对已死实体或带该字段的实体调用 `SetInspectedByCharacter`，普通实体调用 `SetSeenInGame`。它不替代 `inspectable`、health 或其他游戏组件。

这些字段用于描述“图鉴怎样记录和展示”，不能借它们实现物品配方、战斗数值或世界逻辑。修改 Prefab 后要分别验证图鉴数据生成、代理跳转、附近发现和图标加载。

## 4. 技能树图标与背景

```lua
RegisterSkilltreeIconsAtlas("images/mymod_skilltree_icons.xml", "mymod_skill.tex")
RegisterSkilltreeBGForCharacter("images/mymod_skilltree_bg.xml", "mychar")
```

- `RegisterSkilltreeIconsAtlas(atlas, tex)` 注册单个技能图标元素。
- `RegisterSkilltreeBGForCharacter(atlas, charactername)` 会拼出 `<charactername>_background.tex`，再调用背景图集注册。
- 背景 XML 中必须存在该元素名；角色名、Prefab 名和元素名不一致时，不能只改其中一个。
- 技能树 UI 通过 `GetSkilltreeIconAtlas` / `GetSkilltreeBG` 查找；缓存按图片名保存，重复注册会保留先注册图集并打印冲突。

## 5. 注册时机与缓存

- 注册函数应在相关 UI 创建和查询前执行，通常在 `modmain.lua` 加载阶段。
- 先声明 `Asset("ATLAS", xml)` 与 `Asset("IMAGE", tex)`，再注册；仅注册字符串不会加载文件。
- 注册缓存是进程内表，不会因为重新打开菜单自动刷新；修改资源后要重启或按实际重载路径验证。
- 图集 XML 的 `Texture filename` 是实际 TEX 路径，Element 名才是 UI 查询键；两者不必相同。

## 6. 验证清单

- 库存图、配方图、剪贴簿和小地图分别显示正确元素，不回退到通用图。
- `.xml`、`.tex` 和元素名三者一致，大小写和相对路径正确。
- 同名图片没有跨图集冲突；冲突日志能定位到具体注册者。
- 技能树图标和角色背景在首次打开、重连和换角色后仍正确。
- 远端客户端能看到相同图标，不只主机本地缓存命中。

本页于 2026-10-23 对照安装版 `simutil.lua:707-730`、`modutil.lua:511-515`、`prefabs/minimap.lua:44-51` 与相关消费者；未执行真实 UI 图集加载或远端客户端测试。
