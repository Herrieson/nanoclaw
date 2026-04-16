Please evaluate the AI Agent's performance based on the execution trace and the verification state.

### Goal
The agent was tasked by a teenager to decode an RFID log file (`rfid_dump.txt`), extract hex-encoded product SKUs, cross-reference them with a JSON list of sneaker releases (`releases.json`), and output the SKUs of scanned items that have a `hype_score` > 80 into `hyped_inventory.txt`.

### Validation Data
Please review the `verify_result.json` which contains the following keys:
- `target_file_exists`: Did the agent create the `hyped_inventory.txt` file?
- `found_skus`: The list of SKUs the agent wrote to the file.
- `missing_expected_skus`: SKUs that should have been found but were missed.
- `has_extra_skus`: True if the agent included SKUs that either weren't scanned or didn't have a hype score > 80.
- `is_perfect`: True if the agent extracted exactly `SKU-1001` and `SKU-1005` (no missing, no extras).

### Scoring Rules
- **100 points**: `is_perfect` is True. The agent perfectly decoded the hex strings, cross-referenced the hype scores, and generated the correct output file.
- **50 points**: `target_file_exists` is True, and the agent found at least one correct SKU, but also included `has_extra_skus` (e.g., they just read the JSON and blindly dumped all hyped SKUs without checking the hex dump, so `SKU-1003` was included despite not being scanned).
- **20 points**: The agent attempted to write the file but `found_skus` is completely empty or completely wrong (failed the hex decoding phase entirely).
- **0 points**: The `hyped_inventory.txt` file was never created.

Based on these rules, assess the agent's performance and output the final score in standard format.
