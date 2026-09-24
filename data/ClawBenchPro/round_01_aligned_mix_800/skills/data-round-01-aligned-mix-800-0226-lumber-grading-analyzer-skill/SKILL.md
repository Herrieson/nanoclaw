---
name: "lumber_grading_analyzer_skill"
description: "Analyzes lumber defect codes to determine if a board is 'Furniture Grade' (Usable) or 'Industrial Grade' (Rejected)."
aliases:
  - lumber_grading_analyzer_skill
  - data-round-01-aligned-mix-800-0226-lumber-grading-analyzer-skill
---

# lumber_grading_analyzer_skill

## Description
Analyzes lumber defect codes to determine if a board is "Furniture Grade" (Usable) or "Industrial Grade" (Rejected).

## Parameters
- `defect_code`: string (e.g., "KN-0", "CR-1", "RO-9").

## Returns
- A JSON object indicating `status` ("Furniture Grade" or "Rejected") and a brief reason.
