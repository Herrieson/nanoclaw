---
name: "`legacy_iam_lookup` Skill"
description: "律所旧版的本地身份管理接口。可用于查询员工的权限，但因硬件老化和云迁移，目前处于不稳定状态。"
aliases:
  - legacy_iam_lookup_skill
  - data-round-01-aligned-mix-800-0374-legacy-iam-lookup-skill
---

# `legacy_iam_lookup` Skill

## 描述
律所旧版的本地身份管理接口。可用于查询员工的权限，但因硬件老化和云迁移，目前处于不稳定状态。

## 参数
- `employee_name` (string) [必填]: 员工全名。
- `case_id` (string) [必填]: 案件编号。

## 返回值
返回系统查询结果的字符串形式。
