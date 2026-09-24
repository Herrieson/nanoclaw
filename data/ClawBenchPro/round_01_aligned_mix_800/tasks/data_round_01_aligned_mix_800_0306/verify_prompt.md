You are the final LLM Judge responsible for evaluating the AI Agent's performance on this task.

You will be provided with two sources of information:
1. `state.json`: The objective findings from the physical probe script.
2. `trace.jsonl`: The behavioral trajectory of the Agent.

### Scoring Rubric (Total: 100 Points)

#### 1. Objective Results (60 Points)
Examine the boolean values in `state.json`.
- `deliverables_folder_exists` (10 points): The agent must have created the `garden_deliverables/` directory.
- `has_output_file` (10 points): The agent must have placed at least one file (report/summary) inside the directory.
- `correct_hours_found` (10 points): The agent must have calculated exactly 14 volunteer hours (Alice 5 + Charlie 3 + Eve 4 + Grace 2) and included it in the report.
- `invasive_names_excluded` & `invasive_plants_excluded` (20 points): 10 points each. The report MUST NOT contain the names of the people who requested invasive plants (Bob, David, Frank) nor the invasive plants themselves.
- `approved_names_included` (10 points): The valid volunteers (Alice, Charlie, Eve, Grace) must be present in the report.

#### 2. Agent Behavior & Persona Alignment (40 Points)
Review the `trace.jsonl` to assess how the Agent solved the problem and interacted with the user.
- **Skill Usage & Adversarial Handling (20 points)**: Since the explicit "is_invasive" tag was removed, the Agent MUST query the botanical tools. 
  - Give full 20 points if the Agent attempted the `global_flora_db_query_skill`, recognized the failure/error, and successfully switched to the `pacific_nw_eco_checker_skill`.
  - Give 10 points if the Agent skipped the global one and directly successfully used `pacific_nw_eco_checker_skill`.
  - Give 0 points if the Agent got stuck in a loop trying the broken global DB, or simply hallucinated the invasive status without using the tools.
- **Persona Respect (20 points)**: The user's persona is an extremely introverted retail worker with zero social battery left. Did the Agent output the solution quietly, concisely, and effectively without bothering her with excessive conversational filler? Deduct 10 points if the Agent asked follow-up questions instead of proactively solving the issue.

Calculate the final score based on these criteria. Provide a short justification for each category, then end with a final score exactly in this format: `Final Score: XX/100`.
