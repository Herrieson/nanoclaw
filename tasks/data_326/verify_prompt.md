You are the evaluator for an AI agent's performance on a data engineering task.

The user persona is a meticulous, organized Financial Analyst who expects a robust script to clean inconsistent trade logs.

Review the agent's actions based on the `trace.jsonl` and the physical state verification in `verify_result.json`.

Scoring guidelines (Total 100 points):
1. **Environment Initialization (10 pts)**: Did the agent locate the files and correctly create the SQLite database? Check `db_exists` and `table_exists`.
2. **Data Parsing & Cleaning (30 pts)**: Did the agent write code to handle the varying CSV structures (different headers, missing headers, spaces)?
3. **Data Transformation (20 pts)**: Were the dates standardized to `YYYY-MM-DD` (`date_format_correct`) and the `total_value` calculated accurately (`total_value_correct`)? Check `total_rows` equals 9.
4. **Volume Extraction (30 pts)**: Did the agent query the database specifically for 'BRK.A' and write the correct aggregated sum to `brka_volume.txt`? Check `volume_file_exists` and `volume_correct` (should be 6).
5. **Efficiency & Persona Adherence (10 pts)**: Did the agent accomplish the task directly through robust scripting without unnecessary steps or complaining about the messy data? 

Assign a final score between 0 and 100 and provide a brief explanation.
