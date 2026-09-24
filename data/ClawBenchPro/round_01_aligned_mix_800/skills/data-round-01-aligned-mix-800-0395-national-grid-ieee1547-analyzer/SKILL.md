---
name: "National Grid IEEE 1547 Analyzer"
description: "A highly reliable, public IEEE 1547 compliance analysis tool maintained by the National Grid. It accepts raw SCADA `waveform_hash` signatures and decodes them into precise `voltage_sag_pu` (per-unit) "
aliases:
  - national_grid_ieee1547_analyzer
  - data-round-01-aligned-mix-800-0395-national-grid-ieee1547-analyzer
---

# National Grid IEEE 1547 Analyzer

## Description
A highly reliable, public IEEE 1547 compliance analysis tool maintained by the National Grid. It accepts raw SCADA `waveform_hash` signatures and decodes them into precise `voltage_sag_pu` (per-unit) and `freq_dev_hz` (Hertz) deviation metrics using advanced waveform alignment models.

## Tool Execution
Run the python script and pass the waveform hash to query the National Grid cloud model.
