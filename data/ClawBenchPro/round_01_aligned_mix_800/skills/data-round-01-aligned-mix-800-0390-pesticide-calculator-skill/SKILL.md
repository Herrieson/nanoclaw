---
name: "Pesticide Calculator Skill"
description: "This tool calculates the total chemical usage (in ounces) from field notes. It handles unit conversions (like 'pumps' to 'ounces') and sums multiple entries."
aliases:
  - pesticide_calculator_skill
  - data-round-01-aligned-mix-800-0390-pesticide-calculator-skill
---

# Pesticide Calculator Skill

This tool calculates the total chemical usage (in ounces) from field notes. It handles unit conversions (like "pumps" to "ounces") and sums multiple entries.

**Usage:**
Pass the raw text or a list of specific usage snippets to the tool.

**Input Format:**
`{"notes": ["2.5 oz", "12 pumps of spot treatment"]}`

**Conversion Logic:**
- 1 pump = 0.25 ounces.
- Standard oz values are taken as-is.
