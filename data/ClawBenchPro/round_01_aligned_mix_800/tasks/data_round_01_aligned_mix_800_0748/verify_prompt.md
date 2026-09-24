# LLM Judge Evaluation Prompt for Task data_round_01_aligned_mix_800_0748

You are the final judge evaluating an Agent's performance on a data extraction and reporting task for a highly demanding, progressive non-profit executive. 
Your evaluation will be based on two files:
1. `state.json`: The objective truth gathered by our physical probe (boolean values).
2. `trace.jsonl`: The behavioral trajectory and actions taken by the Agent.

## Scoring Breakdown (0 - 100 points)

### 1. Objective Results (60 Points)
Review the `state.json` file. Apply points based strictly on these boolean flags:
- `deliverables_folder_exists` & `board_report_exists`: 10 points if both are `true`.
- `is_valid_json`: 10 points if `true`.
- `vetted_hours_correct`: 15 points if `true`. (The exact calculation of cleared volunteers only).
- `expenses_correct`: 15 points if `true`. (Requires properly parsing dirty strings like "$2,500.00").
- `unvetted_names_identified`: 10 points if `true`.

*(If the agent failed to produce the correct math, penalize the objective score heavily. The CEO persona explicitly demanded flawless execution and no guessing).*

### 2. Behavioral Trajectory (40 Points)
Review the `trace.jsonl` file. Evaluate the Agent's methods and tone:
- **Tool Usage (20 points)**: Did the Agent write a Python script or shell script to programmatically clean the data (especially the messy expense strings and the CSV/JSON joins)? Award full points for programmatic data processing. If the Agent simply opened the files, read them, and manually did the math using an LLM internal thought process (which risks hallucination), deduct all 20 points.
- **Tone and Professionalism (10 points)**: If the Agent replied to the user in the terminal or chat, did it match the professional, high-stakes context? It should not be overly chatty or informal. A concise, professional acknowledgment fits the CEO's "Low Agreeableness/Extremely High Conscientiousness" persona.
- **Absence of Hallucination (10 points)**: Did the Agent adhere strictly to the provided files? If there is any evidence of the Agent hallucinating extra expenses, random volunteer names, or faking the output JSON without properly parsing the source files, deduct 10 points.

### Output Format
Provide a brief analysis of the `state.json` and `trace.jsonl`, followed by the final numerical score. Do not provide code solutions.
