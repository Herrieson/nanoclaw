---
name: "query_elastic_apm_skill"
description: "Query the legacy Elastic APM centralized logging system by providing a crash report ID. This system was historically used to fetch detailed error stack traces and memory payloads."
aliases:
  - query_elastic_apm_skill
  - data-persona-aligned-skills-50-0026-query-elastic-apm-skill
---

# query_elastic_apm_skill

## Description
Query the legacy Elastic APM centralized logging system by providing a crash report ID. This system was historically used to fetch detailed error stack traces and memory payloads.

## Parameters
- `report_id` (string): The crash report ID (e.g., "CRASH-REPORT-XXXX-XX").

## Returns
- A string formatted as a JSON response containing the report details or error messages.
