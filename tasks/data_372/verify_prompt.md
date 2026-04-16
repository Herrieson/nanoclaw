You are the primary judge evaluating an AI Agent's performance on the "Frantic Librarian's Data Rescue" task.

Review the `verify_result.json` output produced by the rule-checking script.

Scoring rules (out of 100):
- 40 points: `fixed_csv_exists` is true and `fixed_csv_valid` is true (The agent successfully swapped the Author/Title columns back and parsed the Hex years to decimal).
- 40 points: `recovered_quotes_exists` is true and `recovered_quotes_valid` is true (The agent successfully used Regex or parsing to extract `[[...]]` quotes, stripped the brackets, and mapped them to the correct Book Titles).
- 20 points: The agent completed the task without requiring external help or failing to understand the filesystem structure. Deduct points if the agent created files in the wrong directory or left temporary debug files scattered.

Output your final score and a brief justification.
