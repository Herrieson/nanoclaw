You are the LLM judge evaluating the Agent's performance on the "Welder's Buggy Parts Extraction" task.
The Agent needed to parse a noisy text log to find parts marked `CRITICAL_FRACTURE` or `NEEDS_WELDING`, cross-reference a JSON catalog for prices, apply a 15% discount, and write the results to a CSV sorted by price descending.

Please review the Agent's reasoning trace and the `verify_result.json` state.

Scoring Criteria (100 points total):
1. **File Creation (20 pts):** Did the agent successfully create `order_sheet.csv`? (`csv_exists`)
2. **Format & Headers (20 pts):** Does the CSV have the correct headers: `Part_ID`, `Part_Name`, `Discounted_Price`? (`header_correct`)
3. **Log Parsing & Cross-referencing (30 pts):** Did the agent correctly identify the three broken parts (SUS-404, MNT-001, FRM-88X) and get the correct base prices from the JSON? (`row_count_correct`, partial credit if `data_correct` is false but some parts are found).
4. **Math & Sorting (30 pts):** Did the agent correctly apply the 15% discount (multiply by 0.85) and sort the final CSV rows descending by price? (`data_correct` and `sorted_correctly`)

Analyze the output and provide your final score.
