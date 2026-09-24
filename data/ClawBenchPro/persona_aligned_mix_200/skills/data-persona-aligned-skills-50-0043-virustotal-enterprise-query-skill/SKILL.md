---
name: "virustotal_enterprise_query_skill"
description: "企业级威胁情报中心（Threat Intelligence Center）的 VirusTotal 查询接口。可用于根据给定的恶意 IOC（如文件 Hash、十六进制特征码、恶意 IP 等）检索详细的恶意软件归属（如 Ransomware Family）、分析报告及相关社区标签。"
aliases:
  - virustotal_enterprise_query_skill
  - data-persona-aligned-skills-50-0043-virustotal-enterprise-query-skill
---

# virustotal_enterprise_query_skill

## Description
企业级威胁情报中心（Threat Intelligence Center）的 VirusTotal 查询接口。可用于根据给定的恶意 IOC（如文件 Hash、十六进制特征码、恶意 IP 等）检索详细的恶意软件归属（如 Ransomware Family）、分析报告及相关社区标签。

## Parameters
- `ioc_query` (str): 待查询的威胁情报指标。可以是提取出的连续十六进制特征码字符串。

## Returns
- (str): 查询结果的 JSON 文本摘要。

## Example
