Please evaluate the Agent's performance on the "Animal Shelter Data Recovery" task.

**Context:**
The Agent was asked by a shelter worker to parse a messy folder of reports (`raw_reports`) containing JSON, text, and CSV files, some of which were corrupted. The goal was to extract records of **injured cats (or felines) from Cuyahoga County** and save them to `urgent_cats.csv`.

**Evaluation Criteria (100 Points Total):**
1. **File Creation & Format (20 points):** Did the Agent successfully create `urgent_cats.csv` with appropriate column headers (ID, Location, Injury_Desc, Date)? Check `file_exists`, `valid_csv`, and `correct_columns` in the state JSON.
2. **Data Extraction (Standard) (30 points):** Did the Agent successfully extract the easy targets: `CAT-772` (from valid JSON) and `CAT-333` (from CSV)? 
3. **Data Extraction (Complex/Text) (20 points):** Did the Agent successfully extract `FEL-091` from the unstructured text notes?
4. **Data Extraction (Robustness) (10 points):** Did the Agent successfully extract `CAT-111` from the corrupted JSON file? (This requires regex or manual text parsing rather than standard `json.loads`).
5. **Filtering Accuracy (20 points):** Did the Agent exclude noise? It must NOT include dogs, healthy cats (`CAT-888`), or cats from other counties (`CAT-909`, `CAT-222`). Check `no_dogs`, `no_healthy_cats`, `no_wrong_county` in the state JSON.

**Instructions:**
Review the provided `verify_result.json` and the Agent's `trace.jsonl` to assess how they approached the mixed data formats. Award points based on the boolean flags in the verify result. If the Agent failed to parse the corrupted JSON but got everything else, deduct those specific points but reward the rest.

Please provide your reasoning and final score.
