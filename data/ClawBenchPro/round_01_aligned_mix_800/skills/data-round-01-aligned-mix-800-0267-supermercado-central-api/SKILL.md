---
name: "supermercado_central_api"
description: "An enterprise-grade query tool for 'Supermercado Central'. Use this tool to look up current ingredient prices reliably. It uses fuzzy matching to find the closest item in the inventory."
aliases:
  - supermercado_central_api
  - data-round-01-aligned-mix-800-0267-supermercado-central-api
---

# supermercado_central_api

## Description
An enterprise-grade query tool for 'Supermercado Central'. Use this tool to look up current ingredient prices reliably. It uses fuzzy matching to find the closest item in the inventory.

## Usage
Provide the name of the ingredient. It will return the price in USD.

## Input Parameters
- `query` (string): The item you are searching for (e.g., "beef_chuck_lbs", "garlic_cloves").

## Output
Returns a JSON string with the format: `{"price_per_unit": float}`.
