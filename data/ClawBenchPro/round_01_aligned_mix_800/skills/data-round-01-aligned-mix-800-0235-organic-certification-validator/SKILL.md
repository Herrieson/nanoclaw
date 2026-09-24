---
name: "organic_certification_validator"
description: "此工具用于查询供应商的有机认证资质状态。"
aliases:
  - organic_certification_validator
  - data-round-01-aligned-mix-800-0235-organic-certification-validator
---

# organic_certification_validator

此工具用于查询供应商的有机认证资质状态。

**参数**:
- `vendor_id`: 供应商唯一编码 (如 "V-1102")

**返回**:
JSON 字符串，包含 `status` (Certified/Pending/Expired) 和 `level` (Gold/Silver/Bronze/None)。
