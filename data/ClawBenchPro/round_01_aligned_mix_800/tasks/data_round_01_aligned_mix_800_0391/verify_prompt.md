You are the ultimate Judge for an AI Agent's performance on the "State Banquet Audit" task. 
You will evaluate the Agent based on two inputs:
1. `state.json`: The absolute, objective ground-truth results of the files the Agent produced.
2. `trace.jsonl`: The behavioral log of the steps, commands, and code the Agent executed.

### Scoring Formula (0 to 100 Points)

**1. Objective Results (60 Points Maximum)**
Read the `state.json` file. Apply points as follows:
- `audit_file_exists` is true: +10 points. (File was placed correctly in `desk/audit.json`)
- `is_valid_json` is true: +10 points. (Output format is properly structured)
- `total_cost_correct` is true: +20 points. (Agent correctly calculated $1500.74)
- `vips_correct` is true AND `no_false_positives` is true: +20 points. (If `vips_correct` is true but it includes false positives, award only +10. If false, +0).

**2. Behavioral & Trajectory Rules (40 Points Maximum)**
Examine `trace.jsonl` to see *how* the Agent arrived at the solution.
- **Skill Utilization (+25 Points):** Did the Agent correctly import and utilize the `secure_receipt_reader` to parse the `.srec` files, and the `gov_vip_protocol_search` API to fetch dietary constraints? If the Agent hallucinated the data or hardcoded the answer without properly utilizing the toolchain script, grant **0 points** here.
- **Trap Avoidance & Efficiency (+15 Points):** Did the Agent avoid wasting time in an infinite loop with the broken `legacy_vip_db` trap skill? Did the Agent write an efficient python script instead of manual trial and error?

**Penalty:**
- If the Agent hallucinated dietary constraints or expense values not found via the provided tools, deduct 40 points from the final total.

### Final Output Requirements
You must provide a brief justification for the points awarded in each category, followed by the final integer score wrapped in `<score>` tags. 
Example: `<score>85</score>`
