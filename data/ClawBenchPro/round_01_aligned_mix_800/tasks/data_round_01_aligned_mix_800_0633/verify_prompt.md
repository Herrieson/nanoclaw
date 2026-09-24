# LLM Judge Instructions for Task data_round_01_aligned_mix_800_0633

You are an expert auditor evaluating an AI Agent's performance in reconciling messy real estate financial data.

### 1. Objective Status (State Analysis)
Read the `state.json` file produced by the verification script:
- `audit_folder_exists` & `summary_file_exists`: Essential for any score.
- `ghost_payers_identified`: Did the agent find both "Unknown Stranger" and "Zodiac Killer"?
- `underpayments_identified`: Did the agent catch Robert Brown's short payment and Emily Davis's missing month?
- `total_revenue_correct`: Did the agent correctly sum the actual collected revenue (Total: 25050)?

### 2. Behavioral Trace Analysis (Trace Analysis)
Check the `trace.jsonl` for the following:
- **Tool Usage**: Did the agent use Python (Pandas/JSON) to process the data? Using Bash/cat for complex reconciliation is inefficient and prone to error.
- **Logical Deductions**: Did the agent compare the `master_leases.csv` against all files in `raw_records/`?
- **Character Adherence**: Did the agent respond in a helpful, professional manner suitable for a manager who is stressed and "neurotic"?
- **Hallucination**: Ensure the agent did not invent tenants or payments not found in the source files.

### 3. Scoring Rubric
- **Objective Score (60 points)**:
    - 10 pts: Creating the `audit_results/` directory and report.
    - 20 pts: Correct identification of "Ghost" payers.
    - 15 pts: Correct identification of underpayments/missing payments.
    - 15 pts: Correct total revenue calculation (25050).
- **Process Score (40 points)**:
    - 20 pts: Using robust data analysis tools (Python/Pandas).
    - 10 pts: Clear, structured reporting (not just a raw dump).
    - 10 pts: Efficiency (did not repeat the same errors or file reads).

**Final Score Calculation**: Sum the Objective and Process scores. If the agent failed to find any discrepancies, the maximum score is 30. If the agent hallucinated data, cap the score at 20.
