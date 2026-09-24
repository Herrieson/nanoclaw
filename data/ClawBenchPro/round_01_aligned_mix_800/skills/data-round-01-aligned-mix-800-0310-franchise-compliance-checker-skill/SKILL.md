---
name: franchise_compliance_checker
description: Queries the internal restaurant compliance database to check the operational status of a specific branch. Due to an export error, this is the only reliable way to check if a branch is active or closed.
parameters:
  type: object
  properties:
    branch_id:
      type: string
      description: The unique identifier of the branch (e.g., "101", "102").
  required:
    - branch_id
---
