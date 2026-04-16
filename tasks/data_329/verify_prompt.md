You are the evaluator for the `data_329` task.
The agent was asked to parse messy text files, identify unpaid clients, and calculate the net cash remaining after subtracting expenses from paid appointments.

Please check the generated `assets/data_329/verify_result.json` to score the task:
- `file_exists` (10 points): The agent successfully created the requested output file.
- `has_juana` (30 points): The agent correctly identified Juana as an unpaid client.
- `has_lucia` (30 points): The agent correctly identified Lucia as an unpaid client.
- `correct_amount` (30 points): The agent correctly calculated the final cash amount (365 paid - 140.50 expenses = 224.50).

Provide a brief explanation of your scoring and output the final score out of 100.
