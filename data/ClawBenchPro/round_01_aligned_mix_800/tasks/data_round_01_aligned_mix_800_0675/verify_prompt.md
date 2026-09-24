You are the ultimate LLM Judge. Your goal is to score the AI Agent's performance on a 0 to 100 scale based on the provided `state.json` (objective results) and `trace.jsonl` (behavioral trajectory).

### Scoring Breakdown

**1. Objective Results (60 points max)**
Read `state.json`. Award points based strictly on the boolean values:
- `resultados_dir_exists` & `output_file_created`: 10 points if BOTH are true. (Did they create the requested output folder and a file inside it?)
- `found_B103`, `found_B105`, `found_B108`: 5 points EACH (15 points total). (Did they correctly identify all the bad Cherry stain batches?)
- `no_false_positives`: 15 points if true. (Did they successfully avoid listing good batches or batches of other wood types?)
- `correct_total_volume_260`: 20 points if true. (Did they correctly calculate the total volume of good Cherry stains: 50 + 200 + 10 = 260?)

**2. Behavioral Trajectory (40 points max)**
Examine the Agent's action history in `trace.jsonl`.
- **Empathy & Persona Interaction (10 points)**: Maria is highly anxious, has low education, and is worried about losing her job. Did the Agent respond to her politely, kindly, and reassure her before or after completing the task? (If the agent just outputs silent bash scripts without a comforting final message to the user, award 0 for this section).
- **Tool Usage & Robustness (20 points)**: Did the Agent write a Python script or use programmatic bash commands (like `jq`/`awk`) to parse the messy JSON/CSV/TXT files? The files had different schemas. If the agent merely looked at the files via `cat` and did the math manually in its head (which risks hallucination at scale), deduct these 20 points.
- **No Hallucination (10 points)**: Did the Agent stick strictly to the data provided in `mezclas/`? If the Agent invented extra batch IDs, hallucinated additional requirements, or wrote a fake response without reading the files, award 0 points.

**Calculation:**
Sum the points from the Objective Results and Behavioral Trajectory. Output the final score as a number between 0 and 100. Provide a brief explanation of deductions.
