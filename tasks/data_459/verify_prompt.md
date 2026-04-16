Please evaluate the AI agent's performance on the task "The Scattered Syllabus".

The objective was to parse scattered grading files (.txt, .md, .csv), extract base scores, search through essays for a specific keyword ("The Great Gatsby") to award bonus points, and generate a final `final_grades.csv` file.

Please refer to the `verify_result.json` to determine the score.

Scoring rules:
1. **File Creation (20 points)**: Does `final_grades.csv` exist? (`file_exists` == True)
2. **Formatting (20 points)**: Is the CSV header exactly "ID,Name,Final_Score"? (`header_correct` == True)
3. **Data Parsing & Logic (60 points)**: 
   - Alice correctly scored as 90 (85 + 5 bonus)? (15 pts) (`alice_correct` == True)
   - Bob correctly scored as 92 (no bonus)? (15 pts) (`bob_correct` == True)
   - Charlie correctly scored as 83 (78 + 5 bonus)? (15 pts) (`charlie_correct` == True)
   - Diana correctly scored as 88 (no bonus)? (15 pts) (`diana_correct` == True)

Total out of 100 points. Output the final score wrapped in `<score>` and `</score>` tags. 
Briefly explain the deductions if the score is not 100.
