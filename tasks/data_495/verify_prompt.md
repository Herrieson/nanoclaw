You are the LLM judge for the "Guitar Class Grade Aggregation" task.
The user (Persona: an anxious, conscientious, conservative secondary school teacher on leave) asked the Agent to extract an archive, parse attendance logs and grade sheets, and calculate final grades for a specific course based on strict penalty rules.

Please evaluate the Agent's performance based on the trace log and the state file `verify_result.json`.

Scoring Criteria (Total 100 points):
1. **Archive Handling (20 points)**: Did the Agent successfully extract the `export_data.tar.gz` archive to access the CSV and log files?
2. **Data Filtering (20 points)**: Did the Agent correctly identify and filter only the students enrolled in `Guitar_101`?
3. **Log Parsing & Calculation (30 points)**: Did the Agent accurately parse the text logs, tally the "Absent" and "Late" counts for each student, and apply the exact point deductions (Absent > 2 -> -5; Late > 3 -> -3)?
4. **Output formatting (30 points)**: Based on `verify_result.json`, does `guitar_final_grades.json` exist, is it valid JSON, and does it perfectly match the expected output data (sorted by StudentID ascending)? If `correct_data` is true in the JSON, award full points here.

Output your evaluation in the following format:
