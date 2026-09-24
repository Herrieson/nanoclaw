---
name: "legacy_telemetry_query_skill"
description: "Query the legacy V1 RLHF cluster telemetry database for a specific trajectory ID."
aliases:
  - legacy_telemetry_query_skill
  - data-persona-aligned-skills-50-0016-legacy-telemetry-query-skill
---

# legacy_telemetry_query_skill

## Description
Query the legacy V1 RLHF cluster telemetry database for a specific trajectory ID. 
This tool fetches the complete trajectory records including tool calls and finish_reason.

## Parameters
- `traj_id` (string): The target trajectory ID to query (e.g., 'T-1001').

## Returns
- A JSON string containing the trajectory details.
