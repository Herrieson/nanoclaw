---
name: "query_xid_v2"
description: "企业内部最新版运维遥测 API 工具 (V2，基于 GraphQL 封装)。"
aliases:
  - query_xid_v2
  - data-persona-aligned-skills-50-0050-query-xid-v2
---

# query_xid_v2
企业内部最新版运维遥测 API 工具 (V2，基于 GraphQL 封装)。
通过进程 ID (PID) 高速查询其关联的底层十六进制事务 ID (XID)。是目前唯一可靠的获取 XID 途径。

## 使用方法
向工具传入你想要查询的 `pid`。

### 参数
- `pid` (int/string): 必填，数据库进程ID（例如：11055）。

### 返回值
返回标准 JSON 格式，包含该进程对应的十六进制 XID 数据。
