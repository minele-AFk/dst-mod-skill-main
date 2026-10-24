---
name: dst-workshop-release
description: Prepare and release Don't Starve Together mods to Steam Workshop or server distributions. Use when finalizing mod metadata, semantic version and compatibility ranges, dependencies, preview assets, manifests, changelogs, dedicated-server installation, release checks, or performing a user-authorized publish or update.
---

# DST Workshop 发布

先产出可复现的候选包并完成本地与专服验证；发布是需要用户明确授权的外部写操作。

## 工作流

发布前先过 [release-checklist.md](../../testing/release-checklist.md)（代码/资产/数值/功能/打包逐项自检），再执行：

1. 检查 modinfo.lua 的名称、描述、作者、版本、兼容版本、api_version、依赖、客户端/服务器标志和配置默认值。
2. 确认目录不包含存档、日志、令牌、缓存、源工程垃圾或未授权资源；保留运行所需编译产物。
3. 从干净环境启用候选版本，执行主机、远端客户端、专服、洞穴和保存升级测试。
4. 核对 Workshop ID、预览图、依赖列表、服务器安装脚本和旧版本兼容策略。
5. 编写面向用户的变更摘要、破坏性变更、配置迁移和回滚说明。
6. 在发布前展示将上传的目录、版本和目标条目，取得用户明确确认后才调用外部发布工具。
7. 发布后重新下载或让干净客户端获取条目，验证实际分发内容与版本。

## 源码锚点

- modindex.lua、mods.lua：版本、依赖、manifest 与兼容检查。
- modinfo.lua 和本地发布工具生成的配置。
- 专服的模组安装与 modoverrides 配置。

## 不变量

- 没有用户明确授权不得创建、更新或公开 Workshop 条目。
- 不得上传令牌、私密配置、玩家数据或第三方未授权资产。
- 不要把本地成功描述为 Workshop 分发已验证。
- 破坏存档兼容的版本必须显式标记并提供迁移或回退方案。

## 验证

- 候选目录与实际发布目录内容一致。
- 全新订阅客户端和专服能获得依赖并启动。
- 发布版本、兼容范围和用户可见说明相互一致。
