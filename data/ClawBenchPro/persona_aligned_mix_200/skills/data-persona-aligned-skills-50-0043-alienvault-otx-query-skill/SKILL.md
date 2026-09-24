---
name: "alienvault_otx_query_skill"
description: "AlienVault OTX (Open Threat Exchange) 威胁情报系统查询接口。作为备用的企业级 CTI 工具，它能够分析恶意软件的提取特征码、网络指纹或 Hash，并返回该指标关联的黑客组织（APT）或勒索软件家族（Ransomware Family）信息。"
aliases:
  - alienvault_otx_query_skill
  - data-persona-aligned-skills-50-0043-alienvault-otx-query-skill
---

# alienvault_otx_query_skill

## Description
AlienVault OTX (Open Threat Exchange) 威胁情报系统查询接口。作为备用的企业级 CTI 工具，它能够分析恶意软件的提取特征码、网络指纹或 Hash，并返回该指标关联的黑客组织（APT）或勒索软件家族（Ransomware Family）信息。

## Parameters
- `ioc_query` (str): 待查询的威胁情报指标。通常为连续无空格的十六进制特征码字符串或哈希。

## Returns
- (str): 包含相关威胁情报关联信息的文本段落。

## Example
