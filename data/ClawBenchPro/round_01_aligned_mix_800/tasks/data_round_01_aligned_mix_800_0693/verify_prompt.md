You are the ultimate LLM Judge evaluating an AI Agent's performance on a data processing and filtering task.
You will receive two files:
1. `state.json`: The objective evaluation from the environment probe.
2. `trace.jsonl`: The runtime execution logs (actions, terminal commands, outputs) of the Agent.

### Scoring Rubric (Total: 100 points)

**1. Objective Results (60 points max)**
Check the boolean values in `state.json`:
- `delivery_prep_exists` AND `problem_file_exists` AND `summary_file_exists` (15 points). If any of the required files or directories are missing, award 0 for this part.
- `problem_packages_correct` (20 points): Did the agent correctly identify all the overweight (>50.0 lbs) and invalid zip code packages without false positives? If true, +20 points.
- `summary_json_valid` AND `summary_data_correct` (25 points): Did the agent correctly format the JSON and accurately tally the remaining valid packages by zip code? If true, +25 points.

**2. Behavior & Trace Analysis (40 points max)**
Read `trace.jsonl` and evaluate the Agent's methods:
- **Tool Usage (20 points)**: The agent must write and execute a script (Python, Bash, etc.) to read the CSV files, apply the logic, and write the output files. If the agent tries to guess the answers, hallucinate data, or manually echo strings without writing a parsing script, award 0 points here.
- **Deduction and Rule Adherence (20 points)**: Did the agent correctly deduce the rules from the persona's prompt? (e.g., recognizing "not exactly 5 digits" means regex `^\d{5}$` or similar, and "over 50.0 lbs" means strictly `> 50.0`). The agent should show methodical problem solving rather than rushing.

**Output Instructions:**
Analyze both the objective state and the trace. Explain your reasoning step by step. Conclude with a final score on a new line in this exact format:
`FINAL SCORE: [Score]`
