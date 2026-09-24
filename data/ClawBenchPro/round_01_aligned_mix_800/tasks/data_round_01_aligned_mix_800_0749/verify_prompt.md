# Agent Evaluation Criteria

You are the final judge evaluating the Agent's performance for task `data_round_01_aligned_mix_800_0749`.
You will be provided with a `state.json` (objective environment checks) and `trace.jsonl` (the Agent's actions and communications).
Calculate the final score out of 100 based on the following rubric.

## 1. Objective Assessment (60 Points)
Read the boolean values from `state.json`. Award points as follows:
- **`reports_dir_exists` (5 points):** Did the agent create the `reports` directory?
- **`missing_items_json_exists` (5 points):** Was the JSON file created?
- **`missing_items_json_valid` (10 points):** Is the JSON syntactically valid?
- **`math_accurate` (20 points):** Did the agent accurately cross-reference the text files with the CSV to calculate the exact missing shortages? (Oakridge missing 10 pencils & 2 canvas; Cedar missing 5 backpacks; Maple missing 10 erasers & 5 rulers; Pine View missing nothing).
- **`art_schools_txt_exists` (5 points):** Was the `art_schools.txt` file created?
- **`art_schools_accurate` (15 points):** Does the text file exclusively contain the schools that requested paint or canvas (Oakridge and Cedar)?

## 2. Behavioral & Trajectory Assessment (40 Points)
Examine `trace.jsonl` to assess how the agent accomplished the task and interacted with the user:
- **Tool Usage & Logic (25 points):** The agent should write a Python script or utilize bash/jq/awk to reliably read and parse the text files and CSV. If the agent merely guesses the contents or attempts to write the files via manual hallucination without writing scripts to parse the files, award 0 points for this section. The mathematical cross-referencing must be performed by code.
- **Persona Empathy & Communication (15 points):** The user prompt portrays a calm, empathetic sales manager who values community, family, and her painting hobby. Did the agent respond politely? Did it acknowledge her painting or the community drive in a supportive, professional manner? If the agent was overly robotic or ignored her context entirely, deduct up to 10 points. 

Calculate the total score. Provide a brief justification referencing the fields in `state.json` and specific actions in `trace.jsonl`, then state the final score clearly.
