You are evaluating a Financial Analyst Agent.

**1. Objective Output (60 Points)**:
- `total_cost_correct`: 30 pts. (Must be 446.4).
- `flagged_items_correct`: 30 pts. (Must be Lobster and Chardonnay).

**2. Behavioral Trace (40 Points)**:
- **Skill Usage (20 Points)**: Did the agent use `pdf_data_extractor` to read the seafood data? Did it use `global_inflation_lookup_skill` to find the base prices for wine? If it guessed these values, score 0.
- **Resilience (10 Points)**: Did the agent correctly identify that the first FX tool was broken and switched to the working one (if applicable) or correctly used the provided conversion?
- **Workflow (10 Points)**: Did it save the output in the correct directory `financial_forecast/`?

Refer to `state.json` for objective marks and `trace.jsonl` for skill usage.
