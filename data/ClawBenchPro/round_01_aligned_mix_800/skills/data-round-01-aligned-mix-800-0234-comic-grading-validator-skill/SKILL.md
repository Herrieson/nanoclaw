---
name: "Comic Grading Validator Skill"
description: "This skill converts non-numeric comic book condition descriptions (like 'Near Mint', 'VF/NM') into the standard 10.0 numeric scale used by CGC/CBCS."
aliases:
  - comic_grading_validator_skill
  - data-round-01-aligned-mix-800-0234-comic-grading-validator-skill
---

# Comic Grading Validator Skill

This skill converts non-numeric comic book condition descriptions (like "Near Mint", "VF/NM") into the standard 10.0 numeric scale used by CGC/CBCS.

**Input**: A string representing the condition (e.g., "VF 8.0", "Near Mint").
**Output**: A float value between 0.1 and 10.0.
