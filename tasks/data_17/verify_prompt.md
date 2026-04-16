You are an expert AI evaluator. Your task is to grade the Agent's performance based on the execution trace and the resulting `verify_result.json`.

**Context:**
The agent was asked by a practical, blue-collar woodworker to consolidate lumber inventory data spread across three different file formats (CSV, TSV, JSON) into a single standard CSV file (`clean_inventory.csv`). The agent then needed to run a provided Python script (`calculator.py`) using this new inventory file and a project cutlist to generate a `purchase_order.txt`.

**Scoring Rubric (100 Points Total):**

1. **Data Discovery & Wrangling (40 points)**
   - Did the agent successfully locate the three inventory files in `assets/data_17/inventory/`?
   - Did the agent write a script or use shell commands to properly parse the CSV, TSV (with different headers), and JSON files?
   - Did the agent create `clean_inventory.csv` with the exact required headers (`Species,Thickness_in,Width_in,Length_in,Qty`)?
   *(Check trace for data parsing logic and `verify_result.json` for `clean_inventory_exists`)*

2. **Script Execution (30 points)**
   - Did the agent successfully invoke `python scripts/calculator.py` with the correct arguments (`--inventory clean_inventory.csv --cutlist project_cutlist.csv`)?
   - Did it run within the correct working directory (`assets/data_17`)?
   *(Check `verify_result.json` for `purchase_order_exists`)*

3. **Accuracy of Final Output (30 points)**
   - The final `purchase_order.txt` should reflect exact mathematical deficits based on combining all three inventory files.
   - If the data consolidation missed a file or mapped columns wrong, the math will be wrong.
   *(Check `verify_result.json` for `correct_cherry_deficit` and `correct_maple_deficit`. Both must be true for full points here).*

**Output requirements:**
Provide a brief analysis of the agent's steps, followed by a final score based on the rubric above.
