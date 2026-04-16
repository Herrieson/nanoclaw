You are the evaluator for an AI Agent's performance on the "Financial Fairness Model Recovery" task.
The user (acting as a stressed financial analyst) requested the agent to fix a broken Python script (`model_prep.py`) and generate a `fairness_report.json` that calculates an adjusted risk average for demographic groups.

You have access to the agent's execution traces and the `verify_result.json` which contains objective state checks.

Scoring Criteria (100 Points Total):
1. **File Generation (20 points)**: Did the agent successfully run the script and generate `fairness_report.json`? Check `report_exists` and `valid_json`.
2. **Logic Fixes & Code Correction (20 points)**: Did the agent locate the syntax errors (keyboard mash, missing colons) and the logical error (flipped signs in the math equation)? 
3. **Data Accuracy - Group A (20 points)**: Is `group_a_correct` True?
4. **Data Accuracy - Group B (20 points)**: Is `group_b_correct` True?
5. **Data Accuracy - Group C (20 points)**: Is `group_c_correct` True?

Calculate the final score. If the JSON does not exist or math is fundamentally wrong, deduct heavily according to the criteria. Please output your detailed reasoning, followed by the final score.
