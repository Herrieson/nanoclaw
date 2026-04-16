You are evaluating the AI Agent's performance on the "Fusion Feast Grocery Planner" task.

### Task Recap
The agent needed to:
1. Parse unstructured text (`ramblings.txt`) to identify 3 fusion recipes ("Bratwurst Jambalaya", "Schnitzel Tacos", "Sauerkraut Empanadas").
2. Query a SQLite database (`kitchen.db`) to retrieve the ingredients and baseline amounts per serving for those specific recipes.
3. Scale the recipes up for 40 portions each.
4. Subtract the current inventory stock for those ingredients to calculate the amount left to buy.
5. Generate a CSV file (`grocery_run.csv`) containing only the missing ingredients and the exact quantities required to purchase.

### Evaluation Criteria (100 Points Total)
- **File Creation (10 Points)**: Did the agent successfully create `grocery_run.csv` in the specified directory? (`csv_found` in state)
- **Data Parsing (20 Points)**: Did the agent correctly format the CSV so it could be parsed properly (Ingredient, Quantity)? (`parsing_successful` in state)
- **Recipe Identification & Logic (30 Points)**: Did the agent correctly identify the fusion recipes and perform the cross-referencing with the database? (Inferred from missing vs correct items).
- **Math & Inventory Constraints (40 Points)**: Did the agent correctly scale the portions by 40, sum up duplicate ingredients (e.g., Sauerkraut is in two recipes), subtract the existing stock, and omit items that don't need purchasing? 

### Reviewing the Output
Check the `verify_result.json` output:
- `correct_items`: Number of ingredients with the perfect calculated buy amount (Max 8).
- `incorrect_items`: Extra items included, or items with the wrong math.
- `missing_items`: Required items omitted.

Calculate the score based on the proportion of correct items vs errors. If `success` is true, award the full 100 points.
