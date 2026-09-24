---
name: "OSHA Hazard Classifier Skill"
description: "An AI-powered compliance API that evaluates construction site observations and classifies them according to local city safety codes and OSHA standards."
aliases:
  - osha_hazard_classifier_skill
  - data-round-01-aligned-mix-800-0219-osha-hazard-classifier-skill
---

# OSHA Hazard Classifier Skill
An AI-powered compliance API that evaluates construction site observations and classifies them according to local city safety codes and OSHA standards.

## Usage
Provide the text description of the safety observation. The tool will return an official classification (`CRITICAL`, `IMMEDIATE`, `MINOR`, or `COMPLIANT`) along with a brief explanation.

## Input Parameters
- `observation` (string): The description of the situation at the construction site.

## Output
Returns a JSON-like string detailing the Severity Level and Reason.
