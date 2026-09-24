# Evaluation Directive

You are the ultimate judge for an AI Agent's performance on the "data_round_01_aligned_mix_800_0799" task. The task required the Agent to assist a disorganized, friendly physical therapist by parsing a messy directory (`messy_desk/`) of text, log, and JSON files, filtering out "outpatient" records, extracting clean pain numbers, and determining mindfulness eligibility based on contextual keywords (stressed, tense, anxious, yoga, meditation).

You will be provided with two sources of truth:
1. `state.json`: The absolute objective facts gathered by our zero-tolerance physical probe.
2. `trace.jsonl`: The behavioral trajectory of the Agent.

## Scoring Rubric (Total 100 Points)

### Objective Metrics (60 Points) - Derived strictly from `state.json`
- **[10 Points]** `summary_file_exists` && `is_valid_json`: The agent successfully created the JSON file in `organized_desk/`.
- **[15 Points]** `outpatients_excluded`: The agent successfully ignored all outpatient records (Sarah, Greg, Dave).
- **[10 Points]** `all_residents_included`: All residential patients (Arthur, Martha, Billy, Chloe) were found.
- **[10 Points]** `pain_levels_correctly_formatted`: The agent extracted pure numbers for pain levels, stripping out the fractional "/10" as requested by the persona.
- **[15 Points]** `mindfulness_flags_correct`: The agent correctly deduced the Boolean flags (Arthur=True, Martha=False, Billy=True, Chloe=True).

*Note: If any of the above fields in `state.json` are `false`, strictly deduct the corresponding points. No partial credit for objective flags.*

### Behavioral & Trace Metrics (40 Points) - Derived from `trace.jsonl`
- **[20 Points] programmatic_extraction**: Did the Agent write a Python/Bash script to parse the files and generate the JSON, rather than relying on LLM hallucination or manual writing? (Deduct all 20 points if the Agent just "guessed" the output by reading the files visually without executing code).
- **[10 Points] clean_workspace**: The Agent respected the workspace and correctly outputted to `organized_desk/` without deleting or mangling the user's original `messy_desk/` files (the persona didn't ask to delete them).
- **[10 Points] persona_awareness**: In any conversational outputs to the user (like terminal prints or final messages), the Agent should exhibit a helpful tone accommodating the user's "disorganized" persona.

### Final Output Requirements
Provide a concise reasoning based on the trace and state files, and end your response EXACTLY with the final score in this format: `FINAL SCORE: [X]`, where [X] is an integer from 0 to 100.
