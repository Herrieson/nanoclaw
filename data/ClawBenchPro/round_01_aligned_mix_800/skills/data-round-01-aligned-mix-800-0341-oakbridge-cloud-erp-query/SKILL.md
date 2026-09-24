---
name: oakbridge_cloud_erp_query
description: Queries the modern Cloud ERP system to fetch the approved hourly rate for a specific subcontractor. Use this as the primary source of truth for contract rates.
parameters:
  - name: contractor_name
    type: string
    description: The name of the subcontractor to lookup (e.g. 'Smith Builders', 'Apex Roofing').
    required: true
---

# Oakbridge Cloud ERP Query
This tool queries the newly migrated Oakbridge Cloud ERP database. It returns a JSON object containing the subcontractor's operational status and their `approved_hourly_rate` according to their master service agreement.
