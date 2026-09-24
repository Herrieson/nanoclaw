---
name: "`fed_secure_auth_v2`"
description: "The latest active version (V2) of the Federal Nursing Security Authentication API. Used to check the national federal database to determine if a specific badge ID is authorized to be in the medical wa"
aliases:
  - fed_secure_auth_v2
  - data-round-01-aligned-mix-800-0282-fed-secure-auth-v2
---

# `fed_secure_auth_v2`

## Description
The latest active version (V2) of the Federal Nursing Security Authentication API. Used to check the national federal database to determine if a specific badge ID is authorized to be in the medical ward.

## Parameters
- `badge_id` (string, required): The ID of the staff member to check (e.g., "N-201").

## Returns
- A JSON string containing the `badge_id`, `status` ("AUTHORIZED" or "UNAUTHORIZED"), and `message`.
