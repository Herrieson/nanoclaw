# Evaluation Rubric for Data_208: Silent Failure Recovery

You are evaluating an Agent's performance on a data engineering debugging task. 
The user is a detail-oriented Software Developer with a low tolerance for inefficiency.

### Information Sources:
- **Task Goal**: Repair `sync_v2.py`, populate `production.db` with exactly 1024 records, and resolve logical bugs.
- **Physical State (`verify_result.json`)**:
    - `logic_bug_resolved`: True if the agent removed the hardcoded limit (1000) and the modulo skip logic.
    - `db_entry_count`: Must be exactly 1024.
    - `db_integrity`: True if count is correct.

### Scoring Criteria (Total 100 points):

1. **Problem Identification (30 points)**:
    - Did the agent inspect the logs in `assets/data_208/logs/`?
    - Did it identify the discrepancy between the expected 1024 records and the actual 500 records?

2. **Technical Execution (40 points)**:
    - Did the agent correctly modify `sync_v2.py`? (Remove `if i > 1000: break` and `if i % 2 == 0: continue`).
    - Did it run the script to update the database?

3. **Efficiency & Professionalism (30 points)**:
    - Did the agent follow the persona's style? (Direct, minimal chatter, system-oriented).
    - Did it avoid unnecessary explanations?
    - Subtract 10 points if the agent failed to clean up or verify its own work before finishing.

### Final Grade Calculation:
- **Pass**: Score >= 80 and `db_integrity` is True.
- **Partial**: Score >= 50 and `logic_bug_resolved` is True but DB has wrong count.
- **Fail**: Score < 50 or `sync_v2.py` remains buggy.

Analyze the `trace.jsonl` to see the thought process and command execution.
