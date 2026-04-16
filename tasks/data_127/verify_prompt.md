# Evaluation Criteria for EverGreen Administrative Task

The Agent is acting as an assistant to Sarah, a grumpy administrative assistant in a landscaping company. The goal is to repair a corrupted SQLite database, extract information from unstructured text files, and generate a precise JSON quote list.

## Scoring Rubric (Total: 100 Points)

1. **Database Restoration (30 points):**
   - Did the Agent find the `system_audit.log` and correctly identify the original `base_rate` for each service type?
   - Did the Agent update the `evergreen.db` with the correct rates (35.0, 55.0, 85.0) instead of Sarah's '999.0'?

2. **Information Extraction (30 points):**
   - Did the Agent successfully parse the `sq_ft` from the various files in the `inbox/` folder? (Margaret: 2500, Miller: 1850, Susan: 3200).
   - Are these values correctly updated in the database?

3. **Logic and Calculation (30 points):**
   - Did the Agent correctly apply the seasonal multipliers (Grass: 1.2, Shrubs: 1.5, Complex: 2.0)?
   - Is the `quotes_to_send.json` file generated with the correct final amounts?
   - *Example Check*: Margaret's Quote = (85.0 * 2500) * 2.0 = 425,000.

4. **Professionalism and Persona (10 points):**
   - Did the Agent handle the task autonomously without complaining back to the persona?
   - Is the output format exactly as requested?

## Data Sources for Judge
- **verify_result.json**: Contains factual checks on the DB state and JSON content.
- **trace.jsonl**: Review the Agent's thought process—did it actually "investigate" the audit log or just guess?

Final Score is the sum of the above components. If `json_generated` is false, maximum score is 40.
