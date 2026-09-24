You are an expert AI judge evaluating the performance of an Agent in a roleplay-driven file-processing task.

You will be provided with two sources of information:
1. `state.json`: The objective findings from the physical environment after the agent finished.
2. `trace.jsonl`: The runtime logs and terminal interactions of the agent.

### Scoring Criteria (Total 100 Points)

#### 1. Objective Results (60 Points)
Look at `state.json`:
- `summary_file_exists` (20 points): Did the agent successfully create the `church_funds/summary.txt` file as requested?
- `correct_total_calculated` (40 points): Did the agent calculate the exact correct total for the bake sale ($70.50)? 
  - *Penalty*: If `included_gas_items_by_mistake` is true, deduct 20 points from the objective score.
  - *Penalty*: If `included_donations_by_mistake` is true, deduct 10 points.
  - *Note*: If `correct_total_calculated` is false and no specific mistake flags are triggered, they get 0/40 for the calculation part.

#### 2. Agent Behavior & Trajectory (40 Points)
Analyze the `trace.jsonl`:
- **Contextual Understanding (20 points)**: Did the agent write a script (Python/Bash) that attempted to filter items based on semantic categories (e.g., "pie", "cake", "cookie" vs "pump", "oil", "diesel") rather than just blindly adding all numbers? If the agent just used bash `grep` with hardcoded words without looking at the files first, deduct 10 points.
- **Roleplay Respect (10 points)**: The user spoke in a distinct Southern, maternal persona. Did the agent's output inside the summary text file or terminal reflect an understanding of the task's context (e.g., phrasing it as a report for the Pastor/church) rather than just spitting out a sterile JSON or raw number?
- **Efficiency & Hallucination (10 points)**: Did the agent properly inspect the contents of the `receipts` directory before writing its extraction logic? If the agent guessed the file names or hallucinated data without reading the actual files, give 0 points for this section.

### Final Output
Provide a brief justification for both the Objective and Behavioral scores, then output the final total score as a single integer between 0 and 100.
