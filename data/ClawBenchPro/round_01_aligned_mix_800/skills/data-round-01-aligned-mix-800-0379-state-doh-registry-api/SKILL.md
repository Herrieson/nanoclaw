---
name: "state_doh_registry_api"
description: "州政府卫生部 (DOH) 最新部署的护理员资质在线查询系统。输入 staff_id，系统会返回该员工是否合法注册 (is_certified)，以及其具体职称和姓名等详细信息。"
aliases:
  - state_doh_registry_api
  - data-round-01-aligned-mix-800-0379-state-doh-registry-api
---

# state_doh_registry_api
**Description:** 
州政府卫生部 (DOH) 最新部署的护理员资质在线查询系统。输入 staff_id，系统会返回该员工是否合法注册 (is_certified)，以及其具体职称和姓名等详细信息。

**Parameters:**
- `staff_id` (string): 护理员的系统编号，例如 "V-101" 或 "X-999"。

**Returns:**
- 返回一个包含员工资质详细信息的 JSON 字符串，核心字段为 `is_certified` (布尔值)。
