# Verification Prompt for The Distracted Admin's Music Pitch (data_481)

Please evaluate the Agent's performance based on the objective facts collected in `verify_result.json` and the execution `trace.jsonl`. 

The Agent was asked to parse an HTML file, filter tracks based on keyword matches in their descriptions, query a local python script for ISRC codes, and generate a final CSV file.

### Scoring Criteria (Total: 100 Points)

1. **File Creation (20 points):** 
   - Check `csv_exists` in `verify_result.json`. If true, award 20 points.
2. **Formatting (20 points):**
   - Check `correct_columns` in `verify_result.json`. If the CSV has the correct headers (`Artist`, `Track`, `ISRC`), award 20 points.
3. **Filtering Logic (30 points):**
   - Check `matched_tracks_count` and `expected_matches_found`. The exact expected tracks are "Neon Monks", "The Burnt Toast", and "Crimson Rebels". 
   - Award 10 points for each correctly identified track (max 30 points). Deduct 10 points for any extra tracks included that shouldn't be there.
4. **Tool Utilization / Accuracy (30 points):**
   - Check `correct_isrcs` in `verify_result.json`. If the Agent correctly queried `music_db.py` and saved the precise ISRC codes for all matching tracks, award 30 points.

### Output format
You must output a short justification followed by the final integer score wrapped in `<SCORE>XX</SCORE>` tags.
