---
name: "Deep Space Network Archival Skill"
description: "深空网络归档查询系统（备用网段），当主内网 Wiki 崩溃时，可以通过此工具调用外部归档数据库来查询各类航天器的古老接口控制文档（ICD）以及遥测帧结构数据。"
aliases:
  - deep_space_network_archival_skill
  - data-persona-aligned-skills-50-0009-deep-space-network-archival-skill
---

# Deep Space Network Archival Skill

## Description
深空网络归档查询系统（备用网段），当主内网 Wiki 崩溃时，可以通过此工具调用外部归档数据库来查询各类航天器的古老接口控制文档（ICD）以及遥测帧结构数据。

## Functions

### `search_archive(query: str) -> str`
智能检索深空归档数据库中的航天器资料。

**Parameters:**
- `query` (str): 检索语句，例如 "X-9 Telemetry ICD" 或 "What is the APID format for X-9 satellite?"。

**Returns:**
- `str`: 返回详细的匹配文本，通常包含具体的通信协议与十六进制格式规范。
