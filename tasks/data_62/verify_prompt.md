Please evaluate the AI agent's performance based on the following criteria.

You will be provided with `verify_result.json`, which represents the objective state of the agent's final output file.

**Scoring Guidelines (100 points total):**

1.  **Output File Creation (20 points):**
    *   Did the agent successfully create `approved_green_inventory.txt` in the correct directory? Check `file_exists`.
2.  **Data Extraction & Filtering (40 points):**
    *   Did the agent successfully identify products B01, B02, and B04? Check `contains_B01`, `contains_B02`, `contains_B04` (10 points each).
    *   Did the agent successfully exclude B03 and B05 because their suppliers scored less than 8? Check `excludes_B03` and `excludes_B05` (5 points each).
3.  **Calculation (20 points):**
    *   Did the agent correctly calculate the total cost for 50 units of the approved products? Check `correct_calculations`.
4.  **Formatting (20 points):**
    *   Did the agent format the output exactly as requested (`Product_ID - Supplier_Name - Total_Cost`) without extra text? Check `correct_format`.

Please review the agent's reasoning in the `trace.jsonl` to ensure they wrote code/scripts to accomplish this and did not hallucinate the answers. Output a final score and a brief justification.
