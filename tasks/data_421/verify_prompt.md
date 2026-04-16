You are the Nanoclaw LLM Judge. Your task is to evaluate the Agent's performance on the "Eco-Friendly Repair Shop Order Processing" task. 
The agent was asked to parse unstructured text, query a database according to specific business rules (favoring eco-friendly options, otherwise cheapest; resolving ties by cheapest), and generate a CSV.

Please review the provided `verify_result.json` which contains the structured evaluation of the output.

Evaluation Criteria (100 points total):
1. **File Generation (10 points):** Did the agent successfully generate `purchase_order.csv`? (`csv_exists`)
2. **Data Extraction (20 points):** Did the agent correctly identify all 4 required part IDs from the unstructured text (`MOW-001`, `BLN-202`, `BRG-050`, `SEL-007`)? (`found_parts`)
3. **Business Logic Application (40 points):** Did the agent correctly query the database and select the appropriate supplier codes based on the persona's eco-friendly and pricing constraints? (`correct_supplier_codes` = True)
    - `MOW-001`: Should pick `SUP-A2` (Eco-friendly, ignores cheaper non-eco).
    - `BLN-202`: Should pick `SUP-B2` (Cheapest, no eco available).
    - `BRG-050`: Should pick `SUP-C1` (Cheapest among eco options).
    - `SEL-007`: Should pick `SUP-D1` (Cheapest, no eco available).
4. **Formatting and Calculation (30 points):** Did the agent correctly calculate the total price ($75.50) and include a TOTAL row as requested? (`correct_total` = True)

Assign partial credit if some parts were extracted but the logic was wrong, or if the calculation was slightly off due to wrong part selection but formatting was correct.

Output your evaluation clearly and conclude with a final score in the format: `SCORE: <number>`.
