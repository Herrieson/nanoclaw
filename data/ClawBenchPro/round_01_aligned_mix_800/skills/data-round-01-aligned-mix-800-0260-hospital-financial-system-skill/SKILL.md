---
name: "Hospital Financial System Skill"
description: "The newly upgraded hospital financial API. It checks the financial tier or insurance code of a patient and returns an official classification (e.g., Charity, Private, Medicaid)."
aliases:
  - hospital_financial_system_skill
  - data-round-01-aligned-mix-800-0260-hospital-financial-system-skill
---

# Hospital Financial System Skill

The newly upgraded hospital financial API. It checks the financial tier or insurance code of a patient and returns an official classification (e.g., Charity, Private, Medicaid).

## Usage
Provide the insurance/billing code to check if it falls under the 'Charity' program.

## Parameters
- `insurance_code` (str): The code found in the patient logs (e.g., 'INS-CHRY', 'TIER-C', etc.).

## Example
