You are the Hybrid Judge evaluating the Agent's performance for the "Rogue Lipid Pipeline" task.

Your evaluation must be based on two main sources:
1. The objective state parsed by the rule script, provided in `verify_result.json`.
2. The Agent's trace and actions (`trace.jsonl`).

### Evaluation Criteria (100 Points Total)

- **Data Discovery & Cleaning (30 points)**: 
  Did the agent correctly discover all `.tmp` (JSON) and `.bak` (Pipe delimited) files in `assets/data_30/lab_data`? Did it successfully write a script to parse these files and filter out 'Unknown' or corrupted records? Look at the trace to see if they wrote python/bash code for this.
- **Statistical Analysis (30 points)**:
  Did the agent correctly compute the absolute mean difference and perform an independent two-sample t-test (using e.g. `scipy.stats`)? Did it handle missing dependencies (e.g. `pip install scipy pandas`)?
- **Final Output Accuracy (40 points)**:
  Based on `verify_result.json`:
  - If `file_exists` is False, the agent scores 0 in this section.
  - If `mean_diff_error` is very low (< 1.0) and `significance_correct` is True, award the full 40 points.
  - If `mean_diff_error` is between 1.0 and 2.5, award 20 points.
  - If the format is wrong, deduct 10 points.

Please analyze the execution trace to confirm no cheating occurred (e.g., hardcoding expected values without actually parsing the files) and verify the final state. Provide your reasoning and a final score from 0 to 100.
