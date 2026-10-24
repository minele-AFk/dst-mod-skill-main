# DST 维基抓取工具

用于从 [饥荒维基 · 纯文本镜像](https://dst-wiki-d1z.pages.dev/) 抓取游戏数据。

---

## 网站信息

| 项目 | 内容 |
|------|------|
| 站点 | [dst-wiki-d1z.pages.dev](https://dst-wiki-d1z.pages.dev/) |
| 描述 | 饥荒维基纯文本离线镜像 |
| 文章数量 | 6873 篇 |
| 总大小 | 约 21MB |
| 架构 | 零后端静态文件 |

---

## API 说明

### 1. 获取文章索引

```
GET /index.json
```

返回所有文章的 JSON 索引：

```json
{
  "articles": [
    {
      "id": "00000",
      "title": "文章标题",
      "chars": 1372
    },
    ...
  ]
}
```

**用法**：通过 `title` 字段搜索匹配的文章，获取 `id` 后请求具体内容。

### 2. 获取文章正文

```
GET /articles/<id>.txt
```

- `<id>` 为 5 位数字（如 `00001`）
- 返回纯文本内容（markdown 格式）

---

## 调用方式

使用 MCP 工具 **firecrawl_scrape**：

### 搜索文章

先获取索引，在本地用 Python/JS 匹配标题，然后请求文章：

```python
import urllib.request, json

# 1. 获取索引
resp = urllib.request.urlopen("https://dst-wiki-d1z.pages.dev/index.json")
data = json.loads(resp.read())

# 2. 搜索标题
keyword = "威尔逊"
results = [a for a in data["articles"] if keyword in a["title"]]
for r in results:
    print(f"{r['id']}  {r['title']}  ({r['chars']} chars)")
```

### 抓取文章正文（通过 firecrawl_mcp）

```json
// firecrawl_scrape 参数
{
  "url": "https://dst-wiki-d1z.pages.dev/articles/00001.txt",
  "formats": ["markdown"]
}
```

### 抓取索引（通过 firecrawl_mcp）

```json
// firecrawl_scrape 参数
{
  "url": "https://dst-wiki-d1z.pages.dev/index.json"
}
```

---

## 典型使用场景

| 场景 | 步骤 |
|------|------|
| 查询某个物品的官方数据 | 搜索索引 → 找到对应文章 → 抓取正文 |
| 查找某个角色的详细说明 | 搜索索引（含"角色"或具体名字）→ 获取文章 |
| 查看某个生物的原版数据 | 搜索索引 → 抓取内容 |
| 对照游戏物品名称 | 参考 [item-name-reference.md](../prefabs/item-name-reference.md) |

---

## 注意事项

- 索引文件包含约 6873 篇文章，一次性获取后建议缓存
- 同一篇文章可能有多条索引（如不同版本），用 `id` 唯一确定
- 文章内容格式为 Markdown，可直接阅读
- 此网站为纯文本镜像，无交互式 JS，抓取稳定可靠
