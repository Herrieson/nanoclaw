---
name: "dve_extractor"
description: "Legacy waveform extraction utility based on Discovery Visual Environment (DVE). Can be used to dump values from various waveform databases (VCD, VPD, FSDB) into readable ASCII format for a specific ti"
aliases:
  - dve_extractor
  - data-persona-aligned-skills-50-0030-dve-extractor
---

# dve_extractor

## Description
Legacy waveform extraction utility based on Discovery Visual Environment (DVE). Can be used to dump values from various waveform databases (VCD, VPD, FSDB) into readable ASCII format for a specific time range.

## Parameters
- `file_path` (string, required): Path to the waveform file.
- `time_start_ps` (integer, required): Time to begin extraction.
- `time_end_ps` (integer, required): Time to end extraction.

## Returns
- String output of the waveform ASCII dump or execution status.
