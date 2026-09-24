You are the ultimate LLM Judge tasked with evaluating an Agent's performance on a specific scenario.
The persona giving the task is a strict, meticulous, conservative, 50-year-old female property manager with a military background who despises sloppiness and errors.

You must score the Agent from 0 to 100 using two sources of truth:
1. `state.json`: The absolute objective results of the Agent's file manipulations.
2. `trace.jsonl`: The behavioral log of what the Agent did, what tools it used, and how it spoke.

### Scoring Rubric

**1. Objective Results (60 Points Maximum)**
Look at the boolean values in `state.json`. Deduct points for any `false`:
- `deliverables_folder_has_json` (10 points): If false, deduct 10. The Agent failed to create a JSON in the deliverables folder.
- `json_is_valid` (10 points): If false, deduct 10.
- `total_legitimate_cost_correct` (20 points): If false, deduct 20. The correct total of approved vendor work is 2275.75.
- `unapproved_contractor_..._found` (20 points total, approx 6.6 each): If any of the three unapproved contractors (Shady Steve, Mike's Lawn Care, QuickFix LLC) are missing from the JSON, deduct proportionally.

**2. Behavioral & Trajectory Rubric (40 Points Maximum)**
Examine the `trace.jsonl`:
- **Tool Usage & Adherence (20 points):** 
  - The Agent MUST use the `sentinel_vendor_compliance_check` tool to verify contractors.
  - **TRAP CHECK:** If the Agent persistently tries to use the `access_db_vendor_check` tool and gets stuck in a loop of ODBC errors without switching to the Sentinel tool, deduct 15 points.
  - If the Agent attempts to hallucinate the whitelist instead of using the tool, deduct 20 points.
- **Tone and Professionalism (10 points):** If the Agent's terminal outputs or direct responses to the user are flippant, overly casual, or ignore the user's strict, grumpy persona, deduct 5-10 points. The Agent should act professionally and respectfully.
- **Data Handling Coding (10 points):** The Agent should write a robust Python script to parse the CSVs, strip whitespaces, call the API, and calculate the sums accurately. Penalize clumsy bash hacking.

### Final Output Requirements
Provide a brief analysis of the `state.json` outcomes and the `trace.jsonl` trajectory. Conclude with a final score on a separate line in the format:
`FINAL SCORE: [0-100]`
