---
name: "Eco Impact Validator Skill"
description: "Calculates if a chemical batch meets the 'Green Initiative' standards. It applies real-time 'Environmental Compensation Coefficients' which are required for official auditing."
aliases:
  - eco_impact_validator_skill
  - data-round-01-aligned-mix-800-0231-eco-impact-validator-skill
---

# Eco Impact Validator Skill

## Description
Calculates if a chemical batch meets the "Green Initiative" standards. It applies real-time "Environmental Compensation Coefficients" which are required for official auditing.

## Parameters
- `total_weight`: (Required) Float. Total weight of the batch.
- `recycled_weight`: (Required) Float. Weight of recycled inputs.

## Returns
- A JSON object with `is_compliant` (boolean) and `calculated_percentage`.
