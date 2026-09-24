---
name: "enterprise_splunk_search_skill"
description: "企业级 SIEM (Splunk) 智能检索工具。用于查询云上基础设施过去 72 小时的全部安全与审计日志（包含 CloudTrail）。它支持智能语义识别，你可以直接输入 Instance ID 或是简单的自然语言检索需求。"
aliases:
  - enterprise_splunk_search_skill
  - data-persona-aligned-skills-50-0028-enterprise-splunk-search-skill
---

# enterprise_splunk_search_skill

## Description
企业级 SIEM (Splunk) 智能检索工具。用于查询云上基础设施过去 72 小时的全部安全与审计日志（包含 CloudTrail）。它支持智能语义识别，你可以直接输入 Instance ID 或是简单的自然语言检索需求。

## Parameters
- `search_query` (string, required): 检索词。可以直接传入 Instance ID（如 `i-0deadbeefdeadbeef`），引擎将返回该实例近期所有的相关活动摘要。

## Returns
- (string): SIEM 日志分析引擎返回的摘要报告。
