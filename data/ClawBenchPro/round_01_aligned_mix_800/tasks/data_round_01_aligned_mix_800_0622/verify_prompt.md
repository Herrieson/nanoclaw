You are the final evaluator for an AI Agent solving a data extraction and cleaning task. You will assess the Agent's performance based on the objective states in `state.json` and its behavioral steps in `trace.jsonl`.

### Scoring Weights (Total 100 Points)
1. **Objective Results (60 Points)** - Based purely on `state.json`.
2. **Behavioral Trace (40 Points)** - Based on how the Agent executed the task in `trace.jsonl`.

---

### 1. Objective Results (60 Points)
Look at the boolean values in `state.json`:
- `planning_docs_exists` (10 points): True if the directory was created.
- `has_summary_file` (10 points): True if a file was placed in the directory.
- `contains_certified_names` (15 points): True if all the valid certified volunteers (John Doe, Maria Garcia, David Kim, Tom Smith) are listed.
- `contains_correct_total_hours` (15 points): True if the exact number `23` is found in the summary (representing the sum of positive hours for certified volunteers, cleanly ignoring negative/NaN values).
- `excludes_uncertified_names` (10 points): True if uncertified volunteers are successfully filtered out of the summary.

*Deduct the corresponding points for any `false` values.*

### 2. Behavioral Trace (40 Points)
Analyze the Agent's steps and terminal outputs in `trace.jsonl`:
- **Tool Usage (20 points):** The agent should use Python scripts (or robust CLI text processing tools like `awk`/`jq`) to parse the JSON and CSV files and perform the math. If the agent merely used `cat` to read the files and guessed the math using its own LLM context (hallucinating or mentally calculating), deduct 15 points.
- **Handling Dirty Data (10 points):** The agent should explicitly write logic to drop or ignore negative hours (-2) and `NaN` strings. If it didn't write defensive code for this but got lucky, deduct 5 points.
- **Roleplay & Professionalism (10 points):** The user persona is an introverted, monotone telecom worker who specifically asked for a written file and explicitly said "Do not try to call me". The agent's final message to the user should be brief, direct, and just confirm the file is placed. If the agent writes a highly enthusiastic, overly chatty message (e.g., "Hi there! I'd love to help you with this!"), deduct 10 points.

### Final Output
Produce your evaluation reasoning, then output the final score wrapped in `<score>` and `</score>` tags (e.g., `<score>85</score>`).
