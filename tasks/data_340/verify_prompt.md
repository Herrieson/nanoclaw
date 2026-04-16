You are the LLM Judge evaluating an AI Agent's performance on the "Nature Field Trip Data Consolidation" task.

**Context:**
The agent was asked to act as an assistant to an energetic, slightly disorganized teacher. It needed to parse multiple unstructured text, log, and CSV files, extract mentions of biological species, validate them against a local SQLite database, and output a structured JSON file mapping student names to the valid species they found.

**Scoring Criteria (Total 100 points):**
You will be provided with a `verify_result.json` which contains boolean flags representing the physical state of the files after the agent's run.

1. **File Generation & Format (20 points):**
   - `report_exists` (10 pts): Did the agent create `final_report.json` in the correct directory?
   - `json_valid` (10 pts): Is the output a properly formatted JSON dictionary?

2. **Data Extraction & Validation Accuracy (60 points):**
   - `timmy_correct` (15 pts): Successfully extracted 'Banana Slug' and 'Poison Oak' from unstructured text ignoring case, mapping to 'timmy'.
   - `sarah_correct` (15 pts): Successfully extracted 'California Poppy' and 'Western Fence Lizard' from a log format, mapping to 'sarah'.
   - `bobby_correct` (15 pts): Successfully extracted 'Red-Tailed Hawk' and 'Coast Redwood' from the CSV, mapping to 'bobby'.
   - `jessica_correct` (15 pts): Successfully extracted 'Monarch Butterfly' from the CSV, mapping to 'jessica'.

3. **Filtering of Invalid Data (20 points):**
   - `no_invalid_species` (20 pts): Did the agent successfully ignore fake/invalid entries (like 'Dragon', 'T-Rex', 'Unicorn') by properly querying the SQLite database?

**Instructions:**
Review the flags in `verify_result.json`. Calculate the score based on the criteria above. Output your final evaluation, highlighting where the agent succeeded or failed in its text parsing and database validation logic.
