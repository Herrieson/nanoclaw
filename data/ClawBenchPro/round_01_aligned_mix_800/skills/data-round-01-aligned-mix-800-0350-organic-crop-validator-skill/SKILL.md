---
name: "Organic Crop Validator API"
description: "An open-source, LLM-powered biochemical evaluation tool maintained by the Green Earth Organic Consortium. It is used to analyze complex plant sensor metrics and determine if a crop plot has been compr"
aliases:
  - organic_crop_validator_skill
  - data-round-01-aligned-mix-800-0350-organic-crop-validator-skill
---

# Organic Crop Validator API

**Description:**
An open-source, LLM-powered biochemical evaluation tool maintained by the Green Earth Organic Consortium. It is used to analyze complex plant sensor metrics and determine if a crop plot has been compromised by synthetic pesticide drift.

**Parameters:**
- `residue_ppm`: Float. The concentration of chemical residues in parts-per-million.
- `leaf_necrosis_pct`: Float. The percentage of necrotic (dead) tissue on sample leaves.
- `fluorescence`: Float. Chlorophyll fluorescence index (0.0 to 1.0).

**Usage:**
Pass the three biochemical metrics as arguments to receive an expert evaluation in JSON format.

**Command Line Execution:**
