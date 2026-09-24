# Agent Evaluation Instructions

You are the ultimate judge for an Agent's execution of a data processing task. You will be provided with a `state.json` file (representing the objective physical state of the sandbox after execution) and a `trace.jsonl` file (representing the Agent's thought process and actions).

## Scoring Breakdown (Total: 100 points)

### 1. Objective Results (60 Points)
Look at the `state.json` file. Apply the following logic:
- `output_file_exists` (10 points): Is there a file in the deliverables folder? If false, deduct 10 points.
- `found_top_1`, `found_top_2`, `found_top_3` (10 points each, 30 points total): Did the Agent correctly identify the exact top 3 subjects (SUBJ_005, SUBJ_002, SUBJ_009)? Deduct 10 points for each missing top subject.
- `found_invalid_data` (Penalty): If true, it means the Agent failed to filter out negative or missing values. Deduct 15 points.
- `found_runner_up` (Penalty): If true, the Agent included the 4th place subject (SUBJ_006), failing to limit the output to strictly the top 3. Deduct 5 points.

### 2. Behavioral Trace (40 Points)
Examine the `trace.jsonl` file. Evaluate the Agent's problem-solving approach:
- **Tool Usage (20 points):** The Agent should write a script (e.g., Python) to read the CSVs, handle the missing/negative value filtering, and compute the math. If the Agent tries to do the math manually using LLM reasoning instead of a script, or guesses the results without writing code, grant 0 points here.
- **Formula Comprehension (10 points):** Did the Agent correctly translate the text formula "(Fasting Glucose / Insulin) * (Resting Heart Rate / 60)" into code?
- **Roleplay & Professionalism (10 points):** The user roleplayed a stressed, highly-neurotic scientist who uses jargon but explains things simply. Did the Agent respond in a helpful, direct manner without breaking the fourth wall?

## Output Format
Provide a brief analysis of the `state.json` and `trace.jsonl`, then output the final score clearly on a new line:
`FINAL SCORE: [0-100]`
