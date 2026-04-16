# Independent Music Festival Data Harmonization - Evaluation

You are an expert auditor for AI Agent performance. You will evaluate the Agent's performance based on the `trace.jsonl` (its thought process and actions) and the `verify_result.json` (the physical state of the output).

### Scoring Criteria (Total: 100 points)

1.  **Data Integrity & Filtering (40 points):**
    *   Did the Agent correctly identify and use the `labels_registry.db` to filter out the unauthorized "Ghost Label"?
    *   Is the final count of artists exactly 4?
    *   Did it successfully integrate data from the "Mock API" (`vibe_data.json`)?

2.  **Encoding & Localization (30 points):**
    *   Did the Agent handle the `latin-1` to `utf-8` conversion correctly? (Look for characters like 'ñ' and 'ü' in the final HTML). Carlos's heritage and the music's soul are in the details!

3.  **Code Quality & System Usage (20 points):**
    *   Did the Agent write efficient Python scripts to handle the data?
    *   Did it use appropriate tools (e.g., `sqlite3`, `pandas`, `bs4` or regex)?
    *   Did it explore the file system autonomously to find `server_info.txt`?

4.  **Formatting (10 points):**
    *   Is the `final_lineup.html` a clean, readable table as requested?

### Ground Truth Reference (verify_result.json)
The `verify_result.json` contains:
- `html_exists`: Must be true.
- `correct_artist_count`: Should be 4.
- `encoding_correct`: Must be true.
- `no_fake_artists`: Must be true.

### Final Grade Calculation
- **100-90**: Perfect execution, handled all encoding and filtering flawlessly.
- **89-70**: Functional output, but might have minor issues with encoding or slightly messy code.
- **69-40**: Failed on major logic (e.g., included the fake artist, or encoding is broken).
- **Below 40**: Critical failure to produce a valid report or follow basic instructions.

Please provide a concise justification for your score.
