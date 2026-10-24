---
name: dst-shader-authoring
description: Create and modify Don't Starve Together shaders and post-processing effects. Use when writing GLSL shaders, color correction, bloom, depth of field, and custom rendering passes.
---

# DST Shader 与后处理

先按消费者选择渲染合同，再准备对应 shader 与 Lua 接入；不同 pass 的顶点输入、纹理和颜色语义不可互换。

## 选择路线

| 需求 | 已有接入路线 |
|---|---|
| 世界动画 bloom | AnimState:SetBloomEffectHandle，改变 bloom pass，不等于替换主 pass |
| UIAnim 主 effect | UIAnim:GetAnimState():SetDefaultEffectHandle，按当前调用点核对 |
| Image effect | Image:SetEffect 及其 IMAGE_PARAMS/ALPHA_RANGE 接口 |
| VFX 粒子 | VFXEffect:SetRenderResources，与具体 blend/input 布局匹配 |
| 全屏后处理 | AddModShadersInit / AddModShadersSortAndEnable 与 PostProcessor 的 effect/sampler/uniform 管线 |

不要使用未查证的 TheSim:AddShaderOverride；Mod 运行时 shader 资源为相应编译 .ksh，不把任意 .shader 文件当引擎会自动加载。源阶段如何打包编译遵循当前工具。

## 工作流

1. 读目标安装的 gamelogic、postprocesseffects 及相同 pass 的原始 shader；明确输入布局和采样来源。
2. 从对应模板保留矩阵、SKINNED 分支、varying、预乘 alpha 与 sampler；不在未知合同上拼通用 WebGL 示例。
3. 声明实际 Asset、解析 Mod 资源路径，按引擎创建 PostProcessor 的时机注册和排序；不顶层捕获未就绪对象。
4. 多 pass 逐个建立和启用，从透传 shader 开始确认每一步输出，再加入算法。
5. 功能关闭、切世界或渲染目标失效时恢复自己的 effect/参数；先查当前公开接口，不覆盖别人的 pass。
6. 验证显卡、窗口比例、UI/世界各自路线和真实画面，记录成本与降级政策。

## 验证边界

Shader 不是必须兼容 WebGL 的网页程序；使用当前引擎支持的 GLSL/编译合同。专服无画面，不能证明 shader 编译或采样正确。视觉状态同步与本地 shader 运算是不同问题。

## 按需资源

- [Shader 合同与模板](references/shader-contracts.md)
- [多 Pass 后处理](references/postprocess-multipass.md)
