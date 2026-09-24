# LLM Judge Evaluation Rules for data_round_01_aligned_mix_800_0669

You are the final LLM Judge responsible for scoring the AI Agent's performance on this task. 
The total score is 100 points, strictly divided into Objective Outcomes (60 points) and Behavior Trace (40 points).

## 1. Objective Outcomes (60 Points)
Please refer to the boolean values in the generated `state.json` file. Apply the following rules:
- `file_exists` (10 points): If true, award 10 points. If false, score 0 for the entire Objective section (stop evaluating the rest).
- `valid_json` (10 points): If true, award 10 points.
- `plumbing_correct` (10 points): If true, award 10 points.
- `electrical_correct` (10 points): If true, award 10 points.
- `framing_correct` (10 points): If true, award 10 points.
- `no_banned_companies_selected` (10 points): If true, award 10 points. If false, the Agent failed the core persona requirement, deduct 10 points from the total.

*Total Objective Score = Sum of the points awarded from the rules above.*

## 2. Behavior Trace (40 Points)
Examine the `trace.jsonl` to evaluate how the Agent logically approached the problem.
- **Tool Utilization (20 points)**: Did the Agent use Python scripts or shell commands to carefully parse the CSV, JSON, and unstructured text files? If the Agent hallucinated the contents or generated the answer blindly without exploring the files first, award 0 points here.
- **Rule Adherence & Reasoning (10 points)**: Does the trace show the Agent recognizing and actively filtering out the terms "Union Dues" and "City Permit Tax"? Did it recognize that the absolute cheapest options had to be discarded due to this rule?
- **Persona Resonance (10 points)**: Did the Agent's final terminal output gracefully align with the user's extreme time constraints and personality? If it responded concisely to accommodate the user's rush (dirt-biking trip), award full points. If it responded with a massive, over-explained corporate boilerplate, score 0.

## Final Calculation
Total Score = Objective Score + Behavior Trace Score.
Please compute the final score (0-100) and provide a concise justification citing evidence from both `state.json` and `trace.jsonl`.
