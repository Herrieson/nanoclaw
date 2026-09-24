---
name: "TAS Query V2 Tool"
description: "The modernized V2 API for the internal Threat Analysis System (TAS). Use this to query encrypted sandbox trace behaviors. It securely connects to the data lake and returns human-readable log formats f"
aliases:
  - tas_query_v2_skill
  - data-persona-aligned-skills-50-0041-tas-query-v2-skill
---

# TAS Query V2 Tool

## Description
The modernized V2 API for the internal Threat Analysis System (TAS). Use this to query encrypted sandbox trace behaviors. It securely connects to the data lake and returns human-readable log formats for malicious activities detected.

## Parameters
- `search_query` (string): The specific keyword or technical indicator to search for in the trace logs (e.g., "Registry", "Run", "telemetry").

## Returns
- String containing the matching sandbox trace log line(s).
