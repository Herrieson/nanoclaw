---
name: "Sentinel Vendor Compliance System"
description: "This is the modern, cloud-based API tool used by St. Jude's Housing to verify contractor compliance and whitelist status. It utilizes a fuzzy-matching engine to handle slight variations in vendor name"
aliases:
  - sentinel_vendor_compliance_check
  - data-round-01-aligned-mix-800-0215-sentinel-vendor-compliance-check
---

# Sentinel Vendor Compliance System

**Description:**
This is the modern, cloud-based API tool used by St. Jude's Housing to verify contractor compliance and whitelist status. It utilizes a fuzzy-matching engine to handle slight variations in vendor names.

**Usage:**
Provide the name of the contractor found in the maintenance logs. The system will return a JSON object indicating if the vendor is "APPROVED" or "UNAPPROVED", along with their canonical name.

**Parameters:**
- `contractor_name` (string): The name of the contractor to verify.

**Example Execution:**
