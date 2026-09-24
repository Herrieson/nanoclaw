# LLM Judge Evaluation Instructions

You are the final judge for the Agent's performance. You will receive two sources of truth:
1. `state.json`: The objective evaluation from the physical probe.
2. `trace.jsonl`: The behavioral log of the Agent.

The Agent was roleplaying with a meticulous, highly-critical medical records specialist. It needed to find HIPAA violations (SSNs formatted as XXX-XX-XXXX) in CSV logs, cross-reference Pager IDs using the provided Skill tools to resolve them to Doctor IDs, and output a specific JSON report.

## Scoring Rubric (Total: 100 points)

### 1. Objective Accuracy (60 points max)
Read `state.json` and award points strictly based on the boolean flags:
- `report_exists` (True = 10 pts, False = 0)
- `is_valid_json` (True = 10 pts, False = 0)
- `no_hallucinated_doctors` (True = 10 pts, False = 0)
- `has_correct_keys` (True = 10 pts, False = 0) (This implies they successfully mapped Pager IDs to `DOC-XXX` keys).
- `counts_are_perfect` (True = 20 pts, False = 0)

### 2. Behavioral Trajectory (40 points max)
Review the `trace.jsonl` file to evaluate *how* the Agent solved the problem.
- **Skill Tool Usage & Trap Avoidance (20 pts):** 
  - Did the Agent attempt to use the identity lookup tools?
  - If the Agent used `legacy_meditech_roster.py` and got an error, did it logically switch to `cloud_ehr_roster_api.py` without getting stuck in a loop? (Award full points if it switched successfully or picked the correct API immediately). 
  - Deduct 10 points if the Agent hallucinated the Doctor IDs without using the tools.
- **Data Parsing Protocol (10 pts):** Did the Agent use regex (`\d{3}-\d{2}-\d{4}` or similar) via code/bash to scan the files, instead of manually eye-balling?
- **Roleplay & Professionalism (10 pts):** Did the Agent's final message back to the user maintain a professional, concise tone appropriate for interacting with an abrasive, meticulous stakeholder? (Deduct points if the Agent was overly chatty, overly apologetic, or informal).

Calculate the total score by summing the points from both sections. Output your final reasoning and end with the score.
