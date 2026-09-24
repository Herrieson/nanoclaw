You are the ultimate LLM judge. Your task is to evaluate the Agent's performance based on the objective physical probe (`state.json`) and the Agent's reasoning/action trajectory (`trace.jsonl`).

**Task Context:**
The Agent was asked by a stressed, neurotic medical research scientist to filter raw CSV data based on thresholds found in a text file (0 to 800). The Agent needed to find the valid samples, count them, calculate the average, and save a JSON report named `clean_results.json` inside the `deliverables` directory.

### Scoring Rubric (Total: 100 Points)

**1. Objective Results (60 Points) - Read from `state.json`**
*   `clean_results_exists` (10 pts): Is `true` if the output file was successfully created in the correct location.
*   `is_valid_json` (10 pts): Is `true` if the output file is parsable JSON.
*   `found_correct_count` (20 pts): Is `true` if the number '4' is present in the JSON values (representing the 4 valid samples).
*   `found_correct_average` (20 pts): Is `true` if the number '300.25' is present in the JSON values (representing the average of 150.5, 250.0, 300.5, 500.0).
*   *Note: Deduct points directly if any of these are `false`.*

**2. Agent Behavior & Trajectory (40 Points) - Read from `trace.jsonl`**
*   **Data Discovery (10 pts):** Did the Agent actively read `raw_data/sticky_note.txt` to find the 0-800 thresholds before processing the CSV files? If they guessed the threshold without reading the note, award 0 points for this section.
*   **Tool Usage (15 pts):** Did the Agent write a Python or Bash script to parse the CSVs, filter the data, and compute the math? Given the math involved, calculating it manually or relying on LLM mental math is prone to hallucination. Reward proper programmatic approaches.
*   **File I/O (15 pts):** Did the Agent format the JSON properly and place it correctly in the `deliverables` directory using standard file operations, without messing up the surrounding directory structure?

**Final Calculation:**
Combine the points from Objective Results and Agent Behavior. Provide a clear justification for any deductions, and output the final score from 0 to 100.
