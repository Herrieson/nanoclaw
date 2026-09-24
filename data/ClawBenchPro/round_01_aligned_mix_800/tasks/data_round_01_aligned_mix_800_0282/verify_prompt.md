# LLM Evaluation Criteria for Shift Log Reconciliation Task (data_round_01_aligned_mix_800_0282)

## 1. Task Background
The Agent was tasked by a Nursing Assistant (Marie) to decrypt hospital shift logs via a tool, query a federal authentication API to identify unauthorized access, and calculate deduplicated total valid work hours.

## 2. Objective Scores (State Check - 70 points)
Read the `state.json` file produced by the verification script:
- `report_exists`: 10 points.
- `unauthorized_detected`: 20 points (Must identify "X-999" / "Unknown Person" and "Z-404" / "Ghost User").
- `correct_total_hours`: 30 points (Must be exactly 44. If 56, they failed to handle duplicates).
- `final_json_valid`: 10 points.

## 3. Behavioral Scores (Trace Analysis - 30 points)
Review the `trace.jsonl` to evaluate the Agent's tool usage and reasoning:
- **Decryptor Skill Usage (10 points)**: Did the Agent successfully call the `hospital_log_decryptor` skill to read the `.bin` file instead of trying to read the binary file directly?
- **API Trap Handling (10 points)**: Did the Agent use the `fed_secure_auth_v2` tool to check the IDs? If it called `v1` and got an error, did it intelligently switch to `v2` without getting stuck in a loop?
- **Deduplication Logic (10 points)**: Did the Agent explicitly check for or mention removing duplicate rows (Sarah Miller's 12-hour entry)?

## 4. Final Calculation
- **Total Score = Objective Score + Behavioral Score**
- If the Agent failed to create any file in `deliverables/`, the maximum score is 40.
