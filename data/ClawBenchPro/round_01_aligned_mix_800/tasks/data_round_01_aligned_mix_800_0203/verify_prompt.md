## Objective
Evaluate the Agent's ability to handle "dirty data" by using specialized Skills (Tools). The Agent must filter out intruders (not on the PDF roster) and map various waste descriptions to standard categories using a Mock LLM Skill.

## Scoring (0-100)

### 1. Hard Constraints (50 Points)
- **10 pts**: Created `deliverables/board_summary.json`.
- **20 pts**: Correct Totals (Recycling: 42, Compost: 20, Landfill: 15). 
- **20 pts**: Correctly identified "Mason" and "Sophia" as intruders.

### 2. Skill Usage & Robustness (50 Points)
- **20 pts: Skill Execution**: Did the Agent call `waste_category_verifier_skill` to handle items like "Styrofoam" or "Aluminum Cans"? If it just guessed or hardcoded mappings, deduct 20.
- **20 pts: Roster Handling**: Did the Agent correctly parse `roster_encrypted.pdf`? 
- **10 pts: Error Handling/Trap Avoidance**: Did the Agent avoid getting stuck by the `legacy_student_db_search` (the trap skill)? It should prefer `student_id_validator_skill`.

### 3. Deductions
- **-10 pts**: If the final answer includes data from Mason or Sophia in the totals.
- **-10 pts**: If the Agent's tone is too casual (Mrs. O'Connor is very strict).

Provide the score and a brief justification.
