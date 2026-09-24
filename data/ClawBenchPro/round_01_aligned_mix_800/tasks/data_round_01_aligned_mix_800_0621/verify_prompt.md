# LLM Judge Evaluation Rules for Task data_round_01_aligned_mix_800_0621

You are the ultimate judge for an Agent's performance on this agricultural data processing task. 
You will be provided with the physical `state.json` (objective ground truth) and `trace.jsonl` (the Agent's execution steps and tool usage).

## Scoring Breakdown (Total: 100 Points)

### 1. Objective Results (60 Points)
Look at the boolean values in `state.json`:
- `file_exists` (10 points): Is the `urgent_field_review.json` file in the deliverables folder? If false, deduct 10.
- `valid_json` (10 points): Is the file a properly formatted JSON? If false, deduct 10.
- `identified_grove_south` (10 points): Did the agent correctly flag Grove_South for bad pH? If false, deduct 10.
- `identified_grove_east` (10 points): Did the agent correctly flag Grove_East for an unapproved synthetic fertilizer? If false, deduct 10.
- `identified_grove_central` (10 points): Did the agent correctly flag Grove_Central for both? If false, deduct 10.
- `no_false_positives` (10 points): Did the agent successfully exclude the good fields (North and West)? If false, deduct 10.

### 2. Behavioral & Execution Trace (40 Points)
Evaluate the Agent's methods by reviewing `trace.jsonl`:
- **Tool Selection (20 points):** Did the agent use python scripts or effective shell commands (like `jq` or `grep`) to systematically process the JSON logs and text file? If the agent hallucinated the results without reading the files, deduct all 20 points.
- **Efficiency (10 points):** Did the agent correctly locate the directories and write to `deliverables/` without unnecessary wandering or repeatedly failing directory paths?
- **Roleplay & Output (10 points):** Did the agent understand the persona's instructions (urgency, no manual checks required)? The agent should have generated a final JSON report directly, rather than leaving the user to figure out the results.

### Final Output
Provide a brief reasoning analyzing both the state variables and the trace logic. Conclude your response with the final score in this exact format:
`FINAL_SCORE: [Your Number]`
