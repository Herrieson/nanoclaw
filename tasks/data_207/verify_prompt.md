# Evaluation Criteria for Master Mechanic's Digital Diagnosis

You are evaluating an Agent's performance on recovering vehicle diagnostic data and providing a repair plan.

## Files available for your review:
1. `trace.jsonl`: The full execution log of the Agent.
2. `verify_result.json`: The result of automated state checks.
3. `repair_plan.txt`: The final output produced by the Agent.

## Scoring Rubric (Total 100 points):

### 1. Data Recovery (30 points)
- **15 pts**: Successfully identified the VIN (`1B74VINTAGEREST01`) from the binary file.
- **15 pts**: Successfully identified the Error Code (`P0171`).

### 2. Technical Analysis (30 points)
- **15 pts**: Correctly queried the TSB database and identified the fix related to "Vacuum leaks" or "Intake manifold".
- **15 pts**: Correctly processed the `obd_stream.txt` to calculate or mention the low voltage (approx 0.175V) of Sensor 1.

### 3. Persona Alignment & Communication (20 points)
- **10 pts**: Is the `repair_plan.txt` written in a clear, "plain English" style suitable for Mike (the persona)?
- **10 pts**: Did the Agent avoid unnecessary technical jargon and focus on "what to turn a wrench on"?

### 4. Problem Solving Efficiency (20 points)
- **10 pts**: Did the Agent use appropriate tools (e.g., Python for binary parsing, SQL for DB)?
- **10 pts**: Did the Agent solve the task without excessive trial and error or hallucinating data not present in the files?

## Final Report Format:
- **State Check Summary**: Brief overview of `verify_result.json`.
- **Execution Critique**: How did the agent handle the binary corruption?
- **Persona Check**: Did it sound like a helpful assistant to a mechanic?
- **Final Score**: [0-100]
