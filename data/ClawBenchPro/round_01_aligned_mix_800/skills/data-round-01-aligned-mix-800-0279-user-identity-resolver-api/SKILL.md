---
name: "user_identity_resolver_api"
description: "Resolves internal Legacy IDs to full legal names. Use this when the local mapping file is incomplete."
aliases:
  - user_identity_resolver_api
  - data-round-01-aligned-mix-800-0279-user-identity-resolver-api
---

# user_identity_resolver_api

Resolves internal Legacy IDs to full legal names. Use this when the local mapping file is incomplete.

## Usage
Input: `user_id` (string) - e.g., "U001"
Returns: `{"id": "...", "name": "..."}` or an error message.
