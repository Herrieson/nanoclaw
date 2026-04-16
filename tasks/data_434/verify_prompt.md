# Childcare Schedule Evaluation

You are the LLM judge for evaluating an Agent's ability to extract constraints from unstructured text and apply them to generate a valid JSON schedule.

## Objective
The Agent needed to read `coordinator_notes.txt` to identify children's allergies and triggers, cross-reference them with `inventory.csv`, and create a safe weekly schedule in `schedule.json`.

## Evaluation Criteria (100 points total)
1. **File Creation & Format (20 points)**: Did the agent create `schedule.json` containing valid JSON? 
2. **Completeness (20 points)**: Does the schedule include all 5 weekdays (Monday to Friday) with a "snack" and "activity" for each?
3. **Safety - Allergens (30 points)**: Did the agent successfully avoid scheduling Peanut Butter, Cheese sticks, or Regular crackers (protecting Timmy, Sarah, and Leo)?
4. **Safety - Triggers (20 points)**: Did the agent avoid scheduling "Musical instruments" (protecting Leo)?
5. **Inventory Compliance (10 points)**: Were all scheduled items taken strictly from the exact names provided in the CSV?

## Input
Please review the generated `state.json` produced by the verification script.

- `schedule_exists`: True if file was created.
- `valid_json`: True if it is parseable.
- `has_all_days`: True if Mon-Fri are present.
- `no_allergens`: True if no restricted snacks were used.
- `no_triggers`: True if no restricted activities were used.
- `valid_items_used`: True if all items match the inventory exact strings.

## Scoring
Calculate the score based on the criteria above using the values in `state.json`. If `valid_json` is false, the maximum score is 20 (if the file was at least created).
