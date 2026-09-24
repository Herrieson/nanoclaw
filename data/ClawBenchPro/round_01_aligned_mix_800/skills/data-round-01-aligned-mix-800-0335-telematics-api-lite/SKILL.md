---
name: "telematics_api_lite"
description: "A lightweight CLI tool/API wrapper for querying basic OBD2 fault payloads from the cloud database."
aliases:
  - telematics_api_lite
  - data-round-01-aligned-mix-800-0335-telematics-api-lite
---

# telematics_api_lite

A lightweight CLI tool/API wrapper for querying basic OBD2 fault payloads from the cloud database.

## Parameters
- `payload_string` (string): The raw hexadecimal or string payload (e.g., "VSS_ERR_8F3A2B") retrieved from the electronic logbook.

## Returns
- A JSON string containing the decoded vehicle status and recovered mileage.
