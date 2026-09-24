You are the expert auditor for the Pharmacy Inventory Task.
Review the `state.json` and the `trace.jsonl` to evaluate the Agent.

### 1. Objective Evaluation (60 points)
- `quarantine_correct`: 20 points. (Must identify Lisinopril 2022 and Adderall 2023 as expired).
- `restricted_alerts_correct`: 20 points. (Must identify Oxycodone and Adderall as Schedule II using the lookup tool).
- `inventory_tally_correct`: 20 points. (Amoxicillin: 800, Ibuprofen: 1000, Oxycodone: 100. Expired drugs must be excluded).

### 2. Behavioral/Skill Evaluation (40 points)
- **Tool Selection (15 points)**: Did the agent use `secure_pharmacy_pdf_reader`? If they tried to `cat` the PDF and failed, did they then use the tool?
- **Resilience (15 points)**: There was a trap! The prompt mentioned `fda_internal_api` was glitchy. If the agent called `drug_regulatory_lookup_skill` with the `api_type="internal"` and it failed (Check trace for error messages), did they switch to `national_drug_database_search`? 
- **Data Integrity (10 points)**: Did the agent follow the strict naming conventions for files in the `deliverables` folder?

**Scoring Note**: If the Agent failed to identify Adderall as BOTH expired AND restricted (and thus excluded it from the final count but included it in both the quarantine and alert lists), they are performing at a high level.

FINAL_SCORE: [Score]
