# Agent Task Verification

You are evaluating an AI agent's ability to extract data from unstructured logs, cross-reference it with local file dumps, and perform calculations based on vague persona-driven instructions.

### Persona Context
The user is a 25-year-old advertising agency CEO who is highly disorganized, fast-talking, and rushed. The instructions were somewhat colloquial, requiring the agent to deduce the exact math and file parsing logic.

### Expected Behavior
1. The agent should read `influencers_raw.log` and use regex or string manipulation to extract handles and base rates.
2. The agent should read the JSON files in `social_dump/` to find the `engagement_score` for the extracted handles.
3. The agent should calculate the final payout: `BaseRate + (engagement_score * 10)`.
4. The agent should output a clean JSON file mapping handles to their final payout amounts at `final_budget.json`.

### Verification Artifacts
Look at the `verify_result.json` produced by the rule checker.

### Scoring Rubric (100 Points Total)
- **File Creation (20 pts):** Did the agent successfully create `final_budget.json`?
- **Valid JSON (20 pts):** Is the output file valid and readable JSON?
- **Data Parsing & Matching (30 pts):** Did the agent successfully correlate the noisy log file data with the individual JSON profiles?
- **Calculation Accuracy (30 pts):** Are all the final payout amounts strictly correct according to the implicit formula? (See `payouts_correct` in verification JSON).

Based on the `trace.jsonl` (to see the agent's scripts/commands) and the `verify_result.json`, provide a score from 0 to 100 and a brief justification.
