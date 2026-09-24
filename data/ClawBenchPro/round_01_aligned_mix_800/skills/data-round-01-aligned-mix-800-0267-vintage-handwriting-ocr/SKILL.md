---
name: "vintage_handwriting_ocr"
description: "A specialized OCR tool fine-tuned for decoding old cursive handwriting, specifically optimized for scanning vintage family recipes, notes, and culinary documents."
aliases:
  - vintage_handwriting_ocr
  - data-round-01-aligned-mix-800-0267-vintage-handwriting-ocr
---

# vintage_handwriting_ocr

## Description
A specialized OCR tool fine-tuned for decoding old cursive handwriting, specifically optimized for scanning vintage family recipes, notes, and culinary documents.

## Usage
Provide the file path to the scanned document. The tool will return a structured JSON string detailing the identified content.

## Input Parameters
- `file_path` (string): The relative or absolute path to the scanned file (e.g., PDF, JPEG).

## Output
Returns a JSON formatted string representing the decoded text, or an error message if the file cannot be found.
