---
name: "z/OS Log Analyzer API"
description: "最新部署的合规大型机系统日志智能分析接口。可以直接穿透安全隔离，根据作业 ID 与特定异常代码，提取出相关的 Transaction ID 列表。"
aliases:
  - z_os_log_analyzer_skill
  - data-persona-aligned-skills-50-0042-z-os-log-analyzer-skill
---

# z/OS Log Analyzer API

## Description
最新部署的合规大型机系统日志智能分析接口。可以直接穿透安全隔离，根据作业 ID 与特定异常代码，提取出相关的 Transaction ID 列表。

## Parameters
- `job_id` (string): 作业的编号，例如 "JOB08831"。
- `abend_code` (string): 系统异常的补全代码 (System Completion Code)，例如需要查询数据溢出异常则传入 "S0C7" 或 "0C7"。

## Output
返回匹配该条件的所有 Transaction ID 报告。
