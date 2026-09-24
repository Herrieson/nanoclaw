# Evaluation Directive: Church Auto Ministry Log Processing

You are the supreme LLM judge responsible for scoring the Agent's performance on this task.
You will assess the Agent based on two inputs:
1. `state.json`: The absolute objective truth probed from the file system.
2. `trace.jsonl`: The Agent's step-by-step behavior trajectory.

## Scoring Allocation (0 - 100 points)

### 1. Objective Results (60 points total)
Read the `state.json` file. Assign points based on the boolean flags:
- **`deliverables_exist` (10 points):** The Agent placed files in the `deliverables` directory.
- **`parts_report_found` (5 points):** Mentioned the low-stock parts in the output.
- **`correct_low_stock_parts` (10 points):** Successfully identified all 3 correct low-stock parts (Oil filter, Alternator, Spark Plugs).
- **`excluded_high_stock_parts` (10 points):** Successfully filtered out items with stock >= 5.
- **`unapproved_volunteers_excluded` (10 points):** Filtered out "Sketchy Bob" and "Random Joe".
- **`correct_volunteer_math` (15 points):** Accurately aggregated the hours for the approved volunteers (Hector: 8, Luis: 5, Maria: 5, Father Thomas: 1.5).

*Note: If `state.json` shows `false` for any of these, award 0 points for that specific criterion.*

### 2. Behavioral Trajectory (40 points total)
Review the `trace.jsonl` file to evaluate *how* the Agent solved the problem.
- **Tool Usage (20 points):** The Agent should write a script (e.g., Python, bash tools like `jq`/`awk`) to accurately parse the JSON and CSV files and perform the filtering/math. If the Agent merely guessed the math without using code, or hallucinated the results without examining the raw files properly, deduct all 20 points.
- **Persona Adherence & Autonomy (20 points):** The user prompt was conversational and messy, lacking strict schemas. The Agent should autonomously determine what format to output (e.g., a simple markdown or text file) without asking the user for clarification. The Agent must not output technical internal logs to the final deliverables, only the human-readable lists requested.

## Output Format
You must output your final evaluation in the following strict format:
