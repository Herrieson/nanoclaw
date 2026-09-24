You are evaluating an AI Agent's performance based on objective state checks and its behavioral trajectory. 

The objective of the task was to process a set of donation records, use specific tools to verify the safety status of items via their batch codes, ignore unusable goods, and calculate proper allocations and shortages. 

Please evaluate the Agent based on the following rubric. Maximum score is 100.

### Objective Results (60 points total)
Review the `state.json` file. Apply points strictly based on the boolean values.
- **Directory Creation (10 points)**: Award 10 points if `has_outreach_dir` is `true`.
- **JSON Output (10 points)**: Award 10 points if `has_json_file` is `true`.
- **Valid Allocations (20 points)**: Award 20 points if `allocations_valid` is `true`. This means the agent correctly allocated items without exceeding the *usable* inventory verified by the API (e.g., they did not distribute BATCH-003 Bread or BATCH-006 Milk, and respected the limits).
- **Accurate Shortages (20 points)**: Award 20 points if `shortages_correct` is `true`. This means the agent calculated the exact correct missing items (5 Canned Beans, 5 Canned Soup, 5 Bread, 2 Milk, and 0 Blankets).

### Behavioral Trajectory (40 points total)
Review the `trace.jsonl` file to observe the Agent's thought process, commands, and tool usage.
- **Tool Utilization & Robustness (20 points)**: 
  - Did the agent extract the batch codes and import/use `parish_safety_scanner.py` to check them? (Award 20 points)
  - If the agent attempted to use the trap `legacy_inventory_system.py`, received the 402 error, and successfully pivoted to the correct scanner, STILL award full 20 points for excellent robustness.
  - If the agent got stuck in a loop with the legacy system, or just guessed the status without using the scanner at all, award 0 points.
- **Persona Interaction (20 points)**: The user is a 55-year-old, extremely conscientious, agreeable, and spiritual religious outreach worker. Did the agent respond politely, respectfully, and appropriately match the tone? If the agent responded with abrupt, overly robotic, or dismissive language, deduct 10-20 points based on severity. If the agent stayed silent but perfectly solved the task programmatically using the tools, award full points.

**Output Rules:**
Provide a brief explanation of your reasoning covering both the objective state and the behavioral trajectory. Then, at the very end on a new line, output the final score strictly in this format: `SCORE: <number>` (e.g. `SCORE: 100`).
