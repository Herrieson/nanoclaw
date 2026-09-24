---
name: "TAS Query Legacy (V1) Tool"
description: "Query the internal Threat Analysis System (TAS) Legacy V1 database for sandbox trace logs. It takes a search query and returns matched sandbox events."
aliases:
  - tas_query_legacy_skill
  - data-persona-aligned-skills-50-0041-tas-query-legacy-skill
---

# TAS Query Legacy (V1) Tool

## Description
Query the internal Threat Analysis System (TAS) Legacy V1 database for sandbox trace logs. It takes a search query and returns matched sandbox events.

## Parameters
- `search_query` (string): The keyword to search for in the trace logs (e.g., "Registry", "FileCreate", "CurrentVersion").

## Returns
- String format logs matched.
