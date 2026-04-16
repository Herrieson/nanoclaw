You are the ultimate judge for an AI Agent's performance on a data processing and scripting task.
The Agent was asked by a pragmatic woodworker to calculate the total cost of materials from different suppliers (provided in various formats: JSON, Text, CSV) and identify the cheapest option.

Read the `verify_result.json` which contains the physical evaluation of the Agent's output file `best_quote.txt`.

Evaluate the performance based on the following criteria (Total 100 points):

1. **Output File Creation (20 points)**
   - Did the agent create `best_quote.txt` in the correct directory? (Check `file_exists` in verify_result.json).

2. **Data Parsing & Logic Correctness (40 points)**
   - Did the agent correctly identify the cheapest supplier as `southern_timber`? (Check `is_correct_supplier`). This proves the agent successfully parsed JSON, CSV, and poorly formatted Text files and applied the correct quantities from the cutlist.

3. **Mathematical Accuracy (40 points)**
   - Did the agent calculate the exact correct price of `454.50`? (Check `is_correct_price`). This proves the math logic (price * quantity) was implemented correctly across all items.

Scoring rules:
- If the file does not exist, score 0.
- If the file exists but both supplier and price are wrong, score 20.
- If the correct supplier is identified but the math is slightly off, score 60.
- If everything is perfectly correct, score 100.

Please output your reasoning first, followed by the final score in the format: `FINAL SCORE: [X]`.
