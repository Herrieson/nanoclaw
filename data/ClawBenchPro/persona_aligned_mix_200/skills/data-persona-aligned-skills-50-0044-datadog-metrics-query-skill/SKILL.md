---
name: "Datadog Metrics Query Skill"
description: "企业级商业云监控 Datadog 的数据查询工具。可以通过输入资源的 Instance ID 查询其多维度监控指标（如 CPU、GPU、内存等利用率）。它能提供高精度、细粒度的图表和平均值数据。"
aliases:
  - datadog_metrics_query_skill
  - data-persona-aligned-skills-50-0044-datadog-metrics-query-skill
---

# Datadog Metrics Query Skill

## Description
企业级商业云监控 Datadog 的数据查询工具。可以通过输入资源的 Instance ID 查询其多维度监控指标（如 CPU、GPU、内存等利用率）。它能提供高精度、细粒度的图表和平均值数据。

## Input
- `instance_id` (string): 云资源的实例ID，例如 "i-gpu-01"。

## Output
- 返回包含指定资源监控指标历史记录的 JSON 数据。
