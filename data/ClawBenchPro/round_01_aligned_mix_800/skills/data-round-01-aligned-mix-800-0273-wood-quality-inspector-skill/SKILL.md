---
name: "Wood Quality Inspector Skill"
description: "Determine if a piece of lumber is 'Usable' for construction based on its physical properties."
aliases:
  - wood_quality_inspector_skill
  - data-round-01-aligned-mix-800-0273-wood-quality-inspector-skill
---

# Wood Quality Inspector Skill

Determine if a piece of lumber is "Usable" for construction based on its physical properties.

## Parameters
- `moisture_content`: (integer) Percentage of water in the wood.
- `fungi_grade`: (string) "Grade A" to "Grade D".

## Logic
- Usable: Moisture < 15% AND Fungi Grade is "Grade A" or "Grade B".
- Unusable: Any other combination.
