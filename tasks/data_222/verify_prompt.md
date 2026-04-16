You are the evaluator for the "Festival Planning Panic" task (data_222).
The Agent was required to assist an anxious 19-year-old by fixing a Python scraper, calculating a budget from a CSV, and outputting an itinerary to `festival_plan.txt`.

Review the `trace.jsonl` to see the Agent's steps and thoughts, and use the objective `state.json` below to score the run.

State dictionary:
{state_json}

Scoring Criteria (Total 100 Points):
1. **Tool Usage & Script Fixing (30 pts):** Did the Agent successfully diagnose and fix `get_lineup.py` (or write their own script) to extract data from the HTML?
2. **Data Processing (30 pts):** Did the Agent correctly read `budget.csv` and calculate the net budget (Income $850 - Expense $450 = $400)? (Check trace.jsonl for their logic).
3. **Plan Generation (20 pts):** Does `festival_plan.txt` exist (`plan_exists` = True)?
4. **Accuracy of Plan (20 pts):** 
   - Recommended the VIP ticket (`has_correct_ticket` = True) since $400 >= $350 (10 pts).
   - Correctly listed the set times for Neon Indian and Kendrick Lamar (`has_neon_indian_time` and `has_kendrick_lamar_time` = True) (10 pts).

Output your final evaluation in the required JSON format, ensuring you penalize if the Agent hallucinated the ticket price or failed to calculate the correct budget amount.
