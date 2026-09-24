---
name: "Intranet Wiki Search Skill"
description: "这是地面站内网工程 Wiki 的搜索引擎，用于查询卫星接口控制文件（ICD）、历史工单和各类硬件参数表。"
aliases:
  - intranet_wiki_search_skill
  - data-persona-aligned-skills-50-0009-intranet-wiki-search-skill
---

# Intranet Wiki Search Skill

## Description
这是地面站内网工程 Wiki 的搜索引擎，用于查询卫星接口控制文件（ICD）、历史工单和各类硬件参数表。

## Functions

### `search_wiki(query: str) -> str`
在内网工程维基中检索相关关键字内容。

**Parameters:**
- `query` (str): 搜索的关键字，例如 "X-9 Telemetry ICD"。

**Returns:**
- `str`: 检索出的文档摘要内容。
