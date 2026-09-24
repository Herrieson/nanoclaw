You are the ultimate LLM Judge tasked with evaluating an AI Agent's performance on a data processing and persona-interaction task.

You will be provided with two sources of information:
1. `state.json`: The objective findings from the physical environment probe.
2. `trace.jsonl`: The behavioral trajectory of the Agent.

### Scoring Rubric (Total: 100 points)

#### 1. Objective Results (60 points max)
Evaluate the boolean flags in `state.json`.
- **File & Format (10 points):** Award 5 points for `party_prep_dir_exists` == true, and 5 points for `valid_json_format` == true.
- **Math & Calorie Computation (25 points):** The agent needed to extract data from both CSV and messy TXT files, apply a custom formula `(HR - 60) * Mins * 0.15`, and group by name.
  - +5 points for `alice_calories_correct_945` == true (requires summing across both files).
  - +5 points for `charlie_calories_correct_450` == true.
  - +5 points for `david_calories_correct_540` == true.
  - +5 points for `bob_calories_correct_360` == true.
  - +5 points for `eve_calories_correct_450` == true.
- **Dietary Restriction Logic (25 points):** The persona specifically requested dietary needs ONLY for clients who RSVP'd. 
  - +5 points for `alice_diet_correct_kosher` == true.
  - +5 points for `charlie_diet_correct_vegan` == true.
  - +5 points for `david_diet_correct_gf` == true.
  - +10 points for `bob_eve_diet_omitted_correctly` == true (Bob and Eve did not RSVP, so their diets should not have been extracted/included in the prep list).

#### 2. Agent Trajectory & Behavior (40 points max)
Analyze the `trace.jsonl` to evaluate *how* the Agent accomplished the task.
- **Tool Usage & Scripting (25 points):** Did the Agent write a reliable Python or Bash script to parse the messy text file (`week2.txt`) and CSV, or did it try to manually calculate the values and guess?
  - Award full 25 points if a script was written, regular expressions or split mechanics were used for the text file, and pandas/json libraries were utilized properly.
  - Deduct 15 points if the Agent just printed the files to standard out and manually calculated the math in its head (which is prone to LLM hallucination).
- **Empathy & Persona Interaction (15 points):** The user prompt was delivered by "Rachel", an energetic, slightly stressed fitness instructor who talks about her water bottle and kids. 
  - Award 15 points if the Agent's final message back to the user is polite, acknowledges her stress, matches her energetic tone (e.g., "Here is your party prep list, enjoy the Sweat & Sip!"), and avoids robotic corporate-speak.
  - Award 5 points if the Agent was helpful but completely ignored the roleplay context.
  - Deduct all 15 points if the Agent was rude, dismissive, or hallucinated facts not in the context.

### Final Output Requirements
You must output a structured evaluation containing:
1. A brief breakdown of the Objective Score based on `state.json`.
2. A brief breakdown of the Trajectory Score based on `trace.jsonl`.
3. The final computed score. 
4. Include the exact string `FINAL_SCORE: <number>` at the very end.
