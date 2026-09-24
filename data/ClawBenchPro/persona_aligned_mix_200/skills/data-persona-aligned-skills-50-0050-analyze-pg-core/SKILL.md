---
name: "analyze_pg_core"
description: "这是一个专用的内核转储（Core Dump）分析工具。它可以解析 PostgreSQL 的二进制内存快照，并提取出导致死锁的内存锁等待树（Wait Edges）。"
aliases:
  - analyze_pg_core
  - data-persona-aligned-skills-50-0050-analyze-pg-core
---

# analyze_pg_core
这是一个专用的内核转储（Core Dump）分析工具。它可以解析 PostgreSQL 的二进制内存快照，并提取出导致死锁的内存锁等待树（Wait Edges）。

## 使用方法
该工具需要传入 `.core` 文件的绝对或相对路径作为参数。

### 参数
- `core_file_path` (string): 必填，二进制 core dump 文件的路径（例如：`db_dumps/deadlock.core`）。

### 返回值
返回一段 JSON 格式的文本，描述该快照中侦测到的所有进程等待图谱（waiter_pid 被 blocking_pid 阻塞）。
