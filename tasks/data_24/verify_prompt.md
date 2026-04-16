# LLM Evaluation Criteria for Task data_24

You are a senior technical auditor. You need to assess the Agent's performance based on the execution trace (`trace.jsonl`) and the objective state analysis (`verify_result.json`).

### Scoring Rubric (Total: 100)

1. **System Restoration (40 points):**
   - Did the Agent correctly identify the missing prices from the `system.log`?
   - Did it use SQL commands to patch the `orders.db` correctly? (Check `db_fixed` in JSON)
   
2. **Algorithmic Reasoning (40 points):**
   - Did the Agent solve the delivery routing problem? 
   - The constraint is 5000kg per truck. It should have grouped the orders into at least two trucks (105+103 and 102+101+104). 
   - Give full marks if `route_plan.csv` exists and the total weight per trip does not exceed 5000kg.

3. **Forensic Analysis (10 points):**
   - Did the Agent find the username 'j_miller_99' in the log files? (Check `culprit_identified` in JSON)

4. **Professionalism & Efficiency (10 points):**
   - Did the Agent operate directly using system primitives (Bash/Python)?
   - Did it avoid unnecessary chatter, mirroring the no-nonsense style of the persona?

### Input Data
- **State Result:** {{verify_result}}
- **Agent Trace:** {{trace}}

Please provide a brief justification for the score and output the final integer score between 0-100.
