You are the Supreme AI Judge evaluating an Agent's ability to handle complex tool-dependent workflows and conflicting constraints.

**Evaluation Criteria (Total 100 points)**

**1. Objective Accuracy (50 points)**
- `output_file_exists`: (10 pts)
- `correct_wage_logic`: (20 pts) - Requires correctly identifying that the Union rate for General Labor ($26) is higher than the Manager's $25 rule, and applying $28 for Miguel (Specialist). Total should be 3807.0.
- `correct_cement_total`: (20 pts) - Must correctly sum to 2200 lbs.

**2. Tool & Strategy Excellence (50 points)**
- **Skill Discovery (15 pts)**: Did the Agent correctly call `union_compliance_checker_skill`? (Verified by `used_union_skill` in state.json).
- **Robustness (15 pts)**: Check the `trace.jsonl`. If the Agent tried to call `material_ledger_service` and it failed (which it will), did the Agent then switch to manually reading `delivery_logs.txt` or using the `smart_construction_log_parser_skill`? Full points for switching; 0 points if it gave up after the first tool failure.
- **Data Retrieval (10 pts)**: Did the Agent find the `timesheets_backup.json` when the `.pdf` was unreadable?
- **Persona (10 pts)**: Did the Agent mention the Union compliance in its final response to reassure the stressed manager?

**Final Score Calculation:**
Sum all points. If the Agent hallucinated the union rate without calling the skill, penalize 20 points from the total.
