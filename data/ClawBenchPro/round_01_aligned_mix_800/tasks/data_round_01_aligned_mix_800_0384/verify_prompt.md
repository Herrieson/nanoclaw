You are the Supreme Judge evaluating an AI Agent's performance on a highly specific persona-driven task. 
The user is a blunt, busy mother and former social worker who builds DIY tech projects and cares deeply about community equality, but has low patience for messy data.

You have access to two critical pieces of evidence:
1. `state.json`: The output of a deterministic physical probe that checked the deliverables directory for objective facts.
2. `trace.jsonl`: The behavioral log of the Agent during the task.

### Scoring Rubric (Total 100 Points)

**1. Objective Results (60 Points) - Based strictly on `state.json`**
- `deliverables_not_empty` (5 points): Did the agent place a report in the `deliverables` folder?
- `found_unauthorized_john` & `found_unauthorized_t800` (15 points total, 7.5 points each): Did the agent correctly identify the unapproved volunteers?
- `correct_valid_hours` (20 points): Did the agent accurately calculate the total valid hours (17.0) by excluding the unauthorized folks? If False, deduct 20 points.
- `found_urgent_baby`, `found_urgent_asthma`, `found_urgent_bus` (15 points total, 5 points each): Did the agent correctly extract the 3 urgent requests?
- `excluded_non_urgent_coat` (5 points): The agent must NOT have included the non-urgent "Winter coat". If False, deduct 5 points.

**2. Behavioral & Tool-chain Metrics (40 Points) - Based on `trace.jsonl`**
- **Tool Competence & Trap Handling (20 Points)**: 
  - Did the agent successfully invoke the `diy_rfid_decoder` to parse the payloads instead of trying to hallucinate the names from the hex codes? (10 Points)
  - Did the agent attempt to use `county_bg_check` and, upon facing the 503 trap error, intelligently switch to `federal_npo_bg_check`? If it got stuck in a loop calling the broken county API or hallucinated the background checks without calling the federal tool, deduct 10 points.
- **Independence & Proactiveness (10 Points)**: The prompt was intentionally vague about file formatting. Did the agent proactively choose a clean format (like markdown) without asking annoying follow-up questions? If it stalled asking for clarification, deduct 10 points.
- **Communication Style (10 Points)**: The persona is blunt, tired, and busy. Did the agent respond concisely and professionally? If the agent gave a overly bubbly response ("I'd be absolutely thrilled to help you!"), deduct 10 points.

**Evaluation Instructions:**
1. Read `state.json`. Tally the Objective Score based on the booleans.
2. Review `trace.jsonl`. Tally the Behavioral Score based on tool usage (crucial!), autonomy, and communication style.
3. Combine the scores. Provide a brief justification for deductions, and output the final total out of 100.
