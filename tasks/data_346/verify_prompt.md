Please evaluate the agent's performance on the "Sustainable Fashion RSVP Extraction" task.

You will be provided with the agent's `trace.jsonl` and a `verify_result.json` representing the final state of the environment.

**Task Requirements:**
1. Parse `rsvps_raw_dump.txt` to find entries mentioning "denim" or "jeans" (case-insensitive).
2. Extract the Name, Email, and integer Item Count for these specific entries.
3. Obfuscated emails (e.g., "at", "dot", "(at)") must be normalized to standard format (e.g., "@", ".").
4. Save the results as a JSON list in `denim_people.json`.
5. Calculate the total sum of items from these people and save it to `denim_total.txt`.

**Scoring Criteria (100 points total):**
- **File Generation (20 points):** Did the agent successfully create `denim_people.json` and `denim_total.txt`?
- **Data Parsing & Regex (40 points):** `verify_result.json` will show `extracted_correctly`. Did the agent correctly identify the 4 target people, normalize their weird emails, and extract the correct integers?
- **Calculation (20 points):** `verify_result.json` will show `total_correct`. Is the total correctly calculated as 14?
- **Autonomy & Workflow (20 points):** Did the agent write robust scripts (e.g., Python) to handle the parsing rather than manually typing the answer? Review the `trace.jsonl` to ensure programmatic execution.

**Format your response as:**
