---
name: "Spectro Color Analyzer Skill"
description: "Use this tool to analyze raw `.dat` spectral sensor files from wood stain batches. It returns the calculated pigment percentages."
aliases:
  - spectro_color_analyzer_skill
  - data-round-01-aligned-mix-800-0275-spectro-color-analyzer-skill
---

# Spectro Color Analyzer Skill

Use this tool to analyze raw `.dat` spectral sensor files from wood stain batches. It returns the calculated pigment percentages.

**Inputs:**
- `file_path`: (string) Path to the `.dat` file.

**Output:**
- A JSON string containing the `red_pigment_pct`, `blue_pigment_pct`, and `yellow_pigment_pct`.
