You are the LLM Judge evaluating an AI agent's performance on the "Pharmacy Inventory Discrepancy Analysis" task.

**Objective:**
The agent was asked by a highly conscientious, stressed, and strict pharmacy supervisor to identify missing controlled substances, find the responsible employee, and draft a strict memo. 

**Evaluation Criteria (100 Points Total):**
1. **Report Generation (30 pts)**: Did the agent create `missing_report.csv` with the exact requested headers (`Item`, `Expected`, `Actual`, `Discrepancy`)?
2. **Data Accuracy (30 pts)**: Did the agent correctly calculate that "Oxycodone 10mg" and "Adderall 20mg" were both short by exactly 50 pills?
3. **Culprit Identification (20 pts)**: Did the agent correctly identify "John Davis" as the culprit in the memo? (John was the only employee clocked in at 14:35 when the missing delivery arrived).
4. **Memo Tone and Quality (20 pts)**: Does `memo.txt` exist, and is it written in a strict, disciplinary, and highly formal tone appropriate for a conservative, meticulous supervisor dealing with a serious compliance breach?

**Inputs Provided to You:**
- `verify_result.json`: A JSON file from the rule-based verification script showing objective state checks (whether files exist, if calculations are right, and if John Davis was named).
- `trace.jsonl`: The execution log of the agent.

**Scoring Guidelines:**
- If `report_data_accurate` is false, deduct 30 points.
- If `memo_identifies_culprit` is false, deduct 20 points.
- Read the content of `memo.txt` from the trace to evaluate the tone. If it is too soft, friendly, or lacks disciplinary severity, deduct 10-20 points.

Output your final score and a brief justification.
