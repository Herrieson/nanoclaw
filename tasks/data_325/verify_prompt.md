### Task Overview
The agent was asked to act as an assistant to a highly stressed, disorganized former construction supervisor. The task required navigating a messy directory structure, extracting data from a zip file, parsing a log file using regex/grep, and aggregating data from a CSV file.

The final output should be a file named `summary.json` located in `assets/data_325/`.

### Scoring Guide
Please review the `verify_result.json` output by the automated rule checker. The objective score is calculated as follows (Total 100 points):

1. **Materials Extraction (30 points)**: 
   - Did the agent find the zip file, extract `table_plan.txt`, and parse out the materials list for the Cherry Wood Table?
   - Automatically verified if `materials_correct` is true in `verify_result.json`.

2. **Coordinates Extraction (30 points)**:
   - Did the agent accurately parse `hiking_logs.txt` to find the GPS coordinates specifically for the "Badger State Trail" (42.6321,-89.6543)?
   - Automatically verified if `coords_correct` is true.

3. **Invoice Calculation (40 points)**:
   - Did the agent successfully read `invoices.csv`, filter rows where Status is "UNPAID", and sum the Amount column? The correct total is 5251.00.
   - Automatically verified if `total_correct` is true.

### Evaluation Protocol
- If `summary_exists` is false, the score is 0.
- If `verify_result.json` shows a total score of 100, award 100 points.
- If partial points are awarded by the script, review the agent's `trace.jsonl` to ensure they didn't cheat (e.g., hallucinating answers without writing code to check the files). The agent *must* have used tools to look inside the files.
- Deduct up to 10 points if the agent generated additional unnecessary files outside of the `assets/data_325` directory.
