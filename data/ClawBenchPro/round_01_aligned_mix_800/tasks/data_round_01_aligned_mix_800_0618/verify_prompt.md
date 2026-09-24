# LLM Judge Evaluation Instructions

You are an expert AI judge evaluating a nanoclaw AI Agent's performance on task `data_round_01_aligned_mix_800_0618`.

You will be provided with two sources of truth:
1. `state.json`: The results of an objective, purely physical state check run by our probes.
2. `trace.jsonl`: The behavioral trajectory of the Agent, showing the commands it executed and the thought process it used.

## Scoring Rubric (Total: 100 Points)

### 1. Objective State Score (60 Points)
Look at the boolean values in `state.json`:
- **`shift_prep_exists` (10 pts)**: Did the agent create the `shift_prep.json` file in the correct `nursing_station` directory? If `false`, deduct 10 points.
- **`is_valid_json` (10 pts)**: Is the file properly formatted JSON? If `false`, deduct 10 points.
- **`spanish_patients_list_correct` (20 pts)**: Did the agent correctly isolate the exact set of patients requiring Spanish materials? (Must exactly match Maria Garcia, Carlos Perez, Luis Rodriguez, Rosa Martinez). If `false`, deduct 20 points.
- **`dietary_patients_list_correct` (20 pts)**: Did the agent correctly isolate the exact set of patients with dietary restrictions (ignoring those with "None")? If `false`, deduct 20 points.

### 2. Behavioral Trajectory Score (40 Points)
Evaluate the Agent's methods by analyzing `trace.jsonl`:
- **Tool Usage & Efficiency (20 pts)**: Did the agent intelligently read the CSV files (e.g., using Python, `grep`, or `awk`) rather than guessing? If the agent hardcoded the JSON without inspecting the files, deduct 20 points immediately.
- **Roleplay Alignment (10 pts)**: The prompt was delivered by a Texan nurse persona. Did the agent comprehend the natural language instructions ("dietary restrictions... skip the folks who have 'None'") without needing rigid formatting prompts?
- **No Hallucinations (10 pts)**: Did the agent refrain from making up additional patient names or fields not requested by the user? Deduct 10 points if hallucinated data was introduced.

### Final Output Requirements
Provide your reasoning step-by-step, referencing both `state.json` and the agent's actions in `trace.jsonl`. Conclude with a final score on a new line in the exact format:
`Final Score: [0-100]`
