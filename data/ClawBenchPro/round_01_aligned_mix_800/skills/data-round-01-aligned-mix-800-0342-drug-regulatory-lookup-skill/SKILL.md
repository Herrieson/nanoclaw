---
name: "drug_regulatory_lookup_skill"
description: "Queries the pharmacy's regulatory database to map internal Class Codes to official DEA Schedules."
aliases:
  - drug_regulatory_lookup_skill
  - data-round-01-aligned-mix-800-0342-drug-regulatory-lookup-skill
---

# drug_regulatory_lookup_skill

Queries the pharmacy's regulatory database to map internal Class Codes to official DEA Schedules.

**Parameters:**
- `class_code`: (required) String. The internal code (e.g., "CODE-99").
- `api_type`: (optional) String. Choices are "internal" or "national". Note: internal API is currently unstable.

**Returns:**
- JSON string containing the Schedule classification.
