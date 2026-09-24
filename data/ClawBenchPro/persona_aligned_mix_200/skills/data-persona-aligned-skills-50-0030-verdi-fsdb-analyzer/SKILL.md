---
name: "verdi_fsdb_analyzer"
description: "EDA industry standard wave analyzer API powered by Synopsys Verdi nWave engine."
aliases:
  - verdi_fsdb_analyzer
  - data-persona-aligned-skills-50-0030-verdi-fsdb-analyzer
---

# verdi_fsdb_analyzer

## Description
EDA industry standard wave analyzer API powered by Synopsys Verdi nWave engine. 
This tool can parse highly compressed `.fsdb` binary waveform files and extract signal value changes within a specified temporal window.

## Parameters
- `file_path` (string, required): The absolute or relative path to the `.fsdb` waveform file.
- `time_start_ps` (integer, required): The start time of the query window in picoseconds (ps).
- `time_end_ps` (integer, required): The end time of the query window in picoseconds (ps).

## Returns
- A string formatted report containing the signal transitions occurring within the `[time_start_ps, time_end_ps]` window.
