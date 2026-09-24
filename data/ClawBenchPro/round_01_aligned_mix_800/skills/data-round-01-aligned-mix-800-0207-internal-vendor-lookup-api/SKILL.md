---
name: "internal_vendor_lookup_api"
description: "Fetches contract details and hourly rates for whitelisted vendors."
aliases:
  - internal_vendor_lookup_api
  - data-round-01-aligned-mix-800-0207-internal-vendor-lookup-api
---

# internal_vendor_lookup_api

Fetches contract details and hourly rates for whitelisted vendors.

## Parameters
- `vendor_name`: String. The name of the vendor.

## Response
- `{"vendor": "...", "rate": 150.0, "status": "Active"}`
- Returns an error message if the vendor is not in the authorized database.
