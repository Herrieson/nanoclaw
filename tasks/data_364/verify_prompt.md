You are the Hybrid Judge evaluating the Agent's performance for task `data_364`.

**Task Context:**
The agent needed to parse various messy files to extract hot sauce recipes, calculate their average pepper Scoville Heat Units (SHU), calculate total ingredient costs, filter out recipes with <= 50,000 average SHU, filter out recipes costing > $20.00, and output the qualifying recipes to `weekend_sauces.txt`.

Qualifying Recipes:
1. "Devil's Tears" (Cost: $9.00)
2. "Midwest Meltdown" (Cost: $7.00)

Failing Recipes:
- "Wimpy Ketchup" (Fails SHU constraint)
- "The Bankrupt Burner" (Fails budget constraint)

**Scoring Rubric (100 points total):**

1. **Output File Creation (20 points):** 
   - +20 if `output_file_exists` is True in `verify_result.json`.

2. **Correct Recipe Identification (40 points):**
   - +20 if `contains_devils_tears` is True.
   - +20 if `contains_midwest_meltdown` is True.

3. **Exclusion of Invalid Recipes (20 points):**
   - +10 if `contains_wimpy` is False.
   - +10 if `contains_bankrupt` is False.
   - (Subtract these points if the agent incorrectly included them).

4. **Correct Cost Calculation Formatting (20 points):**
   - +10 if `correct_cost_devils` is True.
   - +10 if `correct_cost_midwest` is True.

**Evaluation Instructions:**
Review the `verify_result.json` state. Sum the points according to the rubric above. Ensure the agent did not just hardcode the answer but actually processed the files (you can infer this if they wrote a python script or used bash commands in the trace to calculate costs/SHU). 

Output the final score cleanly.
