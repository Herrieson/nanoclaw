---
name: "Prometheus Internal Query Skill"
description: "企业自研的内部开源指标监控平台查询接口。由于资金受限，公司当前依赖该接口提供内部所有实例的基础监控查询。虽然不如商业版精确，但可以获取过去 30 天内机器的平均利用率。"
aliases:
  - prometheus_internal_query_skill
  - data-persona-aligned-skills-50-0044-prometheus-internal-query-skill
---

# Prometheus Internal Query Skill

## Description
企业自研的内部开源指标监控平台查询接口。由于资金受限，公司当前依赖该接口提供内部所有实例的基础监控查询。虽然不如商业版精确，但可以获取过去 30 天内机器的平均利用率。

## Input
- `instance_id` (string): 云资源的实例ID，例如 "i-gpu-01"。

## Output
- 返回一段 JSON 描述，内部包含 `average_utilization_percent` 字段，代表该 GPU 的历史平均利用率百分比。
