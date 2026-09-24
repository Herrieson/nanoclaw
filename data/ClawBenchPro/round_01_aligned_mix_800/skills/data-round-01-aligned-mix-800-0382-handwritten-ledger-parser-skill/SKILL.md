---
name: "Handwritten Ledger Parser Skill"
description: "Uses specialized OCR to read scanned images of the shelter's handwritten ledgers."
aliases:
  - handwritten_ledger_parser_skill
  - data-round-01-aligned-mix-800-0382-handwritten-ledger-parser-skill
---

# Handwritten Ledger Parser Skill

Uses specialized OCR to read scanned images of the shelter's handwritten ledgers.

**Input**:
- `file_path` (string): Path to the image file (e.g., `shelter_data/week3_scanned_ledger.png`).

**Output**:
- `json_data`: A list of entries extracted from the image.
