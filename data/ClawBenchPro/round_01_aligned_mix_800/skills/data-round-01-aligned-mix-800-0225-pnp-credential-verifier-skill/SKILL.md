---
name: "pnp_credential_verifier_skill"
description: "Mandatory tool to verify the current background check status of volunteers. Even if a name is on the whitelist, their credentials might have expired."
aliases:
  - pnp_credential_verifier_skill
  - data-round-01-aligned-mix-800-0225-pnp-credential-verifier-skill
---

# pnp_credential_verifier_skill

Mandatory tool to verify the current background check status of volunteers. Even if a name is on the whitelist, their credentials might have expired.

**Parameters**:
- `volunteer_name`: String. The full name of the volunteer.

**Output**:
- `status`: "ACTIVE", "EXPIRED", or "NOT_FOUND".
