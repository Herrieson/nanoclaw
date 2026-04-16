You are the evaluator for an AI Agent's performance on the "Manufacturing Order Recovery" task.
The user is a middle-aged administrative worker who needs help extracting order info from corrupted log files for a specific supplier ("Krakow Parts").

Please evaluate the agent based on the provided `verify_result.json` and the agent's interaction trace.

**Scoring Rubric (Total 100 points):**
1. **File Creation (20 points):** Did the agent successfully create `krakow_summary.txt` in the `assets/data_430` directory? (`file_exists` is True)
2. **Data Extraction (30 points):** Did the agent correctly identify and list all four parts (KP-001, KP-002, KP-003, KP-004) belonging to Krakow Parts? (`parts_listed` is True)
3. **Calculation Accuracy (50 points):** Did the agent correctly calculate the grand total for these parts and format it at the bottom as "Total: 1100" (or 1100.00)? (`total_correct` is True)

If `total_correct` is False, but the agent attempted the calculation and got a different number, award partial points (up to 20/50 for calculation) based on their logic in the trace.
Provide your final score as a JSON object: `{"score": X, "reason": "..."}`.
