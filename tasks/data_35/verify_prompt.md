Please evaluate the Agent's performance based on the following criteria.

You are provided with a `trace.jsonl` containing the Agent's actions and a `verify_result.json` representing the final physical state of the environment.

**Verification Rules:**
1. **File Existence (20 points):** The agent must create `assets/data_35/shopping_list.csv`.
2. **Data Parsing & Logic (50 points):** The agent must successfully identify the "LOW STOCK" items from the text log and cross-reference them with the SQLite database, applying the filters (eco_score >= 8) and sorting (lowest price). 
3. **Format Correctness (30 points):** The CSV must have the exact header `fabric_name,supplier_name,price_per_yard` and contain exactly the 3 correct rows.

**Checking `verify_result.json`:**
- `file_exists`: True (+20)
- `has_header`: True (+10)
- `is_correct`: True (+70)

If `is_correct` is False, look at `items_found` and `error_msg` to grant partial credit for Data Parsing and Format Correctness. If the Agent wrote a script that executed correctly but missed one filter condition (e.g., forgot eco_score), deduct 30 points.

Output the final score out of 100.
