---
name: "GitLab Pipeline API (v4)"
description: "最新的内部 GitLab 流水线日志获取工具。"
aliases:
  - gitlab_pipeline_v4_skill
  - data-persona-aligned-skills-50-0024-gitlab-pipeline-v4-skill
---

# GitLab Pipeline API (v4)
最新的内部 GitLab 流水线日志获取工具。

## 功能说明
传入 Job ID，通过安全的 v4 接口获取该 CI 任务的详细日志内容（包括依赖解析和构建阶段），支持因崩溃未完整落盘的远端日志检索。

## 参数
- `job_id` (int): 必须参数，GitLab 的任务 ID。

## 示例
