# Evaluation Criteria for Art Investment Audit Task

The Agent's goal was to act as a technical assistant to a high-end art collector, recovering data from a messy and slightly corrupted environment.

## Scoring Rubric (Total: 100 Points)

1. **Environment Exploration & Data Discovery (20 points):**
   - Did the Agent successfully find the `vault.db`, the log files, and the valuation JSON?
   - Did it identify that `vault.db` was corrupted and required a workaround or fix?

2. **Data Recovery & Decryption (30 points):**
   - Did the Agent correctly identify the obfuscation method in `system_trace.log` (Base64 + Reverse)?
   - Did it successfully extract the price `65000.0`?
   - Did it handle the SQLite corruption (either by repairing it, using `strings` command, or reading around the corruption)?

3. **Data Aggregation & Calculation (30 points):**
   - Did it filter only "Modern Latin American" pieces from the correct time period (Oct-Dec 2023)?
   - Are the calculations for total spend ($148,000) and projected increase ($23,000) accurate?

4. **Deliverable Quality (20 points):**
   - Is the `final_report.json` correctly formatted?
   - Does it answer the specific questions posed by the user?

## Input Data for Judgment
- **State JSON:** This contains the objective truth about the final file.
- **Trace JSONL:** Review the Agent's thought process. Award points for efficient problem solving (e.g., realizing the DB is corrupted and using Python to recover what's left rather than giving up).

## Final Score Calculation
- If `correct_total_spend`, `correct_most_expensive`, and `correct_valuation_increase` are all true in `state.json`, the base score is 80. 
- Use the trace to award the remaining 20 points based on the elegance of the Bash/Python scripts used.
- If the Agent failed to decrypt the log price, the maximum score should be 50.
