You are a top-tier AI Agent evaluator. Your task is to review the performance of an agent solving a data extraction and logical reasoning challenge.

The agent was asked by a factory worker to calculate the shortage of "Lavender Essential Oil" based on scattered, messy files.
To solve this, the agent needed to:
1. Parse `production_plan.txt` to count the number of "Lavender Dream" batches (Total: 14).
2. Parse `formulas.json` to find the required amount of Lavender Essential Oil per batch (150). Total needed = 14 * 150 = 2100.
3. Read `inventory.csv` and overcome OCR errors (e.g., "Lavender Essential 0il", "l25O" instead of 1250) to determine the current inventory is 1250.
4. Calculate the shortage: 2100 - 1250 = 850.
5. Write a script `calculate_shortage.py` that outputs the result into `shortage.txt`.

Please review the provided `trace.jsonl` (to understand the agent's thought process and operations) and the `verify_result.json` (objective state).

**Scoring Criteria (100 points total):**
- **20 points:** Did the agent successfully write the `calculate_shortage.py` script? (`script_exists` is True)
- **20 points:** Did the agent run the script or otherwise generate the `shortage.txt` file? (`shortage_file_exists` is True)
- **40 points:** Did the agent correctly calculate the shortage as `850` and output it? (`correct_shortage_calculated` is True)
- **20 points:** Did the agent correctly identify and process the OCR errors in the CSV file programmatically or manually, demonstrating good reasoning in the trace?

Based on these criteria, output your evaluation in the following JSON format:
