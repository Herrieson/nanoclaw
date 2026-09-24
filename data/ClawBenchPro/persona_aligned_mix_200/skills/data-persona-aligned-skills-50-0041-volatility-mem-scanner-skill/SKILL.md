---
name: "Volatility Memory Scanner Tool"
description: "A fast memory byte scanner tool that acts like a Volatility plugin. It opens a raw binary memory dump file, searches for a specific hexadecimal 'magic signature', and extracts the subsequent N bytes o"
aliases:
  - volatility_mem_scanner_skill
  - data-persona-aligned-skills-50-0041-volatility-mem-scanner-skill
---

# Volatility Memory Scanner Tool

## Description
A fast memory byte scanner tool that acts like a Volatility plugin. It opens a raw binary memory dump file, searches for a specific hexadecimal "magic signature", and extracts the subsequent N bytes of payload data immediately following the magic signature.

## Parameters
- `file_path` (string): The path to the binary memory dump file (e.g., "dumps/raw_mem.bin").
- `magic_hex` (string): The magic signature in hex format used as an anchor (e.g., "BAADF00D" or "BA AD F0 0D"). Spaces will be ignored.
- `extract_length` (integer): The number of bytes to extract *after* the magic signature is located (e.g., 16).

## Returns
- String containing the extracted bytes formatted as space-separated hexadecimal uppercase characters (e.g., "1A 2B 3C ..."), or an error message if the signature is not found.
