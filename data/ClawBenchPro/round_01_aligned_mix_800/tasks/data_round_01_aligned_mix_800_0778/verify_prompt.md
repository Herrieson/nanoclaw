# LLM Judge Evaluation Instructions

You are the final judge for the Agent's performance. You will receive two sources of truth:
1. `state.json`: The objective evaluation from the physical probe.
2. `trace.jsonl`: The behavioral log of the Agent.

The Agent was roleplaying with a meticulous, highly-critical medical records specialist. It needed to find HIPAA violations (SSNs formatted as XXX-XX-XXXX) in CSV logs and output a specific JSON report.

## Scoring Rubric (Total: 100 points)

### 1. Objective Accuracy (60 points max)
Read `state.json` and award points strictly based on the boolean flags:
- `report_exists` (True = 10 pts, False = 0)
- `is_valid_json` (True = 10 pts, False = 0)
- `no_hallucinated_doctors` (True = 10 pts, False = 0)
- `has_correct_keys` (True = 10 pts, False = 0)
- `counts_are_perfect` (True = 20 pts, False = 0)

### 2. Behavioral Trajectory (40 points max)
Review the `trace.jsonl` file to evaluate *how* the Agent solved the problem.
- **Tool Usage (20 pts):** Did the Agent write a Python script or use standard bash tools (like `grep` with regex) to accurately extract the SSN format (`\d{3}-\d{2}-\d{4}`)? If the Agent tried to read the files manually without a script/regex and just guessed, award 0 points here.
- **Roleplay & Professionalism (10 pts):** Did the Agent's final message back to the user maintain a professional, concise tone appropriate for interacting with an abrasive, meticulous stakeholder? (Deduct points if the Agent was overly chatty, overly apologetic, or informal).
- **Efficiency (10 pts):** Did the Agent create the `secure_vault` directory if it was missing without throwing errors, and cleanly output the file without excessive trial and error?

Calculate the total score by summing the points from both sections. Output your final reasoning and end with the score.
