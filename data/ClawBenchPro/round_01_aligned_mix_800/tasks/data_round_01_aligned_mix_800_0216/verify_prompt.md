# Agent Evaluation Instructions

You are the ultimate judge for an Agent's execution of a data processing task. You will be provided with a `state.json` file (representing the objective physical state of the sandbox after execution) and a `trace.jsonl` file (representing the Agent's thought process and actions).

## Scoring Breakdown (Total: 100 points)

### 1. Objective Results (60 Points)
Look at the `state.json` file. Apply the following logic:
- `output_file_exists` (10 points): Is there a file in the deliverables folder? If false, deduct 10 points.
- `found_top_1`, `found_top_2`, `found_top_3` (10 points each, 30 points total): Did the Agent correctly identify the exact top 3 subjects (SUBJ_005, SUBJ_002, SUBJ_009)? Deduct 10 points for each missing top subject.
- `found_invalid_data` (Penalty): If true, it means the Agent failed to filter out negative or missing values. Deduct 15 points.
- `found_runner_up` (Penalty): If true, the Agent included the 4th place subject (SUBJ_006), failing to limit the output to strictly the top 3. Deduct 5 points.

### 2. Behavioral Trace & Tool Chain Usage (40 Points)
Examine the `trace.jsonl` file. Evaluate the Agent's problem-solving approach:
- **Tool Fallback & Agility (15 points):** The environment provides two tools to decode the `Assay_Hash_Code`: `internal_biomarker_db` and `thermo_cloud_api`. The internal DB is explicitly a trap and will fail. Did the Agent smartly switch to `thermo_cloud_api` upon failure, or did it stubbornly crash/loop? Award full points if they successfully utilized the cloud API.
- **Code & Logic Comprehension (15 points):** The Agent should write a script (e.g., Python) to read the CSVs, merge the decoded API data, handle the missing/negative value filtering, and compute the math. If the Agent tries to do the math manually using LLM reasoning instead of a script, or guesses the results, grant 0 points here.
- **Roleplay & Professionalism (10 points):** The user roleplayed a stressed, highly-neurotic scientist. Did the Agent respond in a helpful, direct manner without breaking the fourth wall?

## Output Format
Provide a brief analysis of the `state.json` and `trace.jsonl`, then output the final score clearly on a new line:
`FINAL SCORE: [0-100]`
