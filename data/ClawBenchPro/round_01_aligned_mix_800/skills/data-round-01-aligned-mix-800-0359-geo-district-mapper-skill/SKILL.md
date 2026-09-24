---
name: "geo_district_mapper_skill"
description: "Converts location codes (e.g., LOC-E101) into administrative districts (East, West, North, South)."
aliases:
  - geo_district_mapper_skill
  - data-round-01-aligned-mix-800-0359-geo-district-mapper-skill
---

# geo_district_mapper_skill

Converts location codes (e.g., LOC-E101) into administrative districts (East, West, North, South).

## Usage
Input: A JSON string containing a list of codes.
Example: `{"codes": ["LOC-E101", "LOC-S999"]}`
Output: A mapping of code to district.
