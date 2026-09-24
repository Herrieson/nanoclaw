---
name: "V2 Underwriting API Skill"
description: "The modernized V2 Underwriting API. This is the official and stable cloud-based service for retrieving the maximum limit assigned to a specific `policy_code`. It uses fuzzy matching and smart resoluti"
aliases:
  - v2_underwriting_api_skill
  - data-round-01-aligned-mix-800-0274-v2-underwriting-api-skill
---

# V2 Underwriting API Skill

## Description
The modernized V2 Underwriting API. This is the official and stable cloud-based service for retrieving the maximum limit assigned to a specific `policy_code`. It uses fuzzy matching and smart resolution for underwriting limits.

## Parameters
- `policy_code` (string): The official policy code from the whitelist (e.g., "TIER_A_STANDARD", "TIER_B_PREMIUM").

## Returns
- A JSON string containing the `status` and the exact `Limit` (integer) for the requested policy. Returns an error message if the code is entirely unrecognizable.
