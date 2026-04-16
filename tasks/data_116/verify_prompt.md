# Verification Prompt for Task data_116

## Task Objective
The Agent needs to process messy text logs from the `./raw_logs` directory, extract specific structured data (animal feeding schedules and artifact climate info), clean up whitespace, sort them alphabetically by a specific key, and output them to `compiled_report.json`.

## Evaluation Criteria
You will evaluate the Agent's performance based on the execution trace (`trace.jsonl`) and the objective validation state (`state.json`). 

Allocate points out of 100 based on the following:
1. **File Creation (20 points)**: Did the Agent successfully create a valid JSON file named `compiled_report.json`?
2. **Data Extraction (30 points)**: Did the Agent successfully extract all 5 animal records and all 6 artifact records? 
3. **Data Cleaning (20 points)**: Are the extracted values free of weird extra spaces (e.g., `  `, leading/trailing spaces)?
4. **Sorting (30 points)**: Are the animal records sorted alphabetically by `name`? Are the artifact records sorted alphabetically by `id`?

Check the `state.json` (which contains output from the `verify_rules.py` script). 
- If `score` is 100, the Agent performed flawlessly.
- If the score is less than 100, read the `details` to see which constraints failed, and deduct points accordingly.
- Also, observe the `trace.jsonl` to ensure the Agent actually wrote a script or correctly used command-line tools to parse the text files rather than cheating.

Output a detailed reasoning, and final score.
