# deployable：预览与服务端部署

源码签名复核：2026-10-18，components/deployable.lua 与 inventoryitem_replica.lua。

## 真实接口与参数

| 接口 | 作用 |
|---|---|
| SetDeployMode(mode) / GetDeployMode() | 设置当前 DEPLOYMODE 枚举 |
| SetDeploySpacing(spacing) | 使用 DEPLOYSPACING 枚举，不把任意数字当世界半径 |
| SetUseGridPlacer(usegridplacer) | 网格预览策略 |
| DeploySpacingRadius() | 由 spacing 计算半径 |
| CanDeploy(pt, mouseover, deployer, rot) | 第二参是鼠标目标，不是 deployer |
| Deploy(pt, deployer, rot) | 执行前再次调用 CanDeploy |

没有通用 SetDeployAngle/SetDeployRadius，也不使用旧例虚构的 DEPLOYMODE.PLACER。常见模式有 DEFAULT、PLANT、WALL、WATER、TURF、CUSTOM；以当前 constants 与消费者为准。

## 两端自定义规则

需要自定义查询时，先检查公共初始化的 inst._custom_candeploy_fn(inst, pt, mouseover, deployer, rot)。当前主组件和 inventoryitem Replica 的 CUSTOM 分支都读取它；纯查询规则可由双方复用，避免全局修改 Replica。

服务端 ondeploy(inst, pt, deployer, rot) 负责业务效果。当前 Deploy 不读取 ondeploy 的返回值来决定成功；在回调末尾 return false 不能当可靠拒绝。真正的条件应在 CanDeploy 路径复查，成功创建结果后再按单件消费政策处理。

## 输入与生命周期

pt 是位置对象，船/平台坐标及旋转按当前同类原版检查。建筑占地、DEPLOYSPACING 和 Placer 图像是不同概念；预览合法不替代服务器拒绝逻辑。

不要只写 AddNetwork 后直接在所有端加权威组件；完整物品沿 Prefab 的公共区/SetPristine/主机装配。引用建筑示例可查 prefabs/walls.lua、treasurechest.lua；是否属于可部署物或制作建筑要另分管线。

## 验证与资源

检查远端预览、服务器拒绝、边缘阻挡、平台、旋转、单件消费与生成失败；未执行游戏验收。

- [建筑与物理](../../gameplay/dst-building-deployment-physics/GUIDE.md)
- [植物部署](../../gameplay/dst-plants-farming-regrowth/GUIDE.md)
