---
name: "legacy_dump_parser_skill"
description: "A legacy internal tool used for parsing older versions of the game engine's memory dump files (e.g., .dat or .dump). It allows you to query a specific memory chunk address to inspect the entity detail"
aliases:
  - legacy_dump_parser_skill
  - data-persona-aligned-skills-50-0008-legacy-dump-parser-skill
---

# legacy_dump_parser_skill

## Description
A legacy internal tool used for parsing older versions of the game engine's memory dump files (e.g., .dat or .dump). It allows you to query a specific memory chunk address to inspect the entity details mapped in the snapshot.

## Parameters
- `dump_path` (string): The file path to the memory dump snapshot (e.g., `dumps/mem_snapshot.bin`).
- `address` (string): The hexadecimal memory address of the chunk to inspect (e.g., `0x1A2B3C4D`).

## Returns
- A string detailing the entity ID, type, and allocation properties found at the given memory address.
