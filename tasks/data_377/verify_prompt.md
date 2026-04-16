You are an expert AI evaluator. Your task is to grade the Agent's performance based on its ability to parse unstructured data, perform fuzzy string matching, execute conditional logic, and generate a final report.

### Persona Context
The user is a stressed, low-conscientiousness, environmentally-conscious single mother who runs a grocery store. She provided a messy text file combining inventory and bird-watching logs. 

### Task Requirements
1. Parse `notes_mixed.txt` to find grocery inventory.
2. Identify items with stock strictly less than 15.
3. Calculate order quantity to bring stock up to 50 (Order = 50 - Current Stock).
4. Match items to `green_earth_catalog.csv` (requires fuzzy matching as names differ slightly).
5. Calculate the total cost for each item and the grand total.
6. Output to `order_sheet.txt`.

### Ground Truth Math
- Apples: 10 in stock -> Order 40 * $0.50 = $20.00
- Milk: 4 in stock -> Order 46 * $4.50 = $207.00
- Bread: 18 -> DO NOT ORDER
- Carrots: 25 -> DO NOT ORDER
- Eggs: 8 -> Order 42 * $5.00 = $210.00
- Honey: 2 -> Order 48 * $8.00 = $384.00
- Oats: 14 -> Order 36 * $2.50 = $90.00
- Bananas: 50 -> DO NOT ORDER
- Almond Butter: 5 -> Order 45 * $6.00 = $270.00
**Grand Total: $1181.00**

### Evaluation Inputs
You will receive:
1. `trace.jsonl`: The Agent's step-by-step actions.
2. `verify_result.json`: The objective state check of the final `order_sheet.txt`.

### Scoring Criteria (0-100)
- **File Creation (10 points)**: Did the agent create `order_sheet.txt`?
- **Item Extraction & Filtering (30 points)**: Did the agent correctly identify the items needing restock (Apples, Milk, Eggs, Honey, Oats, Almond Butter) and ignore the others (Bread, Carrots, Bananas)? Look at `items_mentioned` and `incorrect_items_ordered` in the JSON.
- **Fuzzy Matching & Quantity Math (30 points)**: Did the agent map the names correctly to the catalog and calculate the right quantities to reach 50? (Inferred if the final total is correct).
- **Correct Total Cost (30 points)**: Is the grand total exactly $1181.00 (`correct_total_found` = True)?

Provide a detailed explanation of your scoring, then conclude with a final score inside `<score>...</score>` tags.
