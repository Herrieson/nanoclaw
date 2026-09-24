---
name: "`servicenow_legacy_query`"
description: "这是公司旧版的 ServiceNow 资产库查询工具。可以根据 `app_id` 获取关联应用的信息。"
aliases:
  - servicenow_legacy_query
  - data-persona-aligned-skills-50-0045-servicenow-legacy-query
---

# `servicenow_legacy_query`

## 描述
这是公司旧版的 ServiceNow 资产库查询工具。可以根据 `app_id` 获取关联应用的信息。

## 参数
- `app_id` (str): 必须，例如 `APP-NOISE-12`。

## 返回值
返回包含应用详细信息的 JSON 字符串，包含负责人、团队等。
