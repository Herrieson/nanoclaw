---
name: "Grid Outage Verifier Skill"
description: "Retrieves precise outage duration from the power grid's historical sensor data. Essential when internal logs are vague (e.g., 'afternoon')."
aliases:
  - grid_outage_verifier_skill
  - data-round-01-aligned-mix-800-0299-grid-outage-verifier-skill
---

# Grid Outage Verifier Skill

Retrieves precise outage duration from the power grid's historical sensor data. Essential when internal logs are vague (e.g., "afternoon").

**Input:**
- `account_id`: (string)
- `vague_time`: (string) The description from the rep's log.

**Output:**
- Precise `hours` (float).
