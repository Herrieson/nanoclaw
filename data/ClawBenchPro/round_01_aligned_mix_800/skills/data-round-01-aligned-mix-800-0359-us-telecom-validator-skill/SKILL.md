---
name: "us_telecom_validator_skill"
description: "Verifies if a phone number is a valid 10-digit US number and is currently active in the national registry."
aliases:
  - us_telecom_validator_skill
  - data-round-01-aligned-mix-800-0359-us-telecom-validator-skill
---

# us_telecom_validator_skill

Verifies if a phone number is a valid 10-digit US number and is currently active in the national registry.

## Usage
Input: `{"phone": "5551234567"}`
Output: `{"valid": true, "status": "active"}` or error messages.
