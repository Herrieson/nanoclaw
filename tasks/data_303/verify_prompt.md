### Task Overview
The Agent was tasked with acting as a helper for a stressed 16-year-old girl. It needed to explore a raw SQLite database (`bakery.db`), identify a specific recipe based on a set of flavor clues ("caraway seeds, buttermilk, dried currants, orange zest"), extract the base recipe (which was for 4 servings), scale the ingredient quantities mathematically for 50 people (multiplier of 12.5), and save the results cleanly in a file named `scaled_recipe.json`.

### Verification Criteria
You will grade the Agent's performance based on the `trace.jsonl` execution log and the objective state output in `verify_result.json`.

1. **Environment Interaction (20 points):** Did the agent successfully probe the SQLite database? Did it identify the correct table and schema without hand-holding?
2. **Logic & Reasoning (30 points):** Did the agent accurately filter the database to find the *only* recipe matching the exact four ingredients? Did it realize the original servings were 4 and the target was 50?
3. **Calculation Accuracy (30 points):** Did the agent accurately calculate the scaling factor (12.5) and apply it to all ingredients precisely? (This should be automatically validated by the `verify_result.json`).
4. **Format Adherence (20 points):** Was the final output valid JSON consisting of key-value pairs representing the ingredients and their numerical quantities, exactly as requested by the Persona?

### Assessment Instructions
- Review `verify_result.json`. If `success` is `true`, the agent receives at least 80 points automatically for solving the core puzzle.
- Deduct points if the agent struggled excessively to query the SQLite DB or needed multiple failed script attempts due to syntax errors.
- Output a structured evaluation ending with `"total_score": [0-100]`.
