---
name: dst-fx-vfx-authoring
description: Create Don't Starve Together visual effects and particles. Use when adding particle systems, light effects, screen shakes, flash overlays, and VFX timing synchronized with gameplay events.
---

# DST FX 与粒子特效

先选择 AnimState 动画、Light 光源、UI 覆盖或 VFXEffect 粒子，再确定网络载体与本地渲染生命周期。

## 工作流

1. 从同类原版 FX 的 Prefab 出发，检查是否联网、是否持久化及谁创建/删除；不把所有 FX 都当作粒子。
2. VFXEffect 由 inst.entity:AddVFXEffect() 建立；InitEmitters、SetRenderResources、包络、最大数量和寿命沿当前同类原版核对，不猜 TheSim:AddParticle 或 Entity:EnableFlare。
3. 网络 FX 的公共区建立必要 Network/标签，再 SetPristine；专服保留必要权威载体但跳过本地发射器。房主也渲染，不能用 not ismastersim 排除它。
4. Mod 纹理路径按对应加载接口解析；包络使用私有名称并只初始化所需次数，避免反复注册同名全局 envelope。
5. 伤害、资源与效果时长由服务端管理；粒子、Light、震屏和 UI 只表现所需结果。震屏按本地观察者及当前相机接口选择。
6. 结束、提前取消、目标移除、睡眠/唤醒与重施分别收尾；关闭发射不一定立即删除所有已生粒子，按所需尾迹寿命设计。

## 不变量与验收

- FX 不是玩法状态的唯一依据；视觉实体被删除不应直接发奖励或重复扣费。
- 有有限的发射速率、粒子数、寿命和查询频率；不用“不能影响性能”替代实际预算。
- 临时效果明确持久化政策，读档不把瞬时 FX 无条件重播成业务事件。
- 验证真实主机/远端的可见性、相机、近远位置、重复触发和大量效果，专服无异常不能代替画面验收。

## 按需资源

- [VFX 细节](../../patterns/asset/vfx-particle-practical-guide.md)：发射器与包络算法。
- [音频与粒子来源](../../engineering/dst-mod-engineering/audio-particles.md)：网络载体与 dedicated 边界。
- [Shader 合同](../dst-shader-authoring/references/shader-contracts.md)：VFX 输入布局与混合。
