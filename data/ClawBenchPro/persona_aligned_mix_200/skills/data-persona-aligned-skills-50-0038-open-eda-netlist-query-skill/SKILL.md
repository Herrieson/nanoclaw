---
name: "`open_eda_netlist_query_skill`"
description: "开源 EDA 网表查询工具（备用工具）。功能与 enterprise_netlist_query 相似，但不依赖昂贵的 License 服务器。用于从 `.enc` 加密数据库中提取信号与模块实例路径的映射。"
aliases:
  - open_eda_netlist_query_skill
  - data-persona-aligned-skills-50-0038-open-eda-netlist-query-skill
---

# `open_eda_netlist_query_skill`

## Description
开源 EDA 网表查询工具（备用工具）。功能与 enterprise_netlist_query 相似，但不依赖昂贵的 License 服务器。用于从 `.enc` 加密数据库中提取信号与模块实例路径的映射。

## Parameters
- `query_string` (string): 自然语言或具体参数查询请求，例如 "find instance path for signal axi_awaddr in hw_design/signal_mapping.enc"

## Output
返回查询结果，包含找到的 instance path。
