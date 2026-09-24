---
name: "optical_frame_analyzer_skill"
description: "Analyzes the structural integrity of eyewear frames based on item type/description."
aliases:
  - optical_frame_analyzer_skill
  - data-round-01-aligned-mix-800-0316-optical-frame-analyzer-skill
---

# optical_frame_analyzer_skill

Analyzes the structural integrity of eyewear frames based on item type/description.

## Parameters
- `item_description`: String. The type of glasses (e.g., "Aviators").

## Returns
JSON string: `{"condition": "Usable" | "Scrap", "confidence": float}`
