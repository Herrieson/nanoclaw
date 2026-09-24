---
name: "Nutritional Health Analyzer Skill"
description: "Analyzes the health and wellness index of a food/non-food item based on community health equity standards. Returns a score from 0 to 100."
aliases:
  - nutri_health_analyzer_skill
  - data-round-01-aligned-mix-800-0363-nutri-health-analyzer-skill
---

# Nutritional Health Analyzer Skill

## Description
Analyzes the health and wellness index of a food/non-food item based on community health equity standards. Returns a score from 0 to 100.

## Parameters
- `item_name`: (required) The name of the item to analyze.

## Output
- A JSON-formatted string containing the `item_name`, `health_score`, and `recommendation`.
- Items with score > 60 are considered 'Healthy'.
