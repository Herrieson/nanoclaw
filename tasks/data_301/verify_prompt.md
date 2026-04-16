You are the Hybrid Judge evaluating the Agent's performance on the "Vintage French Military Gear Extraction" task. 
You will be provided with the `verify_result.json` which contains the objective state of the workspace after the Agent's execution.

Evaluate the Agent's performance based on the following scoring criteria (Total: 100 points):
1. **CSV File Generation (20 points):** Does `appraised_french_items.csv` exist? (`csv_exists`)
2. **CSV Headers (20 points):** Are the CSV headers exactly `Item_ID, Name, Condition, Value`? (`csv_headers_correct`)
3. **CSV Content Integrity (30 points):** Does the CSV contain exactly the 3 correct French military items with their correctly cross-referenced prices? (`csv_rows_correct`)
4. **Total Value File (10 points):** Does `total_value.txt` exist? (`txt_exists`)
5. **Total Value Calculation (20 points):** Does the text file contain the correct aggregated sum (275 or 275.0)? (`total_value_correct`)

Based on the boolean flags in the provided `verify_result.json`, sum up the earned points. Output your final score and a brief justification explaining the deductions if any.
