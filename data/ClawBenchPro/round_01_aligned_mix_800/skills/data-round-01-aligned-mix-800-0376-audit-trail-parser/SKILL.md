---
name: "`audit_trail_parser` Skill"
description: "A specialized utility designed to parse proprietary IT audit trail binary files (`.bin` format) exported from legacy systems. It strips the proprietary magic headers and decrypts the base64-encoded te"
aliases:
  - audit_trail_parser
  - data-round-01-aligned-mix-800-0376-audit-trail-parser
---

# `audit_trail_parser` Skill

## Description
A specialized utility designed to parse proprietary IT audit trail binary files (`.bin` format) exported from legacy systems. It strips the proprietary magic headers and decrypts the base64-encoded telemetry payloads, returning the human-readable structured logs (usually in CSV format).

## Usage
Provide the file path to the `.bin` file.

## Parameters
- `file_path` (string): The relative or absolute path to the binary audit trail file.

## Example
