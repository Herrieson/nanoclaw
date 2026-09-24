---
name: "legacy_ticket_parser_skill"
description: "Decodes and parses the legacy Texas Express `.dat` files which are UTF-16 encoded and base64 wrapped."
aliases:
  - legacy_ticket_parser_skill
  - data-round-01-aligned-mix-800-0371-legacy-ticket-parser-skill
---

# legacy_ticket_parser_skill

## Description
Decodes and parses the legacy Texas Express `.dat` files which are UTF-16 encoded and base64 wrapped.

## Parameters
- `file_path`: (required) String, the path to the .dat file.

## Returns
A list of dictionaries containing ticket information: `ticket_id`, `zip_code`, `assigned_zone`, and `issue`.
