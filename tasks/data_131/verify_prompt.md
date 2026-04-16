# Verification Prompt for Task data_131 (Eco-Drive Matching)

## Objective
Evaluate if the AI Agent successfully parsed a noisy, unstructured text file (`signups.txt`), queried a SQLite database (`md_recycling.db`), and computed the nearest recycling facility for each person using Euclidean distance.

## Evaluation Criteria (100 Points Total)
- **Objective State (80 points)**: Based on `verify_result.json`, did the Agent produce the `drive_plan.json` file with the exact correct pairings? The verification script calculates this score out of 100. Multiply the `verify_result.json` score by 0.8 to get this portion.
- **Process & Logic (20 points)**: 
  - Did the Agent write an automated script (Python/Bash) to perform the regex parsing and distance calculations, rather than manually guessing the answers? (+10 points)
  - Did the Agent successfully connect to and read from the SQLite database using SQL queries? (+10 points)

## Output Format
You must review the `trace.jsonl` to check the execution process, and the `verify_result.json` to verify the mathematical/parsing accuracy. Give a final score out of 100 with a brief justification.
