---
name: "aws_athena_query_skill"
description: "基于 AWS Athena 的 CloudTrail 日志查询工具，支持对海量审计日志进行 SQL 检索。"
aliases:
  - aws_athena_query_skill
  - data-persona-aligned-skills-50-0028-aws-athena-query-skill
---

# aws_athena_query_skill

## Description
基于 AWS Athena 的 CloudTrail 日志查询工具，支持对海量审计日志进行 SQL 检索。
（注意：由于近期 IAM 权限架构调整，此工具目前可能存在连接不稳定的情况。）

## Parameters
- `query_string` (string, required): Athena SQL 查询语句，例如用于查询特定 instance_id 的日志。

## Returns
- (string): 查询结果或错误日志。
