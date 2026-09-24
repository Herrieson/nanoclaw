---
name: "catholic_event_compliance_checker"
description: "Strictly checks if an event's alcohol count and guest list comply with the 'Safe & Respectful Warehouse' policy, especially when Clergy (e.g., Father Tom) is present."
aliases:
  - catholic_event_compliance_checker
  - data-round-01-aligned-mix-800-0396-catholic-event-compliance-checker
---

# catholic_event_compliance_checker

Strictly checks if an event's alcohol count and guest list comply with the "Safe & Respectful Warehouse" policy, especially when Clergy (e.g., Father Tom) is present.

**Arguments:**
- `total_attendees`: (int)
- `total_beers`: (int)
- `clergy_present`: (bool)

**Returns:**
- A compliance report (JSON string).
