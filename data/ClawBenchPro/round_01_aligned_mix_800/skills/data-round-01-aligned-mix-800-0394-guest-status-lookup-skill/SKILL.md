---
name: "guest_status_lookup_skill"
description: "Queries the restaurant's internal guest database to determine the invitation status of an individual."
aliases:
  - guest_status_lookup_skill
  - data-round-01-aligned-mix-800-0394-guest-status-lookup-skill
---

# guest_status_lookup_skill

Queries the restaurant's internal guest database to determine the invitation status of an individual.

**Parameters:**
- `name`: The full name of the guest.

**Returns:**
- "VIP": Invited guest.
- "CRASHER": Not on the original list.
- "NOT_FOUND": No record of this person.
