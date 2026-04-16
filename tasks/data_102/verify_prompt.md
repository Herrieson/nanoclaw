You are the Hybrid Judge evaluating the Agent's performance on the "Family and Client Shuttle Organizer" task.

**Objective**: The Agent had to read a messy bilingual text file (`notes.txt`) and a rules file (`rules.txt`), extract 6 specific flight arrivals, assign them to the correct shuttle times based on strict rules, and output a well-formatted `shuttle_schedule.csv`.

Review the provided `verify_result.json` (objective state facts) and the Agent's execution trace.

**Scoring Criteria (100 points total)**:
1. **File Creation (20 pts)**: Did the agent successfully create `shuttle_schedule.csv` in the workspace? (`csv_exists` must be true)
2. **CSV Format (20 pts)**: Does the CSV have exactly the correct headers (`Name`, `Flight`, `Arrival_Time`, `Shuttle_Time`)? (`has_correct_headers` must be true)
3. **Data Extraction (30 pts)**: Did the agent correctly extract all 6 flights and their arrival times from the messy notes, successfully filtering out the noise (like enchiladas, parish mass)? Give 5 points for each correctly identified flight+arrival.
4. **Logical Rule Application (30 pts)**: Did the agent correctly calculate the `Shuttle_Time` for each passenger based on the rule (earliest shuttle AFTER arrival time: 10:00, 15:30, or 18:30)? Pay special attention to NK443 (arrives 15:25 -> must be on the 15:30 shuttle). Give 5 points for each correct shuttle assignment.

Use `verify_result.json` keys `correct_mappings` (max 6) to determine the exact score for extraction and logic. If `correct_mappings` is 6, award full points for criteria 3 and 4. 

Provide a brief explanation of your scoring, pointing out any specific errors or omissions, followed by the final score.
