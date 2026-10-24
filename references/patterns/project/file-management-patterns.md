# 文件管理模式

当任务涉及mod项目的整体文件结构、Prefab注册管理、命名规范或代码组织时使用本文件。

## 一、目录结构设计

### 官方推荐结构

```
modname/
├── modmain.lua                    -- 入口文件（必需）
├── modinfo.lua                    -- mod信息配置
├── scripts/
│   ├── prefabs/                   -- 预制件定义
│   ├── components/                -- 自定义组件
│   ├── brains/                    -- AI大脑
│   ├── stategraphs/               -- 状态机
│   ├── behaviours/                -- 行为节点
│   ├── widgets/                   -- UI组件
│   ├── utils/                     -- 工具函数
│   └── config/                    -- 配置文件
├── anim/                          -- 动画文件(.zip)
├── build/                         -- 建造图片
├── images/
│   ├── avatars/                   -- 角色头像
│   └── inventoryimages/           -- 物品栏图标
├── bigportraits/                  -- 角色大头像
├── fx/                            -- 特效文件
├── strings.lua                    -- 本地化字符串
└── modicon.tex/modicon.xml        -- mod图标
```

### 按功能分类的子目录

当文件数量超过20-30个时，应按功能分组到子目录：

```
scripts/prefabs/
├── character/                     -- 角色预制件
│   └── sora.lua
├── weapons/                       -- 武器预制件
│   ├── sora2sword.lua
│   └── sora3sword.lua
├── armor/                         -- 护甲预制件
│   ├── sora2amulet.lua
│   └── sora2armor.lua
├── containers/                    -- 容器预制件
│   ├── sora2chest.lua
│   └── sora2birdchest.lua
└── plants/                        -- 植物预制件
    └── sora_plant.lua

scripts/components/
├── buff/                          -- Buff系统组件
│   └── sorabuffs.lua
├── container/                     -- 容器相关组件
│   └── soracontainer.lua
├── data/                          -- 数据管理组件
│   ├── sorasave.lua
│   └── soraplayers.lua
└── ui/                            -- UI相关组件
    └── sorahud.lua

anim/
├── character/                     -- 角色动画
├── weapons/                       -- 武器动画
├── armor/                         -- 护甲动画
├── containers/                    -- 容器动画
└── effects/                       -- 特效动画
```

### 配置与代码分离

使用专门的配置目录，配置文件只存数据，不存逻辑：

```
scripts/config/
├── config.lua                     -- 主配置
├── sorabase.lua                   -- 基础配置
├── soracaneat.lua                 -- 可食用配置
└── soralevelup.lua                -- 升级配置
```

## 二、Prefab注册管理

### 集中式注册（官方推荐）

将所有Prefab集中在一个地方注册，便于追踪和维护：

```lua
PrefabFiles = {
    -- 角色
    "sora",
    
    -- 武器
    "sora2sword",
    "sora3sword",
    
    -- 容器
    "sora2chest",
    "sora2birdchest",
    
    -- 物品
    "sorapocky",
    "sorarepairer",
}
```

### 支持条件注册

根据配置动态决定是否加载某些Prefab：

```lua
if GetModConfigData("enable_new_feature") then
    table.insert(PrefabFiles, "new_feature_prefab")
end
```

### 使用批量添加函数

减少重复的 `table.insert` 调用：

```lua
local function AddPrefabs(list)
    for _, prefab in ipairs(list) do
        table.insert(PrefabFiles, prefab)
    end
end

AddPrefabs({"sora2sword", "sora3sword"})
```

### 分散式注册（各有利弊）

分散式注册通过 `AddPreFile` 等函数在多个文件中注册Prefab：

```lua
-- modmain.lua
PrefabFiles = {"sora", "sorapocky"}
function AddPreFile(str) table.insert(PrefabFiles, str) end

-- 其他文件中调用
AddPreFile("sora2birdchest")
AddPreFile("sora3chest")
AddPreFile("sora_tqy")
```

#### 分散注册的优点

1. **扩展性好**：新增模块时，不需要修改 `modmain.lua` 的主列表，只需在适当位置调用 `AddPreFile`
2. **支持条件注册**：可以根据配置动态决定是否加载某些prefab
3. **搜索可追踪**：在IDE中搜索 `AddPreFile("xxx")` 可以快速定位注册点
4. **逻辑分组**：可以按功能模块分组注册，便于理解代码结构

#### 分散注册的实际工作方式

在饥荒mod中，**注册**和**实现**是分开的：

- **注册**：在 `modmain.lua` 中通过 `PrefabFiles` 或 `AddPreFile` 声明要加载的prefab文件名
- **实现**：在 `scripts/prefabs/xxx.lua` 中定义prefab的构造函数

分散注册的 `AddPreFile` 调用通常还是在 `modmain.lua` 中，只是分散在不同的位置，而不是和实现代码放在一起：

```lua
-- modmain.lua
PrefabFiles = {"sora"}
function AddPreFile(str) table.insert(PrefabFiles, str) end

-- ...其他代码...

-- 分散注册（还是在modmain.lua中，只是位置分散）
AddPreFile("sora2birdchest")
AddPreFile("sora3chest")
```

#### 分散注册的缺点

1. **缺乏全局视图**：想知道"这个mod总共注册了哪些prefab"时，需要搜索整个代码库
2. **注册顺序不可控**：`table.insert` 是追加到数组末尾，无法控制加载顺序
3. **可能重复注册**：如果两个文件都调用了 `AddPreFile("same_prefab")`，会导致重复
4. **调试困难**：当prefab加载失败时，需要排查多个注册点

#### 适用场景

| 场景 | 是否适合分散注册 | 理由 |
|------|-----------------|------|
| 小型mod（<10个prefab） | ✅ 适合 | 简单，就近管理 |
| 中型mod（10-50个prefab） | ⚠️ 谨慎使用 | 建议混合模式 |
| 大型mod（>50个prefab） | ❌ 不适合 | 需要全局视图 |
| 需要条件注册 | ✅ 适合 | 条件逻辑可以就近处理 |

### 使用配置文件管理Prefab列表

对于大型mod，可以将Prefab列表放在配置文件中：

> 以下为字段、公式、多文件或项目占位示意，不能作为独立 Lua 文件直接运行；实现时补齐上下文并核对相应合同。

```text
-- config/prefabs.lua
return {
    character = {"sora"},
    weapons = {"sora2sword", "sora3sword"},
    containers = {"sora2chest", "sora2birdchest"},
}

-- modmain.lua
local prefab_config = require("config/prefabs")
PrefabFiles = {}
for _, prefabs in pairs(prefab_config) do
    for _, prefab in ipairs(prefabs) do
        table.insert(PrefabFiles, prefab)
    end
end
```

## 三、命名规范

### 使用英文或中文全拼

**推荐**：使用清晰的英文或中文全拼命名：

```
✅ sora_sword.lua           -- 英文
✅ sora_container.lua       -- 英文
✅ sora_buff_system.lua     -- 英文
✅ sora_tongqunyi.lua       -- 中文全拼
```

**不推荐**：使用拼音缩写，含义不明：

```
❌ sora_tqy.lua             -- 含义不明
❌ sora_lyj.lua             -- 含义不明
❌ sora_sby.lua             -- 含义不明
```

### 版本号前缀

使用版本号前缀区分不同版本的物品：

```
✅ sora2sword.lua           -- 第二代剑
✅ sora3sword.lua           -- 第三代剑
✅ sora2chest.lua           -- 第二代宝箱
```

### 文件与功能对应

一个文件一个功能，避免巨型文件（超过500行考虑拆分）：

```
✅ sora2buff.lua            -- 只包含Buff相关逻辑
❌ sora2_all_in_one.lua     -- 包含太多功能，难以维护
```

### 避免命名混淆

```
❌ sora2buffer.lua          -- Buffer是计算机术语，容易误解
✅ sora2debuff.lua          -- 明确是Debuff系统
```

## 四、组件管理

### 单一职责原则

每个组件只负责一个功能：

```
✅ sorabuffs.lua            -- 只负责Buff系统
✅ soracontainer.lua        -- 只负责容器系统
✅ sorapacker.lua           -- 只负责打包系统
```

### 组件间通过事件通信

避免组件间直接依赖，通过事件解耦：

```lua
-- ❌ 不推荐：组件A直接调用组件B
function ComponentA:DoSomething()
    self.inst.components.componentB:DoAction()
end

-- ✅ 推荐：通过事件通信
function ComponentA:DoSomething()
    self.inst:PushEvent("componenta_do_something")
end

-- ComponentB监听事件
inst:ListenForEvent("componenta_do_something", function()
    inst.components.componentB:DoAction()
end)
```

### 支持启用/禁用

```lua
function MyComponent:Enable()
    self.enabled = true
end

function MyComponent:Disable()
    self.enabled = false
end
```

## 五、热更新与维护

### 热更新系统

支持不重启游戏更新代码，备份旧版本，支持回滚：

```
scripts/soraupdate/
├── main.lua                 -- 热更新入口
├── patch_0.lua              -- 补丁管理
└── manager.lua              -- 更新管理器
```

### 版本控制

使用Git管理，定期提交，有意义的提交信息：

```
git commit -m "feat: 添加物理伤害转真伤组件"
git commit -m "fix: 修复技能冷却时间计算错误"
git commit -m "refactor: 重构Prefab注册逻辑"
```

### 文档维护

- 添加 `README.md` 说明mod功能
- 添加 `docs/` 目录存放架构文档
- 每个组件和Prefab添加注释说明

## 六、常见陷阱

### 1. 不要分散注册Prefab

分散注册会导致难以追踪所有注册点，建议集中管理。

### 2. 不要用拼音缩写命名

拼音缩写对非作者不友好，难以理解含义。

### 3. 不要平铺大量文件

当文件数量超过20-30个时，应按功能分类到子目录。

### 4. 不要让组件做太多事情

一个组件做太多事情会导致难以复用和测试。

### 5. 不要忽略文档

代码写得再好，没有文档也难以维护。

## 七、快速路由

- "我的Prefab没有加载？"
  - 检查 `PrefabFiles` 是否注册
- "文件太多找不到？"
  - 按功能分类到子目录
- "命名不清晰？"
  - 使用英文或中文全拼
- "组件职责不清？"
  - 遵循单一职责原则
- "如何管理大量Prefab？"
  - 使用配置文件或批量添加函数
