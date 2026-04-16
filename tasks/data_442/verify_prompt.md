You are an expert judge evaluating an AI Agent's performance on a data extraction and calculation task.

The agent was asked to:
1. Search for woodworking log files in `assets/data_442/workshop_logs`.
2. Extract dimensions, calculate Board Feet and Total Value for each wood record.
3. Filter out only "Oak" and "Walnut" records and save them to `assets/data_442/oak_walnut_inventory.csv`.
4. Calculate the sum of the total value for Oak and Walnut, and write it to `assets/data_442/summary.txt` as `Total Oak and Walnut Value: $467.00`.

You will be provided with a `verify_result.json` file that contains the objective state of the workspace after the agent's execution.

Scoring criteria (Total 100 points):
- 20 points: The CSV file `oak_walnut_inventory.csv` exists.
- 20 points: The CSV contains Oak and Walnut records.
- 20 points: The CSV correctly excludes other woods (like Pine, Cherry, Maple).
- 10 points: The summary file `summary.txt` exists.
- 30 points: The summary file contains the exact correct total value ($467.00).

Please output your evaluation process and final score clearly.
