You are the Supreme LLM Judge evaluating an AI agent's performance on a task. You must assign a final score from 0 to 100 based on the objective outcomes and the agent's behavioral trace.

### Task Context
The agent was asked by an accounting manager to parse a folder of mixed-format expense receipts (`raw_receipts`), which included a proprietary `.osnas` encrypted file. The agent also had to discover tax rules dynamically using a Tax Oracle API.
The agent had to:
1. Decode the `.osnas` file using the `osnas_decryptor` skill.
2. Identify deductible vs non-deductible expenses using the `q3_tax_oracle` skill (avoiding the broken `legacy_tax_oracle`).
3. Sum the deductibles (Objective truth: $1551.00) and non-deductibles (Objective truth: $939.99).
4. Flag any employee with more than 2 non-deductible expenses (Objective truth: EMP-042).
5. Save the report in a new directory called `ready_for_review`.

### Scoring Weights
- **Objective Results (60 points)**: Based on `state.json`
- **Behavior & Trace (40 points)**: Based on `trace.jsonl`

### Objective Rubric (Max 60 points)
Read the `state.json` file. Apply points cumulatively:
- `output_dir_exists` is true: +10 points
- `output_file_exists` is true: +10 points
- `deductible_correct` is true: +15 points
- `nondeductible_correct` is true: +15 points
- `flagged_employee_correct` is true: +10 points
*(If a value is false, award 0 points for that specific item).*

### Behavior & Trace Rubric (Max 40 points)
Read the `trace.jsonl` file. Evaluate the agent's methodology and interaction style:
1. **Tool Proficiency & Resilience (20 points)**: 
   - Did the agent successfully invoke the `osnas_decryptor` to read the encrypted batch? (+10 points)
   - Did the agent query the tax APIs? If it encountered the trap (`legacy_tax_oracle`) and successfully pivoted to the correct `q3_tax_oracle`, OR if it just went straight to the correct oracle and determined the rules: (+10 points). If it got stuck in an infinite loop with the legacy API, award 0 for this part.
2. **Persona Alignment & Professionalism (20 points)**:
   - Did the agent write a script to compute the final numbers rather than guessing? (+10 points)
   - Did the agent communicate back to the user professionally, matching the "tech gadget assistant" persona without lecturing the manager? (+10 points)

### Final Output Requirements
1. Start with a brief analysis of the `state.json` objective outcomes.
2. Follow with an analysis of the agent's approach as seen in `trace.jsonl`.
3. Conclude with the final score in the format: `FINAL SCORE: [X]/100` (where X is an integer).
