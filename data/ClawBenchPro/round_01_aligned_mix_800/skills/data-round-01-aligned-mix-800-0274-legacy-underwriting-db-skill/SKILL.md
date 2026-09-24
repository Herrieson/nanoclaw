---
name: "Legacy Underwriting DB Skill"
description: "This is the V1 legacy local database query tool for insurance policy underwriting limits. It accepts a `policy_code` and attempts to connect to the internal legacy database to fetch the maximum claim "
aliases:
  - legacy_underwriting_db_skill
  - data-round-01-aligned-mix-800-0274-legacy-underwriting-db-skill
---

# Legacy Underwriting DB Skill

## Description
This is the V1 legacy local database query tool for insurance policy underwriting limits. It accepts a `policy_code` and attempts to connect to the internal legacy database to fetch the maximum claim limit.

## Parameters
- `policy_code` (string): The code representing the policy tier (e.g., TIER_A_STANDARD).

## Returns
- A string representing the maximum limit for the policy, or an error message if the query fails.
