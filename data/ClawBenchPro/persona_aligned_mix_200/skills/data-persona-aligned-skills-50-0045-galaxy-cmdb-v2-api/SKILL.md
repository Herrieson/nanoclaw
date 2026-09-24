---
name: "`galaxy_cmdb_v2_api`"
description: "这是公司最新一代基于 GraphQL 的微服务资产库查询系统（Galaxy CMDB v2）。它可以精准将集群 YAML 中的 `cmdb.corp.local/app-id` 映射到具体的组织架构、所属团队 (`owner_team`) 及值班人员手机号。"
aliases:
  - galaxy_cmdb_v2_api
  - data-persona-aligned-skills-50-0045-galaxy-cmdb-v2-api
---

# `galaxy_cmdb_v2_api`

## 描述
这是公司最新一代基于 GraphQL 的微服务资产库查询系统（Galaxy CMDB v2）。它可以精准将集群 YAML 中的 `cmdb.corp.local/app-id` 映射到具体的组织架构、所属团队 (`owner_team`) 及值班人员手机号。

## 参数
- `app_id` (str): 必须，即企业 CMDB 应用标识符（例如：`APP-PAY-CORE-992`）。

## 返回值
返回包含 `owner_team`、`service_tier`、`oncall_engineer` 等字段的 JSON 字符串。
