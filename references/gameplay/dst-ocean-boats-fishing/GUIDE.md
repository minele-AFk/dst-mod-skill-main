---
name: dst-ocean-boats-fishing
description: Implement Don't Starve Together ocean gameplay, boats, platforms, rowing, sailing, leaks, ocean fishing, tackle, trawlers, and platform-aware actions. Use when working with boatphysics, boat components and stategraphs, oceanfishingrod, hooks and lures, platform-relative coordinates, water placement, or ocean world generation.
---

# DST 海洋、船与海钓

把船视为移动平台，所有位置、动作、投射物和碰撞都明确使用世界或平台相对坐标。

## 工作流

1. 区分海洋地形生成、船平台运行时、航行动力、船损坏和海钓五类职责。
2. 对照 boat Prefab、SGboat 和 boatphysics 组件建立 Network、物理、平台、漏洞和乘员逻辑。
3. 涉及平台时追踪 GetCurrentPlatform 与平台相对坐标转换，避免世界坐标直接复用。
4. 航行、划船、转向、锚和帆由服务器结算动力，客户端复制表现和输入预测。
5. 海钓按 oceanfishable、oceanfishingrod、hook、tackle 与鱼 Brain/SG 组合实现拉力和脱钩。
6. 船上放置、范围动作、投射物和 AoE 同时检查平台、海面和乘员安全。
7. 测试船靠岸、两船接近、洞穴水域、网络延迟、玩家落水、船毁和鱼竿中断。

## 源码锚点

- components/boatphysics.lua、boatcrew.lua、boatleak.lua、boatdrag.lua、boatrotator.lua。
- prefabs/boat.lua 及 boat、mast、anchor、oar 相关 Prefab。
- stategraphs/SGboat.lua 与玩家划船、钓鱼状态。
- components/oceanfishable.lua、oceanfishingrod.lua、oceanfishinghook.lua、oceanfishingtackle.lua。
- map/ocean_gen.lua：海洋世界生成。

## 不变量

- 平台相对坐标和世界坐标必须显式转换。
- 客户端输入不直接改变船耐久、动力或鱼的权威状态。
- 船移除时清理乘员引用、附着实体、漏洞和循环声音。
- 范围查询不可把另一艘船上的对象误判为同平台目标。

## 验证

- 主机与远端客户端看到相同船位置、转向和损坏状态。
- 靠岸、碰撞、船毁和落水路径不会卡住玩家或实体。
- 海钓开始、咬钩、收线、脱钩和中断均能复位组件与 SG。

