---
name: dst-performance-checklist
description: 性能检查清单。定位热点和常见性能陷阱。
---

# 性能检查清单

## 高频调用点

- [ ] OnUpdate 是否必要？能否改为事件驱动？
- [ ] DoPeriodicTask 频率是否过高？
- [ ] FindEntities 是否做了标签过滤？
- [ ] Brain 条件是否每 tick 都在计算？
- [ ] SG timeline 是否每帧都在处理？

## 内存分配

- [ ] 每 tick 是否有临时表创建？
- [ ] 是否有闭包在循环中重复生成？
- [ ] 字符串拼接是否频繁？
- [ ] 网络 dirty 是否过度发送？

## 实体相关

- [ ] 是否有未清理的子实体？
- [ ] FX 是否在移除时清理？
- [ ] 监听器是否在 OnRemove 中移除？

## 优化建议

| 问题 | 优化方案 |
|---|---|
| FindEntities 慢 | 加标签过滤，使用平方距离 |
| 轮询状态 | 改为事件监听 |
| 高频 Update | 改为 DoPeriodicTask 降低频率 |
| 重复计算 | 缓存结果并设置失效规则 |
