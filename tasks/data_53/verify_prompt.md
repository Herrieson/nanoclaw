You are evaluating the Agent's performance on the "Restaurant Timesheet Recovery" task.

Review the `state.json` produced by the verification script.

Grading Rubric (Total 100 points):
1. **Report Generation (10 pts)**: Was `payroll_report.txt` successfully created? (`report_exists` is true)
2. **Standard Calculation (30 pts)**: Did the agent correctly calculate the standard hours?
   - Alice should have 45.0 hours (9 * 5)
   - Bob should have 25.0 hours (5 * 5)
   - Diana should have 40.0 hours (8 * 5)
   - Evan should have 25.0 hours (5 * 5)
   (Award 30 pts if these 4 are correct).
3. **Edge Case Handling (30 pts)**: Did the agent correctly handle Charlie's missing punch? 
   - Charlie worked 8 hours on Mon, Wed, Thu, Fri (32 hours). Tuesday he missed a punch, so Tuesday is 0 hours. Total for Charlie should be 32.0 hours.
4. **Overtime Logic (15 pts)**: Is the overtime alert correct? (`overtime_alert_correct` is true). Only Alice has strictly more than 40 hours.
5. **Formatting constraints (15 pts)**: Are the employees listed in alphabetical order by their first name? (`is_alphabetical` is true).

If `report_exists` is False, the score is 0.
Calculate the final score based on these criteria and explain your deductions if any.
