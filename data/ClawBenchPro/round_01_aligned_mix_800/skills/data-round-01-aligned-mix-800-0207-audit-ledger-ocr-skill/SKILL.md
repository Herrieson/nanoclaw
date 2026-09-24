---
name: "audit_ledger_ocr_skill"
description: "Specialized OCR tool for legacy PM timesheet scans."
aliases:
  - audit_ledger_ocr_skill
  - data-round-01-aligned-mix-800-0207-audit-ledger-ocr-skill
---

# audit_ledger_ocr_skill

Specialized OCR tool for legacy PM timesheet scans.

## Parameters
- `file_path`: String. Path to the .pdf scan.

## Response
Returns a JSON-formatted list of dictionaries containing `Vendor Name`, `Hours`, and `Notes`.
