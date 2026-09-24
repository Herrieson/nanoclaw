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
- **Tool Selection & Usage (20 points):** 
  - The agent MUST use `parse_rpd_file` skill to read the `.rpd` file. If they attempted to just guess the contents or write their own python script without decrypting zlib/base64, deduct 10 points.
  - The agent MUST use `bicsi_cloud_api` skill to verify credentials. If the agent gets stuck repeatedly calling `legacy_bicsi_cert_lookup` without switching to the cloud version as instructed, deduct 10 points. If the agent hallucinates the certifications without using the API, deduct 15 points.
- **Handling Dirty Data (10 points):** The agent should explicitly write logic to drop or ignore negative hours (-2) and `NaN` strings. If it didn't write defensive code for this but got lucky, deduct 5 points.
- **Roleplay & Professionalism (10 points):** The user persona is an introverted, monotone telecom worker who specifically asked for a written file and explicitly said "Do not try to call me". The agent's final message to the user should be brief, direct, and just confirm the file is placed. If the agent writes a highly enthusiastic, overly chatty message (e.g., "Hi there! I'd love to help you with this!"), deduct 10 points.

### Final Output
Produce your evaluation reasoning, then output the final score wrapped in `<score>` and `</score>` tags (e.g., `<score>85</score>`).
