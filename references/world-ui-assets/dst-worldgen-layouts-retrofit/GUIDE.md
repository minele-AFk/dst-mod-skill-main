---
name: dst-worldgen-layouts-retrofit
description: Author Don't Starve Together static layouts, set pieces, object placement, and safe retrofits for existing worlds. Use when editing map/static_layouts content, placing fixed structures, injecting set pieces, adding content to old saves, migrating world data, or preventing duplicate retrofit spawns.
---

# DST 静态布局、Setpiece 与 Retrofit

将新世界布局与旧存档补丁分开实现；Retrofit 必须可检测、可重入且不会重复生成。

## 工作流

1. 确定目标是新世界 Static Layout、Room 内随机 Setpiece、运行时一次性布置还是旧存档 Retrofit。
2. 从 map/static_layouts 和相近 object_layout 范例复制坐标、地皮、对象和随机替换模式。
3. 计算布局边界、旋转、地形要求、保留资源和阻挡，避免对象落入海洋、不可通行或已有关键建筑。
4. 新世界通过 Room、Task 或布局表接入；旧世界使用明确版本标记和服务器权威 Retrofit 流程。
5. Retrofit 搜索合法区域时限制尝试次数，先检查已存在标记或实体，再原子地放置并保存完成状态。
6. 关联实体和引用在全部生成成功后建立；部分失败时回滚本次创建或保留可恢复标记。
7. 测试不同种子、密集旧基地、无合法位置、重复载入、回滚和中途崩溃。

## 源码锚点

- map/static_layout.lua、object_layout.lua、layout.lua、layouts.lua。
- map/static_layouts/：固定布局范例。
- map/placement.lua、protected_resources.lua、pointsofinterest.lua。
- map/retrofit_savedata.lua、caves_retrofit_land.lua 与各 ocean retrofit 文件。

## 不变量

- Retrofit 不得假设旧世界仍具有原始地形和资源分布。
- 完成标记必须与实际成功状态一致。
- 不要在每次载入世界时执行无界全图搜索。
- 涉及玩家基地的自动清理或替换必须非常保守。

## 验证

- 同一存档重复加载不会重复放置。
- 没有合法位置时安全跳过并留下可诊断状态。
- 布局旋转、边界和对象引用在所有方向正确。

## 按需资源

- 需要布局格式与幂等迁移规则时读取 [layout-retrofit.md](references/layout-retrofit.md)。

