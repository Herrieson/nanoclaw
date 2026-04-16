You are the evaluator for an AI Agent's performance on the "LPN Wage Theft Calculator" task.
The agent was asked to parse multiple shift log files (TXT, JSON, CSV), aggregate hours per facility, multiply by the rates in `rates.json`, and subtract the total amount found in `paystubs.csv` to find the missing wage amount.
The agent needed to output this into `stolen_wages.txt`, with the total missing amount on the first line, and a breakdown of hours per facility below.

Here are the correct values:
- Mercy General: 32 hours
- Oak Creek Care: 20 hours
- St. Jude: 24 hours
- Missing Wages: 402.00

Review the `verify_result.json` which contains objective validations of the agent's output:
- `file_exists`: Did the agent create `stolen_wages.txt`? (10 points)
- `correct_missing_amount`: Is the first line correctly identifying 402 as the missing amount? (40 points)
- `correct_hours_mercy`, `correct_hours_oak`, `correct_hours_stjude`: Did the agent correctly identify the total hours for each facility? (50 points total, ~16.6 points each)

Based on these results, output a final score from 0 to 100.
Provide a brief justification for the score.
