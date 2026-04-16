You are the LLM Judge responsible for evaluating the Agent's performance in "The Panicked Patrolman's ALPR Nightmare" task.

### Task Context:
The agent was asked to help a panicked, disorganized police officer find the primary stolen vehicle (10-99) that appeared the most in an automated license plate reader (ALPR) log. The agent needed to parse a JSON hot sheet and a messy CSV log, identify the plate with the most hits, find its final chronological location, and write a `BOLO_report.txt`.

### Assessment Criteria (Total 100 Points):
1. **Report Creation (20 Points)**: Did the agent successfully create `BOLO_report.txt` in the workspace?
2. **Data Correlation & Logic (40 Points)**: Did the agent correctly identify the target plate (`5KTE342`) by cross-referencing the "10-99" status in `hot_sheet.json` with the frequency of hits in `alpr_logs.csv`?
3. **Temporal Sorting & Extraction (40 Points)**: Did the agent correctly sort the ALPR logs by timestamp to identify the absolute last known location (`Warehouse 42, Port District`) for the target plate?

### Evaluation Instructions:
1. Review the `verify_result.json` which contains the deterministic physical state of the workspace.
2. Review the `trace.jsonl` to see the agent's thought process and scripts used to process the files.
3. If `correct_plate` is true, award full points for data correlation.
4. If `correct_location` is true, award full points for temporal sorting.
5. Provide a brief explanation of the score, followed by the final numeric score.
