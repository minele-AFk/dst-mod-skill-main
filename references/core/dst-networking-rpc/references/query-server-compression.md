---
name: dst-query-server-compression
description: 与外部 HTTP 服务器通信。QueryServer 请求、ZipAndEncodeString 压缩格式与 Python 侧解析。
---

# 与外部服务器通信：QueryServer 与字符串压缩

mod 需要把数据发到游戏外的 HTTP 服务器时使用 `TheSim:QueryServer()`，配合 `TheSim:ZipAndEncodeString()` 压缩可减小传输体积。

## Lua 端调用

```lua
-- 发送请求（回调参数：响应文本, 是否成功, 状态码）
TheSim:QueryServer( "https://example.com/api", function(resp, success, code)
    if success then
        -- resp 为返回的文本
    end
end, "GET" )
```

压缩 / 解压（引擎函数）：

```lua
local encoded = TheSim:ZipAndEncodeString(str)       -- 压缩 + 编码
local raw     = TheSim:DecodeAndUnzipString(encoded) -- 解码 + 解压
```

原版在 [util.lua](file:///d:/mods/scripts/util.lua#L1693-L1703) 里做了包装：`ZipAndEncodeString(data)` 会先把 Lua 表 `DataDumper` 序列化再交给引擎压缩，所以可以直接传表；`DecodeAndUnzipString(str)` 解码后会再反序列化回 Lua 数据。

## 传输格式（引擎侧）

`ZipAndEncodeString` 输出 = base64 包裹的二进制，内部结构：

| 偏移 | 长度 | 内容 |
|------|------|------|
| 0 | 8 | 头（前 8 字节用途未公开）|
| 8 | 4 | 原始字符串长度 `len_str`（小端 uint32）|
| 12 | 4 | 压缩后长度 `len_compressed`（小端 uint32）|
| 16 | `len_compressed` | zlib 压缩数据 |

流程：先 zlib 压缩 → 拼 16 字节头 → 最后 base64 编码。

## Python 3 解析示例

```python
from base64 import b64decode
import zlib
import struct
import logging

logger = logging.getLogger(__name__)

def unzipstring(s):
    ''' 解压字符串，等价于 TheSim:DecodeAndUnzipString() '''
    try:
        return unzipstring_implement(s)
    except Exception as e:
        logger.info("Failed in `unzipstring`: %s", e)
        return None

def unzipstring_implement(s):
    b = b64decode(s)
    assert len(b) >= 16
    len_str, len_compressed = struct.unpack("<II", b[8:16])
    data = b[16:]
    assert len(data) == len_compressed
    s = zlib.decompress(data)
    assert len(s) == len_str
    return s.decode("utf-8")
```

## 注意点

- 引擎压缩 = zlib 压缩 + base64 编码；解析时顺序相反：先 base64 解码，再 zlib 解压。
- 头部 8 字节之后的 `len_str` / `len_compressed` 都是小端 uint32，解析时不要读成大端。
- `QueryServer` 回调在请求完成后触发；回调内若涉及权威逻辑，需自行校验返回值。
