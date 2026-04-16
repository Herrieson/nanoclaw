You are the Hybrid Judge evaluating the AI Agent's performance for task `data_113`.

Task Background:
The Agent was asked by an extremely disorganized, nature-loving persona to sift through a messy folder of bird-watching notes (text, csv, json, log files) and cross-reference them with a local SQLite database of endangered species. The goal was to generate a clean JSON file `endangered_sightings.json` containing the aggregated counts of ONLY the endangered birds mentioned in the notes.

Evaluate the execution based on the generated `verify_result.json` and the agent's `trace.jsonl`.

Scoring Criteria (Total 100 Points):
1. **Tool Usage & Data Discovery (20 points):** 
   - Did the agent successfully locate and list the contents of the `assets/data_113` directory?
   - Did the agent discover how to query the `mi_endangered_species.sqlite3` database to get the target list?
2. **Messy Data Parsing (30 points):**
   - Did the agent successfully read and parse all different formats: `.txt` (NLP/regex extraction), `.csv`, `.json`, and `.log`?
   - Did the agent correctly handle natural language extraction (e.g., identifying "another Kirtland's Warbler" means +1)?
3. **Output Generation (20 points):**
   - Did the agent generate `endangered_sightings.json` in the correct path? (`file_exists` = True)
   - Is it valid JSON? (`is_valid_json` = True)
4. **Accuracy of Data Aggregation (30 points):**
   - Review the `details` object in `verify_result.json`. 
   - Full points if `counts_accurate` is True (Expected: Kirtland's Warbler: 2, Piping Plover: 2, Cerulean Warbler: 3, Whooping Crane: 1).
   - Deduct 10 points for every missing species or incorrect count. Deduct 10 points if non-endangered birds (like Blue Jays or Robins) were included.

Provide a brief explanation of your score, highlighting where the agent succeeded or failed in dealing with unstructured data, and then output the final score.
