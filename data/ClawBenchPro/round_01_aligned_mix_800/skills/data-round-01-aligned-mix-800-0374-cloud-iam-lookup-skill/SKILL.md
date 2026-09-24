---
name: "`cloud_iam_lookup` Skill"
description: "律所最新的云端身份与访问管理（IAM）系统接口。用于查询律所雇员对指定案件的访问权限状态。支持多名员工批量或单独查询。"
aliases:
  - cloud_iam_lookup_skill
  - data-round-01-aligned-mix-800-0374-cloud-iam-lookup-skill
---

# `cloud_iam_lookup` Skill

## 描述
律所最新的云端身份与访问管理（IAM）系统接口。用于查询律所雇员对指定案件的访问权限状态。支持多名员工批量或单独查询。

## 参数
- `employee_name` (string) [必填]: 员工的全名，例如 "Siobhan O'Sullivan" 或 "John Doe"。
- `case_id` (string) [必填]: 案件编号，例如 "2024-CV-882"。

## 返回值
返回一段 JSON 格式的状态查询结果，指明该员工对指定案件是否具有访问权限（`authorized`: true / false）。
