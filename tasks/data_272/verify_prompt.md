# Evaluation Rubric for Agent Task: HR Payroll Reconciliation

The Agent's performance should be evaluated based on its ability to navigate a messy environment, extract specific logic from documents, and execute a technical fix.

## Scoring Criteria (Total 100 Points):

1. **Information Retrieval (30 points):**
   - Successfully located the memo `memo_draft_final_v2_USE_THIS.txt` among the "artistic" clutter.
   - Corrected identified the premium rate ($75) and the condition (Ortho-K AND COMPLETED).

2. **Data Analysis & Calculation (30 points):**
   - Parsed `appointment_logs_q3.log` accurately.
   - Identified the 4 qualifying sessions (July 15, Aug 20, Sept 15, Sept 28). Note: Aug 5 was CANCELLED.
   - Calculated the additional $300 accurately.

3. **System Manipulation & Coding (30 points):**
   - Correctly fixed `reconcile_bonus.py` to use SQLite commands.
   - Successfully updated `payroll_pending.db` to the final amount of $1800.

4. **Communication & Persona (10 points):**
   - Provided a clear summary to Angela as requested.
   - Maintained a professional yet helpful tone fitting for a task assigned by a busy manager.

## Fact-Check Reference (from verify_result.json):
- `db_updated`: Must be `true`.
- `correct_amount`: Must be `true` (Final value should be 1800.0).
- `script_fixed`: Must be `true`.

## Final Grade Calculation:
- If `correct_amount` is false, cap the score at 50.
- If the agent failed to filter out 'CANCELLED' sessions, deduct 20 points.
- If the agent did not fix the script but manually edited the DB, deduct 10 points for not following the spirit of the persona's request.
