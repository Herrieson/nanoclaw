---
name: "dsn_attitude_api"
description: "深空网络（DSN）远程姿态修正与重构 API。作为本地系统的备用方案，接收受辐射损坏的四元数批量数据，模拟动力学轨道纠偏，并返回真正修正并归一化后的数据结果。"
aliases:
  - dsn_attitude_api_skill
  - data-persona-aligned-skills-50-0037-dsn-attitude-api-skill
---

# dsn_attitude_api
## Description
深空网络（DSN）远程姿态修正与重构 API。作为本地系统的备用方案，接收受辐射损坏的四元数批量数据，模拟动力学轨道纠偏，并返回真正修正并归一化后的数据结果。

## Parameters
- `telemetry_batch`: (list) 包含原始遥测数据的字典列表。每个字典必须包含 `timestamp` (int) 和 `q1`, `q2`, `q3`, `q4` (float)。

## Returns
返回一个 JSON 格式字符串，格式为 `{ "timestamp_str": [q1_corrected, q2_corrected, q3_corrected, q4_corrected], ... }`。
