You are evaluating an AI Agent's performance on a data parsing and analysis task disguised as a request from a supermarket supervisor.

**Goal:** The agent needed to read messy JSON and CSV files in `waste_data`, calculate total energy, find the most contaminated bin, and write the answers to `eco_summary.txt`.

**Ground Truth:**
- Total Energy: 345.6 kWh
- Worst Bin: BIN-004

**Evaluation Criteria:**
Review the provided `verify_result.json` which contains the objective state checks:
1. **File Creation (20 pts):** Did the agent create `eco_summary.txt` in the main folder? (`summary_file_exists`)
2. **Energy Calculation (40 pts):** Did the agent correctly parse the JSON, handle invalid/null/string entries, and sum up the float values to exactly 345.6? (`energy_correct`)
3. **Bin Analysis (40 pts):** Did the agent correctly parse the CSV, count the "True" values in the `contamination_flag` column per bin, and identify BIN-004 as the highest? (`bin_correct`)

**Instructions for Scoring:**
- If `summary_file_exists` is false, score is 0.
- Otherwise, assign points based on the boolean flags `energy_correct` and `bin_correct`.
- Check the agent's `trace.jsonl` to ensure they actually wrote scripts or used commands to parse the data rather than hallucinating the answer. Deduct points if severe hallucination occurred without data processing.

Please output the final score and a brief justification.
