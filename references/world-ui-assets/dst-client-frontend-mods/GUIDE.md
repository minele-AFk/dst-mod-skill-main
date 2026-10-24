---
name: dst-client-frontend-mods
description: Build Don't Starve Together client-only runtime mods and server-creation frontend extensions. Use when writing a client-only modmain.lua or modservercreationmain.lua, declaring client_only_mod, extending server-creation screens, adding local HUD helpers, reading client replicas, storing local configuration, or ensuring a mod never requires server-side installation.
---

# DST 纯客户端与建服前端模组

严格区分 FrontEnd、游戏客户端和服务器环境，只使用本地 UI、公开客户端数据或可选 RPC。

## 工作流

1. 确定功能属于游戏内客户端运行时还是建服前端，并证明它无需服务器权威状态。
2. 在 modinfo.lua 设置正确的 client_only_mod 与兼容标志；不要同时要求所有客户端安装。
3. 把普通客户端、HUD、输入和地图逻辑放入 modmain.lua，并延迟到玩家与 HUD 存在；只把服务器创建界面相关注册放入 modservercreationmain.lua。不要创建当前加载器不识别的 modfrontendmain.lua。
4. 只在 modworldgenmain.lua 注册世界预设、世界选项和生成内容；它虽会为配置界面部分加载，但不是通用主菜单入口。
5. 读取 Replica、网络变量或客户端已有数据；服务器未安装模组时不发送自定义 RPC。
6. 本地配置与服务器配置分开；通过当前入口实际提供的 PostConstruct API 小范围扩展 Screen 或 Widget，并为重建、返回主菜单和重连清理。
7. 分别测试加入无模组服务器、装有同模组服务器、启用时的建服界面部分加载、重连和禁用模组。

## 源码锚点

- mods.lua、modindex.lua：client_only_mod、modservercreationmain.lua 与前端部分加载。
- frontend.lua、screens/mainscreen.lua、screens/modsscreen.lua。
- screens/playerhud.lua、widgets/controls.lua。
- entityreplica.lua 与 components/*_replica.lua。

## 不变量

- 纯客户端模组不能依赖服务器 Component、自定义 Prefab 或服务器 RPC 必然存在。
- 前端阶段通常没有 TheWorld 和 ThePlayer。
- 不要修改影响服务器判定的本地值并宣称改变玩法。
- 加入服务器时客户端缺少数据必须优雅降级。

## 验证

- 服务器未安装该模组时仍能加入并使用允许的客户端功能。
- 返回主菜单和多次重连不残留 Widget 或输入处理器。
- 禁用模组后不要求服务器或存档迁移。

## 按需资源

- [frontend-assets-loadingtips.md](references/frontend-assets-loadingtips.md)：`FrontEndAssets`、`ReloadFrontEndAssets`、`PreloadAssets`、加载提示注册和 OTHER 分类权重。
