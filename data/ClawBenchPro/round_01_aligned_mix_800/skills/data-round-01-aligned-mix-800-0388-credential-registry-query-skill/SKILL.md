---
name: "credential_registry_query_skill"
description: "Access the State Counselor Licensing Digital Registry to verify the current status of a counselor. Mandatory for users marked as 'REFER_TO_REGISTRY'."
aliases:
  - credential_registry_query_skill
  - data-round-01-aligned-mix-800-0388-credential-registry-query-skill
---

# credential_registry_query_skill

## Description
Access the State Counselor Licensing Digital Registry to verify the current status of a counselor. Mandatory for users marked as 'REFER_TO_REGISTRY'.

## Parameters
- `query`: string, the name or staff_id of the counselor.

## Response
- A JSON string containing the official license status: `ACTIVE`, `EXPIRED`, or `NOT_FOUND`.
