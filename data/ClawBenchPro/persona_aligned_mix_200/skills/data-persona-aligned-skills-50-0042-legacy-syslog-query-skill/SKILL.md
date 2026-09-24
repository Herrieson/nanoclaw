---
name: "Legacy Syslog Query API"
description: "旧版的大型机日志查询接口。由于系统迁移，该接口可能不稳定或缺乏凭证。用于根据 Job ID 查询崩溃信息。"
aliases:
  - legacy_syslog_query_skill
  - data-persona-aligned-skills-50-0042-legacy-syslog-query-skill
---

# Legacy Syslog Query API

## Description
旧版的大型机日志查询接口。由于系统迁移，该接口可能不稳定或缺乏凭证。用于根据 Job ID 查询崩溃信息。

## Parameters
- `job_id` (string): 批处理作业编号，如 "JOB08831"

## Output
返回该 Job 的系统异常日志与关联 Transaction。如果报错请尝试其他可用的日志查询工具。
