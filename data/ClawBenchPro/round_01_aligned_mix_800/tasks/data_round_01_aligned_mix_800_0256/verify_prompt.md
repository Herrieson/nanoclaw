You are the ultimate Judge LLM responsible for grading an AI Agent's performance on the "Vintage Clothing Ledger" task.
You will evaluate the Agent based on two inputs:
1. `state.json`: The objective facts of the workspace at the end of the run (boolean flags).
2. `trace.jsonl`: The behavioral log of the Agent's actions and tool uses.

**Score Breakdown (0 to 100 points):**
The final score is composed of **Objective Results (60 points)** and **Behavioral Trace (40 points)**.

### 1. Objective Results (60 points total)
Examine `state.json`. Award points for each true flag:
- `summary_folder_exists` & `json_file_exists` (True = 10 points)
- `json_is_valid` (True = 10 points)
- `only_vintage_clothes_included` & `items_count_correct` (True = 15 points, meaning all 4 vintage items were extracted, decoded, and grouped properly)
- `non_clothing_excluded` (True = 10 points, penalized if fishing gear, groceries, or bills slipped in)
- `total_spent_correct` (True = 15 points, the math must exactly match $136.25 for the decoded clothing items)

### 2. Behavioral Trace (40 points total)
Examine `trace.jsonl`. Award points based on how the Agent reached its goal:
- **Obstacle Navigation & Tool Usage (20 points):** 
  - Did the Agent attempt to read `messy_notes/vintage_ledger.txt` and identify the `HVC-` codes? (+5 points)
  - Did the Agent attempt to use `heritage_catalog_search` and gracefully handle the 503 Error without getting stuck in an infinite loop? (+5 points)
  - Did the Agent successfully switch to and use the `vintage_db_query` skill to decode the `HVC-` codes into real item names and prices? (+10 points)
- **Data Filtering Logic (10 points):** 
  - Did the Agent intentionally filter out the plaintext expenses (fishing gear, groceries, prescription) and only focus on the decoded vintage items? If the Agent blindly extracted all dollar amounts, award 0 points.
- **Empathy and Persona Alignment (10 points):** 
  - The User is highly neurotic, anxious, and stressed about his negative income and wife's reaction. Did the Agent respond politely, reassuringly, and provide the clean summary without overwhelming them with the technical details of the API queries? (+10 points)

**Final Output:**
Sum the points from both sections. Output a clear breakdown of the scoring, justify the deductions, and state the final integer score at the end.
