---
name: "nova_telemetry_query_skill"
description: "Query the newly deployed V2 Nova RLHF cluster telemetry database for a specific trajectory ID."
aliases:
  - nova_telemetry_query_skill
  - data-persona-aligned-skills-50-0016-nova-telemetry-query-skill
---

# nova_telemetry_query_skill

## Description
Query the newly deployed V2 Nova RLHF cluster telemetry database for a specific trajectory ID. 
This tool reliably fetches the complete conversational records (including assistant tool calls) and execution metadata (like `finish_reason`).

## Parameters
- `traj_id` (string): The target trajectory ID to query (e.g., 'T-1001').

## Returns
- A JSON string representing the full trajectory, typically containing `traj_id`, `conversations` list, and `metadata` dict.
