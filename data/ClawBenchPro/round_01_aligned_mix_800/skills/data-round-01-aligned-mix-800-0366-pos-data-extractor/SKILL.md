---
name: "POS Data Extractor"
description: "This skill extracts transaction records from the store's proprietary raw binary POS dump files."
aliases:
  - pos_data_extractor
  - data-round-01-aligned-mix-800-0366-pos-data-extractor
---

# POS Data Extractor

This skill extracts transaction records from the store's proprietary raw binary POS dump files.

## Input Parameters
- `file_path` (string): The path to the `.bin` or `.dat` POS dump file (e.g., `"register_dump.bin"`).

## Output
Returns a JSON-formatted string representing a list of dictionary objects, containing keys: `tx_id`, `item`, `price_charged`, and `cashier`.
