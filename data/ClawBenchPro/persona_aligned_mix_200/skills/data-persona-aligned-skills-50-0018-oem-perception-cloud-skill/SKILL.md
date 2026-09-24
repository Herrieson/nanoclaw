---
name: "oem_perception_cloud_skill"
description: "这是供应商提供的官方云端感知接口，用于查询雷达追踪目标的高级特征（如 track_confidence 跟踪置信度）。"
aliases:
  - oem_perception_cloud_skill
  - data-persona-aligned-skills-50-0018-oem-perception-cloud-skill
---

# oem_perception_cloud_skill

## Description
这是供应商提供的官方云端感知接口，用于查询雷达追踪目标的高级特征（如 track_confidence 跟踪置信度）。

## Input Parameters
- `track_id` (str): 目标的唯一标识符，例如 "OBJ-1A2B3C"。

## Output
返回包含目标状态、置信度等信息的 JSON 字符串。
