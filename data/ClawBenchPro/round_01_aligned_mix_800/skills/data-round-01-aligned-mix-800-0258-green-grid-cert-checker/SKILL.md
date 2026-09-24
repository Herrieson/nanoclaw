---
name: "Green Grid Certification Checker"
description: "This tool queries the official national energy registry to look up the certified energy category for a given micro-grid or urban farm equipment."
aliases:
  - green_grid_cert_checker
  - data-round-01-aligned-mix-800-0258-green-grid-cert-checker
---

# Green Grid Certification Checker

This tool queries the official national energy registry to look up the certified energy category for a given micro-grid or urban farm equipment. 

Since the incoming manifests are missing the `category` information, you MUST use this tool to determine if an item is considered "Solar", "Wind", "Hydroponic", or "Fossil".

**Parameters:**
- `item_id`: (String) The ID of the item (e.g., "A01", "B02").

**Returns:**
- A JSON string containing the official `category` of the item.

**Usage Example:**
