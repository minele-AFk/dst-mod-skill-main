# 用户命令与投票

本页说明 `AddUserCommand` 的客户端/服务器分工、权限和投票边界。依据当前安装版 `modutil.lua`、`usercommands.lua`、`builtinusercommands.lua`、`networking.lua` 与 `mods.lua`；游戏更新后重新核对。

## 1. 定义命令

```lua
-- modmain.lua
AddUserCommand("mymod_home", {
    aliases = { "home" },
    prettyname = "回家",
    desc = "传送回出生点。",
    permission = COMMAND_PERMISSION.USER,
    slash = true,
    usermenu = false,
    servermenu = true,
    menusort = 10,
    params = {},
    vote = false,
    serverfn = function(params, caller)
        -- caller 可能是客户端信息表，不能直接当作 EntityScript。
        if caller == nil or caller.IsValid == nil or not caller:IsValid() then
            return
        end
        -- 这里重新校验玩家、目标、距离、冷却和权限。
    end,
})
```

- `localfn` 只在发起者的客户端执行，适合本地 UI 或表现；改变世界状态的逻辑必须放 `serverfn`。
- `serverfn` 在服务器执行。`caller` 可能是 `Ents[guid]`，玩家不在世界中时也可能是 `TheNet:GetClientTableForUser(userid)` 返回的表；不要直接 `caller:IsValid()` 而不做类型判断。
- 命令名和别名用 `smallhash` 保存，必须加模组前缀，避免与内置命令或其他模组冲突。
- `params` 按顺序命名，`paramsoptional` 标记可省略参数，多出的词拼成 `params.rest`；`params.user` 会被解析为目标玩家。
- `hasaccessfn(command, caller, targetid)` 控制可见与可用；`canstartfn` 返回 `false, reason` 时显示为禁用。
- `confirm = true` 会让客户端先弹确认框。

## 2. 执行流程

1. 客户端在聊天框输入 `/命令`，或在菜单点击。
2. `getexectype` 依次检查 `hasaccessfn`、`permission`、`canstartfn`、投票状态等，得到 ALLOW、VOTE、DENY、DISABLED 或 INVALID。
3. ALLOW 时客户端执行 `localfn`；存在 `serverfn` 时通过 `TheNet:SendSlashCmdToServer` 发送命令文本。
4. 服务器由 `Networking_SlashCmd` 再解析一次命令并再检查权限，然后执行 `serverfn(params, caller)`。
5. 投票通过时，`localfn` 和 `serverfn` 都可能在服务器执行，且 `caller` 可能为 nil；处理函数必须支持该路径。

客户端必须能找到命令定义才会解析并发送。只安装在服务器上的模组，客户端输入的 `/命令` 很可能根本发不到服务器；如果功能依赖客户端入口，需要让客户端也加载对应定义，或改走已有 RPC/动作链并明确权限边界。

## 3. 投票

投票命令仍用 `AddUserCommand` 定义，并在数据表中设置 `vote = true`、`votetimeout`、`voteminstartage`、`voteminpasscount`、`voteresultfn` 等字段。需要 `worldvoter` 和 `playervoter` 组件支持。

`AddVoteCommand` 当前只把数据写入模组环境的 `vote_commands`，而 `ModWrangler:GetVoteCommands()` 在当前脚本中没有实际消费者。新代码不要使用它；看到旧代码调用时，应检查其投票功能是否实际生效。

## 4. 安全与验证

- 服务端最终校验玩家身份、目标、距离、权限、冷却和参数范围。
- 客户端菜单可用只是视图，不构成授权。
- 测试主机、远端客户端、专服、玩家不在世界中、目标掉线、重复输入和投票通过/失败。
- 命令名、别名和参数变化时检查旧客户端缓存与重连行为。

本页于 2026-10-22 对照安装版 `usercommands.lua:339-343,418-474,516`、`modutil.lua:928-940` 与 `mods.lua:900`；未执行真实聊天命令、投票或远端客户端测试。
