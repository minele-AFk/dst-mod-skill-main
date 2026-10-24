---
name: dst-mod-scaffolding
description: Create and organize Don't Starve Together mod skeletons. Use when starting a mod, writing modinfo.lua, modmain.lua, modworldgenmain.lua, or modservercreationmain.lua, defining configuration options and compatibility flags, registering assets and prefabs, or correcting a broken mod layout.
---

# DST 模组脚手架

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

从最小可加载结构开始，根据运行上下文逐步加入入口、配置、资源和依赖。

## 工作流

1. 确认目标是客户端可不安装的服务器模组、所有客户端必装模组、纯客户端模组、世界生成模组还是建服前端扩展。
2. 从 assets/minimal-mod/ 复制最小模板，只创建任务真正需要的入口和目录。
3. 填写 modinfo.lua 的名称、描述、作者、版本、api_version、dst_compatible、客户端/服务器标志和 configuration_options。
4. 在 modmain.lua 用明确 GLOBAL 局部引用读取游戏全局，声明 PrefabFiles、Assets、配置与普通运行时钩子；把世界生成注册放入 modworldgenmain.lua，把建服界面注册放入 modservercreationmain.lua。
5. 用 require 加载返回值模块；用 modimport 执行依赖 AddAction、PostInit 等模组环境 API 的注册文件。require 模块直接使用游戏全局，modimport 文件才沿用入口的模组环境。
6. 验证资源路径、Prefab 名称、配置数据类型、依赖关系和服务器过滤标记。
7. 以无缓存重启方式分别测试禁用、启用、改配置、建新世界和载入旧世界。

## 源码锚点

- mods.lua、modindex.lua：入口加载、modinfo 校验、优先级和依赖。
- modutil.lua：GetModConfigData、Prefab、Asset 及各类 Add 开头的公开 API。
- mods.lua、frontend.lua、worldgen_main.lua：建服前端的部分加载与世界生成上下文。

## 不变量

- 环境代理是可选风格，不是必需初始化。优先 local G = GLOBAL；若项目已有代理，先检查其元表，不无条件替换 __index。

- 不要同时声明互斥的 client_only_mod 与 all_clients_require_mod。
- 不要在 modinfo.lua 执行游戏运行时逻辑。
- 不要为未使用的资源、Prefab 或入口添加占位声明。
- 保留已有用户文件和配置；扩展现有模组前先读取其结构。

## 验证

- 游戏能读取 modinfo 且模组列表无错误。
- 目标运行上下文只加载需要的入口。
- 所有配置选项在默认值和非默认值下均能启动。

## 按需资源

- 复制 assets/minimal-mod/ 创建新模组（modinfo.lua + modmain.lua 最小模板：一个布尔配置与明确入口边界）。
- 需要物品/建筑 prefab 骨架模板时复制 dst-prefab-authoring/assets/ 下的 item-template.lua / building-template.lua。
- 需要入口和兼容标志说明时读取 [entrypoints.md](references/entrypoints.md)。
- 需要模组入口 API、上下文、网络方向和最小结构时读取 [modmain-api-reference.md](references/modmain-api-reference.md)。
- 需要大型 mod 模块化工程（多子 mod 加载器 / 全局框架命名空间 / KV 存档 / RPC 封装 / 客户端数据桥 / 自适应定时器 / 野生生成器 / 图鉴 UI）时查阅 `references/mod-notes/` 下 [mod-wanwushu.md](../../mod-notes/mod-wanwushu.md)（万物书原始笔记，含完整实现/数值/题材）。
