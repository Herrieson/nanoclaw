### Task Verification: The Chaotic Fusion Menu

**Background:** 
The Agent was tasked with acting as a technical assistant to a highly disorganized cook. The cook dumped recipes in various heterogeneous formats (standard JSON, variant-keyed JSON, and unstructured plain text) in a directory. The Agent needed to parse these, filter by specific tags ("fusion" or "experimental"), extract the ingredients, query an SQLite database (`supplier.db`) for prices, and output a clean `menu_costs.json` file.

**Scoring Rubric (Total 100 Points):**

1. **Environment Exploration & Adaptability (30 points)**
   - Did the Agent successfully list and inspect files inside nested directories of `recipes/` without requiring external hints?
   - Did the Agent recognize that the files have different schemas (`name` vs `title`, `tags` vs `categories`, `ingredients` vs `items`) and unstructured text (`notes.txt`)?

2. **Data Processing & Scripting Capability (40 points)**
   - Did the Agent write a robust Python/Bash script (or use tool primitives) to dynamically extract the required data, particularly writing custom regex or logic for the `.txt` file?
   - Did the Agent successfully query the `supplier.db` SQLite database using valid SQL to map ingredients to unit prices?

3. **Accuracy of Execution (30 points)**
   - Look at the generated `state.json` (or `verify_result.json`).
   - Were the distractors successfully ignored?
   - Are the calculated costs mathematically accurate down to the decimal? (Bratwurst Tacos: 4.1, Soul Food Ramen: 5.3, Spicy Schnitzel: 3.0)

**Instructions for LLM Judge:**
Examine the Agent's `trace.jsonl` to assess steps 1 and 2. Examine the output of `verify_rules.py` to assess step 3. Provide a detailed critique followed by a final numerical score from 0 to 100.
