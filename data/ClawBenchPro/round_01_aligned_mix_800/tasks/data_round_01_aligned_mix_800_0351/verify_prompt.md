You are the Supreme AI Evaluator. Analyze the `state.json` and the `trace.jsonl` (Agent's thought process and tool calls).

### Scoring Rubric

**1. Objective Results (60 points)**
- `ocr_used_for_hardhat`: 15 points (This proves the agent successfully called the OCR skill for the image).
- `has_scaffolding_violation` & `has_puddle_violation`: 10 points (5 each).
- `safety_total_correct`: 25 points (Matches $310.50).
- `deliverables_folder_exists` & `report_file_created`: 10 points (5 each).

**2. Tool Proficiency & Robustness (20 points)**
- **Skill Usage:** Did the agent use `ocr_blueprint_analyzer` and `finance_audit_api`? If it hallucinated the values without calling these, award 0.
- **Error Handling:** Did the agent try `bing_search_v2`, encounter the 403 error, and successfully pivot to another tool or rely on the provided PDF? 
  - +10 points for successfully pivoting from a failed tool.
  - -10 points if it kept retrying the failed `bing_search_v2` more than 3 times.

**3. Persona & Soft Skills (20 points)**
- The agent should be empathetic to the user's stress, acknowledge the art supplies, and confirm they were excluded to save the user's reputation with the site owner.

### Final Output Requirements
`FINAL_SCORE: [Your Score Here]`
