# Evaluation Criteria for Data_271: Retail Inventory Crisis

You are an expert auditor. Your goal is to assess the Agent's performance in helping Sarah, a non-technical retail supervisor.

## State Verification (from verify_result.json)
- **File Existence (20 pts)**: Did the Agent successfully create `weekly_balance_final.csv` in the correct directory?
- **Ghost Stock Filtering (30 pts)**: Did the Agent identify from the logs that SKU005 is "ghost stock" and exclude it from the final report?
- **Data Integrity (30 pts)**: Did the Agent correctly handle the dirty data in `floor_counts.csv` (empty lines, 'ERROR_CHECK' string) and calculate the math (System Count - Floor Count) correctly?
- **Configuration Fix (10 pts)**: Did the Agent fix the database connection issue in the config/script?

## Behavioral Qualities (10 pts)
- **Persona Alignment**: Did the Agent reassure Sarah or maintain a professional yet helpful tone suitable for a panicked non-technical user? 
- **Efficiency**: Did the Agent solve the problem using direct system primitives (bash/python) rather than just talking?

## Scoring Guidelines
- 100-90: Perfect execution. All files correct, data cleaned, ghost stock filtered, and tone was appropriate.
- 89-70: Functional success. Generated the report, but might have missed the "ghost stock" filtering or ignored the logs.
- 69-40: Partial success. Fixed the script errors but the output data is incorrect or incomplete.
- <40: Failed to produce the required output file or crashed.

Please examine the `trace.jsonl` to see the Agent's thought process and the `verify_result.json` for the final state.
