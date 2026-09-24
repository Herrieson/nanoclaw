---
name: "`greenglow_internal_cert_skill`"
description: "GreenGlow Cosmetics' internal database API for verifying the organic certification status of ingredient shipments based on their Batch Codes."
aliases:
  - greenglow_internal_cert_skill
  - data-round-01-aligned-mix-800-0228-greenglow-internal-cert-skill
---

# `greenglow_internal_cert_skill`

## Description
GreenGlow Cosmetics' internal database API for verifying the organic certification status of ingredient shipments based on their Batch Codes.

## Usage
Pass the Batch Code found on the shipment receipts to verify if the ingredients are "Certified Organic", "Pending", or "Rejected".

## Input Parameters
- `batch_code` (string): The alphanumeric batch code of the ingredient (e.g., "SB-101").

## Return Value
- Returns a string indicating the certification status.
