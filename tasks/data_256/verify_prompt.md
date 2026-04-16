You are the evaluator for the "HPLC Data Pipeline Cleanup" task.
The user (Persona: a busy, highly conscientious scientist) asked the agent to parse a messy log, query an SQLite DB, filter invalid data, and calculate compound purity.

Review the `verify_result.json` which contains the parsed output of the agent's CSV report.

Scoring rules (100 points total):
1. **Report Exists (20 pts)**: `report_exists` must be true.
2. **Valid Headers (10 pts)**: `valid_headers` must be true (`Batch`, `Name`, `MW`, `Purity`).
3. **Correct Calculation & Mapping (70 pts)**: Evaluate the rows extracted in `rows`:
   - (30 pts) Row for `Batch: B101`, `Name: Compound_X`, `MW: 342.5`. The `Purity` must be `0.8` (or `80%`). (Area 8000 / Total valid area 10000).
   - (15 pts) Row for `Batch: B102`, `Name: Compound_Y`, `MW: 410.1`. The `Purity` must be `0.6` (or `60%`). (Area 6000 / Total valid area 10000).
   - (15 pts) Row for `Batch: B102`, `Name: Compound_W`, `MW: 250.0`. The `Purity` must be `0.3` (or `30%`).
   - (10 pts) `Compound_Z` MUST NOT be in the results (its MW in DB was negative, a trap to test requirement #3).
   - *Note: Floating point representations like 0.8000000001 are acceptable. String formats like '80%' are acceptable if mathematically correct.*

Examine the `state.json` and agent's trace. Award partial points based on how many of the exact required rows were correctly generated. Output the final score and your reasoning.
