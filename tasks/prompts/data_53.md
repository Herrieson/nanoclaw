Look, I'm opening the restaurant in three hours and I don't have time for nonsense. I'm tapping my foot so hard I might drill a hole in the floor. 

My friend wrote a script to handle our employee timesheets, but it completely crashed and deleted the weekly summary. All I have left are the raw daily punch logs in the `timesheets/` folder and the employee roster `roster.csv` inside my workspace directory.

Here's what I need you to do, and I need it done perfectly because I cannot stand sloppy work:
1. Go through all those daily punch logs. 
2. Calculate the total hours worked for each employee this week. 
3. If some idiot forgot to clock out (meaning they have an "IN" punch but no "OUT" punch for that day), their hours for that specific day are ZERO. I'm not paying them for forgetting the rules.
4. Generate a neat report and save it exactly as `payroll_report.txt` in the same directory.
5. The report MUST be formatted like this:
   `[Employee Name] - [Total Hours] hours`
   And it MUST be sorted alphabetically by the employee's first name.
6. At the very bottom of the file, add a line: `Overtime alert: [Name1], [Name2]` listing anyone who worked strictly more than 40 hours, alphabetically. If no one, write `Overtime alert: None`.

I'm going back to organizing my crafting supplies to calm my nerves. Just get it done.
