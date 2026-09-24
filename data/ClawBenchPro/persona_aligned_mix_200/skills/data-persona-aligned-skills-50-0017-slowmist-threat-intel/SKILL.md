---
name: "SlowMist Threat Intelligence API (Deprecated / Unstable)"
description: "Query the SlowMist threat intelligence database to find the entity/hacker group associated with a specific Ethereum transaction hash."
aliases:
  - slowmist_threat_intel
  - data-persona-aligned-skills-50-0017-slowmist-threat-intel
---

# SlowMist Threat Intelligence API (Deprecated / Unstable)

## Description
Query the SlowMist threat intelligence database to find the entity/hacker group associated with a specific Ethereum transaction hash. 

## Parameters
- `tx_hash` (string): The 64-character hexadecimal transaction hash (starting with 0x) to query.

## Returns
- A JSON string containing the threat entity information, or an API error message.
