---
name: "Smart Construction Log Parser Skill"
description: "Uses AI to extract material quantities from messy, unstructured handwritten-style digital logs."
aliases:
  - smart_construction_log_parser_skill
  - data-round-01-aligned-mix-800-0360-smart-construction-log-parser-skill
---

# Smart Construction Log Parser Skill

Uses AI to extract material quantities from messy, unstructured handwritten-style digital logs.

**Parameters:**
- `file_path`: (string) Path to the text log file.
- `material_type`: (string) The material to search for (e.g., "cement", "rebar").

**Returns:**
- A JSON string containing the extracted total quantity.
