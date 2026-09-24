---
name: "dietary_risk_assessor_skill"
description: "Analyzes a dietary restriction string and determines if it requires 'Special Chow' preparation."
aliases:
  - dietary_risk_assessor_skill
  - data-round-01-aligned-mix-800-0257-dietary-risk-assessor-skill
---

# dietary_risk_assessor_skill

Analyzes a dietary restriction string and determines if it requires "Special Chow" preparation.

## Parameters
- `restriction_text`: String. The dietary restriction field from personnel logs (e.g., "Peanut Allergy", "None", "Vegan").

## Output
"Standard" or "High Risk - Special Chow Required".
