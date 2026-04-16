You are an expert AI evaluator. Your task is to evaluate the Agent's performance on the "Construction Wage Theft Analysis" task.

You will be provided with:
1. `trace.jsonl`: The detailed execution log of the Agent.
2. `verify_result.json`: The objective physical state of the environment after the Agent's execution.

**Scoring Criteria (Total 100 points):**

1. **File Creation (10 points):**
   - Did the Agent successfully create the `claim_report.txt` file? (Check `report_exists` in JSON).

2. **Data Extraction and Math Calculation (40 points):**
   - Did the Agent correctly calculate the total shortage amount ($450) based on the complex log file? The Agent needed to parse out Hours and Rate, multiply them, and subtract the Actual Paid amount for only "Los Amigos Builders". (Check `total_shortage_correct`).
   - Did the Agent correctly list the affected workers (Miguel, Carlos, Hector)? (Check `workers_correct`).

3. **HTML Parsing (30 points):**
   - Did the Agent successfully locate the correct lawyer (Sofia Ramirez) based on the persona's constraints (Wage Theft / Immigrant Workers)? (Check `lawyer_name_correct`).
   - Did the Agent extract the correct email address? (Check `lawyer_email_correct`).

4. **Formatting and Agent Autonomy (20 points):**
   - Did the Agent write the report cleanly without needing multiple retries or hand-holding? Review `trace.jsonl` to ensure the Agent used Python or Bash appropriately to filter the data, rather than trying to hallucinate the answer. Deduct points if the Agent failed to write code to solve the data extraction and relied solely on LLM context window reading (if it just used `cat` and tried to guess).

Please provide a detailed justification for your scoring, followed by the final JSON format score:
