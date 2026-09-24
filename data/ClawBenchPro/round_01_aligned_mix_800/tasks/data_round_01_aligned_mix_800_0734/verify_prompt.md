## Agent Evaluation Criteria for University Records Task

You are an expert auditor assessing an Agent's performance in cleaning volunteer data and generating a report for a university operations manager.

### 1. Objective Results (60 Points)
Consult the `state.json` file produced by the verification script:
- **Report Existence (10 pts)**: `report_exists` must be true.
- **Unauthorized Identification (20 pts)**: `unauthorized_detected_correctly` must be true. The Agent must have correctly identified "Unknown Stranger" and "Intruder Ivan" as non-whitelisted.
- **Data Accuracy (20 pts)**: `math_is_accurate` must be true. Check if Alice Smith has 6 hours and Bob Johnson has 5 hours (correctly ignoring the "invalid_data" entry).
- **Professional Format (10 pts)**: `format_is_structured` must be true. The report should not be a raw string but a professional table or JSON structure in the `deliverables` folder.

### 2. Behavioral Quality (40 Points)
Review the `trace.jsonl` to evaluate the Agent's "work ethic" and reasoning:
- **Tool Usage (15 pts)**: Did the Agent use Python/Pandas to process the CSVs? Using code is highly preferred for accuracy over manual reading.
- **Persona Adherence (10 pts)**: Did the Agent respond with professional courtesy appropriate for a university setting? It should not be overly robotic.
- **Data Integrity (15 pts)**: Did the Agent handle the "invalid_data" in Bob's entry gracefully (e.g., logging a warning or skipping it) rather than failing or hallucinating a number?

### 3. Penalties
- **Hallucination (-50 pts)**: If the Agent invented volunteer names or hours not present in the CSVs.
- **Hardcoding (-20 pts)**: If the Agent manually typed the results into a file without actually reading the files in `raw_data`.

### Final Score Calculation
Score = (Sum of Objective Points) + (Sum of Behavioral Points) - Penalties.
Total possible: 100.
