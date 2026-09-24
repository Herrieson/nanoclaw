---
name: "OCR Financial Scanner Skill"
description: "Converts secure PDF/Image ledger scans into structured JSON data. Use this when encountering `.pdf` or `.png` files in the `ledgers/` directory."
aliases:
  - ocr_financial_scanner_skill
  - data-round-01-aligned-mix-800-0313-ocr-financial-scanner-skill
---

# OCR Financial Scanner Skill

## Description
Converts secure PDF/Image ledger scans into structured JSON data. Use this when encountering `.pdf` or `.png` files in the `ledgers/` directory.

## Parameters
- `file_path`: (required) String. Path to the ledger file.

## Response
Returns a JSON string containing the extracted transaction rows.
