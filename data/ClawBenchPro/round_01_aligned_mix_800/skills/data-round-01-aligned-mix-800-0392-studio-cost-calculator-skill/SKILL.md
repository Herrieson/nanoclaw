---
name: "studio_cost_calculator_skill"
description: "Queries the internal studio billing system to get official billable hours for a specific Session ID."
aliases:
  - studio_cost_calculator_skill
  - data-round-01-aligned-mix-800-0392-studio-cost-calculator-skill
---

# studio_cost_calculator_skill

Queries the internal studio billing system to get official billable hours for a specific Session ID.

**Parameters:**
- `session_id`: The ID found in the studio log (e.g., SE-101).

**Returns:**
The precise decimal hours billed for that session.
