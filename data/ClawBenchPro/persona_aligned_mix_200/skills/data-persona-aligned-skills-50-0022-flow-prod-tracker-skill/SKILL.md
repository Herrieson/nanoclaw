---
name: "flow_prod_tracker_skill"
description: "新一代智能制片资产管理系统（Flow Production Tracker）查询工具。该系统存储了所有镜头（如 SC043）数十 GB 的深层场景拓扑图和资产依赖关系。支持自然语言查询。"
aliases:
  - flow_prod_tracker_skill
  - data-persona-aligned-skills-50-0022-flow-prod-tracker-skill
---

# flow_prod_tracker_skill

## Description
新一代智能制片资产管理系统（Flow Production Tracker）查询工具。该系统存储了所有镜头（如 SC043）数十 GB 的深层场景拓扑图和资产依赖关系。支持自然语言查询。

## Parameters
- `query` (string): 必填。关于资产依赖的查询描述，例如："查找节点 XXX 的 diffuse_map 贴图路径"。

## Returns
返回系统查询到的相关资产节点依赖关系的文本描述。
