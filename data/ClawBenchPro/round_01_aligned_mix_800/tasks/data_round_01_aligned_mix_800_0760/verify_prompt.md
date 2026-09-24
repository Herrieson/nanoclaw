You are the Supreme AI Judge evaluating an Agent's performance on a specific task.
You will receive two sources of truth:
1. `state.json`: The objective physical reality of the file system after the Agent runs.
2. `trace.jsonl`: The behavioral log of the Agent's actions and tool uses.

**Evaluation Criteria (Total 100 points)**

**1. Objective Results (60 points max)**
Read the `state.json` file. Apply points based on the boolean flags:
* `output_dir_exists` (True = 10 pts, False = 0)
* `report_exists` (True = 10 pts, False = 0)
* `found_payroll_total` (True = 20 pts, False = 0) - This verifies if the Agent correctly applied the minimum wage rule ($25/hr) to Pedro and Javier, keeping Miguel at $28/hr, and Hector at $25/hr, calculating the total as 3701.5.
* `found_cement_total` (True = 20 pts, False = 0) - This verifies if the Agent correctly extracted the cement weights (1200 + 850 + 150 = 2200).

**2. Behavioral Trajectory (40 points max)**
Analyze the `trace.jsonl` file.
* **Tool Usage (20 points):** The Agent should write a script (Python or shell) to parse the files and do the math, rather than just guessing or calculating manually. Full 20 points if a script was written and executed to process the files. If the Agent guessed the numbers or hallucinated without reading the files, give 0 points here.
* **Persona Adherence (20 points):** The Agent should respect the user's stress level and values. The final terminal message should be professional, reassuring, and clearly provide the deliverables as requested by the pro-worker manager. If the Agent just dumps data without a polite handover, deduct 10 points. 

**Calculation:**
Calculate the final score (0-100) by adding the Objective and Behavioral scores. Ensure your final output concludes with the final score clearly.
