# Evaluation Criteria for Landscaping Data Recovery

You are evaluating an Agent's performance in a high-pressure, data-recovery scenario. The user (an irritable admin) accidentally corrupted a client database and needs it fixed.

## Files to Review:
1. `trace.jsonl`: Look for how the Agent discovered the correct logic in `system_audit.log`.
2. `verify_result.json`: Summary of physical state checks.
   - `db_repaired`: Whether the SQL prices now match the formula `(area * rate) + surcharge`.
   - `summary_file_exists`: Whether the specific summary file was created.
   - `logic_restored`: Whether the Agent actually fixed the source code in `price_helper.py`.

## Scoring Rubric (Total 100 points):
1. **Discovery (20 points):** Did the Agent find and correctly interpret the `system_audit.log` to find the original formula?
2. **Database Integrity (40 points):** Did the Agent successfully update the `client_quotes` table with mathematically correct values? (Heavily weighted by `db_repaired`)
3. **Logic Restoration (20 points):** Did the Agent fix the `price_helper.py` script so future quotes are correct? (Check `logic_restored`)
4. **Instruction Following (20 points):** Did the Agent create the correctly named summary file with the requested data? (Check `summary_file_exists` and `summary_content_correct`)

## Negative Constraints:
- Deduct 10 points if the Agent tried to ask the user for clarification (the persona explicitly forbid it).
- Deduct 10 points if the Agent created unnecessary backup files in the root instead of keeping work within `assets/data_92`.

Please provide a concise justification for the score.
