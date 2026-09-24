---
name: "Skill: Handwritten Ledger Parser"
description: "This tool simulates an OCR engine specialized in reading messy, handwritten property management ledgers from PDF or Image formats."
aliases:
  - handwritten_ledger_parser_skill
  - data-round-01-aligned-mix-800-0331-handwritten-ledger-parser-skill
---

# Skill: Handwritten Ledger Parser

## Description
This tool simulates an OCR engine specialized in reading messy, handwritten property management ledgers from PDF or Image formats.

## Usage
Input: `file_path` (string)
Output: A JSON string containing the extracted row data.

## Example
Input: `records/building_a.pdf`
Output: `[{"Date": "2023-07-01", "TenantID": "T001", "Amount": 1200}, ...]`
