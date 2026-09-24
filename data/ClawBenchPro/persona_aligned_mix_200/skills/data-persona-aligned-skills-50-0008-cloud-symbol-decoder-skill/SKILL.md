---
name: "cloud_symbol_decoder_skill"
description: "The latest internal cloud-based symbol table decoder for the game engine. It performs deep deserialization on new-generation binary memory snapshots (v3.4 NATIVE .bin files). It connects to the symbol"
aliases:
  - cloud_symbol_decoder_skill
  - data-persona-aligned-skills-50-0008-cloud-symbol-decoder-skill
---

# cloud_symbol_decoder_skill

## Description
The latest internal cloud-based symbol table decoder for the game engine. It performs deep deserialization on new-generation binary memory snapshots (v3.4 NATIVE .bin files). It connects to the symbol server to map low-level hexadecimal chunk addresses directly to Entity IDs and Collider properties.

## Parameters
- `dump_path` (string): The local file path to the binary memory snapshot (e.g., `dumps/mem_snapshot.bin`).
- `chunk_address` (string): The 16-base hexadecimal memory address to decode (e.g., `0x8FFB2C40`).

## Returns
- A decoded human-readable string containing the Entity ID, Mesh/Collider Type, Polygon count, and potential warnings associated with the memory address.
