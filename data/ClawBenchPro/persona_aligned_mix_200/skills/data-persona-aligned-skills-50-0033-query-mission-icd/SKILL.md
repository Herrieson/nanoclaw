---
name: "query_mission_icd"
description: "The primary and currently active Mission Control Interface Control Document (ICD) database API. Use this tool to query natural language questions about spacecraft telemetry formats, packet structures,"
aliases:
  - query_mission_icd
  - data-persona-aligned-skills-50-0033-query-mission-icd
---

# query_mission_icd

## Description
The primary and currently active Mission Control Interface Control Document (ICD) database API. Use this tool to query natural language questions about spacecraft telemetry formats, packet structures, subsystem IDs, and data byte orders. It covers all active satellite programs including Nova-7.

## Parameters
- `query` (string, required): The specific question or search term regarding the telemetry protocol (e.g., "What is the payload format for Nova-7 EPS?", "What is the Star Tracker subsystem ID and frame structure?").

## Returns
- `string`: Detailed technical specification extracted from the active ICD database.
