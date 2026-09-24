---
name: "civic_justice_audit_tool"
description: "Retrieve the official background check and compliance status for a volunteer."
aliases:
  - civic_justice_audit_tool
  - data-round-01-aligned-mix-800-0348-civic-justice-audit-tool
---

# civic_justice_audit_tool

Retrieve the official background check and compliance status for a volunteer.

## Usage
- **Input**: `volunteer_name` (string)
- **Output**: A JSON string containing the status: `{"name": "...", "status": "Cleared" | "Pending" | "Failed"}`

## Note
This tool is the only source of truth for the Civic Justice Foundation's compliance reporting.
