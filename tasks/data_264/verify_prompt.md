You are evaluating an AI agent's ability to process and analyze mixed-format telemetry data based on a demanding user's instructions.

**Task Requirements:**
1. Parse a CSV file and a JSON file containing machinery downtime data.
2. Sum up the total downtime in minutes, convert to hours, and multiply by $850.
   - Total downtime = 300 minutes = 5 hours.
   - Total cost = 5 * 850 = $4250.
3. Identify the top 3 fault codes by frequency across both files.
   - Correct top 3 codes: E-001, E-002, E-003.
4. Output these results into `presentation_summary.md`.

**State JSON File (`verify_result.json`):**
- `summary_file_exists`: Did the agent create `presentation_summary.md`?
- `contains_correct_cost`: Does the file contain the value `4250` (or `4,250`)?
- `contains_top_codes`: Does the file contain `E-001`, `E-002`, and `E-003`?
- `file_content`: The raw text of the generated file.

**Scoring Rubric (Total: 100 points):**
- **File Creation (20 points):** `summary_file_exists` is true.
- **Cost Calculation (40 points):** `contains_correct_cost` is true. Deduct these points if the calculation is incorrect.
- **Top Codes Extraction (40 points):** `contains_top_codes` is true. Deduct partial points if only 1 or 2 codes are present, or if incorrect codes (like E-005) are included in the top 3 list.

Analyze the `verify_result.json` and provide the final score based strictly on the above criteria.
