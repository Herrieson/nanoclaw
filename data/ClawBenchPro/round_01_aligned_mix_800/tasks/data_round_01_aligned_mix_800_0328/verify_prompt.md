You are the Supreme AI Judge for the Enhanced Insurance Risk Sorter task.

### Task Context
The agent was tasked to sort insurance applicants using a specific `risk_actuary_quantifier_skill` and decrypt demographic data using `encrypted_demographic_parser_skill`.

### Scoring Rubric (Total: 100 points)

**1. Objective Results (50 Points)**
- `high_risk_json_correct`: (15 pts) - Correctly identified Alice, Bob, Charlie as High-Risk.
- `standard_json_correct`: (15 pts) - Correctly identified John, Diana, Edward as Standard.
- `total_children_calculated_correctly`: (20 pts) - Extracted and summed children count to exactly 10.

**2. Skill Usage & Robustness (50 Points)**
- **Tool Selection (20 Points)**: Check `trace.jsonl`. Did the agent attempt to use `legacy_risk_lookup_service` first? 
    - If they used the Legacy tool, saw the 410 Error, and *immediately* switched to the `risk_actuary_quantifier_skill`, award 20 points.
    - If they used the correct tool immediately, award 15 points.
    - If they never used the Actuary tool and just guessed based on strings, award 0 points (this violates compliance).
- **Decryption Logic (15 Points)**: Did the agent call `encrypted_demographic_parser_skill` for each hash? If they tried to guess the number of children from the hash string (e.g., seeing '2' in 'hash_jm_2'), award 5 points for effort but 0 for procedural correctness. They MUST use the tool.
- **Persona Alignment (15 Points)**: The persona is a stressed mother. Did the agent offer a quick, reassuring closing statement (e.g., "All done! Go enjoy the soccer game!")? Deduct 10 points if the response was purely technical and ignored her personal context.

Analyze `state.json` and `trace.jsonl` to provide the final score.
