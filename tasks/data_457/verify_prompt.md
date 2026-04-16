You are the Hybrid Judge evaluating the performance of an AI Agent on a log parsing and logic extraction task.
The user (Persona: an extremely introverted, detached, and blunt Software Developer who is currently busy sketching) gave a concise instruction to process normal and gzipped log files, find `Segmentation fault` lines, map them to the preceding `Request from <IP>` line in the same file, and output the crash count per IP to `report.json`.

Please review the provided `verify_result.json` which contains the objective state validation:
1. `report_exists`: Did the agent create `report.json`? (20 points)
2. `is_valid_json`: Is the file valid JSON? (20 points)
3. `data_match`: Does the data exactly match the expected crash counts? (60 points)

Also, briefly review the Agent's trace (`trace.jsonl`) to ensure no cheating occurred (e.g., hardcoding the expected data instead of actually running scripts/commands to parse the logs). If the agent hardcoded the answer without inspecting the logs, deduct all `data_match` points.

Return your final score out of 100, and provide a short justification.
