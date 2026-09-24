---
name: "property_emergency_classifier_skill"
description: "A specialized NLP tool for the real estate industry. It analyzes a maintenance note and classifies it as 'EMERGENCY' or 'ROUTINE'. It also provides a severity score (1-10)."
aliases:
  - property_emergency_classifier_skill
  - data-round-01-aligned-mix-800-0240-property-emergency-classifier-skill
---

# property_emergency_classifier_skill

## Description
A specialized NLP tool for the real estate industry. It analyzes a maintenance note and classifies it as 'EMERGENCY' or 'ROUTINE'. It also provides a severity score (1-10).

## Parameters
- `text`: (Required) String. The text content of the maintenance note.

## Returns
A JSON string containing `classification` and `severity`.
