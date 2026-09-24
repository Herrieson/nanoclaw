---
name: "property_tax_calculator_skill"
description: "Retrieves the dynamic municipal property tax for a specific unit. This must be deducted from the gross rent to calculate net revenue."
aliases:
  - property_tax_calculator_skill
  - data-round-01-aligned-mix-800-0233-property-tax-calculator-skill
---

# property_tax_calculator_skill

Retrieves the dynamic municipal property tax for a specific unit. This must be deducted from the gross rent to calculate net revenue.

**Inputs:**
- `unit_id`: String (e.g., "101", "202").

**Outputs:**
- `tax_amount`: Float.
