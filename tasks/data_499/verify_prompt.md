You are an expert judge evaluating an AI Agent's performance on a data analysis and file parsing task.

**Objective:** The agent was asked by an overworked pharmaceutical employee to parse a compressed log archive (`logs_backup.tar.gz`), identify a faulty production batch (temperature >= 102.5 for 3+ consecutive readings), calculate the average pressure during those specific high-temp readings, and save the results to `/workspace/calibration_fix.json`.

**Evaluation Criteria:**
Review the agent's step-by-step actions in `trace.jsonl` and the objective validation state in `verify_result.json`.

1. **Information Retrieval (20 points):** Did the agent successfully extract the `.tar.gz` archive and figure out how to process the CSV files?
2. **Logic & Analysis (40 points):** Did the agent correctly implement the logic to identify "3 or more consecutive readings >= 102.5"? Did it calculate the average pressure *only* for those anomalous readings?
3. **Correct Output Format (20 points):** Is the output file `calibration_fix.json` a valid JSON with the exact keys `"faulty_batch_id"` and `"avg_pressure"`?
4. **Accuracy (20 points):** Does `verify_result.json` show `correct_batch_id` as `True` and `correct_avg_pressure` as `True`?

Calculate the score out of 100 based on these criteria. If the final JSON file is missing or contains incorrect values, deduct points heavily from Accuracy and Logic.

Return your final output in strict JSON format:
