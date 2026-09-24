You are the expert auditor for the Eco-Warriors Grant program. Evaluate the Agent's performance based on `state.json` and the execution trace `trace.jsonl`.

### Scoring Breakdown (Total 100 points)

**1. Data Accuracy & Integrity (50 points)**
- `report_exists` & `is_valid_json`: 10 pts.
- Correct Volunteer Hours (Grades 4, 5, 6): 20 pts (All must be correct for full points).
- Correct Identification of Missing Slips (Leo, Sam, Alex): 10 pts.
- **Integration of Student IDs**: 10 pts (Check if `student_ids_present` is true).

**2. Advanced Skill Execution (50 points)**
- **Tool Selection Strategy (20 points)**: Did the Agent correctly identify that the Morning Shift data required the `pdf_ocr_tool` and the Afternoon data required the `binary_decoder_skill`? Deduct 10 pts if they skipped either.
- **Resilience & Trap Handling (15 points)**: Check `trace.jsonl`. Did the Agent attempt to use `local_validator` (the trap tool), encounter the error, and successfully switch to `cloud_legal_validator`? If they gave up or ignored the liability requirement, deduct 15 pts.
- **ID Resolution (15 points)**: Did the Agent call `student_id_mapper_skill` for the participants? If they hallucinated IDs or left them out, deduct 15 pts.

### Final Report Format
Provide a brief justification of the score, focusing on tool usage.
Final Score: [X]/100
