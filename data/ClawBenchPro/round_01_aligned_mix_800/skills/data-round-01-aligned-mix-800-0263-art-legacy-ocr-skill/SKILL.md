---
name: "art_legacy_ocr_skill"
description: "A specialized high-contrast OCR tool designed for elderly users and damaged art records. It can extract text from blurry images, specifically tuned for the 'Legacy Art Archive' format."
aliases:
  - art_legacy_ocr_skill
  - data-round-01-aligned-mix-800-0263-art-legacy-ocr-skill
---

# art_legacy_ocr_skill

## Description
A specialized high-contrast OCR tool designed for elderly users and damaged art records. It can extract text from blurry images, specifically tuned for the "Legacy Art Archive" format.

## Parameters
- `image_path`: (required, string) The local path to the image file (e.g., "art_records/damaged_legacy_record.png").

## Response
- `text`: (string) The extracted text content from the image.
- `confidence`: (float) Confidence score of the extraction.
