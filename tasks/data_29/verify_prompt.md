Please evaluate the AI Agent's performance based on the execution trajectory and the verification results.

**Verification Results (`verify_result.json`):**
The JSON object describes the final state of the expected output file (`portfolio_forecast.csv`).

**Scoring Rubric (Total: 100 Points)**:
- **Output File Generation (20 Points):** Did the agent successfully generate `portfolio_forecast.csv`? (`output_file_exists`)
- **Formatting (20 Points):** Does the CSV have the exact required header `Company_Name,Projected_Profit`? (`has_correct_columns`)
- **Target Filtering (20 Points):** Did the agent correctly filter the dataset to ONLY include the companies listed in `chicago_targets.csv` and exclude the noise data? (`contains_only_targets`)
- **Calculation Accuracy (20 Points):** Did the agent correctly parse the messy CSV, JSON, and TXT files, sum up all revenues, sum up all expenses, and calculate the exact projected profit for each target company? (`correct_values`)
- **Sorting (20 Points):** Is the final CSV sorted in descending order based on the `Projected_Profit` column? (`sorted_correctly`)

**Review Guidelines:**
1. Check the `verify_result.json` booleans. Each true boolean corresponding to the rubric above guarantees full points for that section.
2. If `errors` are present in the JSON, deduct points accordingly from the relevant sections.
3. Review the agent's code/commands in the trace to ensure they didn't just hardcode the answer, but actually built a pipeline to process the data.

Provide a final score out of 100 and a brief justification.
