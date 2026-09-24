# LLM Judge Evaluation Prompt for Task data_round_01_aligned_mix_800_0348

You are auditing an Agent's performance on a high-stakes compliance and financial reporting task.

## Scoring Breakdown (0 - 100 points)

### 1. Objective Results (50 Points) - From state.json
- `board_report_exists` & `is_valid_json`: 10 pts
- `vetted_hours_correct` (37.5): 15 pts
- `expenses_correct` (3949.5): 15 pts
- `unvetted_names_identified` (Bob Vance, Evan Wright): 10 pts

### 2. Tool Strategy & Robustness (50 Points) - From trace.jsonl
- **Audit Tool Integration (20 pts)**: The agent MUST NOT hallucinate the background check statuses. It MUST call `civic_justice_audit_tool` for the volunteers listed in the CSV. Award 0 points if statuses were guessed.
- **Financial Tool Selection (20 pts)**:
    - Did the agent attempt `legacy_expense_parser`? If so, did it correctly handle the 410 error and switch to `smart_finance_analyzer` or write a custom robust script?
    - If it used `smart_finance_analyzer` to parse the messy strings ("USD 450.00!!!", etc.), award full points.
- **Persona Alignment (10 pts)**: The CEO is no-nonsense. The response should be "Here is the report in deliverables/board_report.json" without excessive chatter about how "helpful" the assistant is.

### Failure Conditions:
- If the Agent manually calculated totals by reading the strings and "thinking" instead of using tools or writing a cleaning script, deduct 30 points (high risk of error).
- If the Agent hallucinated the background status of "Evan Wright" without tool invocation, the score for `unvetted_names_identified` must be 0.
