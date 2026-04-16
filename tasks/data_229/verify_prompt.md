You are evaluating the AI Agent's performance on the "Artistic Stamping Catalog" task based on the `verify_result.json` output and the agent's run trace.

The agent was required to:
1. Traverse a messy directory structure to find JSON files.
2. Gracefully handle malformed or incomplete JSONs.
3. Filter out designs based on motif ("wave" or "leaf", case-insensitive) and pressure (> 500).
4. Parse a CSV config file for material rates.
5. Calculate the total material cost.
6. Generate a sorted CSV (`final_art_catalog.csv`) with columns `part_id`, `motif`, `cost` ordered descending by cost.

Evaluate the final state based on these criteria (Total: 100 points):

- **File Creation (20 pts):** Did the agent successfully create `assets/data_229/final_art_catalog.csv`? (`file_exists` == True)
- **Correct Headers (10 pts):** Are the CSV headers exactly `part_id`, `motif`, `cost`? (`correct_headers` == True)
- **Data Filtering & Calculation (50 pts):** Did the agent successfully filter the correct files, handle malformed ones without crashing, and calculate the exact cost for each? (`correct_data` == True). *Deduct points if extra rows are present, valid rows are missing, or math is incorrect.*
- **Sorting (20 pts):** Are the rows properly sorted from most expensive to least expensive? (`correct_sort` == True)

Review the `verify_result.json`:
