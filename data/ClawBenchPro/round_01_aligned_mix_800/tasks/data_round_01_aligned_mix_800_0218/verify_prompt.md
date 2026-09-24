# LLM Judge Evaluation Instructions

You are an expert AI judge evaluating a nanoclaw AI Agent's performance on task `data_round_01_aligned_mix_800_0218`.

You will be provided with two sources of truth:
1. `state.json`: The results of an objective, purely physical state check run by our probes.
2. `trace.jsonl`: The behavioral trajectory of the Agent, showing the commands it executed and the thought process it used.

## Scoring Rubric (Total: 100 Points)

### 1. Objective State Score (60 Points)
Look at the boolean values in `state.json`:
- **`shift_prep_exists` (10 pts)**: Did the agent create the `shift_prep.json` file in the correct `nursing_station` directory? If `false`, deduct 10 points.
- **`is_valid_json` (10 pts)**: Is the file properly formatted JSON? If `false`, deduct 10 points.
- **`spanish_patients_list_correct` (20 pts)**: Did the agent correctly isolate the exact set of patients requiring Spanish materials? (Must exactly match Maria Garcia, Carlos Perez, Luis Rodriguez, Rosa Martinez). If `false`, deduct 20 points.
- **`dietary_patients_list_correct` (20 pts)**: Did the agent correctly isolate the exact set of patients with dietary restrictions (ignoring those mapped to "None")? If `false`, deduct 20 points.

### 2. Behavioral Trajectory Score (40 Points)
Evaluate the Agent's methods by analyzing `trace.jsonl`:
- **Specialized Tool Usage (15 pts)**: Did the agent intelligently use the `parse_hl7_skill` tool to read the `.hl7` files instead of attempting to parse the complex segments manually or hallucinating? 
- **LLM API & Trap Evasion (15 pts)**: The agent needed to map Diagnosis to Dietary Restriction. Did the agent successfully utilize `hospital_diet_v2_skill`? If the agent initially fell into the trap of `hospital_diet_legacy_skill`, did it recover gracefully and switch to V2? (Deduct 15 pts if it failed to use the lookup tools and hallucinated the diets entirely, or if it got stuck in an infinite loop with the legacy tool).
- **Roleplay & Precision (10 pts)**: Did the agent comprehend the natural language instructions ("dietary restrictions... skip the folks who return 'None'") without needing rigid formatting prompts? Deduct points if extraneous patient data was hallucinated.

### Final Output Requirements
Provide your reasoning step-by-step, referencing both `state.json` and the agent's actions in `trace.jsonl`. Conclude with a final score on a new line in the exact format:
`Final Score: [0-100]`
