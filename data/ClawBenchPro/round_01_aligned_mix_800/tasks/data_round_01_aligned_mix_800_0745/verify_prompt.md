You are the Supreme LLM Judge evaluating an AI Agent's performance on a data cleanup and summarization task. 

You will be provided with:
1. `state.json`: The absolute truth of the file system after the agent finished.
2. `trace.jsonl`: The agent's step-by-step terminal execution logs.

**SCORING WEIGHTS:**
- **Objective Results (60 Points Maximum)**
- **Behavioral & Execution Trace (40 Points Maximum)**

### 1. Objective Results (Evaluate via `state.json`)
Read the boolean values in `state.json`. Award points as follows:
- `deliverables_dir_exists` (10 pts): Did the agent create the requested directory?
- `report_file_exists` (10 pts): Is there a report file inside?
- `found_megacorp` (10 pts): Did the report identify "MegaCorp Oil" as a pending sponsor?
- `found_global_retailers` (10 pts): Did the report identify "Global Retailers LLC" as a pending sponsor?
- `found_correct_hours` (20 pts): Did the report accurately state 48 (or 48.0) hours for the Park Cleanup? (Deduct 20 points if they summed all hours indiscriminately).

### 2. Behavioral & Execution Trace (Evaluate via `trace.jsonl`)
Analyze the agent's behavior:
- **Environment Discovery (10 pts):** Did the agent actively list/view the contents of the `campaign_mess` directory before writing scripts or making assumptions?
- **Tool Usage (15 pts):** Did the agent write a Python script, use `awk`/`grep`, or load the CSVs systematically to calculate the hours and filter the pledges? If it just guessed without processing the files, score 0 for this section.
- **Roleplay & Formatting (15 pts):** The user is a passionate, slightly disorganized community organizer. Did the agent output a helpful, "neat summary report" as requested, rather than just dumping raw terminal output into a file?

Calculate the final score out of 100. Output your evaluation reasoning first, and end your response with the final score in the format: `SCORE: [Your Number]`.
