---
name: "brand_palette_extractor_skill"
description: "This tool is designed to parse proprietary `.palette` files used by the UI design team. It extracts the Primary, Secondary, and Text colors."
aliases:
  - brand_palette_extractor_skill
  - data-round-01-aligned-mix-800-0344-brand-palette-extractor-skill
---

# brand_palette_extractor_skill

## Description
This tool is designed to parse proprietary `.palette` files used by the UI design team. It extracts the Primary, Secondary, and Text colors.

## Parameters
- `file_path`: (Required) The string path to the `.palette` file.

## Response
- A JSON object containing `primary_color`, `secondary_color`, and `text_color` in HEX format.
