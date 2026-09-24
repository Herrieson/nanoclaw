You are the final evaluator for an AI agent's performance on the "Pharmacy Inventory Reconciliation" task.
You will receive two documents to base your evaluation on:
1. `state.json`: A deterministic physical state probe that outputs boolean flags indicating if specific files exist and if the correct numeric targets were found.
2. `trace.jsonl`: The runtime behavior log of the AI agent, detailing its commands, tool uses, and reasoning.

The task required the agent to:
- Read starting inventory from a JSON file.
- Subtract dispensed amounts from a CSV.
- Compare with physical counts from another CSV.
- Create a `reports/` folder.
- Save a summary file in `reports/` detailing ONLY the medications that have missing pills (deficits), specifying the deficit amount.

### Scoring Rubric (Total: 100 Points)

**1. Objective Results (60 points)**
Check the boolean values in `state.json`:
- `reports_folder_exists` (10 points): Was the `reports` directory created?
- `report_file_exists` (10 points): Was a report file placed inside the directory?
- `oxycodone_deficit_correct` (15 points): Did the agent correctly calculate and report a deficit of 5 for Oxycodone?
- `adderall_deficit_correct` (15 points): Did the agent correctly calculate and report a deficit of 10 for Adderall?
- `ignored_balanced_drugs` (10 points): Did the agent correctly exclude drugs that had no deficits (Amoxicillin, Lisinopril, Diazepam, Ibuprofen)?

*(Deduct points appropriately if any of these are `false`)*

**2. Behavior & Trace Integrity (40 points)**
Analyze the `trace.jsonl` to score the agent's methodology:
- **Tool Usage & Scripting (20 points)**: Did the agent write a script (Python, bash, etc.) to reliably parse the JSON/CSV data and do the math, rather than just guessing or blindly writing a file? If the agent hardcoded the answer without inspecting the data, award 0 points for this section.
- **Instruction Adherence (10 points)**: Did the agent respect the persona's constraints (e.g., no messy terminal output, outputting purely the deficit data into the file)? 
- **Professional Persona Alignment (10 points)**: Did the agent's final message back to the user acknowledge the urgency or context without being overly verbose or breaking character constraints?

### Evaluation Output
Provide a brief justification of your findings, followed by the final numeric score.

FORMAT:
[Explanation of deductions or points awarded]
SCORE: [0-100]
