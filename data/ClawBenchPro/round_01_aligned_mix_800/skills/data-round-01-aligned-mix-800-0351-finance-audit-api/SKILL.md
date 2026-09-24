---
name: "Finance Audit API"
description: "Retrieves line-item details for construction transaction IDs."
aliases:
  - finance_audit_api
  - data-round-01-aligned-mix-800-0351-finance-audit-api
---

# Finance Audit API

Retrieves line-item details for construction transaction IDs.

**Arguments:**
- `transaction_id`: The ID from the expense CSV (e.g., 'TXN_001').

**Returns:**
JSON object containing 'description' and 'internal_code'.
