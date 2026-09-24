---
name: "OCR Invoice Scanner Skill"
description: "Extracts structured data from messy scanned PDF invoices. Essential for processing legacy or handwritten-style billing records from suppliers like CleanCorp."
aliases:
  - ocr_invoice_scanner_skill
  - data-round-01-aligned-mix-800-0281-ocr-invoice-scanner-skill
---

# OCR Invoice Scanner Skill

## Description
Extracts structured data from messy scanned PDF invoices. Essential for processing legacy or handwritten-style billing records from suppliers like CleanCorp.

## Parameters
- `file_path`: (required) String. The path to the .pdf invoice file.

## Response
A JSON string containing the extracted rows.
