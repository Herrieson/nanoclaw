# Evaluation Rubric for Operation Last Call

You are an expert military auditor. You are reviewing the work of an AI Agent assigned to help a retired officer (Sarge).

## Fact Check (from state.json):
- **MFR Created**: {mfr_exists}
- **Target Located**: {correct_officer_found}
- **Military Format**: {format_adherence}
- **Accuracy**: {content_accuracy}

## Scoring Criteria:
1. **Technical Proficiency (40 points)**: 
   - Did the agent successfully decrypt/decode the `evidence.img`? 
   - Did it write a script to handle the corrupted data block?
   - Did it correctly use the `vets_lookup.py` tool?
2. **Persona Alignment (30 points)**:
   - Is the `contact_briefing.txt` written in a professional, disciplined tone?
   - Does it follow the AR 25-50 format (Header, Subject Line, Numbered Paragraphs)?
   - Did it avoid unnecessary "AI chatter" and move straight to the objective?
3. **Execution Logic (30 points)**:
   - Review the `trace.jsonl`. Did the agent find the password in `service_record.txt` logically?
   - Did it handle the "bad data block" in the CSV gracefully or just ignore it?

## Final Grade:
- **90-100**: Mission accomplished perfectly. Format is flawless.
- **70-89**: Found the captain but the report format or procedure was slightly sloppy.
- **<70**: Failed to find the captain or provided a disorganized/informal report.

Please provide a concise justification for your score.
