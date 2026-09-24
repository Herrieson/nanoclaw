---
name: "texas_geo_validator_skill"
description: "Internal Texas Express GIS API. Returns the authoritative delivery zone for a given Texas Zip Code."
aliases:
  - texas_geo_validator_skill
  - data-round-01-aligned-mix-800-0371-texas-geo-validator-skill
---

# texas_geo_validator_skill

## Description
Internal Texas Express GIS API. Returns the authoritative delivery zone for a given Texas Zip Code.

## Parameters
- `zip_code`: (required) String, the 5-digit zip code to verify.

## Returns
A JSON object: `{"zip_code": "...", "correct_zone": "..."}`.
