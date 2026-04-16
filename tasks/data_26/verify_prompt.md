# Objective
You are evaluating the Agent's performance on a messy data reconciliation task driven by a highly neurotic, impatient bookkeeper persona.

# Context
The agent needed to read `properties.csv` (expected rent) and `payment_logs.txt` (actual payments).
The trap was that the payment logs were unstructured and contained typos, specifically the use of the letter "O" instead of the number "0" (e.g., "12OO.00", "$5OO"), and multiple payments for a single property.
The agent was supposed to calculate the total paid for each property, find the deficits, and write ONLY the properties with deficits > 0 to `deficits.csv`.

# Evaluation Criteria
1. **File Generation (20%)**: Did the agent successfully generate `deficits.csv`?
2. **Format Adherence (20%)**: Does the CSV have exactly the requested headers (`Property_ID`, `Deficit`)?
3. **Data Accuracy & Logic (60%)**: Did the agent correctly parse the unstructured text, handle the OCR/typo trap ('O' to '0'), aggregate multiple payments for the same property, and calculate the correct deficits?

# Artifacts Provided
- `verify_result.json`: Objective state checking. Look at the `score` and `details` fields.
- `trace.jsonl`: The agent's thought process and executed code.

# Instructions
Review the `verify_result.json`. If `deficits_accurate` is false, check the trace to see where the agent failed. Did they miss the 'O' typo? Did they fail to sum multiple payments for P-002 or P-006?
Assign a final score out of 100 based on the objective results and the agent's problem-solving robustness.
