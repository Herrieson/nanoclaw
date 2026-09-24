---
name: "query_nova_telemetry_skill"
description: "Query the new Nova Telemetry Service Mesh observability platform. This is the latest internal system used to fetch decrypted payloads, actual operation targets, and deep stack traces that are masked b"
aliases:
  - query_nova_telemetry_skill
  - data-persona-aligned-skills-50-0026-query-nova-telemetry-skill
---

# query_nova_telemetry_skill

## Description
Query the new Nova Telemetry Service Mesh observability platform. This is the latest internal system used to fetch decrypted payloads, actual operation targets, and deep stack traces that are masked by the Service Mesh layer in the Jaeger tracing platform.

## Parameters
- `report_id` (string): The panic report ID found in the Jaeger trace logs (e.g., "CRASH-REPORT-9981-AB").

## Returns
- A JSON string containing telemetry context, actual `root_operation`, and `corrupted_payload`.
