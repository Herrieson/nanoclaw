---
name: oakbridge_legacy_sap_query
description: Queries the legacy on-premise SAP ERP system to fetch the approved hourly rate for a specific subcontractor.
parameters:
  - name: contractor_name
    type: string
    description: The name of the subcontractor to lookup.
    required: true
---

# Oakbridge Legacy SAP Query
This tool sends a request to the company's legacy on-premise SAP ERP system to retrieve subcontractor contract details and approved hourly billing rates.
