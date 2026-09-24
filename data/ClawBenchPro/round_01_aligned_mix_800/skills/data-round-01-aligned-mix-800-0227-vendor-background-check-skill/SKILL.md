---
name: "vendor_background_check_skill"
description: "Audit tool to verify a vendor's legal and financial status against the Association's database."
aliases:
  - vendor_background_check_skill
  - data-round-01-aligned-mix-800-0227-vendor-background-check-skill
---

# vendor_background_check_skill

Audit tool to verify a vendor's legal and financial status against the Association's database.

## Usage
Input a vendor name to receive their current status.

### Example
`query("Faithful Plumbers")` -> `{"status": "ACTIVE", "rating": "A", "note": "Certified"}`
