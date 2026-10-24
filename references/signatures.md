# 高频函数签名

使用此页面作为签名查询的导航。

仅阅读 `references/signatures/` 下你需要的特定页面：

- [hook-signatures.md](signatures/hook-signatures.md)
  - `modutil.lua` 中的注册 API
- [entityscript-signatures.md](signatures/entityscript-signatures.md)
  - 高频 `EntityScript` 方法
- [helper-signatures.md](signatures/helper-signatures.md)
  - `standardcomponents.lua` 中的高频辅助函数
- [runtime-signatures.md](signatures/runtime-signatures.md)
  - 观察到的高频运行时全局变量

## 快速导航

- "我需要确切的 `modutil.lua` 注册签名"
  - 阅读 [hook-signatures.md](signatures/hook-signatures.md)
- "我需要常见的预制件辅助函数签名"
  - 阅读 [helper-signatures.md](signatures/helper-signatures.md)
- "我需要确切的 `inst:` 调用格式"
  - 阅读 [entityscript-signatures.md](signatures/entityscript-signatures.md)
- "我需要运行时全局变量或输入方法格式"
  - 阅读 [runtime-signatures.md](signatures/runtime-signatures.md)

## 使用原则

- 使用这些页面来避免猜测参数顺序
- 编写实际 mod 代码之前，验证最接近的官方调用者