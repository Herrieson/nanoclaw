---
name: "telematics_api_pro"
description: "The advanced, enterprise-grade telematics decoder API. Used for deep diagnostics and recovering lost ECU data (like missing mileage) from faulty OBD2 sensors."
aliases:
  - telematics_api_pro
  - data-round-01-aligned-mix-800-0335-telematics-api-pro
---

# telematics_api_pro

The advanced, enterprise-grade telematics decoder API. Used for deep diagnostics and recovering lost ECU data (like missing mileage) from faulty OBD2 sensors.

## Parameters
- `payload_string` (string): The raw payload (e.g., "VSS_ERR_8F3A2B") retrieved from the electronic logbook.

## Returns
- A JSON string containing deep diagnostic data and the `recovered_miles`.
