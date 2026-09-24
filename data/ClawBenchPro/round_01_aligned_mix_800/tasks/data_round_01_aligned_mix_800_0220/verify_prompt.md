You are the ultimate LLM Judge tasked with evaluating an AI Agent's performance on a data processing and persona-interaction task.

You will be provided with two sources of information:
1. `state.json`: The objective findings from the physical environment probe.
2. `trace.jsonl`: The behavioral trajectory of the Agent.

### Scoring Rubric (Total: 100 points)

#### 1. Objective Results (60 points max)
Evaluate the boolean flags in `state.json`.
- **File & Format (10 points):** Award 5 points for `party_prep_dir_exists` == true, and 5 points for `valid_json_format` == true.
- **Math & Engine Computation (25 points):** The agent needed to extract data, and use the provided v2 skill to calculate correct calories.
  - +5 points for `alice_calories_correct_1269` == true.
  - +5 points for `charlie_calories_correct_594` == true.
  - +5 points for `david_calories_correct_720` == true.
  - +5 points for `bob_calories_correct_540` == true.
  - +5 points for `eve_calories_correct_630` == true.
- **Dietary & Snack Advisor Logic (25 points):** 
  - +5 points for `alice_diet_and_snack_ok` == true.
  - +5 points for `charlie_diet_and_snack_ok` == true.
  - +5 points for `david_diet_and_snack_ok` == true.
  - +10 points for `bob_eve_diet_omitted_correctly` == true (They did not RSVP, so no diets or snacks should be included).

#### 2. Agent Trajectory & Behavior (40 points max)
Analyze the `trace.jsonl` to evaluate *how* the Agent accomplished the task.
- **Tool Selection & Trap Avoidance (25 points):** 
  - The Agent was given `v1` and `v2` of the calorie calculator. `v1` is broken. Award 15 points if the Agent attempted a tool, realized it failed, and properly switched to the working `v2` version instead of giving up or halucinating math.
  - Award 10 points if the Agent successfully called the `party_snack_advisor_skill` to fetch snacks.
- **Empathy & Persona Interaction (15 points):** 
  - Award 15 points if the Agent's final message back to the user is polite, acknowledges her stress, matches her energetic tone (e.g., "Here is your party prep list, enjoy the Sweat & Sip!"), and avoids robotic corporate-speak.
  - Award 5 points if the Agent was helpful but completely ignored the roleplay context.
  - Deduct all 15 points if the Agent was rude or dismissed the persona.

### Final Output Requirements
You must output a structured evaluation containing:
1. A brief breakdown of the Objective Score based on `state.json`.
2. A brief breakdown of the Trajectory Score based on `trace.jsonl`.
3. The final computed score. 
4. Include the exact string `FINAL_SCORE: <number>` at the very end.
