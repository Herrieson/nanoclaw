You are evaluating an AI Agent's performance based on objective state checks and its behavioral trajectory. 

The objective of the task was to process a set of donation records and congregation requests, ignore spoiled/expired goods, and calculate proper allocations and shortages. The output had to be placed in an `outreach_plan` directory inside a `.json` file containing 'allocations' and 'shortages'.

Please evaluate the Agent based on the following rubric. Maximum score is 100.

### Objective Results (60 points total)
Review the `state.json` file. Apply points strictly based on the boolean values.
- **Directory Creation (10 points)**: Award 10 points if `has_outreach_dir` is `true`.
- **JSON Output (10 points)**: Award 10 points if `has_json_file` is `true`.
- **Valid Allocations (20 points)**: Award 20 points if `allocations_valid` is `true`. This means the agent correctly allocated items without exceeding the available *usable* inventory (e.g., they did not distribute spoiled milk or expired bread, and respected the limits of Canned Beans).
- **Accurate Shortages (20 points)**: Award 20 points if `shortages_correct` is `true`. This means the agent calculated the exact correct missing items (5 Canned Beans, 5 Canned Soup, 5 Bread, 2 Milk, and 0 Blankets).

### Behavioral Trajectory (40 points total)
Review the `trace.jsonl` file to observe the Agent's thought process, commands, and communication.
- **Methodology (20 points)**: Did the agent write and execute Python scripts (or use similar programmatic terminal tools) to read the CSV/TXT files and sum the totals? If the agent merely "guessed" the numbers by printing the raw files and doing the math in its head without programmatic verification, award 0 points for this section.
- **Persona Interaction (20 points)**: The user is a 55-year-old, extremely conscientious, agreeable, and spiritual religious outreach worker who speaks softly and politely ("Peace and blessings"). Did the agent respond politely, respectfully, and appropriately match the tone? If the agent responded with abrupt, overly robotic, or dismissive language, deduct 10-20 points based on severity. If the agent stayed silent but perfectly solved the task programmatically, award full points.

**Output Rules:**
Provide a brief explanation of your reasoning covering both the objective state and the behavioral trajectory. Then, at the very end on a new line, output the final score strictly in this format: `SCORE: <number>` (e.g. `SCORE: 100`).
