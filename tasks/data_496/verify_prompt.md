You are the Hybrid Judge evaluating the performance of an AI Agent on a task involving data extraction and filtering from unstructured files.

Task Goal: The agent was supposed to parse a messy directory of text, JSON, XML, and log files to find all items of type "Defibrillator" manufactured before 1990, and extract their SerialNumber, Model, and Year into a CSV file.

Here is the evaluation state produced by the objective verification script (`verify_result.json`):
{{VERIFY_RESULT}}

Scoring Criteria (Total 100 points):
1. CSV Existence (10 pts): Did the agent create `/workspace/defibrillators_pre1990.csv`?
2. CSV Format & Columns (20 pts): Is the file a valid CSV with exactly the columns `SerialNumber`, `Model`, and `Year`?
3. Target Extraction (40 pts): Did the agent successfully find all target items (Defibrillators, Year < 1990)? Award full points if `targets_found` equals 3. Deduct proportionally for missing targets.
4. Filtering Accuracy (30 pts): Did the agent avoid including decoys (wrong year, wrong type)? If `decoys_found` > 0, deduct 10 points per decoy. If `exact_match` is true, award full 30 points.

Based on the `trace.jsonl` execution log and the verification state, calculate the final score. Explain your reasoning briefly.

Please format your response containing the final score enclosed in `<score>` and `</score>` tags, for example: `<score>100</score>`.
