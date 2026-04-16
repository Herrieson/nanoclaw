You are an AI judge evaluating a task where the agent was asked to organize a disorganized teaching assistant's workspace.

The agent was required to:
1. Parse a messy folder to extract student grades, differentiating between text notes and CSV structures, and ignoring recipe instructions or yoga plans.
2. Calculate the average score for each student (Alice: 80.0, Bob: 92.0, John: 86.5, Sarah: 92.5).
3. Output the results to a clean `consolidated_grades.csv` containing columns for Name and Average.
4. Move any purely recipe-related files into a `recipes/` directory.

Please review the `verify_result.json` outputted by the automated test script and the agent's `trace.jsonl` execution log.
- `grades_csv_exists` (20 points): The output CSV file was created.
- `grades_correct` (50 points): The parser successfully found all 4 students, calculated the correct averages across multiple files, and formatted them properly.
- `recipes_folder_exists` (10 points): The agent created the `recipes` directory.
- `recipe_moved` (20 points): The pure recipe file (`dinner_ideas.txt`) was moved or copied into the recipes directory.

Provide the final score (0 to 100) along with a brief explanation of the agent's performance in navigating the unstructured data.
