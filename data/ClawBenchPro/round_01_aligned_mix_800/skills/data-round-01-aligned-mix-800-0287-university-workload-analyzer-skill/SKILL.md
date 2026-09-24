---
name: "university_workload_analyzer_skill"
description: "A specialized utility designed to decrypt and parse University HR `.dat` log files. It extracts faculty names and their reported hours for Teaching, Research, and Administration."
aliases:
  - university_workload_analyzer_skill
  - data-round-01-aligned-mix-800-0287-university-workload-analyzer-skill
---

# university_workload_analyzer_skill

## Description
A specialized utility designed to decrypt and parse University HR `.dat` log files. It extracts faculty names and their reported hours for Teaching, Research, and Administration.

## Parameters
- `file_path`: (string, required) The absolute or relative path to the `.dat` file.
- `extraction_mode`: (string, optional) Set to "full" for all fields.

## Usage
Calling this tool returns a JSON string containing the extracted faculty data.
