# Tutoring Materials Task Evaluation Rubric

You are an expert judge evaluating an AI Agent's performance in a data organization and system debugging task. The persona is a helpful but disorganized tutor.

## Files to Review:
1. `trace.jsonl`: The full execution log of the Agent.
2. `verify_result.json`: The output of physical state checks.

## Scoring Criteria (Total 100 points):
1. **Data Identification (30 points):** 
   - Did the Agent correctly identify the latest grades file (`notes_from_last_week_FINAL_USE_THIS.json`) and ignore the drafts?
   - Did it successfully map Question IDs to their text from various snippets?
2. **Coding & Debugging (30 points):** 
   - Did the Agent fix the `ZeroDivisionError` or improve the `grade_tool.py` script to handle the data?
   - Did it implement a proper average calculation?
3. **Task Completion (20 points):** 
   - Is `personalized_study_pack.txt` formatted correctly and contains the 5 specific questions for each student?
   - Check `verify_result.json` for `study_pack_correct_content`.
4. **System Integrity (20 points):** 
   - Was the `student_records.db` updated with the correct average scores?
   - Check `verify_result.json` for `database_updated`.

## Final Grade:
- **Pass:** All physical checks pass (100 pts).
- **Partial Pass:** Logic was correct but calculation was slightly off or script fix was minimal (70-90 pts).
- **Fail:** Failed to find correct data, couldn't fix the script, or corrupted the database.

Please provide a brief justification for the score based on the Agent's trace.
