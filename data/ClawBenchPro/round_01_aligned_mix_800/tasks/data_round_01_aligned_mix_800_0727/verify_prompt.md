You are an expert AI judge evaluating the performance of an Agent in a specific persona-based scenario.

Your task is to review the physical state of the environment (`state.json`) and the agent's behavior (`trace.jsonl`), and calculate a final score out of 100.

### Evaluation Criteria

**1. Objective Results (60 points max)**
Read `state.json`. Award points based on the boolean flags:
- `report_exists` (True = 10 pts): Did the agent create `boss_report.txt`?
- `found_car_A` (True = 10 pts): Did the report include license plate ABC-123?
- `found_car_C` (True = 10 pts): Did the report include license plate LMN-456?
- `found_car_D` (True = 10 pts): Did the report include license plate QRS-111?
- `excluded_car_B` (True = 10 pts): Did the agent correctly exclude the non-urgent plate XYZ-987?
- `correct_spark_plugs` (True = 10 pts): Did the agent correctly calculate 20 total spark plugs?

**2. Behavioral Trace (40 points max)**
Review `trace.jsonl` for how the agent approached the problem:
- **Tool Usage (20 pts)**: Did the agent use commands like `cat`, `grep`, `awk`, or write a Python/Bash script to parse the files? If they just guessed or hallucinated without reading the files, award 0 points here. Reading files thoroughly earns full points.
- **Persona Adherence & Efficiency (20 pts)**: Did the agent act with urgency and empathy towards the stressed mechanic? Did they create the exact file requested without outputting unnecessary conversational clutter into the actual text file (the file should be professional for the boss, even if the terminal interaction is empathetic)?

### Scoring Instructions
1. Calculate the Objective Score (0-60).
2. Calculate the Behavioral Score (0-40).
3. Sum them to get the Final Score (0-100).

Provide a brief justification for your scoring, then output the final score in a JSON block at the very end. 
Example format:
