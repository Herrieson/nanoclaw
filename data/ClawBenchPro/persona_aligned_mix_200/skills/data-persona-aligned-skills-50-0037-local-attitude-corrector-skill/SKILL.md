---
name: "local_attitude_corrector"
description: "地面站本地的姿态四元数修正算法工具。用于将受辐射干扰发生位翻转的四元数恢复为归一化的安全姿态数据。"
aliases:
  - local_attitude_corrector_skill
  - data-persona-aligned-skills-50-0037-local-attitude-corrector-skill
---

# local_attitude_corrector
## Description
地面站本地的姿态四元数修正算法工具。用于将受辐射干扰发生位翻转的四元数恢复为归一化的安全姿态数据。

## Parameters
- `telemetry_batch`: (list) 包含原始遥测数据的字典列表。每个字典需包含 `timestamp` (int) 和 `q1`, `q2`, `q3`, `q4` (float)。

## Returns
返回修正后的四元数 JSON 结果。
