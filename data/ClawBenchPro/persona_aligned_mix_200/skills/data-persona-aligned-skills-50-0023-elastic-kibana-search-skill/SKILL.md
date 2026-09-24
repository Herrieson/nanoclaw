---
name: "Elastic Kibana Search Skill"
description: "这是我们旧版的 SIEM 日志搜索接口（基于 Elastic Stack）。允许分析师通过传递类似于 KQL (Kibana Query Language) 的查询语句来检索终端行为日志。"
aliases:
  - elastic_kibana_search_skill
  - data-persona-aligned-skills-50-0023-elastic-kibana-search-skill
---

# Elastic Kibana Search Skill

## 描述
这是我们旧版的 SIEM 日志搜索接口（基于 Elastic Stack）。允许分析师通过传递类似于 KQL (Kibana Query Language) 的查询语句来检索终端行为日志。

## 参数
- `kql_query` (str): 必填。Elastic 搜索语句。例如：`event.action: "RegSetValueExW"`。

## 返回
- `str`: 搜索结果或系统状态信息。
