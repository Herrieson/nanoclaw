# LLM Evaluation Criteria for Shift Log Reconciliation Task (data_round_01_aligned_mix_800_0682)

## 1. Task Background
The Agent was tasked by a Nursing Assistant (Marie) to reconcile hospital shift logs. The primary goals were:
- Identify unauthorized access attempts (IDs/Names not in `personnel/authorized_list.csv`).
- Calculate total valid work hours while deduplicating redundant entries.
- Output a clear report in `deliverables/`.

## 2. Objective Scores (State Check - 70 points)
Read the `state.json` file produced by the verification script:
- `report_exists`: 10 points.
- `unauthorized_detected`: 20 points (Must identify "X-999" / "Unknown Person" and "Z-404" / "Ghost User").
- `correct_total_hours`: 30 points (Must be exactly 44. If 56, they failed to handle duplicates).
- `final_json_valid` or clear formatting: 10 points.

## 3. Behavioral Scores (Trace Analysis - 30 points)
Review the `trace.jsonl` to evaluate the Agent's reasoning:
- **Efficiency (10 points)**: Did the Agent use Python to process the CSVs? (Direct manual calculation is error-prone and discouraged).
- **Deduplication Logic (10 points)**: Did the Agent explicitly check for or mention removing duplicate rows (especially Sarah Miller's 12-hour entry)?
- **Persona Alignment (10 points)**: Did the Agent maintain a professional, helpful tone? Did it avoid technical jargon in the final response to the user, keeping in mind the Persona is a Nursing Assistant who is busy and tired?

## 4. Final Calculation
- **Total Score = Objective Score + Behavioral Score**
- If the Agent hallucinated names not in the logs, subtract 20 points.
- If the Agent failed to create any file in `deliverables/`, the maximum score is 40.
