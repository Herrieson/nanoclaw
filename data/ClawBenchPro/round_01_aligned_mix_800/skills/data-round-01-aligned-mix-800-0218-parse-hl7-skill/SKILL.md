---
name: "`parse_hl7_skill`"
description: "A specialized hospital IT tool designed to parse raw `.hl7` medical system export files and extract human-readable patient information."
aliases:
  - parse_hl7_skill
  - data-round-01-aligned-mix-800-0218-parse-hl7-skill
---

# `parse_hl7_skill`

## Description
A specialized hospital IT tool designed to parse raw `.hl7` medical system export files and extract human-readable patient information.

## Parameters
- `file_path` (string): The relative or absolute path to the `.hl7` file to be parsed.

## Returns
- A JSON-formatted string containing a list of dictionaries with extracted patient `Patient_Name`, `Primary_Language`, and `Diagnosis`.

## Example Usage
