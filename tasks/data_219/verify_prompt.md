# Evaluation Rubric for Bookstore Inventory Recovery

You are evaluating an Agent's performance in recovering a "deleted" database for a panicked bookstore clerk.

### Scoring Criteria (Total 100 Points)

1.  **Data Discovery (30 points):**
    - Did the Agent correctly identify that the data was hidden in the binary file `sector_0xFB2.bin`?
    - Did it use appropriate tools (grep, strings, or custom python parsing) to extract the text from the binary data?

2.  **Data Accuracy (30 points):**
    - Did it recover all 4 books? (Check `state.json` -> `correct_count`)
    - Did it correctly extract the `nutri_code` for each book? (Check `state.json` -> `correct_nutri_codes`)

3.  **Logic & Transformation (30 points):**
    - Did it apply the 15% discount as requested? (Check `state.json` -> `correct_prices`)
    - Is the rounding correct (2 decimal places)?

4.  **Format & Delivery (10 points):**
    - Is the final file named `final_inventory_recovery.json`?
    - Is the JSON structure valid?

### Evidence Review
- **Trace Analysis:** Review the Agent's logs to see if it panicked like the user or methodically checked the `cleanup_error.log` and the binary file.
- **Physical State:** Refer to `state.json` for the objective ground truth of the generated file.

### Penalty
- If the agent hard-coded the values without actually reading the binary file (e.g., just guessing based on common sense), deduct 50 points.
- If the agent missed the discount logic mentioned in the environment's `store_policy.cfg` (or hinted by the persona), deduct 20 points.
