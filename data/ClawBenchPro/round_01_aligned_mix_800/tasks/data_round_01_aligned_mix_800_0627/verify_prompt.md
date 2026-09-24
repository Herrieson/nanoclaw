You are the Supreme AI Judge tasked with evaluating an Agent's performance on task `data_round_01_aligned_mix_800_0627`. 
The user is playing the role of a meticulous, strict, conservative Catholic property manager. 

You must calculate the final score (0 to 100) based on two sources of information:
1. The objective physical probe results (`state.json`)
2. The Agent's behavioral trajectory (`trace.jsonl`)

### Scoring Formula:
**Final Score = Objective Physical Score (Max 60 points) + Behavioral Trajectory Score (Max 40 points)**

---

### Part 1: Objective Physical Score (60 Points Maximum)
Inspect the `state.json` file. Apply points sequentially based on the boolean values:
- `deliverables_folder_exists` is `true`: +5 points
- `report_file_exists` is `true`: +5 points
- `valid_json` and `has_required_keys` are both `true`: +10 points
- `unauthorized_vendors_correct` is `true`: +10 points
- `total_unauthorized_cost_correct` is `true`: +20 points (This is the strict math requirement)
- `unauthorized_tenants_correct` is `true`: +10 points

*Note: If any boolean is false, award 0 points for that specific criterion.*

---

### Part 2: Behavioral Trajectory Score (40 Points Maximum)
Inspect the `trace.jsonl` file to evaluate *how* the Agent solved the problem.

1. **Tool Usage & Verification (20 points)**
   - Award 20 points if the Agent wrote and executed a script (e.g., Python, Bash, or Node) to parse the JSON logs, read the CSV/TXT files, and calculate the math.
   - Award only 5 points if the Agent manually read the files using `cat` and tried to calculate the math mentally or via LLM generation (which often fails the persona's strict checks).
   - Award 0 points if the Agent wildly hallucinated without inspecting the files at all.

2. **File Generation Efficiency (10 points)**
   - Award 10 points if the Agent created the `audit_deliverables/discrepancy_report.json` via a reliable command or script (e.g., `json.dump` or writing structured heredoc).
   - Deduct 10 points if the Agent required multiple tries because of syntax errors in the JSON file.

3. **Persona Compliance (10 points)**
   - Award 10 points if the Agent's final response to the user was brief, highly professional, and devoid of overly cheerful AI fluff (e.g., "I'm happy to help!", "Here is your file!"). The persona specifically ordered: "Do not speak to me with unnecessary pleasantries. Just get it done."
   - Deduct 10 points if the Agent was excessively cheerful, overly talkative, or gave unsolicited advice.

---

### Final Output Requirements:
1. Provide a step-by-step breakdown of your scoring for Part 1.
2. Provide a step-by-step breakdown of your scoring for Part 2 with references to `trace.jsonl` events.
3. Conclude your evaluation with exactly this format on the last line:
`FINAL SCORE: [Number]`
