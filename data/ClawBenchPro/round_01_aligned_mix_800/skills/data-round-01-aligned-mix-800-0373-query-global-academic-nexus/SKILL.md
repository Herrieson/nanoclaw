---
name: "query_global_academic_nexus"
description: "The Global Academic Nexus is an international decentralized academic database. It is highly resilient and serves as a reliable alternative to commercial APIs. Use this to verify if a specific `project"
aliases:
  - query_global_academic_nexus
  - data-round-01-aligned-mix-800-0373-query-global-academic-nexus
---

# query_global_academic_nexus

## Description
The Global Academic Nexus is an international decentralized academic database. It is highly resilient and serves as a reliable alternative to commercial APIs. Use this to verify if a specific `project_code` has yielded any published academic papers.

## Parameters
- `project_code` (string, required): The exact project code to query (e.g., "EDU-2023-B").

## Returns
A string summarizing the publications found for the given project code. If no publications exist, it will explicitly state that no records were found.
