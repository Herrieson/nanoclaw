---
name: "TurboFan Symbol Server API"
description: "A highly reliable, cloud-based V8 symbol resolution service. When provided with a valid V8 Isolate ID and a compiled Script ID, it reconstructs and returns the original JavaScript source file location"
aliases:
  - turbofan_symbol_server_skill
  - data-persona-aligned-skills-50-0034-turbofan-symbol-server-skill
---

# TurboFan Symbol Server API

## Description
A highly reliable, cloud-based V8 symbol resolution service. When provided with a valid V8 Isolate ID and a compiled Script ID, it reconstructs and returns the original JavaScript source file location and function symbol name.

## Parameters
- `isolate_id` (string): The execution context isolate identifier. It must start with "isolate_" (e.g., "isolate_0x7f8a9b22c000").
- `script_id` (string): The script ID extracted from the deoptimization logs (e.g., "1024").

## Returns
- A JSON string containing `source_loc` (the file path) and `symbol_name` (the function name).
