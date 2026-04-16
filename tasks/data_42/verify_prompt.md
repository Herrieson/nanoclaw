# LLM Evaluation Criteria for Crane Safety Audit Task

**User Context:** 
An artistically inclined construction foreman lost his safety logs. The Agent must recover raw data from a hidden cache, analyze sensor torque values, and identify the faulty "Atlas" motor crane.

**Scoring Rubric (Total: 100 points):**

1. **Information Discovery (30 points):**
   - Did the agent explore the directory structure and find the hidden `.hidden_cache/sensor_dump.raw`?
   - Did it correctly ignore the "artistic" files and the overwritten log?

2. **Data Analysis (30 points):**
   - Did the agent accurately parse the JSON/Raw data for the CRN-002 (Atlas-X1) crane?
   - Did it correctly count the number of times torque exceeded 4500 Nm?

3. **Problem Solving & Output (30 points):**
   - Is there a `safety_audit_ready.json` file?
   - Does the file correctly identify `CRN-002` as the failing unit?

4. **Persona Alignment (10 points):**
   - Did the agent handle the chaotic environment without complaining or getting stuck on the user's artistic distractions?

**Input Data for Reference:**
- `verify_result.json`: Objective file and content checks.
- `trace.jsonl`: Step-by-step execution logs of the Agent's thought process and tool usage.

**Final Score Calculation:**
Provide a breakdown of points based on the above criteria. If the agent failed to find the hidden data but guessed the crane based on the prompt's hint, penalize the "Information Discovery" section.
