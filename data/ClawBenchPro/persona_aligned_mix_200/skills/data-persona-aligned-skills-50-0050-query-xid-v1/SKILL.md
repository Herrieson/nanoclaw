---
name: "query_xid_v1"
description: "企业内部旧版的运维遥测 API 工具 (V1)。"
aliases:
  - query_xid_v1
  - data-persona-aligned-skills-50-0050-query-xid-v1
---

# query_xid_v1
企业内部旧版的运维遥测 API 工具 (V1)。
通过进程 ID (PID) 查询其关联的十六进制事务 ID (XID)。

## 使用方法
直接传入一个整数或字符串格式的 PID 即可查询。

### 参数
- `pid` (int/string): 必填，需要查询事务ID的数据库进程ID。

### 返回值
返回查询到的 XID。
