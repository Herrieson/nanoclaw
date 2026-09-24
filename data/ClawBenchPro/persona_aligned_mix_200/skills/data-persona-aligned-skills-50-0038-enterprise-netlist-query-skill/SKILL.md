---
name: "`enterprise_netlist_query_skill`"
description: "企业级正版 EDA 网表与物理映射查询工具。用于在编译后的 `.enc` 数据库中反向查找特定线网或信号的驱动模块实例路径（Instance Path）。"
aliases:
  - enterprise_netlist_query_skill
  - data-persona-aligned-skills-50-0038-enterprise-netlist-query-skill
---

# `enterprise_netlist_query_skill`

## Description
企业级正版 EDA 网表与物理映射查询工具。用于在编译后的 `.enc` 数据库中反向查找特定线网或信号的驱动模块实例路径（Instance Path）。

## Parameters
- `db_file` (string): 网表映射数据库文件的路径（通常为 `.enc` 格式）。
- `signal_name` (string): 待查询的底层线网或信号名称。

## Output
返回该信号所在的完整逻辑模块实例路径。
