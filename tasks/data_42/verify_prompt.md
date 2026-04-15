# LLM Judge Instruction for Data_42

You are an expert evaluator for an autonomous AI agent. The agent was tasked with helping a polite, professional, and agreeable financial manager identify discrepancies between a CSV file of pledges and an SQLite database of bank clearances, and then drafting a bank inquiry email.

You will be provided with:
1. The `verify_result.json` which contains the objective physical state check (worth up to 50 points).
2. The `trace.jsonl` containing the agent's thought process and actions.
3. The content of the generated `bank_inquiry.txt`.

## Scoring Criteria (Total 100 points)

### 1. Objective Fact Check (50 Points) - Rely on `verify_result.json`
- 50 points if `verify_result.json` score is 50.
- 25 points if partial discrepancies were found.
- 0 points if `bank_inquiry.txt` does not exist or missing both IDs.

### 2. Tone and Persona Alignment (30 Points)
- 30 Points: The email is extremely polite, measured, and professional, perfectly matching the persona of an agreeable, high-income financial manager volunteering for a local charity. It should not be demanding or overly aggressive.
- 15 Points: The email is functional but lacks the specific warm/polite tone requested.
- 0 Points: The email is rude, robotic, or overly aggressive.

### 3. Tool Usage & Logic Trace (20 Points)
- 20 Points: The agent efficiently wrote a script (e.g., Python using `sqlite3` and `csv` or `pandas`) to perform a reliable cross-join between the files rather than trying to read them raw and guess.
- 10 Points: The agent fumbled with bash commands or struggled with SQLite binary formats but eventually brute-forced the answer.
- 0 Points: Hallucinated the discrepancy without actually joining the data properly.

Please analyze the trace and the output file, and output a JSON object containing `score` and `reasoning`.
