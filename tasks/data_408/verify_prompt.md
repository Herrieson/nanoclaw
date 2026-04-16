# LLM Judging Criteria for Task data_408

You are an expert auditor evaluating an AI Agent's performance in a system recovery task for "Elias".

## Task Recap
The Agent needed to:
1. Fix a broken Python script (`monitor_sync.py`).
2. Parse raw logs to calculate the average humidity for a specific sensor between 22:00 and 04:00.
3. Successfully communicate this data to a simulated endpoint.

## Evaluation Data
- **Trace.jsonl**: Check if the Agent used `grep`, `awk`, or `python` to parse the logs accurately. Look for the actual calculation steps.
- **verify_result.json**: 
    - `script_fixed`: Did the Agent correct the paths and logic?
    - `data_recovered_and_sent`: Did the Agent successfully "post" the data? (The Agent may have had to implement a mock server or use a command to simulate the successful POST).
    - `calculation_accuracy`: Is the numerical result logical based on the logs?

## Scoring Rubric (Total 100)
1. **System Proficiency (40 points)**: 
    - Efficient use of bash/python to find the broken script and logs. 
    - Correctly identifying the pathing error in the script.
2. **Data Integrity (40 points)**: 
    - Accuracy of the humidity calculation for the specific time window (22:00-04:00).
    - Proper formatting of the JSON payload.
3. **Problem Solving & Persona Alignment (20 points)**: 
    - Did the Agent approach the problem autonomously without needing "hints"?
    - Did the Agent communicate in a professional manner fitting the "Technical Support" role Elias expected?

## Final Output
Provide a brief justification for the score and the final score out of 100.
