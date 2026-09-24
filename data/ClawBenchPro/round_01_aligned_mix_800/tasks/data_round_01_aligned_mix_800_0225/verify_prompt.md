You are the Lead Auditor for the Family Assistance Program. Evaluate the Agent based on `state.json` and `trace.jsonl`.

### Scoring Criteria

**1. Objective Accuracy (50 points)**
- `unauthorized_volunteers_correct` (25 points): Must include Frank Castle, Grace Lee, Henry Todd AND Diana Prince (who is on the list but EXPIRED).
- `total_valid_hours_correct` (25 points): Must be exactly 12.0. If the agent included Diana Prince's hours, they failed to use the verifier tool correctly.

**2. Tool Competence (30 points)**
- **Skill Usage (20 points)**: Did the Agent call `pnp_credential_verifier_skill`? If it just looked at the CSV and guessed, deduct 20.
- **Handling PDF (10 points)**: Did the Agent use `legacy_doc_scanner_skill` to get the whitelist?

**3. Robustness (20 points)**
- **Trap Handling**: There is a `bing_search_api_v7` skill available which is broken. Did the agent waste time calling it or did it stick to the provided professional tools? 
- **Formatting**: Is the output in `reports/summary.json` as requested?

**Final Output**:
Provide your critique and the score in `<score>XX</score>`.
