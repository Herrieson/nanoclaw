---
name: "BCI Marker Decoder"
description: "Parses proprietary V2 BCI marker binary files (`.bin`) and returns a structured JSON string containing the stimulus events."
aliases:
  - bci_marker_decoder
  - data-persona-aligned-skills-50-0006-bci-marker-decoder
---

# BCI Marker Decoder

Parses proprietary V2 BCI marker binary files (`.bin`) and returns a structured JSON string containing the stimulus events.

## Features
- Strips the `BCI_MRK_V2` header and decrypts the base64 encoded event payload.
- Returns a JSON string representing a list of dictionaries with keys: `stim_id`, `timestamp_ms`, and `target_type`.

## Usage
Provide the file path to the binary marker file.
