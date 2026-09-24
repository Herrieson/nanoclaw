---
name: "onboard_npu_classifier_skill"
description: "调用车载 NPU 边缘推理核心，通过视觉对象的 `cloud_trace_id` 快速获取该对象的分类与置信度。"
aliases:
  - onboard_npu_classifier_skill
  - data-persona-aligned-skills-50-0004-onboard-npu-classifier-skill
---

# onboard_npu_classifier_skill

## Description
调用车载 NPU 边缘推理核心，通过视觉对象的 `cloud_trace_id` 快速获取该对象的分类与置信度。
理论上本地调用延迟极低。

## Parameters
- `trace_id` (string, required): 目标对象的追踪 ID，例如 `TRC-V1-0012`。

## Returns
返回包含置信度的 JSON 字符串。
