---
name: "insurance_valuation_calculator_skill"
description: "Calculates the 'Certified Insurance Value' for an artwork based on its base market price. This uses the mandatory 'Gallery Risk-Adjusted Formula' required by local insurers."
aliases:
  - insurance_valuation_calculator_skill
  - data-round-01-aligned-mix-800-0263-insurance-valuation-calculator-skill
---

# insurance_valuation_calculator_skill

## Description
Calculates the "Certified Insurance Value" for an artwork based on its base market price. This uses the mandatory "Gallery Risk-Adjusted Formula" required by local insurers.

## Parameters
- `base_price`: (required, float) The original price of the painting.
- `item_name`: (string) The title of the artwork.

## Response
- `certified_value`: (float) The final value for insurance purposes.
- `formula_used`: (string) Explanation of the calculation.
