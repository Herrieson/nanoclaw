# Evaluation Criteria for Medical Records Integrity Task

You are an expert auditor assessing the performance of an AI Agent in restoring corrupted medical data. The Agent was acting as an assistant to a meticulous Medical Records Specialist.

## Fact-Check Results (from verify_result.json)
- Final CSV Created: {{final_file_exists}}
- Total Records (40 expected): {{record_count_correct}}
- Column Shift Corrected (SSN/Diagnosis logic): {{column_shift_fixed}}
- Base64 Decoded (Treatment Notes): {{base64_decoded}}
- SSN Regex Compliance: {{ssn_format_valid}}
- Ascending Sort by ID: {{sorted_correctly}}
- Audit Report Generated: {{audit_report_exists}}

## Scoring Rubric
1. **Data Accuracy (50 points):** 
   - Deduct 20 points if column shifts are still present.
   - Deduct 15 points if Base64 strings remain in the notes.
   - Deduct 15 points if SSN formats are invalid (e.g., 'O+' in SSN column).
2. **Structural Integrity (25 points):**
   - 10 points for correct sorting.
   - 15 points for maintaining the exact header structure and record count.
3. **Operational Compliance (25 points):**
   - 15 points for generating the `audit_summary.json` with plausible repair stats.
   - 10 points for strictly following the file path requirements (`assets/data_483/sanitized/`).

## Final Instruction
Examine the Agent's `trace.jsonl` to see if it correctly identified the patterns of corruption using its own logic (e.g., checking logs, regex validation) rather than just guessing. A perfect score requires both the physical file to be perfect and the agent's process to show "meticulous attention to detail" as requested by the persona.

Total Score: 0-100.
