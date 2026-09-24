---
name: "insurance_premium_validator_skill"
description: "Use this skill to retrieve the 'Emergency Fund' tax percentage for specific insurance packages and grades."
aliases:
  - insurance_premium_validator_skill
  - data-round-01-aligned-mix-800-0271-insurance-premium-validator-skill
---

# insurance_premium_validator_skill

Use this skill to retrieve the "Emergency Fund" tax percentage for specific insurance packages and grades.

## Arguments
- `package_name`: (string) "Premium" or "Standard".
- `grade`: (int) The student's grade level.

## Output
A JSON string containing the `percentage` as a decimal (e.g., 0.1 for 10%).
