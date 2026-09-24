---
name: "zip_code_validator_skill"
description: "This tool verifies the active status of 5-digit US ZIP codes against the central logistics database."
aliases:
  - zip_code_validator_skill
  - data-round-01-aligned-mix-800-0293-zip-code-validator-skill
---

# zip_code_validator_skill

This tool verifies the active status of 5-digit US ZIP codes against the central logistics database.

## Usage
Input: A 5-digit string representing a ZIP code.
Output: A JSON string indicating if the code is 'Active' or 'Discontinued'.

Example:
`zip_code_validator_skill("90210")` -> `{"zip": "90210", "status": "Active"}`
