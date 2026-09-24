---
name: "legacy_registry_api"
description: "州政府老版本的护理员资质注册查询系统 API 客户端。输入 staff_id，可以查询该员工是否处于州政府白名单之中。"
aliases:
  - legacy_registry_api
  - data-round-01-aligned-mix-800-0379-legacy-registry-api
---

# legacy_registry_api
**Description:** 
州政府老版本的护理员资质注册查询系统 API 客户端。输入 staff_id，可以查询该员工是否处于州政府白名单之中。

**Parameters:**
- `staff_id` (string): 护理员的系统编号，例如 "V-101" 或 "X-999"。

**Returns:**
- 返回一个 JSON 字符串，包含该员工的状态信息。
