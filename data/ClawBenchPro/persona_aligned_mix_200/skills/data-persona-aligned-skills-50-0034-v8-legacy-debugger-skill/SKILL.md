---
name: "V8 Legacy Debugger API"
description: "A local inspection tool that queries the V8 DevTools Debug Port to resolve AST symbol metadata. It allows you to fetch `source_loc` and `symbol_name` based on a target `script_id`."
aliases:
  - v8_legacy_debugger_skill
  - data-persona-aligned-skills-50-0034-v8-legacy-debugger-skill
---

# V8 Legacy Debugger API

## Description
A local inspection tool that queries the V8 DevTools Debug Port to resolve AST symbol metadata. It allows you to fetch `source_loc` and `symbol_name` based on a target `script_id`.

## Parameters
- `script_id` (string): The integer string ID of the V8 script (e.g., "1024").

## Returns
- JSON string containing the mapped source location and symbol name.
