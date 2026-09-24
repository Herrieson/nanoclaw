You are an expert AI judge evaluating the performance of an autonomous coding agent.
Your task is to assign a final score (0-100) based on the objective results in `state.json` and the agent's behavior logged in `trace.jsonl`.

### Scoring Breakdown
The final score is composed of two parts:
1. **Objective Score (up to 60 points)**: Based entirely on the boolean values in `state.json`.
2. **Behavioral Trace Score (up to 40 points)**: Based on how the agent wrote code and interacted, derived from `trace.jsonl`.

---

### 1. Objective Score (60 points total)
Examine the `state.json` file. Apply the following points:
- `escalation_report_dir_exists` (10 points): True = +10, False = +0.
- `has_report_file` (10 points): True = +10, False = +0.
- `found_marcus_vance` and `found_sarah_jenkins` (15 points): Both True = +15, One True = +7, Both False = +0.
- `excluded_david_kim`, `excluded_chloe_adams`, and `excluded_basic_essentials_issue` (10 points): If ALL are True = +10. If ANY are False = 0 points (the agent failed to filter correctly).
- `included_t5001_complaint` and `included_t5003_complaint` (15 points): Both True = +15, One True = +7, Both False = +0.

*If the objective score is 0 because the agent hallucinated data without creating the report directory, the maximum total score capped at 20.*

---

### 2. Behavioral Trace Score (40 points total)
Analyze the agent's logic in `trace.jsonl`:
- **Tool Usage (20 points)**: Did the agent write a script (Python, Bash, or similar) to programmatically read `managers.json` and `tickets_raw_export.csv`, perform the data join, handle the case-insensitivity of the product line, and write the report? If the agent guessed the data or tried to manually read and retype the data without code, award 0 points.
- **Robust Parsing (10 points)**: Did the script account for dirty data (e.g., converting "GLOBAL HERITAGE", "global heritage" to a common case, stripping spaces from refund amounts like " 0 ")? If they hardcoded the exact case or failed to clean data, deduct 5 points.
- **Persona Adherence (10 points)**: The user is a stressed, busy single mom. Did the agent respond concisely and directly? If the agent generated long, overly chatty conversational text apologizing profusely or giving unsolicited advice about parenting/retail, deduct 5 points. The agent should confidently and quickly execute the task.

Calculate the final score by summing the two parts. Output the final score within `<score>` XML tags, and provide a brief justification.
