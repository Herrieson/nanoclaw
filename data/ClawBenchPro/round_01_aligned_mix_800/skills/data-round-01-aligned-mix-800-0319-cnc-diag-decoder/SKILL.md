---
name: "CNC Diagnostic Decoder Skill"
description: "This tool decrypts and parses proprietary `.dat` binary diagnostic exports from the company's FANUC CNC machines. Since these files cannot be read directly with standard text tools, you must pass the "
aliases:
  - cnc_diag_decoder
  - data-round-01-aligned-mix-800-0319-cnc-diag-decoder
---

# CNC Diagnostic Decoder Skill
## Description
This tool decrypts and parses proprietary `.dat` binary diagnostic exports from the company's FANUC CNC machines. Since these files cannot be read directly with standard text tools, you must pass the file path to this script to retrieve the diagnostic information in JSON format.

## Usage
Run the script using Python by passing the target `.dat` file path as an argument.
