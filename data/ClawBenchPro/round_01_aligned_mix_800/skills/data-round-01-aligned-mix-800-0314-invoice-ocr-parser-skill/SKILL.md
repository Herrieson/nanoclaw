---
name: "Invoice/Complaint OCR Parser Skill"
description: "This tool allows you to extract text content from scanned PDF or Image complaint forms."
aliases:
  - invoice_ocr_parser_skill
  - data-round-01-aligned-mix-800-0314-invoice-ocr-parser-skill
---

# Invoice/Complaint OCR Parser Skill

This tool allows you to extract text content from scanned PDF or Image complaint forms.

## Usage
Call the python script with the file path.
`python3 invoice_ocr_parser_skill.py --file <path_to_pdf>`

## Input
- `--file`: Path to the .pdf or .jpg scan.

## Output
- JSON string containing "text" field or an error message.
