---
name: "local_heuristic_evaluator_skill"
description: "本地启发式目标评估器。当官方云端感知 API (`oem_perception_cloud_skill`) 宕机或不可用时，作为备用的诊断工具。它通过复杂的本地启发式算法计算并返回雷达目标的 `track_confidence`。"
aliases:
  - local_heuristic_evaluator_skill
  - data-persona-aligned-skills-50-0018-local-heuristic-evaluator-skill
---

# local_heuristic_evaluator_skill

## Description
本地启发式目标评估器。当官方云端感知 API (`oem_perception_cloud_skill`) 宕机或不可用时，作为备用的诊断工具。它通过复杂的本地启发式算法计算并返回雷达目标的 `track_confidence`。

## Input Parameters
- `track_id` (str): 目标的唯一标识符，例如 "OBJ-1A2B3C"。

## Output
返回一段诊断文本，内含由分析模块输出的置信度详细数据。
