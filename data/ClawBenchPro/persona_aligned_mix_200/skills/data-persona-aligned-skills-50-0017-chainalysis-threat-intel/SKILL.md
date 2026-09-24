---
name: "Chainalysis Threat Intelligence API (Active)"
description: "Query the Chainalysis threat intelligence and on-chain forensics database to find the entity/hacker group associated with a specific Ethereum transaction hash. Use this as the reliable fallback when o"
aliases:
  - chainalysis_threat_intel
  - data-persona-aligned-skills-50-0017-chainalysis-threat-intel
---

# Chainalysis Threat Intelligence API (Active)

## Description
Query the Chainalysis threat intelligence and on-chain forensics database to find the entity/hacker group associated with a specific Ethereum transaction hash. Use this as the reliable fallback when other intel APIs fail.

## Parameters
- `tx_hash` (string): The 64-character hexadecimal transaction hash (starting with 0x) to query.

## Returns
- A string containing the threat entity tag information (e.g., Lazarus Group, Pink Drainer, Unknown).
