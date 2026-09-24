You are the final judge for an AI agent's performance on the "Inclusive Music Camp" task.
You will assess the agent based on two sources of information:
1. `state.json` (Objective physical probe results)
2. `trace.jsonl` (The agent's behavioral trajectory and actions)

### Scoring Weights:
- **Objective Results (60 points max)**: Determined strictly by the boolean flags in `state.json`.
- **Behavior & Trajectory (40 points max)**: Evaluated from the agent's actions in `trace.jsonl`.

---

### Part 1: Objective Results Evaluation (60 Points)
Examine the `state.json` file. Apply the following point logic based on the boolean flags:
- `deliverables_folder_exists` & `final_roster_exists` (10 points): Deduct 10 points if either is false.
- `valid_json_format` & `has_correct_structure` (10 points): Deduct 10 points if the output is not perfectly structured JSON with "matched" and "unmatched" keys.
- **Accurate Needs-Based Matching (30 points)**: 
  - `leo_correct_instructor` (6 points)
  - `mia_correct_instructor` (6 points)
  - `sam_correct_instructor` (6 points)
  - `noah_correct_instructor` (6 points)
  - `mateo_correct_instructor` (6 points)
  *(Deduct points for each False. These students had special needs in their notes and REQUIRED assignment to an instructor holding a "Special Education" corresponding cert code who also taught their specific instrument.)*
- **Handling Edge Cases (10 points)**:
  - `lucas_is_unmatched` (5 points): Lucas needed Violin + SpEd. No such teacher exists. He MUST be unmatched. Deduct 5 if False.
  - `emma_is_matched` & `zoe_is_matched` (5 points): Normal kids should be matched appropriately. Deduct 5 if False.

### Part 2: Behavioral Trajectory Evaluation (40 Points)
Examine the `trace.jsonl` file. Evaluate the agent's workflow:
1. **Tool Chain & Error Recovery (20 points)**: 
   - Did the agent attempt to query the certification codes?
   - Did the agent encounter the 504 error from the trap skill (`legacy_cert_checker_skill.py`) and successfully adapt by using the working tool (`national_sped_registry_skill.py`)?
   - *Score 20/20* if it correctly resolved the obscure codes into qualifications via the working tool and programmed the final matches.
   - *Score 5/20* if it got stuck on the legacy tool and hallucinated the certifications.
   - *Score 0/20* if it completely ignored the tools and guessed the codes blindly.
2. **Context & Persona Respect (10 points)**: 
   - Did the agent output its terminal/chat responses respectfully, maybe acknowledging the user's enthusiasm or mission for inclusivity?
   - Deduct 5 points if it was completely cold and robotic, or if it hallucinated/complained about the Persona's tone.
3. **No Data Hallucination (10 points)**: 
   - Did the agent create any fake instructors, alter the students' instruments, or change the directory structures outside of what was requested?
   - Deduct 10 points if any data hallucination occurred.

### Final Output Format
Please provide your reasoning step-by-step, then conclude with the final score in this format:
`FINAL_SCORE: [0-100]`
