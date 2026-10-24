---
name: dst-dedicated-server-testing
description: Set up and test Don't Starve Together mods on dedicated servers and multi-shard clusters. Use when validating server-only and all-client mods, Master and Caves shards, modoverrides and workshop setup, startup and shutdown logs, remote-client behavior, reconnects, rollbacks, or failures that do not reproduce in hosted games.
---

# DST 专用服务器与多分片测试

把 Master、Caves、远端客户端和模组安装视为独立进程，记录每端日志与配置。

## 工作流

1. 确认 Cluster、Master、Caves、modoverrides.lua、dedicated_server_mods_setup.lua 和模组目录的实际位置，不覆盖现有服务器配置。
2. 核对 modinfo 的 client_only_mod、all_clients_require_mod、版本和依赖是否符合纯客户端、全客户端必装或客户端可不安装的服务器部署方式；不要依赖当前加载器不识别的 server_only_mod。
3. 备份目标测试 Cluster；使用独立测试世界和端口启动 Master，再启动 Caves，保存完整启动日志。
4. 从远端客户端加入，验证握手、资源、Prefab、RPC、Replica、角色和 UI，而不是只观察服务器控制台。
5. 执行建新世界、保存、重启、洞穴往返、断线重连、回滚、空服务器运行和版本不一致场景。
6. 分别检查 Master、Caves 和客户端的第一条错误与关闭顺序。
7. 只在用户明确要求时修改实际生产 Cluster 或发布配置。

## 源码锚点

- networking.lua：StartDedicatedServer、客户端连接与重置。
- shardnetworking.lua、shardindex.lua：多分片。
- mods.lua、modindex.lua：服务器模组加载和版本。
- serverpreferences.lua、worldsettingsutil.lua。

## 不变量

- 不要把本地主机测试等同于专服测试。
- 不要在未经确认的生产 Cluster 上回滚、再生世界或改配置。
- 令牌、cluster_token、密码和用户数据不得写入 Skill、日志摘要或提交。
- 每个进程的日志和时间戳分别保存，避免混淆根因。

## 验证

- Master、Caves 和至少一个远端客户端完成目标测试。
- 关服重启和回滚后状态一致。
- 报告明确列出实际执行命令、环境、日志结果和未执行项。
