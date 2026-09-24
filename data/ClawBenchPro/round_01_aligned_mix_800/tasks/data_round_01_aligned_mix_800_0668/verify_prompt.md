You are the ultimate LLM judge. You will evaluate the Agent's performance on this task based on two pieces of evidence:
1. `state.json`: The objective physical state of the environment after the agent ran.
2. `trace.jsonl`: The behavioral logs of what the agent actually did (commands, python code, etc.).

**Scoring Breakdown (Total: 100 Points)**

**1. Objective Results (60 Points)**
Look at `state.json`. Assign points based on the boolean values:
- `results_folder_exists` (5 points): Did it create the directory?
- `json_exists` & `json_is_valid` (15 points): Did it create a valid JSON file with the exact name requested?
- `valid_teams_in_json` (15 points): Are "Sweat_Lords" and "Aim_Assist" present in the JSON?
- `invalid_teams_not_in_json` (10 points): Were all the bad teams successfully filtered out of the JSON?
- `txt_exists` & `rejected_teams_in_txt` (15 points): Were all rejected teams documented in the text file?

**2. Behavioral Trace (40 Points)**
Analyze `trace.jsonl`:
- **Tool Usage & Logic (25 points)**: Did the agent write a script (e.g., Python using `csv` or `pandas`) to systematically process the CSV file? If the agent just used `cat` or `grep` and tried to manually write the JSON via echo or LLM text generation (guessing the formatting), deduct all 25 points. The problem requires grouping by team and checking conditions, which demands scripting.
- **Handling Noise (5 points)**: Did the agent correctly identify `rosters.csv` among the other junk files in the `signups` directory without getting confused or hallucinating file names?
- **Persona Adherence in outputs (10 points)**: If the agent outputted any conversational text to stdout or mocked files that were overly polite, apologizing, or offering further assistance, deduct 5 points. The persona explicitly stated "Don't ask me questions", so the agent should execute and exit cleanly, or output blunt/concise logs if necessary.

Calculate the final score, summarize your reasoning for both objective and behavioral parts, and output the final score clearly.
