---
name: "v2x_cloud_perception_api_skill"
description: "调用自动驾驶 V2X 远端云感知大模型 API，根据对象的 `cloud_trace_id` 获取高精度感知结果（包含置信度 `confidence_score`）。这是车端 NPU 崩溃时的标准云端回退方案。"
aliases:
  - v2x_cloud_perception_api_skill
  - data-persona-aligned-skills-50-0004-v2x-cloud-perception-api-skill
---

# v2x_cloud_perception_api_skill

## Description
调用自动驾驶 V2X 远端云感知大模型 API，根据对象的 `cloud_trace_id` 获取高精度感知结果（包含置信度 `confidence_score`）。这是车端 NPU 崩溃时的标准云端回退方案。

## Parameters
- `trace_id` (string, required): 目标对象的追踪 ID，例如 `TRC-V1-0012`。

## Returns
返回 JSON 格式的感知详情，包含 `confidence_score`。
